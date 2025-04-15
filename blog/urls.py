from django.urls import path
from .views import (
    HomeView,
    PostDetailView,
    UserPostView, 
    PostCreateView,
    PostUpdateView,
    PostDeleteView,
    CommentView,
    LikeView,
    SubscriptionView,
    UnSubscriptionView,
    SubscriptionPostView,
    MostPopular
)
from . import views

urlpatterns = [
    path("", HomeView.as_view(), name = "blog-home"),
    path("user/<str:username>/", UserPostView.as_view(), name = "user-post"),
    path("post/<int:pk>/", PostDetailView.as_view(), name = "post-detail"),
    path("post/new/", PostCreateView.as_view(), name = "post-create"),
    path("post/<int:pk>/update/", PostUpdateView.as_view(), name = "post-update"),
    path("post/<int:pk>/delete/", PostDeleteView.as_view(), name = "post-delete"),
    path("post/<int:pk>/comment/", CommentView.as_view(), name="comment"),
    path("post/<int:pk>/like/", LikeView.as_view(), name="post-like"),
    path("subscribe/<int:pk>/", SubscriptionView.as_view(), name="subscribe"),
    path("unsubscribe/<int:pk>/", UnSubscriptionView.as_view(), name="unsubscribe"),
    path("subscribe_post/", SubscriptionPostView.as_view(), name="subscribe-post"),
    path("top5/", MostPopular.as_view(), name="top5"),
    path("about/", views.about, name = "blog-about") 
]