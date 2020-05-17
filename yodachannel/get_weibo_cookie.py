import os
import pickle
import platform
import time

import selenium.webdriver as se
from django.conf import settings
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def get_weibo_account_password(filepath):
    with open(filepath) as f:
        lines = f.read().splitlines()
    filtered_lines = list(filter(lambda line: line and line[0] != '#', lines))
    dic = {}
    for line in filtered_lines:
        line = line.strip()
        pair = line.split("=")
        dic[pair[0]] = pair[1]
    return dic


def get_cookie_from_network():
    options = se.ChromeOptions()
    options.add_argument('headless')
    if platform.system() == 'Linux':
        print('Linux')
        driver_location = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                       'chromedriver/Linux/chromedriver')
    else:
        print('MacOS')
        driver_location = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                       'chromedriver/MacOS/chromedriver')
    driver = se.Chrome(driver_location, options=options)
    dic = get_weibo_account_password(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'webapps/.env'))
    url_login = 'https://passport.weibo.cn/signin/login?entry=mweibo&res=wel&wm=3349&r=https%3A%2F%2Fm.weibo.cn'
    driver.get(url_login)
    # try:
    # 	WebDriverWait(driver, 10).until(
    # 		EC.visibility_of_element_located((By.ID, "loginName"))
    # 	).send_keys('441580902@qq.com')
    # finally:
    # 	driver.quit()
    # # driver.find_element_by_xpath('//input[@type="text"]').send_keys('441580902@qq.com')
    # time.sleep(2)
    # try:
    # 	WebDriverWait(driver, 10).until(
    # 		EC.visibility_of_element_located((By.ID, "loginPassword"))
    # 	).send_keys('yoka1997sgs')
    # finally:
    # 	driver.quit()
    # # driver.find_element_by_xpath('//input[@type="password"]').send_keys('yoka1997sgs')
    # time.sleep(2)
    # try:
    # 	WebDriverWait(driver, 10).until(
    # 		EC.element_to_be_clickable((By.ID, "loginAction"))
    # 	).click()
    # finally:
    # 	driver.quit()
    # driver.find_element_by_xpath('//a[@id="loginAction"]').click()
    time.sleep(2)
    driver.find_element_by_xpath('//input[@type="text"]').send_keys(dic['WEIBO_ACCOUNT_NAME'])  # 改成你的微博账号
    time.sleep(2)
    driver.find_element_by_xpath('//input[@type="password"]').send_keys(dic['WEIBO_ACCOUNT_PASSWORD'])  # 改成你的微博密码
    time.sleep(2)
    driver.find_element_by_xpath('//a[@id="loginAction"]').click()  # 点击登录
    # 获得 cookie信息
    time.sleep(2)
    cookie_list = driver.get_cookies()
    print(cookie_list)
    cookie_dict = {}
    for cookie in cookie_list:
        # 写入文件
        f = open(os.path.join(settings.BASE_DIR, 'yodachannel/cookies/') + cookie['name'] + '.weibo', 'wb')
        pickle.dump(cookie, f)
        f.close()
        if 'name' in cookie and 'value' in cookie:
            cookie_dict[cookie['name']] = cookie['value']
    print(cookie_dict)
    return cookie_dict


def get_cookie_from_cache():
    cookie_dict = {}
    for (parent, dirnames, filenames) in os.walk(os.path.join(settings.BASE_DIR, 'yodachannel/cookies/')):
        for filename in filenames:
            if filename.endswith('.weibo'):
                print(filename)
                with open(os.path.join(settings.BASE_DIR, 'yodachannel/cookies/') + filename, 'rb') as f:
                    d = pickle.load(f)
                    if 'name' in d and 'value' in d \
                            and 'expiry' in d:
                        expiry_date = int(d['expiry'])
                        if expiry_date > int(time.time()):
                            cookie_dict[d['name']] = d['value']
                        else:
                            return {}
    print(cookie_dict)
    return cookie_dict


def get_cookie():
    cookie_dict = get_cookie_from_cache()
    if not cookie_dict:
        cookie_dict = get_cookie_from_network()
    return cookie_dict



