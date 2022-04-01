import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.reverse_templates = {
            'create': reverse('posts:post_create'),
            'profile': reverse(
                'posts:profile', kwargs={'username': cls.user.username}
            ),
            'edit': reverse(
                'posts:post_edit', kwargs={'post_id': cls.post.id}
            ),
            'detail': reverse(
                'posts:post_detail', kwargs={'post_id': cls.post.id}
            ),
            'add_comment': reverse(
                'posts:add_comment', kwargs={'post_id': cls.post.id}
            )
        }
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded_create = SimpleUploadedFile(
            name='small_create.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.uploaded_edit = SimpleUploadedFile(
            name='small_edit.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.test_data_create = {
            'text': 'Тестовый текст для создания поста',
            'group': cls.group.id,
            'image': cls.uploaded_create,
        }
        cls.test_data_edit = {
            'text': 'Измененный тестовый текст',
            'group': cls.group.id,
            'image': cls.uploaded_edit,
        }
        cls.name_image_create = 'posts/small_create.gif'
        cls.name_image_edit = 'posts/small_edit.gif'
        cls.test_comment = {
            'text': 'Тестовый комментарий',
        }

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        """Валидная форма создает запись в Post"""
        posts_count = Post.objects.count()
        response = self.authorized_client.post(
            self.reverse_templates['create'],
            data=self.test_data_create,
            follow=True
        )
        create_post = response.context['page_obj'][0]
        self.assertRedirects(response, self.reverse_templates['profile'])
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(create_post.text, self.test_data_create['text'])
        self.assertEqual(create_post.group, self.group)
        self.assertEqual(create_post.image, self.name_image_create)

    def test_edit_post(self):
        """Валидная форма изменяет запись в Post"""
        response = self.authorized_client.post(
            self.reverse_templates['edit'],
            data=self.test_data_edit,
            follow=True
        )
        edit_post = Post.objects.get(id=self.post.id)
        self.assertRedirects(response, self.reverse_templates['detail'])
        self.assertEqual(
            edit_post.text, self.test_data_edit['text']
        )
        self.assertEqual(
            edit_post.group_id, self.group.id
        )
        self.assertEqual(
            edit_post.image, self.name_image_edit
        )

    def test_add_comment(self):
        """Валидная форма  создает запись в Comment"""
        response = self.authorized_client.post(
            self.reverse_templates['add_comment'],
            data=self.test_comment,
            follow=True
        )
        comment = response.context['comments'][0]
        self.assertEqual(comment.text, self.test_comment['text'])
