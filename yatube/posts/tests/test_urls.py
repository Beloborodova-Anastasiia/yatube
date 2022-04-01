from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.user_other = User.objects.create_user(username='OtherUser')
        cls.other_authorized_client = Client()
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание тестовой группы',
        )
        cls.public_urls = [
            '/',
            f'/group/{cls.group.slug}/',
            f'/profile/{cls.user.username}/',
            f'/posts/{cls.post.id}/',
        ]
        cls.private_urls = [
            '/create/',
            f'/posts/{cls.post.id}/edit/',
        ]
        cls.templates_urls_names = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.user.username}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{cls.post.id}/edit/': 'posts/create_post.html',
        }

    def test_public_pages_url_exists_at_desired_location(self):
        """Общедоступные страницы доступны любому пользователю."""
        for address in self.public_urls:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_pages_url_exists_at_desired_location__authorized(self):
        """
        Страницы создания поста доступна авторизованному пользователю,
        страница редактирования поста доступна автору поста.
        """
        for address in self.private_urls:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_private_pages_url_redirect_anonymous(self):
        """
        Страницы /create/, /...edit/ перенаправляют
        анонимного пользователя.
        """
        for address in self.private_urls:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_edit_url_redirect_not_author(self):
        """Страница /post/test-slug/edit/ перенаправляет
        не автора поста.
        """
        self.other_authorized_client.force_login(self.user_other)
        response = self.other_authorized_client.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_unexisting_page_response(self):
        """Вызов несуществующей страницы возвращает код 404"""
        response = self.client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for address, template in self.templates_urls_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
