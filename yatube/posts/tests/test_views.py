from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms
from django.core.cache import cache

from posts.models import Post, Group


User = get_user_model()

pattern_create_post = 'posts/create_post.html'


class ContextView(TestCase):
    """Тестируем соответствие контекста view ожидаемому."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Artem')
        cls.user_n = User.objects.create_user(username='Nikita')
        Group.objects.create(
            title="Second title",
            slug="SecondSlug",
            description="Second description",
        )
        cls.group = Group.objects.create(
            title="Test title",
            slug="TestSlug",
            description="Test description",
        )
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        for i in range(1, 16):
            if i <= 4:
                Post.objects.create(
                    text=f"Test text{i}", author=cls.user_n, group=cls.group)
            elif 4 < i <= 13:
                Post.objects.create(
                    text=f"Test text{i}", author=cls.user, group=cls.group)
            elif 13 < i <= 16:
                Post.objects.create(
                    text=f"Test text{i}", author=cls.user)

    def test_templates(self):
        """Теституем правильное использование шаблонов для view."""
        pattern_pages = {
            pattern_create_post: (reverse('posts:post_edit',
                                          kwargs={'post_id': '1'})),
            'posts/group_list.html': (reverse('posts:group',
                                              kwargs={'slug': 'TestSlug'})),
            'posts/profile.html': (reverse('posts:profile',
                                           kwargs={'username': 'Artem'})),
            'posts/post_detail.html': (reverse('posts:post_detail',
                                               kwargs={'post_id': '1'})),
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/index.html': reverse('posts:home'),
        }
        for template, reverse_name in pattern_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_context(self):
        """Index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:home'))
        first_obj = response.context['page_obj'].object_list[0]
        post_text_0 = first_obj.text
        post_author_0 = first_obj.author.username
        post_group_0 = first_obj.group.title
        self.assertEqual(post_text_0, 'Test text1')
        self.assertEqual(post_author_0, 'Nikita')
        if post_group_0:
            self.assertEqual(post_group_0, 'Test title')

    def test_profile_context(self):
        """Profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Nikita'}))
        first_obj = response.context['page_obj'].object_list[0]
        post_text_0 = first_obj.text
        post_author_0 = first_obj.author.username
        post_group_0 = first_obj.group.title
        self.assertEqual(post_text_0, 'Test text1')
        self.assertEqual(post_author_0, 'Nikita')
        if post_group_0:
            self.assertEqual(post_group_0, 'Test title')

    def test_group_context(self):
        """Group сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': 'TestSlug'}))
        first_obj = response.context['page_obj'].object_list[0]
        post_text_0 = first_obj.text
        post_author_0 = first_obj.author.username
        post_group_0 = first_obj.group.title
        self.assertEqual(post_text_0, 'Test text1')
        self.assertEqual(post_author_0, 'Nikita')
        if post_group_0:
            self.assertEqual(post_group_0, 'Test title')

    def test_index_paginator(self):
        """Работоспособность паджинатора главной страницы."""
        response = self.authorized_client.get(reverse('posts:home'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_paginator_second(self):
        """Работоспособность паджинатора главной страницы (2-я страница)."""
        response_second = self.authorized_client.get(
            reverse('posts:home') + '?page=2')
        self.assertEqual(len(response_second.context['page_obj']), 5)

    def test_group_list_context(self):
        """Список постов отфильтрованных по группе."""
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': 'TestSlug'}))
        response_second = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': 'TestSlug'}) + '?page=2')
        summ_posts = (len(response.context['page_obj'])
                      + len(response_second.context['page_obj']))
        self.assertEqual(summ_posts, 13)

    def test_group_list_paginator(self):
        """Работоспособность паджинатора постов конкретной группы."""
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': 'TestSlug'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_paginator_second(self):
        """Паджинатора постов конкретной группы (2-я страница)."""
        response_second = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': 'TestSlug'}) + '?page=2')
        self.assertEqual(len(response_second.context['page_obj']), 3)

    def test_profile_context(self):
        """Список постов отфильтрованных по пользователю Nikita."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Nikita'}))

        self.assertEqual(len(response.context['page_obj']), 4)

    def test_profile_paginator(self):
        """Работоспособность паджинатора постов конкретного пользователя."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Artem'}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_paginator_second(self):
        """Паджинатор постов конкретного пользователя (2-я страница)."""
        response_second = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'Artem'}) + '?page=2')
        self.assertEqual(len(response_second.context['page_obj']), 1)

    def test_post_detail_context(self):
        """Один пост отфильтрованный по id."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'}))
        context_post_d = response.context['post_valid']
        text = context_post_d.text

        self.assertEqual(text, 'Test text1')

    def test_create_post(self):
        """Проверка view функции создания поста."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit(self):
        """Проверка view функции редактирования поста."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': '6'}))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_not_in_else_group(self):
        """А не попал ли пост не в ту группу?)."""
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': 'SecondSlug'}))
        self.assertEqual(len(response.context['page_obj']), 0)
        Post.objects.create(
            text="Test text", author=self.user_n, group=self.group,)
        cache.clear()
        response = self.authorized_client.get(
            reverse('posts:group', kwargs={'slug': 'SecondSlug'}))
        self.assertEqual(len(response.context['page_obj']), 0)
