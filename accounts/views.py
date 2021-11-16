from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as auth_login
#from django.contrib.auth import authenticate
from .forms import SignUpForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from django.urls import reverse_lazy


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, "Successful signup")
            return redirect('home')
        else:
            messages.error(request, "Invalid signup")
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = User
    fields = ('first_name', 'last_name', 'email', ) #this creates a form on the fly. Context "form" trong template tự động lấy mẫu này
                                                    #nên ko cần phải specify form context ở đây
    template_name = 'my_account.html'
    success_url = reverse_lazy('my_account') #reverse_lazy vì lúc import chưa cần define ngay, bao giờ url gọi thì trả

    def get_object(self): #
        return self.request.user