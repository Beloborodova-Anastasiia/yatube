import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.client = Client()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.following = User.objects.create_user(username='Following')
        cls.follower = User.objects.create_user(username='Follower')
        cls.authorized_follower = Client()
        cls.authorized_follower.force_login(cls.follower)
        cls.follow = Follow.objects.create(
            user=cls.follower,
            author=cls.following,
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.test_group = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-other',
            description='Тестовое описание 2',
        )
        cls.post_is_edit = True
        for i in range(1, 14):
            Post.objects.create(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group
            )
        cls.post_test_edit = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для редактирования',
            group=cls.group,
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост последний для проверки шаблона',
            group=cls.group,
            image=cls.uploaded,
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Тестовый комментарий',
            post=cls.post,
        )
        cls.templates_page_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', kwargs={'username': cls.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': cls.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': cls.post.id}
            ): 'posts/create_post.html',
        }
        cls.reverse_templates = {
            'index': reverse('posts:index'),
            'group': reverse(
                'posts:group_list', kwargs={'slug': cls.group.slug}
            ),
            'group-other': reverse(
                'posts:group_list', kwargs={'slug': cls.test_group.slug}
            ),
            'profile': reverse(
                'posts:profile', kwargs={'username': cls.user.username}
            ),
            'detail': reverse(
                'posts:post_detail', kwargs={'post_id': cls.post.id}
            ),
            'create': reverse('posts:post_create'),
            'edit': reverse(
                'posts:post_edit', kwargs={'post_id': cls.post.id}
            ),
            'edit_guest': reverse(
                'posts:post_edit', kwargs={'post_id': cls.post_test_edit.id}
            ),
            'add_comment': reverse(
                'posts:add_comment', kwargs={'post_id': cls.post.id}
            ),
            'follow': reverse(
                'posts:profile_follow', kwargs={
                    'username': cls.following.username
                }
            ),
            'unfollow': reverse(
                'posts:profile_unfollow', kwargs={
                    'username': cls.following.username
                }
            ),
            'follow_index': reverse('posts:follow_index'),
        }
        cls.page_names = {
            cls.reverse_templates['index'],
            cls.reverse_templates['group'],
            cls.reverse_templates['profile'],
        }
        cls.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        cls.posts_count = {
            'all': Post.objects.count(),
            'group': Post.objects.filter(group=cls.group).count(),
            'author': Post.objects.filter(group=cls.group).count(),
        }
        cls.page_limit = settings.POSTS_PAGE_LIMIT
        cls.create_text = 'Создание тестового поста',
        cls.test_data_edit = {
            'text': 'Измененный тестовый текст',
            'group': cls.test_group.id,
        }
        cls.test_comment_authorized = {
            'text': 'Комментарий авторизованного пользователя'
        }
        cls.test_comment_guest = {
            'text': 'Комментарий неавторизованного'
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for reverse_name, template in self.templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.reverse_templates['index']
        )
        first_object = response.context['page_obj'][0]
        page_context = {
            first_object.text: self.post.text,
            first_object.group: self.post.group,
            first_object.author: self.post.author,
            first_object.pub_date: self.post.pub_date,
            first_object.image: self.post.image,
        }
        for response, expected in page_context.items():
            with self.subTest(response=response):
                self.assertEqual(response, expected)

    def test_group_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.reverse_templates['group']
        )
        first_object = response.context['page_obj'][0]
        page_context = {
            first_object.text: self.post.text,
            first_object.group: self.post.group,
            first_object.author: self.post.author,
            first_object.pub_date: self.post.pub_date,
            first_object .image: self.post.image,
            response.context['group']: self.group,
        }
        for response, expected in page_context.items():
            with self.subTest(response=response):
                self.assertEqual(response, expected)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.reverse_templates['profile']
        )
        first_object = response.context['page_obj'][0]
        page_context = {
            first_object.text: self.post.text,
            first_object.group: self.post.group,
            first_object.author: self.post.author,
            first_object.pub_date: self.post.pub_date,
            first_object .image: self.post.image,
            response.context['posts_count']: self.posts_count['author'],
            response.context['author']: self.user,
        }
        for response, expected in page_context.items():
            with self.subTest(response=response):
                self.assertEqual(response, expected)

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.reverse_templates['detail']
        )
        page_context = {
            response.context['post'].text: self.post.text,
            response.context['post'].group: self.post.group,
            response.context['post'].author: self.post.author,
            response.context['post'].pub_date: self.post.pub_date,
            response.context['post'].image: self.post.image,
            response.context['posts_count']: self.posts_count['author'],
            response.context['comments'][0]: self.comment
        }
        for response, expected in page_context.items():
            with self.subTest(response=response):
                self.assertEqual(response, expected)

    def test_create_page_show_correct_context(self):
        """Шаблон create сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.reverse_templates['create']
        )
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            self.reverse_templates['edit']
        )
        page_context = {
            response.context['post'].text: self.post.text,
            response.context['post'].group: self.post.group,
            response.context['is_edit']: self.post_is_edit,
        }
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        for response, expected in page_context.items():
            with self.subTest(response=response):
                self.assertEqual(response, expected)

    def test_first_page_contains_ten_records(self):
        """Количество постов на первой странице равно 10"""
        for page_name in self.page_names:
            with self.subTest(page_name=page_name):
                response = self.client.get(page_name)
                self.assertEqual(
                    response.context['page_obj'].start_index(), 1
                )
                self.assertEqual(
                    response.context['page_obj'].end_index(), self.page_limit
                )

    def test_second_page_contains_ten_records(self):
        """Количество постов на втрой странице"""
        page_names = {
            self.reverse_templates[
                'index'
            ] + '?page=2': self.posts_count['all'],
            self.reverse_templates[
                'group'
            ] + '?page=2': self.posts_count['group'],
            self.reverse_templates[
                'profile'
            ] + '?page=2': self.posts_count['author'],
        }
        for page_name, posts_count in page_names.items():
            with self.subTest(page_name=page_name):
                response = self.client.get(page_name)
                self.assertEqual(
                    response.context[
                        'page_obj'
                    ].start_index(), self.page_limit + 1
                )
                self.assertEqual(
                    response.context['page_obj'].end_index(), posts_count
                )

    def test_new_post_appeared_on_the_pages(self):
        """
        Проверка появления нового поста в контексте шаблонов главной страницы,
        страницы группы и профиля пользователя. Отстутствие нового поста в
        контексте шаблона группы, к которой пост не принадлежит.
        """
        create_post = Post.objects.create(
            author=self.user,
            text=self.create_text,
            group=self.group
        )
        for page_name in self.page_names:
            with self.subTest(page_name=page_name):
                response = self.client.get(page_name)
                self.assertIn(create_post, response.context['page_obj'])
        response = self.client.get(self.reverse_templates['group-other'])
        self.assertNotIn(create_post, response.context['page_obj'])

    def test_edit_post_changed_on_the_pages(self):
        """
        Проверка изменения текста поста в контексте шаблонов главной страницы,
        страницы группы и профиля пользователя.
        """
        page_names = {
            self.reverse_templates['index'],
            self.reverse_templates['group-other'],
            self.reverse_templates['profile'],
        }
        response = self.authorized_client.post(
            self.reverse_templates['edit'],
            data=self.test_data_edit,
            follow=True
        )
        for page_name in page_names:
            with self.subTest(page_name=page_name):
                response = self.client.get(page_name)
                self.assertIn(self.post, response.context['page_obj'])
        response = self.client.get(self.reverse_templates['group'])
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_post_not_edit_quest_user(self):
        """
        Контекст шаблонов не изменяется при попытке редактирования
        неавторизованным пользователем.
        """
        response = self.client.post(
            self.reverse_templates['edit_guest'],
            data=self.test_data_edit,
            follow=True
        )
        for page_name in self.page_names:
            with self.subTest(page_name=page_name):
                response = self.client.get(page_name)
                self.assertIn(self.post, response.context['page_obj'])
        response = self.client.get(self.reverse_templates['group-other'])
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_new_comment_appeared_on_post_page(self):
        """Новый комментарий появляется на странице поста"""
        create_comment = Comment.objects.create(
            author=self.user,
            text='Тест создания комментария',
            post=self.post,
        )
        response = self.client.get(f'/posts/{self.post.id}/')
        self.assertIn(create_comment, response.context['comments'])

    def test_comment_add_authorized_user(self):
        """Комментарий может оставлять только авторизованный пользователь"""
        response = self.client.post(
            self.reverse_templates['add_comment'],
            data=self.test_comment_guest,
            follow=True
        )
        response = self.client.get(self.reverse_templates['detail'])
        self.assertNotEqual(
            response.context[
                'comments'
            ][0].text, self.test_comment_guest['text']
        )
        response = self.authorized_client.post(
            self.reverse_templates['add_comment'],
            data=self.test_comment_authorized,
            follow=True
        )
        response = self.client.get(self.reverse_templates['detail'])
        self.assertEqual(
            response.context[
                'comments'
            ][0].text, self.test_comment_authorized['text']
        )

    def test_cache(self):
        """Главная страница кэшируется"""
        create_post = Post.objects.create(
            author=self.user,
            text='Тестовый пост для кэширования',
            group=self.group,
        )
        response = self.authorized_client.get(
            self.reverse_templates['index']
        ).content
        create_post.delete()
        response_cached = self.authorized_client.get(
            self.reverse_templates['index']
        ).content
        self.assertEqual(response, response_cached)
        cache.clear()
        response_non_cached = self.authorized_client.get(
            self.reverse_templates['index']
        ).content
        self.assertNotEqual(response, response_non_cached)

    def test_following_authorized_user(self):
        """
        Авторизованный пользователь может подписываться на других авторов
        и отписываться от них
        """
        self.authorized_client.get(self.reverse_templates['follow'])
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.following
            ).exists()
        )
        self.authorized_client.get(self.reverse_templates['unfollow'])
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.following
            ).exists()
        )

    def test_new_post_appeared_in_following(self):
        """Новый пост появляется в ленте только подписавшегося пользователя"""
        new_post = Post.objects.create(
            author=self.following,
            text=self.create_text,
        )
        response_unfollower = self.authorized_client.get(
            self.reverse_templates['follow_index']
        )
        response_follower = self.authorized_follower.get(
            self.reverse_templates['follow_index']
        )
        self.assertIn(new_post, response_follower.context['page_obj'])
        self.assertNotIn(new_post, response_unfollower.context['page_obj'])
