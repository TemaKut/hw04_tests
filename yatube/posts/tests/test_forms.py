from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Post, Group


User = get_user_model()


class TestFormCreate(TestCase):
    """Проверяем формы."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Artem')
        cls.group = Group.objects.create(
            title="Test title",
            slug="TestSlug",
            description="Test description",
        )
        cls.post = Post.objects.create(
            text="Test text",
            author=cls.user,
        )

    def setUp(self):
        """Создаём пользователя."""
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверяем создала ли форма запись в БД."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Test Text',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'Artem'}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Test Text',
                group=self.group,
            ).exists()
        )

    def test_post_edit(self):
        """Происходит изменение поста с post_id в базе данных."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Test Text',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=('1',)),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:post_detail', args=('1',)))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(
            Post.objects.filter(
                text='Test Text',
                group=self.group,
            ).exists()
        )
