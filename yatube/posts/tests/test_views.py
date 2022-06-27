from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from django.core.cache import cache

from posts.models import Post, Group
from posts.constants import NUM_PAGE, TEST_PAGE_2


User = get_user_model()


class TestPostViews(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Artem')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание')
        cls.post = Post.objects.create(
            author=cls.author,
            text=('Тестовый пост для тестирования'),
            group=cls.group)
        cls.index = 'posts:home'
        cls.group_post = 'posts:group'
        cls.profile = 'posts:profile'
        cls.post_id = 'posts:post_detail'
        cls.create = 'posts:post_create'
        cls.edit = 'posts:post_edit'

    def setUp(self):
        self.user = User.objects.create_user(username='test_user')
        self.authorized_client = Client()
        self.author_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client.force_login(self.author)

    def check_add_post_in_context(self, obj_1):
        """Этот метод проверяет на соответствие
        объекты поста в БД и соответствующем контексте. на входе необходимо
        указать объект из БД а так же объект из контекста view."""
        obj_2 = self.post
        self.assertEqual(obj_1.id, obj_2.id)
        self.assertEqual(obj_1.text, obj_2.text)
        self.assertEqual(obj_1.group, obj_2.group)
        self.assertEqual(obj_1.author.username, obj_2.author.username)

    def test_correct_templates(self):
        """URL использует нужный шаблон."""
        url_templates = {reverse(self.index): 'posts/index.html',
                         reverse(self.create): 'posts/create_post.html',
                         reverse(self.group_post,
                                 kwargs={'slug': 'test_slug'}):
                         'posts/group_list.html',
                         reverse(self.profile, kwargs={'username': 'Artem'}):
                         'posts/profile.html',
                         reverse(self.post_id,
                                 kwargs={'post_id': TestPostViews.post.pk}):
                         'posts/post_detail.html',
                         reverse(self.edit,
                                 kwargs={'post_id': TestPostViews.post.pk}):
                         'posts/create_post.html'}
        for reverse_name, template in url_templates.items():
            with self.subTest(template=template):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        """Шаблон index с правильным контекстом."""
        response = self.client.get(reverse(self.index))
        first_obj = response.context['page_obj'].object_list[0]
        self.check_add_post_in_context(first_obj)

    def test_group_posts_context(self):
        """Шаблон group_list с правильным контекстом."""
        response = self.client.get(reverse(
            self.group_post, kwargs={'slug': 'test_slug'}))
        first_obj = response.context['page_obj'].object_list[0]
        self.check_add_post_in_context(first_obj)
        context_group = response.context['group']
        self.assertEqual(context_group.slug, 'test_slug')

    def test_profile_context(self):
        """Шаблон profile с правильным контекстом."""
        response = self.client.get(reverse(
            self.profile, kwargs={'username': 'Artem'}))
        first_obj = response.context['page_obj'].object_list[0]
        self.check_add_post_in_context(first_obj)
        author = response.context['author']
        self.assertEqual(author.username, 'Artem')

    def test_post_detail_context(self):
        """Шаблон post_detail  с правильным контекстом."""
        response = self.client.get(
            reverse(self.post_id, kwargs={'post_id': TestPostViews.post.pk}))
        first_obj = response.context['post_valid']
        self.check_add_post_in_context(first_obj)

    def test_create_context(self):
        """Шаблон post_create с правильным контекстом."""
        response = self.authorized_client.get(reverse(self.create))
        form_fields = {'text': forms.fields.CharField,
                       'group': forms.fields.ChoiceField}
        for field, field_type in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context['form'].fields[field]
                self.assertIsInstance(form_field, field_type)

    def test_post_edit_context(self):
        """Шаблон post_edit  с правильным контекстом."""
        response = self.author_client.get(reverse(
            self.edit, kwargs={'post_id': self.post.pk}))
        form_fields = {'text': forms.fields.CharField,
                       'group': forms.fields.ChoiceField}
        for field, field_type in form_fields.items():
            with self.subTest(field=field):
                form_field = response.context['form'].fields[field]
                self.assertIsInstance(form_field, field_type)

    def test_new_post_in_pages(self):
        """Пост не попадает в ненужную группу."""
        self.group = Group.objects.create(
            title='Неправильная группа',
            slug='wrong',
            description='Не та группа')
        response = self.client.get(reverse(
            self.group_post, kwargs={'slug': 'wrong'}))
        self.assertEqual(response.context['page_obj'].paginator.count, 0)
        Post.objects.create(
            author=TestPostViews.author,
            text='Тестовый пост для тестирования неверной группы',
            group=TestPostViews.group)
        cache.clear()
        response = self.client.get(reverse(
            self.group_post, kwargs={'slug': 'wrong'}))
        self.assertEqual(response.context['page_obj'].paginator.count, 0)
        responses = (self.client.get(reverse(self.index)),
                     self.client.get(reverse(
                         self.group_post, kwargs={'slug': 'test_slug'})),
                     self.client.get(reverse(
                         self.profile, kwargs={'username': 'Artem'})))
        for response in responses:
            with self.subTest(response=response):
                self.assertEqual(response.context['page_obj'].paginator.count,
                                 2)

    def test_paginators(self):
        """Выводится правильное количество постов."""
        postss = (
            (Post(author=self.author,
                  text=f'Тестовый пост {i}',
                  group=self.group,
                  ))for i in range(NUM_PAGE + TEST_PAGE_2 - 1)
        )

        self.post = Post.objects.bulk_create(list(postss))

        responses = (self.client.get(reverse(self.index)),
                     self.client.get(reverse(
                         self.group_post,
                         kwargs={'slug': 'test_slug'})),
                     self.client.get(reverse(
                         self.profile,
                         kwargs={'username': 'Artem'})))

        for response in responses:
            with self.subTest(response=response):
                self.assertEqual(len(response.context['page_obj'].object_list),
                                 NUM_PAGE)

        responses = (self.client.get(reverse(self.index) + '?page=2'),
                     self.client.get(reverse(
                         self.group_post,
                         kwargs={'slug': 'test_slug'}) + '?page=2'),
                     self.client.get(reverse(
                         self.profile,
                         kwargs={'username': 'Artem'}) + '?page=2'))

        for response in responses:
            with self.subTest(response=response):
                self.assertEqual(len(response.context['page_obj'].object_list),
                                 TEST_PAGE_2)
