from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from .forms import UserRegisterForm, UserLoginForm, PostForm, CommentForm
from .models import Post, Likes, Comment


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"Аккаунт {username} успешно создан")
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, "app/register.html", {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, "Неправильное имя пользователя или пароль!")

    else:
        form = UserLoginForm()
    return render(request, 'app/login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')


@login_required
def home(request):
    # Получаем все объекты Post из базы данных
    posts = Post.objects.all()

    # Передаем список posts в шаблон home.html через контекст
    context = {
        'posts': posts,  # 'posts' - это имя переменной, которое будет доступно в шаблоне
    }
    return render(request, 'app/home.html', context)


@login_required
def post_detail(request, post_id):
    # Получаем конкретный пост по ID или возвращаем 404, если пост не найден.
    post = get_object_or_404(Post, id=post_id)

    user_liked = False
    if request.user.is_authenticated:
        post.user_liked = post.likes.filter(user=request.user).exists()

    comment_form = CommentForm()

    # Можно передать дополнительные данные, например, комментарии
    return render(request, 'app/post_detail.html', {
        'post': post,
        'user_liked': user_liked,
        'comment_form': comment_form,
    })


@login_required
def post_create(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            messages.success(request, "Пост успешно создан!")
            return redirect('home')
    else:
        form = PostForm()
    return render(request, 'app/post_create.html', {'form': form})


@login_required
def post_delete(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        messages.error(request, "Ты чё, пёс?! 🐶 Ты не можешь удалить пост котика!")
        return redirect('home')

    if request.method == "POST":
        post_title = post.title
        post.delete()
        messages.success(request, f"Пост {post_title} успешно удалён!")
        return redirect('home')

    messages.warning(request, "Ты чё, пёс?! 🐶 Для удаления используй кнопку удаления поста!")
    return redirect('post_detail', post_id=post.id)


@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like_obj, created = Likes.objects.get_or_create(user=request.user, post=post)

    if created:
        action = 'liked'
    else:
        like_obj.delete()
        action = 'unliked'
        messages.info(request, f"Вы {action} пост {post.title}.")

    next_url = request.META.get('HTTP_REFERER', reverse('home'))
    return HttpResponseRedirect(next_url)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.author != request.user:
        messages.error("Ты чё, псина дрожащая. Редактировать сей кошачий опус ты права не имеешь!")
        return redirect('home')

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, f"Пост успешно обновлён.")
            return redirect("post_detail", post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, 'app/post_edit.html', {'form': form, 'post': post})


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Твоё мяу засчитано.')
            return redirect('post_detail', post_id=post.id)
    return redirect('post_detail', post_id=post.id)