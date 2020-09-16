#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import json
import yiban.mail
import yiban.YiBan
from yiban.utils import *
from yiban.config import *
from yiban.mail import mail


def clock(user):
       mail.mail(user['email'], datetime.now().strftime("%m-%d") + "易班打卡失败，出现新表单，请自行打卡一天",
                          "姓名:" + user["name"] + "\n"  +
                          "打卡时间:" + datetime.now().strftime("%m-%d") + "\n",img=None)
            


if __name__ == '__main__':
    print("**************全局信息**************")
    print('START_TIME', datetime.now().strftime("%m-%d %H:%M:%S %a"))
    print('MY_SENDER', MY_SENDER)
    print('MY_ADMIN', MY_ADMIN)
    print('MY_PASS', '********')
    print('NEED_SAVE_IMG', NEED_SAVE_IMG)
    if NEED_SAVE_IMG:
        print('IMG_SAVE_PATH', IMG_SAVE_PATH)
    print('DRIVER_PATH', DRIVER_PATH)
    print('DATA_PATH', DATA_PATH)
    
    print("**************全局信息**************")
    
    load_list = []
    if len(sys.argv) >= 2:
        with open(sys.argv[1], "r", encoding='utf-8')as fp:
            load_list = json.load(fp)
    else:
        with open(DATA_PATH + 'data.json', "r", encoding='utf-8')as fp:
            load_list = json.load(fp)
    print_and_log("**************开启报告**************")
    print_and_log("打卡人数:" + str(len(load_list)))
    for user in load_list:
        try:
            print('开始打卡:', user['name'])
            clock(user)
            print('结束打卡')
        except:
            print("[-]出现错误")
        if not DEBUG:
            print('休眠10s')
            time.sleep(10)
    print_and_log("**************结束报告**************")
    
    mail.quit()
    exit(0)
