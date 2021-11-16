from django.test import TestCase
from django.urls import reverse, resolve
from ..views import signup
from ..forms import SignUpForm
from django.contrib.auth.models import User #này sao nó lại lưu user vào đây mà ko ph vào vị trí riêng trong db nhỉ

# Create your tests here.
class SignUpTests(TestCase):
    def setUp(self):
        url = reverse('signup')
        self.response = self.client.get(url)

    def test_200_ok(self):
        self.assertEquals(self.response.status_code, 200)
    
    def test_resolve_correctly(self):
        view = resolve('/signup/')
        self.assertEquals(view.func, signup)

    def test_csrf_contained(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, SignUpForm)

class SuccessfulSignupTests(TestCase):
    def setUp(self):
        url = reverse('signup')
        data = {
            'username': 'John',
            'email': 'john.doe@example.com',
            'password1': 'test1234',
            'password2': 'test1234'
        }
        self.response = self.client.post(url, data)
        self.home_url = reverse('home')

    def test_successful_redirect(self): #fail, expected code is 302, not 200
        self.assertRedirects(self.response, self.home_url)

    def test_successful_user_creation(self):#fail nốt, why
        self.assertTrue(User.objects.exists()) 

    def test_authentication(self): #fail, maybe user is not authenticated yet?
        response = self.client.get(self.home_url)
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated) #user nó chỉ là data form đã save vào thôi mà??

class InvalidSignupTest(TestCase):
    def setUp(self):
        url = reverse('signup')
        self.response = self.client.get(url, {})
    
    def test_200_ok(self):
        self.assertEquals(self.response.status_code, 200) #ủa đâu có nghĩa là it stays on the same page?

    def test_form_errors(self):#fail, why is there nothing in errors list
        form = self.response.context.get('form')
        self.assertTrue(form.errors) #errors là attribute của class UserFormCreation instance

    def test_user_not_created(self):
        self.assertFalse(User.objects.exists())

