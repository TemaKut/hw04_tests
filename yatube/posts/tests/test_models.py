from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    """Тестируем модель поста на 15 символов поста и название группы."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='TestGroupTitle',
            slug='TestSlug',
            description='TestDescription',
        )
        cls.post = Post.objects.create(
            text='а' * 15,
            author=cls.user,
        )

    def test_post_model_str(self):
        """Корректность работы __str__ поста."""
        post = PostModelTest.post
        text_post = post.text
        self.assertEqual(text_post, str(post), 'Работает некорректно!')

    def test_group_model(self):
        """Корректность работы __str__ группы."""
        group = PostModelTest.group
        gtoup_title = group.title
        self.assertEqual(gtoup_title, str(group),
                         'Что-то не так с отображением группы')

    def test_post_verbowses(self):
        """Тест на наличие VN в посте."""
        post = PostModelTest.post
        field_verboses = {
            'author': 'Автор поста',
            'group': 'Группа',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)
