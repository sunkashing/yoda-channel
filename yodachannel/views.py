import json
import mimetypes
import os
import re
from wsgiref.util import FileWrapper

from django.core import serializers
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.db.models import Q
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.shortcuts import render

# Create your views here.
# 定义最基本的 API 视图
from django.templatetags.static import static
from django.views import View

from webapps import settings
from .load_weibo import load_weibo
from .mixins import APIDetailMixin, APIUpdateMixin, \
    APIDeleteMixin, APIListMixin, \
    APICreateMixin, APIMethodMapMixin, APISingleObjectMixin  # 引入我们编写的所有
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

from django.http import HttpResponseRedirect

from .models import Weibo, WeiboPicture, WeiboVideo
from .weibo import main

consumer_key = ''  # 设置你申请的appkey
consumer_secret = ''  # 设置你申请的appkey对于的secret

mails_per_page = 5
blogs_per_page = 5
videos_per_page = 9


class APIView(View):
    def response(self,
                 queryset=None,
                 fields=None,
                 **kwargs):
        """
        序列化传入的 queryset 或 其他 python 数据类型。返回一个 JsonResponse 。
        :param queryset: 查询集，可以为 None
        :param fields: 查询集中需要序列化的字段，可以为 None
        :param kwargs: 其他需要序列化的关键字参数
        :return: 返回 JsonResponse
        """

        # 根据传入参数序列化查询集，得到序列化之后的 json 字符串
        if queryset and fields:
            serialized_data = serialize(format='json',
                                        queryset=queryset,
                                        fields=fields)
        elif queryset:
            serialized_data = serialize(format='json',
                                        queryset=queryset)
        else:
            serialized_data = None

        instances = json.loads(serialized_data) if serialized_data else 'No instance'
        data = {'instances': instances}
        data.update(kwargs)  # 添加其他的字段
        return JsonResponse(data=data)  # 返回响应


class APICodeView(APIListMixin,  # 获取列表
                  APIDetailMixin,  # 获取当前请求实例详细信息
                  APIUpdateMixin,  # 更新当前请求实例
                  APIDeleteMixin,  # 删除当前实例
                  APICreateMixin,  # 创建新的的实例
                  APIMethodMapMixin,  # 请求方法与资源操作方法映射
                  APIView):  # 记得在最后继承 APIView
    model = None

    def list(self):
        return super(APICodeView, self).list(fields=['name'])


# 主页视图
def template(request, filename):
    """
    读取 'index.html' 并返回响应
    :param filename: str-> 文件名:
    :param request: 请求对象
    :return: HttpResponse
    """
    with open('yodachannel/templates/yodachannel/{}'.format(filename), 'rb') as f:
        content = f.read()
    return HttpResponse(content)


# 读取 js 视图
def js(request, filename):
    """
    读取 js 文件并返回 js 文件响应
    :param request: 请求对象
    :param filename: str-> 文件名
    :return: HttpResponse
    """
    with open('yodachannel/static/yodachannel/js/{}'.format(filename), 'rb') as f:
        js_content = f.read()
    return HttpResponse(content=js_content,
                        content_type='application/javascript')  # 返回 js 响应


# 读取 css 视图
def css(request, filename):
    """
    读取 css 文件，并返回 css 文件响应
    :param request: 请求对象
    :param filename: str-> 文件名
    :return: HttpResponse
    """
    with open('yodachannel/static/yodachannel/css/{}'.format(filename), 'rb') as f:
        css_content = f.read()
    return HttpResponse(content=css_content,
                        content_type='text/css')  # 返回 css 响应


def index_action(request):
    print('Blog_nums: {}'.format(Weibo.objects.filter(is_blog=True).count()))
    print('Mail_nums: {}'.format(Weibo.objects.filter(is_mail=True).count()))
    print('Other_nums: {}'.format(Weibo.objects.filter(is_other=True).count()))
    context = {}
    if not Weibo.objects.exists():
        load_weibo(os.path.join(settings.STATICFILES_DIR, 'yodachannel/json/5173636286.json'), True)
    return render(request=request, template_name='yodachannel/index.html', context=context)


