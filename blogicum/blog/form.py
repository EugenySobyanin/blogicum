from django import forms
from django.contrib.auth import get_user_model

from blog.models import Comment, Post

Users = get_user_model()


class PostForm(forms.ModelForm):
    """Форма для создания поста на основе модели."""

    class Meta:
        model = Post
        exclude = ('author',)
        widgets = {
            'pub_date': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%d %H:%M:%S',
            )
        }


class CommentForm(forms.ModelForm):
    """Форма для создания комментария на основе модели."""

    class Meta:
        model = Comment
        fields = ('text',)


class UserUpdateForm(forms.ModelForm):
    """Форма измененения профиля пользователя."""

    class Meta:
        model = Users
        fields = ('first_name', 'last_name', 'username', 'email', )
