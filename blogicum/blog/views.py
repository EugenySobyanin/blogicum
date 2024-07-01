from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, QuerySet
from django.db.models.base import Model as Model
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView,
                                  UpdateView,)

from blog.form import CommentForm, PostForm, UserUpdateForm
from blog.models import Category, Post
from blog.mixins import (CommentCheckUserMixin, ListViewMixin,
                         PostsUpdateDeleteMixin)
from blog.utils import annotate_and_order

Users = get_user_model()


class PostListView(ListViewMixin):
    """Список всех опубликованных постов на главноей странице."""

    template_name = 'blog/index.html'


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание поста."""

    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        """Добавление автора поста в объект формы."""
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse(
            'blog:profile',
            kwargs={'username_slug': self.request.user.username})


class PostUpdateView(LoginRequiredMixin, PostsUpdateDeleteMixin, UpdateView):
    """Редактирование поста."""

    form_class = PostForm


class PostDeleteView(LoginRequiredMixin, PostsUpdateDeleteMixin, DeleteView):
    """Удаление поста."""

    success_url = reverse_lazy('blog:index')

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = kwargs['object']
        return context


class PostDetailView(DetailView):
    """Представление отдельного поста."""

    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'

    def get_object(self, queryset=None) -> Model:
        dt_now = timezone.now()
        obj = super().get_object()
        get_object_or_404(
            Post,
            (Q(author=self.request.user.pk)
             | (Q(category__is_published=True)
             & Q(is_published=True)
             & Q(pub_date__lte=dt_now))),
            pk=obj.pk,
        )
        return obj

    def get_context_data(self, **kwargs: reverse_lazy) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = (
            self.object.comments.select_related('author')
        )
        return context


class CategoryListView(ListViewMixin):
    """Представление постов по категории."""

    template_name = 'blog/category.html'

    def get_queryset(self):
        slug = self.kwargs['category_slug']
        get_object_or_404(Category, slug=slug, is_published=True)
        queryset = super().get_queryset().filter(category__slug=slug,)
        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'])
        return context


@login_required
def add_comment(request, post_id):
    """Создание комментария."""
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        # Создаем объект поздравления но не сохраняем его в БД
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id)


class CommentUpdateView(CommentCheckUserMixin, UpdateView):
    """Редактирование комментария."""

    form_class = CommentForm


class CommentDeleteView(CommentCheckUserMixin, DeleteView):
    """Удаление комментария."""


class UserProfileView(ListViewMixin):
    """Представление публикаций на страницах пользователей."""

    template_name = 'blog/profile.html'

    def get_queryset(self) -> QuerySet[Any]:
        user = get_object_or_404(Users, username=self.kwargs['username_slug'])
        if self.request.user != user:
            return super().get_queryset().filter(
                author=user.id
            )
        return annotate_and_order(Post.objects.filter(author=user.id))

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        user = get_object_or_404(Users, username=self.kwargs['username_slug'])
        context['profile'] = user
        return context


def profile_edit(request):
    """Редактирование пользователя."""
    user = get_object_or_404(Users, username=request.user)
    form = UserUpdateForm(request.POST or None, instance=user)
    context = {'form': form}
    if form.is_valid():
        form.save()
        return redirect('blog:profile', user.username)
    return render(request, 'blog/user.html', context)