def profile_action(request):
    context = {}
    return render(request=request, template_name='yodachannel/profile.html', context=context)


def mail_action(request, order):
    context = {}
    if str(order) == 'old':
        mails = Weibo.objects.filter(is_mail=True).order_by('created_at')
        context['old'] = True
    else:
        mails = Weibo.objects.filter(is_mail=True).order_by('-created_at')
        context['old'] = False
    mails_paginator = Paginator(mails, mails_per_page)

    mail_page_num = 1
    context['mails'] = mails_paginator.get_page(mail_page_num).object_list
    context['mails_pictures'] = get_weibo_pictures(context['mails'])
    context['page_num'] = 1
    return render(request=request, template_name='yodachannel/mail.html', context=context)


def mail_page_action(request):
    context = {}
    order = str(request.GET.get('order'))
    if order == 'old':
        mails = Weibo.objects.filter(is_mail=True).order_by('created_at')
    else:
        mails = Weibo.objects.filter(is_mail=True).order_by('-created_at')
    mails_paginator = Paginator(mails, mails_per_page)
    mail_page_num = int(request.GET.get('page_num'))

    context['status'] = 'SUCCESS'
    if type(mail_page_num) is not int:
        mail_page_num = 1
        context['status'] = 'FAIL'
    else:
        mail_page_num += 1
    mails_list = [mail for mail in mails_paginator.get_page(mail_page_num).object_list]
    context['mails'] = [serializers.serialize('json', [mail, ]) for mail in mails_list]
    context['mails_pictures'] = [serializers.serialize('json', [pic, ]) for pic in get_weibo_pictures(mails_list)]
    context['new_page_num'] = mail_page_num

    # 判断是否有下一页数据
    if mails_paginator.get_page(mail_page_num).has_next():
        context['has_next'] = 'true'
    else:
        context['has_next'] = 'false'
    return JsonResponse(context)


# def get_new_mail():
#


def get_weibo_pictures(weibos):
    res = []
    for weibo in weibos:
        res.extend([pic for pic in WeiboPicture.objects.filter(weibo=weibo)])
    return res


def get_weibo_videos(weibos):
    res = []
    for weibo in weibos:
        res.extend([pic for pic in WeiboVideo.objects.filter(weibo=weibo)])
    return res


def blog_action(request, order):
    context = {}
    if str(order) == 'old':
        blogs = Weibo.objects.filter(is_blog=True).order_by('created_at')
        context['old'] = True
    else:
        blogs = Weibo.objects.filter(is_blog=True).order_by('-created_at')
        context['old'] = False
    blogs_paginator = Paginator(blogs, blogs_per_page)

    blog_page_num = 1
    context['blogs'] = blogs_paginator.get_page(blog_page_num).object_list
    context['page_num'] = 1
    return render(request=request, template_name='yodachannel/blog.html', context=context)


def blog_page_action(request):
    context = {}
    order = str(request.GET.get('order'))
    if order == 'old':
        blogs = Weibo.objects.filter(is_blog=True).order_by('created_at')
    else:
        blogs = Weibo.objects.filter(is_blog=True).order_by('-created_at')
    blogs_paginator = Paginator(blogs, blogs_per_page)
    blog_page_num = int(request.GET.get('page_num'))

    context['status'] = 'SUCCESS'
    if type(blog_page_num) is not int:
        blog_page_num = 1
        context['status'] = 'FAIL'
    else:
        blog_page_num += 1
    blogs_list = [blog for blog in blogs_paginator.get_page(blog_page_num).object_list]
    context['blogs'] = [serializers.serialize('json', [blog, ]) for blog in blogs_list]
    context['new_page_num'] = blog_page_num

    # 判断是否有下一页数据
    if blogs_paginator.get_page(blog_page_num).has_next():
        context['has_next'] = 'true'
    else:
        context['has_next'] = 'false'
    return JsonResponse(context)


def blog_view_action(request, blog_id):
    context = {}
    if type(blog_id) is int:
        blog = [Weibo.objects.get(id=blog_id)]
        context['blog_pictures'] = get_weibo_pictures(blog)
        if blog and blog[0].blog_title:
            context['blog_title'] = blog[0].blog_title
    return render(request=request, template_name='yodachannel/blog_view.html', context=context)


