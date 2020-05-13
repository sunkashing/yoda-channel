import json
import os

from django.core import serializers
from django.core.paginator import Paginator
from django.core.serializers import serialize
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
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

from django.http import HttpResponseRedirect

from .models import Weibo, WeiboPicture

consumer_key = ''  # 设置你申请的appkey
consumer_secret = ''  # 设置你申请的appkey对于的secret

mails_per_page = 5


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
        # 这一步很重要，在经过上面的查询步骤之后， serialized_data 已经是一个字符串
        # 我们最终需要把它放入 JsonResponse 中，JsonResponse 只接受 python 数据类型
        # 所以我们需要先把得到的 json 字符串转化为 python 数据结构。
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

    def list(self):  # 这里仅仅是简单的给父类的 list 函数传参。
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
    context = {}
    if not Weibo.objects.exists():
        load_weibo(os.path.join(settings.STATICFILES_DIR, 'yodachannel/json/5173636286.json'))
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
    context['mails_pictures'] = get_mails_pictures(context['mails'])
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
    context['mails_pictures'] = [serializers.serialize('json', [pic, ]) for pic in get_mails_pictures(mails_list)]
    context['new_page_num'] = mail_page_num

    # 判断是否有下一页数据
    if mails_paginator.get_page(mail_page_num).has_next():
        context['has_next'] = 'true'
    else:
        context['has_next'] = 'false'
    return JsonResponse(context)


def get_mails_pictures(mails):
    res = []
    for mail in mails:
        res.extend([pic for pic in WeiboPicture.objects.filter(weibo=mail)])
    return res
