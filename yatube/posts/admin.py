from django.contrib import admin

from .models import Comment, Follow, Group, Post


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


class CommentAdmin(admin.ModelAdmin):
    """Настройки отображения модели Comment в интерфейсе админа"""
    list_display = ('post', 'text', 'created', 'author')
    search_fields = ('created',)
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    """Настройки отображения модели Follow в интерфейсе админа"""
    list_display = ('author', 'user', 'total_follower', 'total_following', )
    search_fields = ('author',)
    empty_value_display = '-пусто-'

    def total_follower(self, obj):
        return obj.author.following.count()

    def total_following(self, obj):
        return obj.author.follower.count()


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
