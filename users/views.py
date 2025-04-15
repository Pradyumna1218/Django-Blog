from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import UserRegistrationForm, CustomLogin, UserUpdateForm, ProfileUpdateForm 
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

class Register(View):
    def get(self, request):
        form = UserRegistrationForm()
        return render(request, "users/register.html", {"form": form})

    def post(self, request):
        form = UserRegistrationForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, f"Your account has been created. Now you are able to login")
            return redirect("login")
        else:
            return render(request, "users/register.html", {'form': form})

class UserLogin(View):
    def get(self, request):
        form = CustomLogin()
        return render(request, "users/login.html", {"forms": form})
    
    def post(self, request):
        form = CustomLogin(request.POST)
        if form.is_valid():
            user = form.authenticate_user()
            login(request, user)
            return redirect('blog-home')
        else:
            return render(request, 'users/login.html', {"forms": form})

class UserLogout(View):
    def post(self, request):
        logout(request)
        return redirect('logout_page')
    
class UserLogoutPage(View):
    def get(self,request):
        return render(request, 'users/logout_page.html')

class ProfileView(LoginRequiredMixin, View):
    def get(self, request):
        u_form = UserUpdateForm(initial={
            'username': request.user.username,
            'email': request.user.email,
        })
        p_form = ProfileUpdateForm(initial={
            'image': request.user.profile.image 
        })
        context = {
            'u_form': u_form,
            'p_form': p_form,
        }

        return render(request, "users/profile.html", context)

    def post(self, request):
        u_form = UserUpdateForm(request.POST)
        p_form = ProfileUpdateForm(request.POST, request.FILES)

        if u_form.is_valid():
            u_form.save(user = request.user)

        if p_form.is_valid():
            p_form.save(user= request.user)

        messages.success(request, "Your account has been updated.")

        return redirect('profile')
 