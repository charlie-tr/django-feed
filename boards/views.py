from django.views.generic import UpdateView, ListView
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, Http404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.urls import reverse

from .models import Board, Topic, Post
from .forms import NewTopicForm, PostForm

# Create your views here.

class BoardListView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'


class TopicListView(ListView): #nó tự phân ra r hiển thị các kq tương ứng cho mình luôn
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 20 #phân trang ở đây. Cái phân trang này nó làm cho mình cả url luôn cái phần ?page= ấy

    def get_context_data(self, **kwargs):
        kwargs['board'] = self.board    #bên topics.html vx cần có 1 context là 'board', 
                                        #nên specify thêm ở đây vì view này dựa trên model Topic, k có sẵn context khác
        return super().get_context_data(**kwargs) #super() là để reach tới parent class, override method cũ vs kwargs tạo mới ở đây để ốp thêm cái "board" vào context

    def get_queryset(self): ##by default nó show hết các object trong model, sẽ đc đưa vào phân trang
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk')) #self.kwargs là arguments từ url
        queryset = self.board.topics.order_by('-last_update').annotate(replies=Count('posts')) #'posts' là related_name, related_name là manager, count đc à??
        return queryset
    
'''
Đây là implementation cũ cho hiển thị các topic trong 1 board sử dụng FBV

def board_topics(request, pk): #cái pk này là bên urls.py truyền vào
    #request chứa thông tin để tạo thành view. Mỗi view lại trả về 1 response.
    try:
        board = Board.objects.get(pk=pk)
    except Board.DoesNotExist:
        raise Http404
    queryset = board.topics.order_by('-last_update').annotate(replies=Count('posts')) 
    #biến replies xuất hiện ở đây, đáng lẽ nên là Count('posts') - 1 vì k tính cái post đầu, mà k hiểu sao như v lại hiển thị thành -1
    page = request.GET.get('page', 1)   #cái 'page' này chắc là param có sẵn trong request
                                        #nếu ko tồn tại thì lấy 1
                                        #từ từ lúc process đến đây thì làm gì đã có pagination, nên nó cứ lấy là 1, 
                                        #xong xuống dưới này mới process pagination chia queryset ra các trang,
                                        #bao h lúc đầu vào cx là 1, xong user hit trang khác thì page sẽ đổi sang số khác
    paginator = Paginator(queryset, 20)

    try:
        topics = paginator.page(page) #lấy topics tương ứng mỗi trang
    except PageNotAnInteger: #nếu cái link ko chứa số
        topics = paginator.page(1) #thì quay lại page đầu
    except EmptyPage: #nếu cái số page trong link k tồn tại
        topics = paginator.page(paginator.num_pages) #hiển thị page cuối, num_pages là số các trang, ý là lấy số của trang cuối cùng

    return render(request, 'topics.html', {'board': board, 'topics':topics})
'''


class PostListView(ListView):
    model = Post
    context_object_name = 'posts' #tên gọi của các object trong ListView
    template_name = 'topic_posts.html'
    paginate_by = 20

    def get_context_data(self, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk) #nhưng instance phải là list, list thì làm gì có attr topic nhỉ
        #refreshing hay dạo lung tung nhưng vẫn đang logged in thì vẫn là cùng 1 phiên, 
        #ở đây tạo ra 1 cái mẩu thông tin tên là session_key trong cái session data 
        #để track là đang ở trong cái phiên này, có quay qua topic đã xem vài lần cũng ko cần tăng lượt view, 
        #và vẫn cần id của topic như 1 cách track xem user đã qua topic nào rồi
        if not self.request.session.get(session_key, False):
            self.topic.views += 1 #cứ mỗi lần get view là tính thêm 1 lượt xem
            self.topic.save()
            self.request.session[session_key] = True
        kwargs['topic'] = self.topic #thêm 1 từ khoá "topic" vào template
        return super().get_context_data(**kwargs) #ốp thêm cái "topic" vào context của template

    def get_queryset(self): 
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('board_pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset

'''
Đây là implementation cũ cho hiển thị các post trong 1 topic sử dụng FBV, chưa có pagination

#show a thread with its posts
def topic_posts(request, board_pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk = board_pk, pk = topic_pk) #board__pk là query đến cái id của board ứng vs topic, so xem nó có bằng vs cái board_pk không
        #also cái board_pk ứng vs cái <int:board_pk> bên url, nó lấy thông số trên url r truyền vào view function, cẩn thận nhầm đặt khác nhau
    topic.views += 1
    topic.save()
    return render(request, 'topic_posts.html', {'topic': topic})
'''


@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)

    #bh k phải làm cái dòng dưới nữa vì phải login ms đc lập topic nên cái user nó có trong request object, k phải mò vào db moi ra
    #user = User.objects.first() #get the currently logged in user

    if request.method == 'POST': #nếu có submit, trang chuyển tình trạng thành POST
        form = NewTopicForm(request.POST) #map thông tin (request.POST là 1 dict chứa các thông tin từ cái POST request) vào form
        if form.is_valid():
            topic = form.save(commit = False) #ở đây form đc map theo Topic nên nếu save sẽ trả về 1 instance theo model Topic, 
            #commit = False là chưa lưu vào db vội, vì còn chưa có các field khác

            topic.board = board
            topic.starter = request.user
            topic.save()
            post = Post.objects.create(
                message = form.cleaned_data.get('message'),
                topic = topic,
                created_by = request.user #user object
            )
        return redirect('board_topics', pk=board.pk)
    else:
        form = NewTopicForm() #phải có cái này ko bên template ko tìm ra form
        #lúc đầu, khi hit url, view này sẽ đc render vs template new_topic vs form trống, vì request chưa có thông tin gì, 
        #khi submit form như ở template đã specify method="POST", nên lúc này request.method là "POST", 
        #tạo ra 1 form vs thông tin từ POST, nếu valid thì save lại
        #thực sự cx k hiểu nó truyền cho view function ntn, nhưng nchung đến đây thì thông tin sẽ đc lưu như trong if bên trên
        #cái chính là phải hiểu kỹ các bước, có nhx cái gì tạo ra, loại gì

    return render(request, 'new_topic.html', {'board': board, 'form': form})


@login_required
def reply_topic(request, board_pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk = board_pk, pk = topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False) #post ở đây là ModelForm object, 1 instance của model mà form ăn theo
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_update = timezone.now()
            topic.save()

            topic_url = reverse('topic_posts', kwargs={'board_pk': topic.board.pk, 'topic_pk': topic.pk})
            topic_last_post_url = '{url}?page={page}#{id}'.format(
                url = topic_url,
                page = topic.get_page_count(),
                id = post.pk
            )
            return redirect(topic_last_post_url)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView): #using GCBV to implement edit post view
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post' #

    def get_queryset(self):
        queryset=super().get_queryset()
        return queryset.filter(created_by=self.request.user)    #request đc define trong UpdateView class r 
                                                                #còn user chắc là lúc submit form thì đc truyền vào params trong HttpRequest

    def form_valid(self, form):
        post = form.save(commit = False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', board_pk = post.topic.board.pk, topic_pk = post.topic.pk)