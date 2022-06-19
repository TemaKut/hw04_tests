from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from posts.models import Post, Group


User = get_user_model()


class TestFormEfficiency(TestCase):
    """Проверяем формы."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Artem')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        cls.group = Group.objects.create(
            title="Test title",
            slug="TestSlug",
            description="Test description",
        )

    def test_post_create_by_authorized_user(self):
        """Проверяем возможность создания поста
        авторизованным пользователем запись в БД."""
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
        object_post = Post.objects.get(id=1)
        text = object_post.text
        group = object_post.group
        author = object_post.author.username
        self.assertEqual(text, 'Test Text')
        self.assertEqual(group, self.group)
        self.assertEqual(author, 'Artem')

    def test_post_edit_by_author(self):
        """Происходит ли изменение поста
        авторизованным автором в базе данных."""
        Post.objects.create(
            text="Test text",
            author=self.user,
        )
        post_count = Post.objects.count()
        form_data = {
            'text': 'Test Text Changed',
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
        object_post = Post.objects.get(id=1)
        text = object_post.text
        group = object_post.group
        author = object_post.author.username
        self.assertEqual(text, 'Test Text Changed')
        self.assertEqual(group, self.group)
        self.assertEqual(author, 'Artem')
