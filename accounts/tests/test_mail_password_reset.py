from django.core import mail
from django.contrib.auth.models import User
from django.template import context
from django.urls import reverse
from django.test import TestCase

class PasswordResetMailTests(TestCase):
    def setUp(self):
        User.objects.create_user(username = 'john', email = 'john@doe.com', password = '123')
        url = reverse('password_reset')
        self.response = self.client.post(url, {'email': 'john@doe.com'})
        self.email = mail.outbox[0] #cái 'john@doe.com' ấy

    #These tests examine the email sent by the application: the subject line, the body contents, and to who was the email sent to.    
    def test_email_subject(self):
        self.assertEqual('[Django Boards] Please reset your password', self.email.subject)

    def test_email_body(self):
        context = self.response.context
        #token vs uid này có trong response object trả về sau khi submit email, nhưng mình vx k rõ cụ thể nằm đâu
        token = context.get('token')
        uid = context.get('uid')

        #ốp cái uid vs token vào url form 'password_reset_confirm' r xem cái url đấy có trong email ko
        password_reset_token_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        self.assertIn(password_reset_token_url, self.email.body)
        
        self.assertIn('john', self.email.body)
        self.assertIn('john@doe.com', self.email.body)

    def test_email_to(self):
        self.assertEqual(['john@doe.com',], self.email.to)