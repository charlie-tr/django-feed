from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views
from django.urls import resolve, reverse
from django.test import TestCase

class PasswordChangeTests(TestCase):
    def setUp(self):
        username = 'john'
        password = 'secret123'
        user = User.objects.create_user(username=username, email='john@doe.com', password=password)
        url = reverse('password_change')
        self.client.login(username=username, password=password)
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_correct_view(self):
        view = resolve('/settings/password/')
        self.assertEquals(view.func.view_class, auth_views.PasswordChangeView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, PasswordChangeForm)


class LoginRequiredPasswordChangeTests(TestCase):
    def test_redirection(self):
        url = reverse('password_change')
        login_url = reverse('login')
        response = self.client.get(url)
        
        self.assertRedirects(response, f'{login_url}?next={url}')
        #link login là combo của login_url và ?next specify link change password sẽ đc redirect đến sau khi login xong


class PasswordChangeTestCase(TestCase): 
    def setUp(self, data={}): #cái này là mẫu thôi, data chưa có gì đâu
        self.user = User.objects.create_user(username='john', email='john@doe.com', password='old_password')
        self.url = reverse('password_change')
        self.client.login(username='john', password='old_password')
        self.response = self.client.post(self.url, data) #vứt data vô là thay password


class SuccessfulPasswordChangeTests(PasswordChangeTestCase):
    def setUp(self):
        #super() refers to base class. Ở đây đã có data
        super().setUp({
            'old_password': 'old_password',
            'new_password1': 'new_password',
            'new_password2': 'new_password',
        })

    def test_redirection(self):
        self.assertRedirects(self.response, reverse('password_change_done'))

    def test_password_changed(self):
        self.user.refresh_from_db() #Phải refresh á?
        self.assertTrue(self.user.check_password('new_password'))

    def test_user_authentication(self):
        response = self.client.get(reverse('home'))
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)


class InvalidPasswordChangeTests(PasswordChangeTestCase):
    #ko cần set up 1 cái invalid request ở đây làm gì, vì inherit từ PasswordChangeTestCase nó là data trống rồi

    #vx phải redirect lại trang change password
    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_didnt_change_password(self):
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('old_password'))