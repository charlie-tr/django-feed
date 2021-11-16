from django import forms
from .models import Post, Topic

class NewTopicForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(attrs={'rows':5, 'placeholder': 'The content'}), #này là attrs của chúng nó thiết kế
        max_length=4000, 
        help_text='The max length of the text is 4000.')

    class Meta: 
        model = Topic #NewTopicForm là 1 ModelForm dựa trên model Topic
        fields = ['subject','message']

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['message'] #là 1 cái template để điền form thôi, bên views có action log topic và creator rồi