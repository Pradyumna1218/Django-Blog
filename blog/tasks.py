from celery import shared_task
from .models import Post


@shared_task
def soft_delete_post():
    delete_post = Post.objects.filter(is_deleted= False)
    deletecount = 0
    for post in delete_post:
        avg_ratings= post.average_rating()
        if avg_ratings < 2:
            post.is_deleted= True
            post.save()
            deletecount += 1

    return f"{deletecount} posts were soft deleted."

 