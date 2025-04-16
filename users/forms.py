from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from blog.models import Post, Ratings

class UserRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Username already exists")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email already exists")
        return email
    
    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")
        if not any(char.isdigit() for char in password1):  
            raise forms.ValidationError("Password must contain at least one number.")
        return password1

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2:
            if password1 != password2:
                self.add_error("password2", "Passwords do not match")

        return cleaned_data
    
    def save(self):
        username = self.cleaned_data['username']
        email = self.cleaned_data['email']
        password = self.cleaned_data['password1']

        user = User.objects.create(username= username, email= email)
        user.set_password(password)
        user.save()
        return user
    
class CustomLogin(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=  forms.PasswordInput)

    def authenticate_user(self):
        username = self.cleaned_data['username']
        password = self.cleaned_data['password']
        user = authenticate(username=username, password=password)

        if User is None:
            raise ValidationError("Invalid Username or Password")
        return user

class CreatePost(forms.Form):
    title = forms.CharField()
    content = forms.CharField(widget=forms.Textarea)

    def save(self, author):
        title = self.cleaned_data['title']
        content = self.cleaned_data['content']
        post = Post.objects.create(title = title, content = content, author = author)
        return post

class UserUpdateForm(forms.Form):
    username = forms.CharField(max_length=150)  
    email = forms.EmailField()

    def save(self, user):

        if self.cleaned_data.get('username') != user.username:
            user.username = self.cleaned_data['username']

        if self.cleaned_data.get('email') != user.email:
            user.email = self.cleaned_data['email']

        user.save()
        return user

class ProfileUpdateForm(forms.Form):
    image = forms.ImageField()

    def save(self, user):
        if self.cleaned_data.get('image'):
            profile = user.profile
            profile.image = self.cleaned_data['image']
            profile.save()
        return user.profile
    
class RatingForm(forms.Form):
    value = forms.ChoiceField(choices=[(i,i) for i in range(1,6)], 
                              widget= forms.Select(attrs={"class": "form-control"}), 
                              label= "Rate this post")
    