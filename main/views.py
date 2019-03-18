from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.http import request, HttpResponse
from django.shortcuts import render

# Create your views here.
from django.urls import reverse_lazy
from django.views import generic, View

class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'signup.html'

class CheckUser(View):
    def get(self, request):
        users = User.objects.all()
        session = ' | '.join("{}={}".format(key, val) for (key, val) in request.session.items())
        cookies = ' | '.join('{}: {}'.format(key, value) for key, value in request.COOKIES.items())
        return render(request, "users_list.html", {"users": users, "session": session, "cookies": cookies})


# class UserView(View):
#     def get(self, request, id):
#         plans =


