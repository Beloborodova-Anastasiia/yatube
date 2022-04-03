from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User


def index(request):
    """View-функция для отображения главной страницы"""
    template = 'posts/index.html'
    index = True
    posts = Post.objects.select_related('group').order_by('-pub_date')
    paginator = Paginator(posts, settings.POSTS_PAGE_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'index': index,
    }
    return render(request, template, context)


def group_posts(request, slug):
    """View-функция для отображение страницы группы"""
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    posts = group.posts.order_by('-pub_date')
    paginator = Paginator(posts, settings.POSTS_PAGE_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = author.posts.order_by('-pub_date')
    posts_count = posts.count()
    paginator = Paginator(posts, settings.POSTS_PAGE_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
            user=request.user,
            author=author,
        ).exists()
    show_button = request.user.is_authenticated and author != request.user
    context = {
        'page_obj': page_obj,
        'posts_count': posts_count,
        'author': author,
        'following': following,
        'is_user': show_button
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    posts_count = author.posts.count()
    post_title = post.text[:settings.POST_TITLE_LIMIT]
    comments = post.comments.order_by('-created')
    form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'posts_count': posts_count,
        'post_title': post_title,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', request.user.username)
    groups = Group.objects.all()
    context = {
        'form': form,
        'groups': groups
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    template = 'posts/create_post.html'
    post = get_object_or_404(Post, id=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post.id)
    is_edit: bool = True
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.save()
        return redirect('posts:post_detail', post.id)
    groups = Group.objects.all()
    context = {
        'is_edit': is_edit,
        'form': form,
        'groups': groups,
        'post': post
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    follow = True
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(posts, settings.POSTS_PAGE_LIMIT)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'follow': follow,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(
            user=request.user,
            author=author,
        )
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = get_object_or_404(Follow, user=request.user, author=author,)
    follow.delete()

    return redirect('posts:profile', username=username)
