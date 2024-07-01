from typing import Any

from django.db.models import Count, QuerySet


def annotate_and_order(queryset: QuerySet[Any]) -> QuerySet[Any]:
    """Добавление поля к объектам постов в выборке.

    Добавляем количество комментарив связанных с этим постом
    и соритруем выборку.
    """
    return queryset.annotate(
        comment_count=Count('comments')).order_by('-pub_date')
