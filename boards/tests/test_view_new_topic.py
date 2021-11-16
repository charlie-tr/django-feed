from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.models import User

from ..views import new_topic
from ..models import Board, Post, Topic
from ..forms import NewTopicForm


class NewTopicTest(TestCase):
    def setUp(self):
        Board.objects.create(name ="Board Test", description= "For testing")
        User.objects.create_user(username='john', email='john@doe.com', password='123')
        self.client.login(username='john', password='123')
        #phải login đây vì function new_topic có @login_required

    def test_new_topic_view_success(self):
        url = reverse('new_topic',kwargs={'pk':1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_error_404(self): #sao chưa raise404 mà nó lại chạy đúng nhỉ
        url = reverse('new_topic',kwargs={'pk':99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)
    
    def test_resolve_ok(self): 
        #dafuq sao nếu làm ntn thì cái này lại fail
        #view = resolve('/boards/1/new')
        #self.assertEquals(view.func, new_topic)
        url = reverse('new_topic', kwargs={'pk': 1})
        view = resolve(url)
        self.assertEquals(view.func, new_topic)

    def test_does_newTopicPage_contain_boardTopicsPage(self):
        new_topic_url = reverse('new_topic', kwargs={'pk': 1})
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(new_topic_url)
        self.assertContains(response, board_topics_url)

    def test_csrf_included(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_contains_new_topic_form(self):
        url = reverse('new_topic', kwargs={'pk':1})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm)

    def test_valid_post_newTopic(self): #fail, because theres no user logged-in in the testing process?
        url = reverse('new_topic', kwargs={'pk': 1})
        data = {
            'subject': 'Test topic',
            'message': 'Just for testing'
        }
        response = self.client.post(url, data) #post request
        self.assertTrue(response, Topic.objects.exists())
        self.assertTrue(response, Post.objects.exists())

    def test_invalid_post_newTopic(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.post(url, {}) #no data here, which is invalid
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors)

    def test_invalid_post_newTopic_with_empty_fields(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        data = {
            'subject': '',
            'message': ''
        }
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Post.objects.exists())


class LoginRequiredWhenMakingNewTopicTests(TestCase):
    def setUp(self):
        Board.objects.create(name="Test Board", description= "For testing")
        self.url = reverse('new_topic', kwargs={'pk': 1})
        self.response = self.client.get(self.url)

    def test_redirection_when_not_logged_in(self):
        login_url = reverse('login')
        self.assertRedirects(self.response,'{login_url}?next={new_topic_url}'.format(login_url=login_url, new_topic_url=self.url))