def video_action(request, order):
    context = {}
    if str(order) == 'old':
        videos = Weibo.objects.filter(is_video=True).order_by('created_at')
        context['old'] = True
    else:
        videos = Weibo.objects.filter(is_video=True).order_by('-created_at')
        context['old'] = False
    videos_paginator = Paginator(videos, videos_per_page)

    video_page_num = 1
    context['videos'] = videos_paginator.get_page(video_page_num).object_list
    context['videos_video'] = get_weibo_videos(context['videos'])
    context['page_num'] = 1
    return render(request=request, template_name='yodachannel/video.html', context=context)


def video_page_action(request):
    context = {}
    order = str(request.GET.get('order'))
    if order == 'old':
        videos = Weibo.objects.filter(is_video=True).order_by('created_at')
    else:
        videos = Weibo.objects.filter(is_video=True).order_by('-created_at')
    videos_paginator = Paginator(videos, videos_per_page)
    video_page_num = int(request.GET.get('page_num'))

    context['status'] = 'SUCCESS'
    if type(video_page_num) is not int:
        video_page_num = 1
        context['status'] = 'FAIL'
    else:
        video_page_num += 1
    videos_list = [video for video in videos_paginator.get_page(video_page_num).object_list]
    context['videos'] = [serializers.serialize('json', [video, ]) for video in videos_list]
    context['videos_video'] = [serializers.serialize('json', [video, ]) for video in get_weibo_videos(videos_list)]
    context['new_page_num'] = video_page_num

    # 判断是否有下一页数据
    if videos_paginator.get_page(video_page_num).has_next():
        context['has_next'] = 'true'
    else:
        context['has_next'] = 'false'
    return JsonResponse(context)


def file_iterator(file_name, chunk_size=8192, offset=0, length=None):
    with open(file_name, "rb") as f:
        f.seek(offset, os.SEEK_SET)
        remaining = length
        while True:
            bytes_length = chunk_size if remaining is None else min(remaining, chunk_size)
            data = f.read(bytes_length)
            if not data:
                break
            if remaining:
                remaining -= len(data)
            yield data


def get_video_action(request, path):
    path = os.path.join(os.path.join(settings.STATICFILES_DIR, 'yodachannel/videos/weibo/'), path)
    range_header = request.META.get('HTTP_RANGE', '').strip()
    range_re = re.compile(r'bytes\s*=\s*(\d+)\s*-\s*(\d*)', re.I)
    range_match = range_re.match(range_header)
    size = os.path.getsize(path)
    content_type, encoding = mimetypes.guess_type(path)
    content_type = content_type or 'application/octet-stream'
    if range_match:
        first_byte, last_byte = range_match.groups()
        first_byte = int(first_byte) if first_byte else 0
        last_byte = first_byte + 1024 * 1024 * 8
        if last_byte >= size:
            last_byte = size - 1
        length = last_byte - first_byte + 1
        resp = StreamingHttpResponse(file_iterator(path, offset=first_byte, length=length), status=206,
                                     content_type=content_type)
        resp['Content-Length'] = str(length)
        resp['Content-Range'] = 'bytes %s-%s/%s' % (first_byte, last_byte, size)
    else:
        resp = StreamingHttpResponse(FileWrapper(open(path, 'rb')), content_type=content_type)
        resp['Content-Length'] = str(size)
    resp['Accept-Ranges'] = 'bytes'
    return resp


# 实例化调度器
scheduler = BackgroundScheduler()
# 调度器使用默认的DjangoJobStore()
scheduler.add_jobstore(DjangoJobStore(), 'default')


# 每天8点半执行这个任务
@register_job(scheduler, "interval", seconds=60, id='test_job')
def test():
    main()
    load_weibo(os.path.join(settings.BASE_DIR, 'yodachannel/weibo/yoda-channel/7452234433.json'), False)
    print('Refresh weibo successfully!')


# 注册定时任务并开始
register_events(scheduler)
scheduler.start()
