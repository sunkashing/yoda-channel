import os
import sys
import traceback
from datetime import datetime

import requests
from requests.adapters import HTTPAdapter

from webapps import settings
from yodachannel.get_frame import get_frame_from_video
from yodachannel.models import Weibo, WeiboPicture, WeiboVideo
import json


def load_weibo(weibo_json_path):
    with open(weibo_json_path) as weibo_json:
        data = json.load(weibo_json)

    for weibo in data['weibo']:
        create_weibo(weibo)


def create_weibo(weibo):
    new_weibo = Weibo(weibo_num=str(weibo['id']),
                      user_id=str(weibo['user_id']),
                      screen_name=weibo['screen_name'],
                      bid=weibo['bid'],
                      text=weibo['text'].lower(),
                      article_url=weibo['article_url'],
                      pics=weibo['pics'],
                      video_url=weibo['video_url'],
                      location=weibo['location'],
                      created_at=datetime.strptime(weibo['created_at'], '%Y-%m-%d'),
                      source=weibo['source'],
                      attitudes_count=weibo['attitudes_count'],
                      comments_count=weibo['comments_count'],
                      reposts_count=weibo['reposts_count'],
                      topics=weibo['topics'],
                      at_users=weibo['at_users'])
    new_weibo.save()
    download_pictures(new_weibo, weibo)
    download_videos(new_weibo, weibo)
    if check_mail(new_weibo, weibo):
        parse_mail(new_weibo, weibo)
    elif check_blog(new_weibo, weibo):
        parse_blog(new_weibo, weibo)
    elif check_video(new_weibo, weibo):
        parse_video(new_weibo, weibo)
    else:
        new_weibo.is_other = True
        new_weibo.save()


def parse_video(new_weibo, weibo):
    video_text = weibo['text']
    if '超话' in video_text:
        new_weibo.video_title = video_text[video_text.rindex('超话') + 2:].strip(' ')
    else:
        new_weibo.video_title = video_text.strip(' ')
    new_weibo.save()


def parse_blog(new_weibo, weibo):
    paresd_blog = weibo['text'].lower()
    if '「' and '」' in paresd_blog:
        new_weibo.blog_title = paresd_blog[paresd_blog.index('「'):paresd_blog.rindex('」') + 1]
    else:
        new_weibo.blog_title = '「無題」'
    new_weibo.save()


def parse_mail(new_weibo, weibo):
    parsed_mail = weibo['text'].lower()
    if '名：' in parsed_mail:
        parsed_mail = parsed_mail[parsed_mail.rindex('名：') + 2:].strip(' ')
    elif '名:' in parsed_mail:
        parsed_mail = parsed_mail[parsed_mail.rindex('名:') + 2:].strip(' ')
    elif '题：' in parsed_mail:
        parsed_mail = parsed_mail[parsed_mail.rindex('题：') + 2:].strip(' ')
    elif '题:' in parsed_mail:
        parsed_mail = parsed_mail[parsed_mail.rindex('题:') + 2:].strip(' ')
    elif 'jst' in parsed_mail:
        parsed_mail = parsed_mail[parsed_mail.rindex('jst') + 3:].strip(' ')
    elif '#' in parsed_mail:
        parsed_mail = parsed_mail[parsed_mail.rindex('#') + 1:].strip(' ')
    if 'jst' in parsed_mail:
        parsed_mail = parsed_mail[parsed_mail.rindex('jst') + 3:].strip(' ')

    if '无题' in parsed_mail:
        new_weibo.mail_title = '無題'
        parsed_mail = parsed_mail[2:].strip(' ')
    elif '無題' in parsed_mail:
        new_weibo.mail_title = '無題'
        parsed_mail = parsed_mail[2:].strip(' ')
    elif '/' in parsed_mail:
        index = parsed_mail.index('/')
        new_weibo.mail_title = parsed_mail[:index]
        parsed_mail = parsed_mail[index + 1:].strip(' ')
    else:
        new_weibo.mail_title = '無題'

    new_weibo.mail_text = parsed_mail
    new_weibo.save()


def check_video(new_weibo, weibo):
    if weibo['video_url'].strip(' ') != '':
        new_weibo.is_video = True
        new_weibo.save()
        return True
    return False


def check_mail(new_weibo, weibo):
    if '手机博' in weibo['source'] or '手机博' in weibo['topics'] or '手机博#' in weibo['text']:
        new_weibo.is_mail = True
        new_weibo.save()
        return True
    return False


def check_blog(new_weibo, weibo):
    lo = weibo['text'].lower()
    if '博客' not in weibo['source'] and '博客' not in weibo['topics'] and '博客#' not in lo:
        if 'blog' not in lo or ('blog' in lo and 'via' in lo):
            return False
    new_weibo.is_blog = True
    new_weibo.save()
    return True


def download_pictures(new_weibo, weibo):
    pictures = weibo['pics'].strip(' ').split(',')
    for i, picture in enumerate(pictures):
        picture = picture.strip(' ')
        if picture is '':
            continue
        file_name = str(weibo['id']) + '_' + str(i + 1) + '.jpg'
        file_path = os.path.join(
            os.path.join(
                settings.STATICFILES_DIR, 'yodachannel/images/weibo/'), file_name)

        if not download_one_file(picture, file_path):
            continue
        new_weibo_picture = WeiboPicture(weibo=new_weibo,
                                         url=picture,
                                         file_name=file_name)
        new_weibo_picture.save()


def download_videos(new_weibo, weibo):
    videos = [weibo['video_url'].strip(' ')]
    for i, video in enumerate(videos):
        if video is '':
            continue
        file_name = new_weibo.created_at.strftime('%Y%m%d') + '_' + str(weibo['id']) + '.mp4'
        file_path = os.path.join(
            os.path.join(
                settings.STATICFILES_DIR, 'yodachannel/videos/weibo/'), file_name)
        if not download_one_file(video, file_path):
            continue
        new_weibo_video = WeiboVideo(weibo=new_weibo,
                                     url=video,
                                     file_name=file_name)

        picture_file_name = new_weibo.created_at.strftime('%Y%m%d') + '_' + str(weibo['id']) + '.jpg'
        get_frame_from_video(file_path,
                             1,
                             os.path.join(settings.STATICFILES_DIR, 'yodachannel/videos/weibo/images/'),
                             picture_file_name)
        new_weibo_video.picture_file_name = picture_file_name
        new_weibo_video.save()


def download_one_file(url, file_path):
    """下载单个文件(图片/视频)"""
    try:
        if not os.path.isfile(file_path):
            s = requests.Session()
            s.mount(url, HTTPAdapter(max_retries=5))
            downloaded = s.get(url, timeout=(5, 10))
            with open(file_path, 'wb') as f:
                f.write(downloaded.content)
    except Exception as e:
        print('Error: ', e)
        traceback.print_exc()
        return False
    return True


