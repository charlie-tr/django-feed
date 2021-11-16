from django.test import TestCase
from django.urls import reverse, resolve

from ..views import TopicListView
from ..models import Board


class BoardTopicsTests(TestCase):
    def setUp(self):
        #tạo 1 record trong 1 db hoàn toàn mới chỉ để test
        self.board = Board.objects.create (name="Board Test", description = "For testing")

    def test_ok_200(self):
        url = reverse('board_topics', kwargs={'pk': 1}) #hiện tại chỉ có 1 record
        response = self.client.get(url) #bản thân tk TestCase có attribute client
        self.assertEquals(response.status_code, 200) #assertEquals là 1 hàm thừa hưởng từ TestCase

    def test_error_404(self):
        url = reverse('board_topics', kwargs={'pk':99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_correct_view(self):
        url = reverse('board_topics', kwargs={'pk': 1})
        view = resolve(url)
        self.assertEquals(view.func.view_class, TopicListView)
    
    #when I dont include the anchor in the template, this still works. Strange
    def test_does_singleBoardPage_contain_homeViewLink(self):
        single_board_url = reverse('board_topics', kwargs = {'pk': self.board.pk})
        home_url = reverse('home')
        new_topic_url = reverse('new_topic', kwargs = {'pk': self.board.pk})
        response = self.client.get(single_board_url)
        self.assertContains(response, home_url)
        self.assertContains(response, new_topic_url)