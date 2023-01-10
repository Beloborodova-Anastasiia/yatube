from django.contrib.auth import get_user_model
from django.test import TestCase
from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!',
        )
        cls.field_str = {
            cls.post: cls.post.text[:15],
            cls.group: cls.group.title,
        }
        cls.field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        cls.field_help = {
            'text': 'Введите текст поста',
            'group': 'Группа, к которой будет относиться пост',
        }

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        for field, expected_value in self.field_str.items():
            with self.subTest(field=field):
                self.assertEqual(
                    expected_value, str(field))

    def test_models_verbose_name(self):
        """Проверяем verbose_name моделей"""
        for field, expected_value in self.field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(
                        field
                    ).verbose_name, expected_value
                )

    def test_models_help_text(self):
        """Проверяем help моделей"""
        for field, expected_value in self.field_help.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, expected_value)
