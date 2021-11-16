from django.http import response
from django.test import TestCase
from django.urls import reverse, resolve

from ..views import BoardListView
from ..models import Board

# Create your tests here.

class HomeTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name = "Board Test", description="For testing")
        url = reverse('home')
        self.response = self.client.get(url) #response chỉ là 1 cái biến, ám chỉ response object mà view trả về khi get đc view
                                            #client có vẻ là 1 object có sẵn của TestCase giống như 1 client tương tác vs view để lấy mẫu
        
    def test_home_view_status_code(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_home_url_resolves_home_view(self):
        view = resolve('/')
        self.assertEquals(view.func.view_class, BoardListView)
    
    def test_does_homeView_contain_singleBoardPageLink(self):
        single_board_url = reverse('board_topics', kwargs = {'pk': self.board.pk})
        self.assertContains(self.response, single_board_url) #xem home page có chứa link dẫn đến từng board một không