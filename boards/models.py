from django.db import models
from django.contrib.auth.models import User
from django.utils.text import Truncator
import math

# Create your models here.

class Board(models.Model):
    name = models.CharField(max_length=30, unique = True)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def get_posts_count(self):
        return Post.objects.filter(topic__board=self).count() #self ở đây là Board object
    
    def get_last_post(self):
        return Post.objects.filter(topic__board=self).order_by('-created_at').first() #dấu - đằng trước là descending, ý là lấy cái mới nhất
        

class Topic(models.Model): #ở đây Topic là cái to, Post là cái bé
    subject = models.CharField(max_length=255)
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="topics")
    starter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="topics")
    views = models.PositiveIntegerField(default=0)
    last_update = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject

    def get_page_count(self):
        count = self.posts.count() #ê làm sao để cái biến count nó không đụng vào cái method count()
        pages = count / 20
        return math.ceil(pages)

    def has_many_pages(self, count = None): #tại sao phải thêm count = None
        if count is None:
            count = self.get_page_count()
        return count > 6

    def get_page_range(self):
        count = self.get_page_count()
        if self.has_many_pages(count):
            return range(1,5)
        return range(1,count+1)

    def get_last_ten_posts(self):
        return self.posts.order_by('-created_at')[:10]


class Post(models.Model):
    message = models.CharField(max_length=4000)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name="posts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null = True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    updated_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE, related_name='+') #xem lại null = True, tại sao k có nó thì k đc

    def __str__(self):
        truncated_message = Truncator(self.message) #self ở đây là Topic object
        return truncated_message.chars(30) #string thường ko có feature này à