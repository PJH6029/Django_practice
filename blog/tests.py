from django.test import TestCase, Client
from bs4 import BeautifulSoup
from django.contrib.auth.models import User
from .models import Post, Category

# Create your tests here.

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        # Class와 Class()의 차이점: variable = Class: variable을 namespace로 사용할 수 있음. 클래스 자체를 넘기는거,, variable = Class(): instance를 생성하는 것
        self.user_trump = User.objects.create_user(username='trump', password='somepassword')
        self.user_obama = User.objects.create_user(username='obama', password='somepassword')

        self.category_1 = Category.objects.create(name='category1', slug='category1')
        self.category_2 = Category.objects.create(name='category2', slug='category2')
        # Category의 __init__이 없고, 상속받았으므로, 객체 생성은 superclass 이용해서 하는게 편리

        self.post_001 = Post.objects.create(
            title='첫 번째 포스트입니다',
            content='Hello World',
            category=self.category_1,
            author=self.user_trump,
        )
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

        self.posts = [self.post_001, self.post_002]

    def category_card_test(self, soup):
        categories_card = soup.find('div', id='categories-card')
        self.assertIn('Categories', categories_card.text)
        self.assertIn(f'{self.category_1.name} ({self.category_1.post_set.count()})', categories_card.text)
        # 전체 카테고리(or Post) 수: Category(or Post).objects.count()
        # 특정 카테고리의 포스트 수: category_name.post_set.count()
        self.assertIn(f'{self.category_2.name} ({self.category_2.post_set.count()})', categories_card.text)
        self.assertIn(f'미분류 (1)', categories_card.text)
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

        for i, post in enumerate(self.posts):
            post_card = main_area.find('div', id=f'post-{i+1}')
            self.assertIn(post.title, post_card.text)
            self.assertIn(post.category.name, post_card.text)
            
        post_uncategorized_card = main_area.find('div', id='post-3')
        self.assertIn(self.post_uncategorized.title, post_uncategorized_card.text)
        self.assertIn(uncategorizedMessage, post_uncategorized_card.text)

        self.assertIn(self.user_trump.username.upper(), main_area.text)
        self.assertIn(self.user_obama.username.upper(), main_area.text)

        # 포스트가 없는 경우
        Post.objects.all().delete()
        self.assertEqual(Post.objects.count(), 0)
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        main_area = soup.find('div', id='main-area')
        self.assertIn(postNotFoundMessage, main_area.text)


    '''
    def test_post_detail(self):
        # 1.1 포스트가 하나 있음
        post_001 = Post.objects.create(
            title='첫 번째 포스트',
            content='Hello World',
            author=self.user_trump,
        )
        self.assertEqual(Post.objects.count(), 1)
        # 1.2 그 포스트의 url은 '/blog/1/'임임
        self.assertEqual(post_001.get_absolute_url(), '/blog/1/')

        # 2 첫 번째 포스트의 상세 페이지 테스트
        # 2.1 첫 번째 포스트의 url로 접근하면 정상적으로 작동
        response = self.client.get(post_001.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        soup = BeautifulSoup(response.content, 'html.parser')
        # 2.2 포스트 목록 페이지와 똑같은 내비게이션 바가 존재
        self.navbar_test(soup)
        # 2.3 첫 번째 포스트의 제목이 웹 브라우저 탭 타이틀에 있음
        self.assertIn(post_001.title, soup.title.text)
        # 2.4 첫 번째 포스트의 제목이 포스트 영역에 있음
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(post_001.title, post_area.text)
        # 2.5 첫 번째 포스트의 작성자가 포스트 영역에 있음
        self.assertIn(self.user_trump.username.upper(), post_area.text)
        # 2.6 첫 번째 포스트의 내용이 포스트 영역에 있음
        self.assertIn(post_001.content, post_area.text)
    '''
