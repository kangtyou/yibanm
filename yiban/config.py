#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os

_BASE_PATH = os.path.split(os.path.abspath(__file__))[0]

MY_SENDER = '1573049371@qq.com'  # 发件人邮箱账号
MY_ADMIN = '452370205@qq.com'  # 管理邮箱账号
MY_PASS = 'jnlprubnjzejgjij'  # 发件人邮箱密码

DEBUG = False
NEED_SAVE_IMG = False
NEED_IMG = False
IMG_SAVE_PATH = _BASE_PATH + "/../img/"  # 截图目录
DRIVER_PATH = _BASE_PATH + "/../driver/"  # chromedriver
DATA_PATH = _BASE_PATH + "/../data/"  # chromedriver

UserAgent = 'Mozilla/5.0 (Linux; Android 6.0.1; MuMu Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) ' \
            'Version/4.0 Chrome/52.0.2743.100 Mobile Safari/537.36 yiban_android '

WF_FORM_INFO = [
    ['a52a36ecb810e25060e1b33e3c718223', "学生每日健康打卡({}）", '**学院'],
]

DRIVER = ""
