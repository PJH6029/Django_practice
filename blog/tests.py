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