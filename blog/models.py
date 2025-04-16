from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Post(models.Model):
    title = models.CharField(max_length= 100)
    content = models.TextField()
    date_posted = models.DateTimeField(default= timezone.now)
    author = models.ForeignKey(User, on_delete= models.CASCADE)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)
    is_deleted = models.BooleanField(default=False)
    
    def toggle_like(self, user):
        liked = False
        if self.likes.filter(id=user.id).exists():
            self.likes.remove(user)
        else:
            self.likes.add(user)
            liked = True

        return liked

    def total_likes(self):
        return self.likes.count()

    def average_rating(self):
        ratings = self.ratings.all()
        return ratings.aggregate(models.Avg('value'))['value__avg'] or 0

    def __str__(self):
        return self.title
    
class Comments(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blog_comments")
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    date_posted = models.DateTimeField(default=timezone.now)
 
    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"
    
class Subscription(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return f"{self.follower.username} is following {self.following.username}"

class Ratings(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField(choices =[(i,i) for i in range(1,6)])
    class Meta:
        unique_together = ('post', 'user')
    
    def __str__(self):
        return f"{self.user.username} rated {self.post.title} - {self.value}"
    
