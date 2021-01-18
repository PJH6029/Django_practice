from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category, Tag

# Create your tests here.

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        # Class와 Class()의 차이점: variable = Class: variable을 namespace로 사용할 수 있음. 클래스 자체를 넘기는거,, variable = Class(): instance를 생성하는 것
        self.user_trump = User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')
        self.user_obama.is_staff = True
        self.user_obama.save()

        self.category_1 = Category.objects.create(name='category1', slug='category1')
        self.category_2 = Category.objects.create(name='category2', slug='category2')
        # Category의 __init__이 없고, 상속받았으므로, 객체 생성은 superclass 이용해서 하는게 편리

        self.tag_hello = Tag.objects.create(name='hello', slug='hello')
        self.tag_python = Tag.objects.create(name='python', slug='python')
        self.tag_python_kor = Tag.objects.create(name='파이썬 공부', slug='파이썬-공부')

        self.tags = [self.tag_hello, self.tag_python, self.tag_python_kor]

        self.post_001 = Post.objects.create(
            title='첫 번째 포스트입니다',
            content='Hello World',
            category=self.category_1,
            author=self.user_trump,
        )
        self.post_001.tags.add(self.tag_hello) # Many2Many라서 이렇게 연결
        
        self.post_002 = Post.objects.create(
            title='두 번째 포스트입니다',
            content='두번째두번째 두번째',
            category=self.category_2,
            author=self.user_obama,
        )
        self.post_uncategorized = Post.objects.create(
            title='세 번째 포스트입니다',
            content='카테고리가 없는 경우',
            author=self.user_obama,
        )
        # TODO: QuerySet order
        self.post_uncategorized.tags.add(self.tag_python_kor)
        self.post_uncategorized.tags.add(self.tag_python)

        # print(self.post_001.tags.all())
        # print(self.post_uncategorized.tags.all())
        # print(self.post_001.tags.exists())
        # print(self.post_002.tags.exists())
        # print(self.post_uncategorized.tags.exists())


        self.posts = [self.post_001, self.post_002]

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_1.name} ({self.category_1.post_set.count()})', categories_card.text)
        # 전체 카테고리(or Post) 수: Category(or Post).objects.count()
        # 특정 카테고리의 포스트 수: category_name.post_set.count()
        self.assertIn(f'{self.category_2.name} ({self.category_2.post_set.count()})', categories_card.text)
        self.assertIn(f'미분류 ({Post.objects.filter(category=None).count()})', categories_card.text)
        # TODO: 미분류 (uncategorized_post_number) print

    def navbar_test(self, soup):
        # test로 시작하면 함수 내부에서 test함수로 인식해버림
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About Me', navbar.text)

        logo_btn = navbar.find('a', text='Do It Django')
        self.assertEqual(logo_btn.attrs['href'], '/')

        home_btn = navbar.find('a', text='Home')
        self.assertEqual(home_btn.attrs['href'], '/')

        blog_btn = navbar.find('a', text='Blog')
        self.assertEqual(blog_btn.attrs['href'], '/blog/')

        about_me_btn = navbar.find('a', text='About Me')
        self.assertEqual(about_me_btn.attrs['href'], '/about_me/')

    def test_tag_page(self):
        response = self.client.get(self.tag_hello.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.tag_hello.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.tag_hello.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_uncategorized.title, main_area.text)

    def test_category_page(self):
        response = self.client.get(self.category_1.get_absolute_url())
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')
        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.category_1.name, soup.h1.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn(self.category_1.name, main_area.text)
        self.assertIn(self.post_001.title, main_area.text)
        self.assertNotIn(self.post_002.title, main_area.text)
        self.assertNotIn(self.post_uncategorized.title, main_area.text)

    def test_post_list(self):
        postNotFoundMessage = '아직 게시물이 없습니다'
        uncategorizedMessage = '미분류'

        # 포스트가 있는 경우
        self.assertEqual(Post.objects.count(), 3)

        response = self.client.get('/blog/')
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        main_area = soup.find('div', id='main-area')
        self.assertNotIn(postNotFoundMessage, main_area.text)

        assert_dict = {
            0: (self.assertIn, self.assertNotIn, self.assertNotIn),
            1: (self.assertNotIn, self.assertNotIn, self.assertNotIn),
            2: (self.assertNotIn, self.assertIn, self.assertIn)
        }

        for i, post in enumerate(self.posts):
            post_card = main_area.find('div', id=f'post-{i+1}')
            self.assertIn(post.title, post_card.text)
            self.assertIn(post.category.name, post_card.text)
            for j, tag in enumerate(self.tags):
                assert_dict[i][j](tag.name, post_card.text)
            
        post_uncategorized_card = main_area.find('div', id='post-3')
        self.assertIn(self.post_uncategorized.title, post_uncategorized_card.text)
        self.assertIn(uncategorizedMessage, post_uncategorized_card.text)
        for j, tag in enumerate(self.tags):
            assert_dict[2][j](tag.name, post_uncategorized_card.text)

        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_obama.username.upper(), main_area.text)

        # 포스트가 없는 경우
        Post.objects.all().delete()
        # print(f"post list exist? {bool(Post.objects.all().exists())}")
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn(postNotFoundMessage, main_area.text)

    def test_post_detail(self):
        self.assertEqual(self.post_001.get_absolute_url(), '/blog/1/')

        response = self.client.get(self.post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')

        self.navbar_test(soup)
        self.category_card_test(soup)

        self.assertIn(self.post_001.title, soup.title.text)

        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(self.post_001.title, post_area.text)

        self.assertIn(self.user_trump.username.upper(), post_area.text)
        self.assertIn(self.post_001.content, post_area.text)

    def test_create_post(self):
        # log in x: status_code != 200
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # non-staff(trump) log in
        self.client.login(username='trump', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertNotEqual(response.status_code, 200)

        # staff(obama) log in
        self.client.login(username='obama', password='somepassword')
        response = self.client.get('/blog/create_post/')
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Create Post - Blog', soup.title.text)

        main_area = soup.find('div', id='main-area')
        self.assertIn('Create New Post', main_area.text)

        tag_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tag_str_input)

        # TODO: url 마지막에 /이 붙는 이유?
        self.client.post(
            '/blog/create_post/',
            {
                'title': 'Post Form 만들기',
                'content': "Post form page building",
                'tags_str': 'new tag; 한글 태그, python'
            }
        )
        self.assertEqual(Post.objects.count(), 4)
        last_post = Post.objects.last()
        self.assertEqual(last_post.title, "Post Form 만들기")
        self.assertEqual(last_post.author.username, 'obama')

        self.assertEqual(last_post.tags.count(), 3)
        self.assertTrue(Tag.objects.get(name='new tag'))
        self.assertTrue(Tag.objects.get(name='한글 태그'))
        self.assertTrue(Tag.objects.get(name='python'))
        self.assertEqual(Tag.objects.count(), 5)


    def test_update_post(self):
        update_post_url = f'/blog/update_post/{self.post_uncategorized.pk}/'

        # login x
        response = self.client.get(update_post_url)
        self.assertNotEqual(response.status_code, 200)

        # non-staff login
        self.assertNotEqual(self.post_uncategorized.author, self.user_trump)
        self.client.login(
            username=self.user_trump.username,
            passowrd='somepassword'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 403)

        # staff login
        self.client.login(
            username=self.user_obama.username,
            password='somepassword'
        )
        response = self.client.get(update_post_url)
        self.assertEqual(response.status_code, 200)

        soup = BeautifulSoup(response.content, 'html.parser')

        self.assertEqual('Edit Post - Blog', soup.title.text)
        main_area = soup.find('div', id='main-area')
        self.assertIn('Edit Post', main_area.text)

        tags_str_input = main_area.find('input', id='id_tags_str')
        self.assertTrue(tags_str_input)
        self.assertIn('python; 파이썬 공부', tags_str_input.attrs['value'])
        '''
        response = self.client.post(
            update_post_url,
            {
                'title': '세 번째 포스트 수정',
                'content': 'hello world!',
                'category': self.category_1.pk,
                # 'tags_str': '파이썬 공부; 한글 태그, some tag'
                'tags_str': 'python; 한글 태그, some tag'
            },
            follow=True
        )
        '''
        response = self.client.post(
            update_post_url,
            {
                'title': '세 번째 포스트 수정',
                'content': 'hello world!',
                'category': self.category_1.pk,
                # 'tags_str': '파이썬 공부; 한글 태그, some tag'
                'tags_str': 'python; 한글 태그, some tag'
            },
            follow=True
        )

        # response = self.client.get(update_post_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        print(main_area.text)
        self.assertIn('세 번째 포스트 수정', main_area.text)
        self.assertIn('hello world!', main_area.text)
        self.assertIn(self.category_1.name, main_area.text)
        self.assertIn('파이썬 공부', main_area.text)
        # TODO: 파이썬 공부 태그는 이미 있던거라 패스해야하는데 안됨. 확인해보니 main_area.text에 comment들이 들어있음
        self.assertIn('한글 태그', main_area.text)
        self.assertIn('some tag', main_area.text)
        self.assertIn('python', main_area.text)
