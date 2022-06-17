from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from .models import Post, Group, User
from .forms import PostForm
from .utils import paginator


def _get_post_objects():
    """Получаем объекты модели пост."""
    result = Post.objects.all()

    return result


def index(request):
    """Вывод главной страницы с постами."""
    posts = _get_post_objects()
    context = {
        'page_obj': paginator(request, posts),
    }

    return render(request, "posts/index.html", context)


def group_posts(request, slug):
    """Вывод страницы с постами конкретной группы."""
    group = Group.objects.get(slug=slug)
    posts = group.posts.all()

    context_group = {
        'group': group,
        'page_obj': paginator(request, posts),
    }

    return render(request, "posts/group_list.html", context_group)


def profile(request, username):
    """Вывод страницы с постами конкретного пользователя."""
    user = get_object_or_404(User, username=username)
    posts = user.posts.all()

    context_profile = {
        'author': user,
        'page_obj': paginator(request, posts),
    }

    return render(request, "posts/profile.html", context_profile)


def post_detail(request, post_id):
    """Вывод информации о конкретном посте."""
    post_valid = get_object_or_404(Post, id=post_id)
    context_detail = {
        'post_valid': post_valid,
    }

    return render(request, "posts/post_detail.html", context_detail)


@login_required
def post_create(request):
    """Страница создания поста."""
    form = PostForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        form.save()

        return redirect('posts:profile', username=request.user.username)

    return render(request, "posts/create_post.html", {'form': form})


@login_required
def post_edit(request, post_id):
    """Страница редактирования созданного ранее поста."""
    post_obj = Post.objects.get(id=post_id)
    form = PostForm(request.POST or None, instance=post_obj)
    if request.user == post_obj.author and post_obj:
        if request.method == 'POST' and form.is_valid():
            form.author = request.user
            form.save()

            return redirect(
                'posts:post_detail',
                post_id=post_id,
            )

        return render(
            request,
            "posts/create_post.html",
            {'is_edit': True, 'form': form, },
        )

    return redirect(
        'posts:post_detail',
        post_id=post_id,
    )
