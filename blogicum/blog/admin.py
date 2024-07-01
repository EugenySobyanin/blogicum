from django.contrib import admin

from blog.models import Category, Comment, Location, Post

admin.site.empty_value_display = 'Не задано'


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'is_published',
        'pub_date',
        'author',
        'location',
        'category'
    )
    list_editable = ('is_published', 'pub_date',)
    search_fields = ('title',)
    list_filter = ('author', 'category', 'location')
    list_display_links = ('title',)


admin.site.register(Post, PostAdmin)
admin.site.register(Category)
admin.site.register(Location)
admin.site.register(Comment)
