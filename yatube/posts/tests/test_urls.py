from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class StaticURLTest(TestCase):
    """Тест Урлов (Только главная страница!)."""

    def test_homepage(self):
        guest_client = Client()
        response = guest_client.get("/")
        self.assertEqual(response.status_code, 200)


class GuestURLTest(TestCase):
    """Тест доступности урл для неавторизованного юзера."""

    @classmethod
    def setUpClass(cls):
        """Создаём записи в БД."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='Artem')
        cls.group = Group.objects.create(
            title='TestTitle',
            slug='test',
            description='TestDescription',
        )
        cls.post = Post.objects.create(
            text='TestText',
            author=cls.user,
        )

    def setUp(self):
        self.guest = Client()
        self.autorized_user = Client()
        self.autorized_user.force_login(self.user)

    def test_group_access(self):
        """Тест для неавторизованного /group/slug."""
        response = self.guest.get('/group/test/')
        self.assertEqual(response.status_code, 200, 'Страница недоступна')

    def test_profile_access(self):
        """Тест общедоступности profile/<str:username>/."""
        response = self.guest.get('/profile/Artem/')
        self.assertEqual(response.status_code, 200, 'Страница недоступна')

    def test_post_info(self):
        """Тест общедоступности posts/<int:post_id>/."""
        response = self.guest.post('/posts/1/')
        self.assertEqual(response.status_code, 200,
                         'Страница о посте недоступна')

    def test_unexisting_page(self):
        """Тест общедоступности 404 page."""
        response = self.guest.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)

    def test_create(self):
        """Тест доступности create для авторизованного."""
        response = self.autorized_user.get('/create/')
        self.assertEqual(response.status_code, 200,
                         'Страница create недоступна')

    def test_create_guest(self):
        """Недоступность для гостя /create/ . (Переадресация)"""
        response = self.guest.get('/create/')
        self.assertEqual(response.status_code, 302)

    def test_edit(self):
        """Доступность posts/<int:post_id>/edit/ для автора."""
        post = Post.objects.get(author=self.user)
        if post:
            response = self.autorized_user.get('/posts/1/edit/')
            self.assertEqual(response.status_code, 200)

    def test_templates(self):
        """Проврка на соответствие урл и шаблонов"""
        url_templates_names = {
            '/': 'posts/index.html',
            '/group/test/': 'posts/group_list.html',
            '/profile/Artem/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.autorized_user.get(address)
                self.assertTemplateUsed(response, template)
