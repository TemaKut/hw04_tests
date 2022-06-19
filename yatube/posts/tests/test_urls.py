from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Group, Post

User = get_user_model()


class GuestURLTest(TestCase):
    """Тест доступности урл для неавторизованного юзера."""

    @classmethod
    def setUpClass(cls):
        """Создаём записи в БД."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='Artem')
        cls.guest = Client()
        cls.autorized_user = Client()
        cls.autorized_user.force_login(cls.user)
        cls.group = Group.objects.create(
            title='TestTitle',
            slug='test',
            description='TestDescription',
        )
        cls.post = Post.objects.create(
            text='TestText',
            author=cls.user,
        )

    def test_homepage_public_access(self):
        """Тест общей доступности для пользователей главной страницы."""
        response = self.guest.get("/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_public_access(self):
        """Тест общей доступности для пользователей /group/slug."""
        response = self.guest.get('/group/test/')
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         'Страница недоступна')

    def test_profile_public_access(self):
        """Тест общей доступности для пользователей profile/<str:username>/."""
        response = self.guest.get('/profile/Artem/')
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         'Страница недоступна')

    def test_post_info_public_access(self):
        """Тест общей доступности для пользователей posts/<int:post_id>/."""
        response = self.guest.post('/posts/1/')
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         'Страница о посте недоступна')

    def test_unexisting_page_public_access(self):
        """Тест общей доступности для пользователей 404 page."""
        response = self.guest.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_create_by_authorized_user(self):
        """Тест доступности create для авторизованного."""
        response = self.autorized_user.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK,
                         'Страница create недоступна')

    def test_create_unavailability_by_guest(self):
        """Недоступность для гостя /create/ . (Переадресация)"""
        response = self.guest.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_edit_by_author(self):
        """Доступность posts/<int:post_id>/edit/ для автора."""
        post = Post.objects.get(author=self.user)
        if post:
            response = self.autorized_user.get('/posts/1/edit/')
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_by_guest(self):
        """Не доступность posts/<int:post_id>/edit/
        для пользователя не являющегося автором."""
        self.user_2 = User.objects.create_user(username='Darya')
        self.user_not_author = Client()
        self.user_not_author.force_login(self.user_2)
        post = Post.objects.get(author=self.user)
        if post:
            response = self.user_not_author.get('/posts/1/edit/')
            self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_accordance_urls_and_templates(self):
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
