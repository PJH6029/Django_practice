from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Post, Category, Tag
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify

# Create your views here.
# context는 dict타입
# 기본적으로 super의 get_context_date에 의해서 models.py에 정의된 Post를 불러옴(post_list = Post.objects.all())
# 추가로 categories 등을 추가시킬 수 있


class PostList(ListView):
    model = Post
    ordering = '-pk'

    def get_context_data(self, **kwargs):
        context = super(PostList, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()
        # objects.filter(): 여러개 걸러냄
        # objects.get(): unique한 variable(ex. pk)로 하나만 가져옴

        return context


class PostDetail(DetailView):
    # 특정 post의 category는 Category Class에서 관리하는게 아닌(->이렇게 되면 Category 하나에 여러개의 포스트 pk를 저장해야함), 각 Post에서 관리
    model = Post

    def get_context_data(self, **kwargs):
        context = super(PostDetail, self).get_context_data()
        context['categories'] = Category.objects.all()
        context['no_category_post_count'] = Post.objects.filter(category=None).count()

        return context


class PostCreate(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    # LoginRequiredMixin: 로그인한 사용자만 페이지를 접근할 수 있게 해줌
    # UserPassesTestMixin: 권한 있는 사용자만 페이지를 접근할 수 있게 해줌
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category']
    # author: 이미 로그인 되어있으면 채울 필요 x
    # created_at: 현재시간이므로 필요 x
    # tags: 나중에 방문자가 텍스트로 따로 입력하도록 구현 방법 달리함

    def test_func(self):
        return self.request.user.is_superuser or self.request.user.is_staff

    def form_valid(self, form):
        current_user = self.request.user
        if current_user.is_authenticated and (current_user.is_staff or current_user.is_superuser):
            form.instance.author = current_user
            response = super(PostCreate, self).form_valid(form) # Post에 pk를 부여해서 db에 저장해놓기 위해 먼저 실행

            tags_str = self.request.POST.get('tags_str') # POST로 전달된 정보 중 name='tags_str'인 input값을 가져옴 
            if tags_str:
                tags_str = tags_str.strip()

                tags_str = tags_str.replace(',', ';')
                tags_list = tags_str.split(';')

                for t in tags_list:
                    t = t.strip()
                    tag, is_tag_created = Tag.objects.get_or_create(name=t)
                    if is_tag_created:
                        tag.slug = slugify(t, allow_unicode=True)
                        tag.save()
                    self.object.tags.add(tag)

            return response
        else:
            return redirect('/blog/')


class PostUpdate(LoginRequiredMixin, UpdateView):
    # UserPassesTestMixin 안하는 이유? -> 권한이 아니라 그냥 본인이어야함! 그래서 dispatch 사용
    model = Post
    fields = ['title', 'hook_text', 'content', 'head_image', 'file_upload', 'category', 'tags']

    template_name = 'blog/post_update_form.html'

    def dispatch(self, request, *args, **kwargs):
        # TODO: 왜 current_user = self.request.user 후 current_user.is.authenticated 라고 쓰지 않는가?
        if request.user.is_authenticated and request.user == self.get_object().author:
            # self.get_object() == Post.objects.get(pk=pk)
            return super(PostUpdate, self).dispatch(request, *args, **kwargs)
        else:
            raise PermissionDenied



def category_page(request, slug):
    if slug == 'no_category':
        category = '미분류'
        post_list = Post.objects.filter(category=None)
    else:
        category = Category.objects.get(slug=slug)
        post_list = Post.objects.filter(category=category)

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'category': category,
        }
    )

def tag_page(request, slug):
    tag = Tag.objects.get(slug=slug)
    post_list = tag.post_set.all()
    # post_list = Post.objects.filter(tags=tag)

    return render(
        request,
        'blog/post_list.html',
        {
            'post_list': post_list,
            'categories': Category.objects.all(),
            'no_category_post_count': Post.objects.filter(category=None).count(),
            'tag': tag,
        }
    )

'''
def index(request):
    posts = Post.objects.all().order_by('-pk')

    return render(
        request,
        'blog/post_list.html',
        {
            'posts': posts,
        }
    )

def single_post_page(request, pk):
    post = Post.objects.get(pk=pk)

    return render(
        request,
        'blog/post_detail.html',
        {
            'post': post,
        }
    )
'''
