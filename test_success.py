#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import sys
import json
import yiban.mail
import yiban.YiBan
from yiban.utils import *
from yiban.config import *
from yiban.mail import mail


def check(user):
    yb = yiban.YiBan.YiBan(user)
    if yb.login() is None:
        print_and_log_failed("[-]账号密码错误,打卡失败")
        print_and_log_failed("[-]账号:" + user['account'])
        return
    result_auth = yb.auth()
    data_url = result_auth["data"].get("Data")
    if data_url is not None:  # 授权过期
        print("授权过期")
        print("访问授权网址")
        result_html = yb.session.get(url=data_url, headers=yb.HEADERS,
                                     cookies={"loginToken": yb.access_token}).text
        re_result = re.findall(r'input type="hidden" id="(.*?)" value="(.*?)"', result_html)
        print("输出待提交post data")
        print(re_result)
        post_data = {"scope": "1,2,3,"}
        for i in re_result:
            post_data[i[0]] = i[1]
        print("进行授权确认")
        usersure_result = yb.session.post(url="https://oauth.yiban.cn/code/usersure",
                                          data=post_data,
                                          headers=yb.HEADERS, cookies={"loginToken": yb.access_token})
        if usersure_result.json()["code"] == "s200":
            print("授权成功！")
        else:
            print("授权失败！")
        print("尝试重新二次登录")
        yb.auth()
    all_task = yb.get_uncompleted_list()
    
    wf_form_list = []
    for form in WF_FORM_INFO:
        if form[2] == user['school']:
            wf_form_list.append(form[0])
    for i in all_task["data"]:
        task_detail = yb.get_task_detail(i["TaskId"])["data"]
        StartTime = int(task_detail['StartTime'])
        TimeNow = int(time.time())
        EndTime = int(task_detail['EndTime'])
        if StartTime <= TimeNow < EndTime:
            if task_detail["WFId"] not in wf_form_list:
                print("出现新的表单,终止打卡")
                print('[-]出现新的表单,终止打卡')
                print("[-]账号:" + user['account'])
                print("[-]表单:" + task_detail["WFId"])
                print("[-]学校:" + user['school'])
                return "出现新的表单,终止打卡"
            print("[-]" + user['account'] + task_detail["Title"] + " 可以打卡但是还未打卡")
            return "[-]" + user['account'] + task_detail["Title"] + " 可以打卡但是还未打卡"
    return None


if __name__ == '__main__':
    print("**************全局信息**************")
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
    print("**************开启检查**************")
    print("检查人数:" + str(len(load_list)))
    
    for user in load_list:
        try:
            buf = check(user)
            if buf is not None:
                LOG.append(buf + "\n")
        except Exception as e:
            print("[-]出现错误")
            print(e)
    print("**************结束检查**************")
    msg2me = ""
    for i in LOG:
        msg2me += i
    if msg2me != "":
        mail.mail(MY_ADMIN, "未打卡检查记录", msg2me)
    mail.quit()
    exit(0)
