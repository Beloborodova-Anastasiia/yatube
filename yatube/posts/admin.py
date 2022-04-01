from django.contrib import admin

from .models import Group, Post


class PostAdmin(admin.ModelAdmin):
    """Настройки отображения модели Post в интерфейсе админа"""
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group',
        'image',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    """Настройки отображения модели Group в интерфейсе админа"""
    list_display = ('title', 'slug', 'description')
    search_fields = ('title',)
    empty_value_display = '-пусто-'


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
