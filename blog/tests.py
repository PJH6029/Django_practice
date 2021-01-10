from django.test import TestCase, Client
from bs4 import BeautifulSoup
from .models import Post

# Create your tests here.

class TestView(TestCase):
    def setUp(self):
        self.client = Client()
        # Class와 Class()의 차이점: variable = Class: variable을 namespace로 사용할 수 있음. 클래스 자체를 넘기는거,, variable = Class(): instance를 생성하는 것

    def test_post_list(self):
        # 1.1 포스트 목록 페이지 가져오기
        response = self.client.get('/blog/')
        # 1.2 정상적으로 페이지 로드
        self.assertEqual(response.status_code, 200)
        # 1.3 페이지 타이틀은 'Blog'
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(soup.title.text, 'Blog')
        # 1.4 내비게이션 바 존재
        navbar = soup.nav
        # 1.5 Blog, About Me가 내비게이션 바 문구에 있음
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)

        postNotFoundMessage = '아직 게시물이 없습니다'
        # 2.1 메인 영역에 게시물이 하나도 없다면
        self.assertEqual(Post.objects.count(), 0)
        # 2.2 '아직 게시물이 없습니다'라는 문구가 보임
        main_area = soup.find('div', id='main-area')
        self.assertIn(postNotFoundMessage, main_area.text)

        # 3.1 게시물이 2개 있다면
        post_001 = Post.objects.create(
            title='첫 번째 포스트입니다',
            content='Hello World',
        )
        post_002 = Post.objects.create(
            title='두 번째 포스트입니다',
            content='두번째두번째 두번째',
        )
        self.assertEqual(Post.objects.count(), 2)
        # 3.2 포스트 목록 페이지를 새로고침했을 때
        response = self.client.get('/blog/')
        soup = BeautifulSoup(response.content, 'html.parser')
        self.assertEqual(response.status_code, 200)
        # 3.3 main area 영역에 포스트 2개의 타이틀이 존재.
        main_area = soup.find('div', id='main-area')
        self.assertIn(post_001.title, main_area.text)
        self.assertIn(post_002.title, main_area.text)
        # 3.4 '아직 게시물이 없습니다'라는 문구는 더 이상 보이지 않음
        self.assertNotIn(postNotFoundMessage, main_area.text)

    def test_post_detail(self):
        # 1.1 포스트가 하나 있음음
        post_001 = Post.objects.create(
            title='첫 번째 포스트',
            content='Hello World'
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
        navbar = soup.nav
        self.assertIn('Blog', navbar.text)
        self.assertIn('About me', navbar.text)
        # 2.3 첫 번째 포스트의 제목이 웹 브라우저 탭 타이틀에 있음
        self.assertIn(post_001.title, soup.title.text)
        # 2.4 첫 번째 포스트의 제목이 포스트 영역에 있음
        main_area = soup.find('div', id='main-area')
        post_area = main_area.find('div', id='post-area')
        self.assertIn(post_001.title, post_area.text)
        # 2.5 첫 번째 포스트의 작성자가 포스트 영역에 있음
        # TODO
        # 2.6 첫 번째 포스트의 내용이 포스트 영역에 있음
        self.assertIn(post_001.content, post_area.text)