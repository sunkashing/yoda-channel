from django.db import models


# Create your models here.

class Weibo(models.Model):
    weibo_num = models.CharField(max_length=50)
    user_id = models.CharField(max_length=30)
    screen_name = models.CharField(max_length=50)
    bid = models.CharField(max_length=30)
    text = models.TextField()
    article_url = models.TextField()
    pics = models.TextField()
    video_url = models.TextField()
    location = models.CharField(max_length=100)
    created_at = models.DateTimeField()
    source = models.CharField(max_length=100)
    attitudes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    reposts_count = models.IntegerField(default=0)
    topics = models.CharField(max_length=100)
    at_users = models.TextField()
    is_mail = models.BooleanField(default=False)
    is_blog = models.BooleanField(default=False)
    is_video = models.BooleanField(default=False)
    is_yoda_other = models.BooleanField(default=False)
    is_other = models.BooleanField(default=False)
    mail_title = models.TextField(blank=True)
    mail_text = models.TextField(blank=True)
    blog_title = models.TextField(blank=True)
    video_title = models.TextField(blank=True)

    def __str__(self):
        return '[weibo_id: {}, user_id: {}, screen_name: {}, text: {}, pics: {}, video_url: {}, created_at: {}]'.format(
            self.weibo_num, self.user_id, self.screen_name, self.text, self.pics, self.video_url, self.created_at)


class WeiboPicture(models.Model):
    weibo = models.ForeignKey(Weibo, related_name='picture', on_delete=models.PROTECT, blank=True)
    url = models.TextField()
    file_name = models.TextField()


class WeiboVideo(models.Model):
    weibo = models.ForeignKey(Weibo, related_name='video', on_delete=models.PROTECT, blank=True)
    url = models.TextField()
    file_name = models.TextField()
    picture_file_name = models.TextField()
