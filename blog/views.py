from django.shortcuts import render
from django.views.generic import ListView, DetailView
from .models import Post, Category, Tag

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
