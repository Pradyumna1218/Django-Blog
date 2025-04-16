from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Comments, Subscription, Ratings
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin
from users.forms import CreatePost, RatingForm
from django.http import HttpResponseForbidden
from django.views import View
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Avg, F


class HomeView(View):
    def get(self, request):
        post = Post.objects.filter(is_deleted= False).order_by('-date_posted')

        page_number = request.GET.get('page') or 1 
        page_size = request.GET.get('page_size') 

        try:
            page_size = int(page_size) if page_size else settings.DEFAULT_PAGE_SIZE
        except ValueError:
            page_size = settings.DEFAULT_PAGE_SIZE 
        
        page_size = min(page_size, settings.MAX_PAGE_SIZE)

        paginator = Paginator(post, page_size)  
        page_obj = paginator.get_page(page_number)  

        context = {
            "page_obj": page_obj,
            "page_size": page_size
        }
        return render(request, "blog/home.html", context)

class PostDetailView(View):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk, is_deleted=False)
        comments = Comments.objects.filter(post=post).order_by("-date_posted")
        existing_rating = Ratings.objects.filter(post=post, user=request.user).first()

        is_following = False
        if request.user.is_authenticated:
            is_following = Subscription.objects.filter(follower=request.user, following=post.author).exists()

        profile_user = post.author
        avg_rating = post.average_rating()
        form = RatingForm()
        context = {
            "posts": post,
            "comments": comments,
            "profile_user": profile_user,
            "is_following": is_following,  
            'avg_rating': avg_rating,
            "form": form,
            "rating": existing_rating
        }
        return render(request, "blog/post_detail.html", context)

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk, is_deleted=False)
        form = RatingForm(request.POST)

        if form.is_valid():
            # Update or create the rating for the user on this post
            rating, created = Ratings.objects.update_or_create(
                post=post,
                user=request.user,
                defaults={"value": form.cleaned_data["value"]},
            )

            return redirect('post-detail', pk=post.id)

        comments = Comments.objects.filter(post=post).order_by("-date_posted")
        is_following = False
        if request.user.is_authenticated:
            is_following = Subscription.objects.filter(follower=request.user, following=post.author).exists()

        profile_user = post.author
        avg_rating = post.average_rating()

        context = {
            "posts": post,
            "comments": comments,
            "profile_user": profile_user,
            "is_following": is_following,
            "avg_rating": avg_rating,
            "form": form,
        }
        return render(request, "blog/post_detail.html", context)

class UserPostView(View):
    def get(self, request, username):
        user = get_object_or_404(User, username=username)        
        posts = Post.objects.filter(author=user, is_deleted= False).order_by("-date_posted")

        page_number = request.GET.get('page') or 1
        page_size = request.GET.get('page_size')

        try:
            page_size = int(page_size) if page_size else settings.DEFAULT_PAGE_SIZE
        except ValueError:
            page_size = settings.DEFAULT_PAGE_SIZE

        page_size = min(page_size, settings.MAX_PAGE_SIZE)

        is_following = False
        if request.user.is_authenticated:
            is_following = Subscription.objects.filter(follower=request.user, following=user).exists()


        paginator = Paginator(posts, page_size)
        page_obj = paginator.get_page(page_number)

        context = {
            'page_obj': page_obj,
            'user_obj': user,
            "profile_user": user,
            "is_following": is_following,
        }

        return render(request, 'blog/user_post.html', context)



class PostCreateView(LoginRequiredMixin, View):
    def get(self, request):
        form = CreatePost()
        return render(request, 'blog/post_form.html', {'form': form})
    
    def post(self, request):
        form = CreatePost(request.POST)

        if form.is_valid():
            post = form.save(author = request.user)
            return redirect('post-detail', pk = post.pk)
            
        return render(request, 'blog/post_form.html', {"form": form})


class PostUpdateView(LoginRequiredMixin, View):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        
        if request.user != post.author:
            return HttpResponseForbidden("You are not allowed to edit this post.")

        form = CreatePost(initial={'title': post.title, 'content': post.content})
        
        return render(request, 'blog/post_form.html', {'form': form, 'post': post})

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)
        
        if request.user != post.author:
            return HttpResponseForbidden("You are not allowed to edit this post.")
        
        form = CreatePost(request.POST)

        if form.is_valid():
            post = form.save(author = request.user)
            return redirect('post-detail', pk=post.pk)
        
        return render(request, 'blog/post_form.html', {'form': form, 'post': post})

   
class PostDeleteView(LoginRequiredMixin, View):
    def get(self, request, pk):
        post = get_object_or_404(Post, pk=pk)

        if request.user != post.author:
            return HttpResponseForbidden("You are not allowed to delete this post.")
        
        return render(request, 'blog/post_confirm_delete.html', {'post': post})

    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk)

        if request.user != post.author:
            return HttpResponseForbidden("You are not allowed to delete this post.")

        post.delete()
        return redirect('blog-home')  


class CommentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk, is_deleted=False)
        content = request.POST.get('content')
        
        if content.strip():
            Comments.objects.create(user= request.user, post=post, content=content)

        return redirect('post-detail', pk=pk)
        

class LikeView(LoginRequiredMixin, View):
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk, is_deleted=False)
        liked = post.toggle_like(request.user)
        
        return JsonResponse({"total_likes": post.total_likes(), "liked": liked})


class SubscriptionView(LoginRequiredMixin,View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user != request.user:
            Subscription.objects.get_or_create(follower=request.user, following = user)
        return redirect("subscribe-post")
    
class UnSubscriptionView(LoginRequiredMixin,View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        Subscription.objects.filter(follower= request.user, following = user).delete()
        return redirect("subscribe-post")
    
class SubscriptionPostView(LoginRequiredMixin, View):
    def get(self, request):
        followed_users = request.user.following.values_list('following', flat = True)
        posts = Post.objects.filter(author__id__in = followed_users, is_deleted= False).order_by("-date_posted")

        page_number = request.GET.get('page') or 1
        page_size = request.GET.get('page_size')

        try:
            page_size = int(page_size) if page_size else settings.DEFAULT_PAGE_SIZE
        except ValueError:
            page_size = settings.DEFAULT_PAGE_SIZE
        page_size = min(page_size, settings.MAX_PAGE_SIZE)

        paginator = Paginator(posts, page_size)
        page_obj = paginator.get_page(page_number)

        context = {
            "page_obj": page_obj,
        }

        return render(request, "blog/subscribed_posts.html", context)


class RatingView(LoginRequiredMixin, View):
    def get(self, request,pk):
        post = get_object_or_404(Post, pk=pk, is_deleted=False)
        form = RatingForm()
        
        return render(request, 'blog/rate_post.html', {"form": form, "post":post})
    
    def post(self, request, pk):
        post = get_object_or_404(Post, pk=pk, is_deleted=False)
        form = RatingForm(request.POST)

        if form.is_valid():
            rating, created = Ratings.objects.update_or_create(
                post= post, user= request.user, defaults={"value": form.cleaned_data["value"]}
            )
            return redirect('post-detail', pk=post.id)



class MostPopular(View):
    def get(self, request):
        posts = Post.objects.annotate(avg_rating=Avg('ratings__value')).filter(is_deleted= False).order_by(F('avg_rating').desc(nulls_last=True))[:5]
        return render(request, 'blog/popular.html', {'posts': posts})

def about(request):
    return render(request, "blog/about.html", {"title" : "About"})
