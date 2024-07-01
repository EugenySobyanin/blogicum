from typing import Any

from django.http import HttpRequest
from django.db.models import QuerySet
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.views.generic import ListView, View

from blog.constants import PAGINATE
from blog.models import Comment, Post
from blog.utils import annotate_and_order


class CommentCheckUserMixin(View):
    """Миксин для редактирования и удаления комментариев."""

    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request: HttpRequest,
                 *args: Any, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        if request.user != self.object.author:
            return redirect(self.object.post.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse('blog:post_detail',
                       kwargs={'post_id': self.object.post.pk})


class ListViewMixin(ListView):
    """Миксин для представлений где отображается список постов.

    (Главная, стараница категоии, страница пользователя).
    """

    model = Post
    paginate_by = PAGINATE

    def get_queryset(self) -> QuerySet[Any]:
        queryset = super().get_queryset()
        dt_now = timezone.now()

        return annotate_and_order(
            queryset.select_related(
                'category', 'location', 'author'
            ).filter(
                is_published=True,
                category__is_published=True,
                pub_date__lte=dt_now)
        )


class PostsUpdateDeleteMixin(View):
    """Миксин для представлений редактированя и удаления постов."""

    model = Post
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request: HttpRequest,
                 *args: Any, **kwargs: Any) -> HttpResponse:
        self.object = self.get_object()
        if self.object.author != request.user:
            # Если пользователь не является автором поста,
            # перенаправляем его на страницу этого поста.
            return redirect(self.object.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)
