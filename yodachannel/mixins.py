from django.db import models, IntegrityError  # 查询失败时我们需要用到的模块
import subprocess  # 用于运行代码
from django.http import Http404  # 当查询操作失败时返回404响应
import json

from django.core.serializers import serialize
from django.http import JsonResponse
from django.shortcuts import render

# Create your views here.
# 定义最基本的 API 视图
from django.views import View


class APIQuerysetMinx(object):
    """
    用于获取查询集。在使用时，model 属性和 queryset 属性必有其一。

    :model: 模型类
    :queryet: 查询集
    """
    model = None
    queryset = None

    def get_queryset(self):
        """
        获取查询集。若有 model 参数，则默认返回所有的模型查询实例。
        :return: 查询集
        """

        # 检验相应参数是否被传入，若没有传入则抛出错误
        assert self.model or self.queryset, 'No queryset fuound.'
        if self.queryset:
            return self.queryset
        else:
            return self.model.objects.all()


class APISingleObjectMixin(APIQuerysetMinx):
    """
    用于获取当前请求中的实例。

    :lookup_args: list, 用来规定查询参数的参数列表。默认为 ['pk','id]
    """
    lookup_args = ['pk', 'id']

    def get_object(self):
        """
        通过查询 lookup_args 中的参数值来返回当前请求实例。当获取到参数值时，则停止
        对之后的参数查询。参数顺序很重要。
        :return: 一个单一的查询实例
        """
        queryset = self.get_queryset()  # 获取查询集
        for key in self.lookup_args:
            if self.kwargs.get(key):
                id = self.kwargs[key]  # 获取查询参数值
                try:
                    instance = queryset.get(id=id)  # 获取当前实例
                    return instance  # 实例存在则返回实例
                except models.ObjectDoesNotExist:  # 捕捉实例不存在异常
                    raise Http404('No object found.')  # 抛出404异常响应
        raise Http404('No object found.')  # 若遍历所以参数都未捕捉到值，则抛出404异常响应


class APIListMixin(APIQuerysetMinx):
    """
    API 中的 list 操作。
    """

    def list(self, fields=None):
        """
        返回查询集响应
        :param fields: 查询集中希望被实例化的字段
        :return: JsonResopnse
        """
        return self.response(
            queryset=self.get_queryset(),
            fields=fields)  # 返回响应


class APICreateMixin(APIQuerysetMinx):
    """
    API 中的 create 操作
    """

    def create(self, create_fields=None):
        """
        使用传入的参数列表从 POST 值中获取对应参数值，并用这个值创建实例，
        成功创建则返回创建成功响应，否则返回创建失败响应。
        :param create_fields: list, 希望被创建的字段。
        若为 None, 则默认为 POST 上传的所有字段。
        :return: JsonResponse
        """
        create_values = {}
        if create_fields:  # 如果传入了希望被创建的字段，则从 POST 中获取每个值
            for field in create_fields:
                create_values[field] = self.request.POST.get(field)
        else:
            for key in self.request.POST:  # 若未传入希望被创建字段，则默认为 POST 上传的
                # 字段都为创建字段。
                create_values[key] = self.request.POST.get(key);
        queryset = self.get_queryset()  # 获取查询集
        try:
            instance = queryset.create(**create_values)  # 利用查询集来创建实例
        except IntegrityError:  # 捕捉创建失败异常
            return self.response(status='Failed to Create.')  # 返回创建失败响应
        return self.response(status='Successfully Create.')  # 创建成功则返回创建成功响应


class APIDetailMixin(APISingleObjectMixin):
    """
    API 操作中查询实例操作
    """

    def detail(self, fields=None):
        """
        返回当前请求中的实例
        :param fields: 希望被返回实例中哪些字段被实例化
        :return: JsonResponse
        """
        return self.response(
            queryset=[self.get_object()],
            fields=fields)


class APIUpdateMixin(APISingleObjectMixin):
    """
    API 中更新实例操作
    """

    def update(self, update_fields=None):
        """
        更新当前请求中实例。更新成功则返回成功响应。否则，返回更新失败响应。
        若传入 updata_fields 更新字段列表，则只会从 PUT 上传值中获取这个列表中的字段，
        否则默认为更新 POST 上传值中所有的字段。
        :param update_fields: list, 实例需要被更新的字段
        :return: JsonResponse
        """
        instance = self.get_object()  # 获取当前请求中的实例
        if not update_fields:  # 若无字段更新列表，则默认为 PUT 上传值的所有数据
            update_fields = self.request.PUT.keys()
        try:  # 迭代更新实例字段
            for field in update_fields:
                update_value = self.request.PUT.get(field)  # 从 PUT 中取值
                setattr(instance, field, update_value)  # 更新字段
            instance.save()  # 保存实例更新
        except IntegrityError:  # 捕捉更新错误
            return self.response(status='Failed to Update.')  # 返回更新失败响应
        return self.response(
            status='Successfully Update')  # 更新成功则返回更新成功响应


class APIDeleteMixin(APISingleObjectMixin):
    """
    API 删除实例操作
    """

    def remove(self):
        """
        删除当前请求中的实例。删除成功则返回删除成功响应。
        :return: JsonResponse
        """
        instance = self.get_object()  # 获取当前实例
        instance.delete()  # 删除实例
        return self.response(status='Successfully Delete')  # 返回删除成功响应


class APIMethodMapMixin(object):
    """
    将请求方法映射到子类属性上

    :method_map: dict, 方法映射字典。
    如将 get 方法映射到 list 方法，其值则为 {'get':'list'}
    """
    method_map = {}

    def __init__(self, *args, **kwargs):
        """
        映射请求方法。会从传入子类的关键字参数中寻找 method_map 参数，期望值为 dict类型。寻找对应参数值。
        若在类属性和传入参数中同时定义了 method_map ，则以传入参数为准。
        :param args: 传入的位置参数
        :param kwargs: 传入的关键字参数
        """
        method_map = kwargs['method_map'] if kwargs.get('method_map', None) \
            else self.method_map  # 获取 method_map 参数
        for request_method, mapped_method in method_map.items():  # 迭代映射方法
            mapped_method = getattr(self, mapped_method)  # 获取被映射方法
            method_proxy = self.view_proxy(mapped_method)  # 设置对应视图代理
            setattr(self, request_method, method_proxy)  # 将视图代码映射到视图代理方法上
        super(APIMethodMapMixin, self).__init__(*args, **kwargs)  # 执行子类的其他初始化

    def view_proxy(self, mapped_method):
        """
        代理被映射方法，并代理接收传入视图函数的其他参数。
        :param mapped_method: 被代理的映射方法
        :return: function, 代理视图函数。
        """

        def view(*args, **kwargs):
            """
            视图的代理方法
            :param args: 传入视图函数的位置参数
            :param kwargs: 传入视图函数的关键字参数
            :return: 返回执行被映射方法
            """
            return mapped_method()  # 返回执行代理方法

        return view  # 返回代理视图
