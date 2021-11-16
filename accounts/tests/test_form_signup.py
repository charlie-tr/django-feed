from django.test import TestCase
from ..forms import SignUpForm

class SignUpFormTest(TestCase):

    #this test is too strict. You have to change it in the future if the form gets modified.
    def test_full_fields(self):
        form = SignUpForm()
        expected = ['username', 'email', 'password1', 'password2'] #it should be like this
        on_display = list(form.fields) #tạo list các field có trong form
        self.assertSequenceEqual(expected, on_display) #so 2 list có giống nhau k