from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse, resolve

from ..forms import PostForm
from ..models import Board, Topic, Post
from ..views import reply_topic


class ReplyTopicTestCase(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board')
        self.username = 'john'
        self.password = '123'
        user = User.objects.create_user(username = self.username, email = 'john@doe.com', password = self.password)
        self.topic = Topic.objects.create(subject='Hello, world', board=self.board, starter=user)
        Post.objects.create(message='Lorem ipsum dolor sit amet', topic=self.topic, created_by=user)
        self.url = reverse('reply_topic', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})


class LoginRequiredReplyTopicTests(ReplyTopicTestCase):
    def test_redirection(self):
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))
        #trang login là trang mà sẽ đc redirect tới bởi vì cần ph login r ms reply đc, login xong lại redirect về trang reply


class ReplyTopicTests(ReplyTopicTestCase):
    def setUp(self):
        super().setUp() #giữ setUp của class cũ và thêm thắt 1 chút như dưới
        self.client.login(username=self.username, password=self.password) #đã login
        self.response = self.client.get(self.url) #trang reply, should be ok since user has logged in

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/boards/1/topics/1/reply/')
        self.assertEquals(view.func, reply_topic)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')
        
    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, PostForm)

    #còn 1 test nữa ko hiểu chưa cho vào


class SuccessfulReplyTopicTests(ReplyTopicTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {'message': 'hello, world!'}) #1st arg là link đang dùng (link reply ấy)
    
    def test_redirection(self):
        topic_posts_url = reverse('topic_posts', kwargs={'pk': self.board.pk, 'topic_pk': self.topic.pk})
        self.assertRedirects(self.response, topic_posts_url) #sau khi post reply xong thì phải redirect về trang chứa các posts trong topic

    def test_reply_created(self):
        self.assertEquals(Post.objects.count(), 2) #tính cả post chính thì nó là 2 post objects, ý là 1 post và 1 reply


class InvalidReplyTopicTests(ReplyTopicTestCase):
    def setUp(self):
        super().setUp()
        self.client.login(username=self.username, password=self.password)
        self.response = self.client.post(self.url, {}) #post 1 reply trống (invalid)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200) #vx ph stay lại trang reply cũ

    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors) #hollup, tức là form sẽ log lại invalid action vừa r à