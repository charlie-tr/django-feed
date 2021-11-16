"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from re import template
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from boards import views as boards_views
from accounts import views as accounts_views

urlpatterns = [
    path('', boards_views.BoardListView.as_view(), name = 'home'), #cái name này nó gọi là viewname

    path('boards/<int:pk>/', boards_views.TopicListView.as_view(), name='board_topics'), #ê mặc nhiên nó biết cái domain name r hả
    path('boards/<int:pk>/new/', boards_views.new_topic, name='new_topic'),
    path('boards/<int:board_pk>/topics/<int:topic_pk>/', boards_views.PostListView.as_view(), name='topic_posts'),
    path('boards/<int:board_pk>/topics/<int:topic_pk>/reply/', boards_views.reply_topic, name='reply_topic'),
    path('boards/<int:board_pk>/topics/<int:topic_pk>/posts/<int:post_pk>/edit/',
        boards_views.PostUpdateView.as_view(), name='edit_post'),

    path('signup/', accounts_views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),    #làm hộ hết r

    #reset password, Django làm sẵn logic rồi, chỉ wire vs nhau thôi
    path('reset/',   #nhập email để reset password
    auth_views.PasswordResetView.as_view(template_name = 'password_reset.html', 
                                        email_template_name = 'password_reset_email.html',  #mail sẽ gửi cho user sau khi submit tên email
                                        #url là map vs view thôi, tự làm view thì template specify bên view, ko thì specify ra đây
                                        subject_template_name = 'password_reset_subject.txt'), 
        name='password_reset'),
    path('reset/done/', #sau khi submit email
        auth_views.PasswordResetDoneView.as_view(template_name = 'password_reset_done.html'), 
        name='password_reset_done'),
    path('reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20}/)',   #confirm xuất hiện sau khi hit reset pw link in the email
    #uidb64 và token là tên cho mỗi field, có thể access từ tên đó
    #uiddb64: The user’s id encoded in base 64; token: Token to check that the password is valid
        auth_views.PasswordResetConfirmView.as_view(template_name = 'password_reset_confirm.html'), 
        name='password_reset_confirm'),
        #hiện tại thì mình CHƯA CÓ HỆ THỐNG MANAGE EMAILS nên log tạm email vào console. 
        #Nó có gửi đấy nhưng vấn đề là mình đang xài email fake nên không mử ra mà nhận được
        #đây chính là cái link mà nó send vào email của mình
    path('reset/complete/', 
        auth_views.PasswordResetCompleteView.as_view(template_name = 'password_reset_complete.html'), 
        name='password_reset_complete'),

    #change password, Django làm sẵn logic rồi, chỉ wire vs nhau thôi
    #These views only works for logged in users. 
    #They make use of a view decorator named @login_required. This decorator prevents non-authorized users to access this page. ¨
    #If the user is not logged in, Django will redirect them to the login page.
    path('settings/password/', 
        auth_views.PasswordChangeView.as_view(template_name='password_change.html'), 
        name='password_change'),
    path('settings/password/done/', 
        auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'),
        name='password_change_done'),

    path('settings/account/',
        accounts_views.UserUpdateView.as_view(), name='my_account'),    #bên view đã specify template_name
    path('admin/', admin.site.urls),
]