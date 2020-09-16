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
    yb = yiban.YiBan.YiBan(user)
    if yb.login() is None:
        print_and_log_failed("[-]账号密码错误,打卡失败")
        print_and_log_failed("[-]账号:" + user['account'])
        print_and_log_failed("[-]姓名:" + user['name'])
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
    wf_form_list = []
    for form in WF_FORM_INFO:
        if form[2] == user['school']:
            wf_form_list.append(form[0])
    all_task = yb.get_uncompleted_list()
    for i in all_task["data"]:
        task_detail = yb.get_task_detail(i["TaskId"])["data"]
        StartTime = int(task_detail['StartTime'])
        TimeNow = int(time.time())
        EndTime = int(task_detail['EndTime'])
        if StartTime <= TimeNow < EndTime:
            if task_detail["WFId"] not in wf_form_list:
                print_and_log_failed('[-]出现新的表单,终止打卡')
                print_and_log_failed("[-]账号:" + user['account'])
                print_and_log_failed("[-]姓名:" + user['name'])
                print_and_log_failed("[-]表名:" + task_detail['Title'])
                print_and_log_failed("[-]表单:" + task_detail["WFId"])
                print_and_log_failed("[-]学校:" + user['school'])
                return
            wf_form = yb.get_form(task_detail["WFId"])
            form = make_from(user, wf_form, task_detail)
            submit_result = yb.submit(task_detail["WFId"], form)
            if submit_result.get('code') == 0:
                print_and_log("[+]" + task_detail["Title"] + " 打卡成功")
                share_url = yb.get_share_url(submit_result["data"])["data"]["uri"]
                print_and_log("分享的链接为: " + share_url)
                
                img = None
                if NEED_IMG:
                    img_path = None
                    if NEED_SAVE_IMG:
                        file_name = "%s-%s-%s.png" % (user['name'], task_detail["Title"], time.strftime("%Y-%m-%d"))
                        img_path = IMG_SAVE_PATH + file_name
                    img = getimage(
                        DRIVER,
                        share_url,
                        img_path
                    )
                mail.mail(user['email'], datetime.now().strftime("%m-%d") + " 易班打卡成功",
                          "姓名:" + user["name"] + "\n" +
                          "打卡名称:" + task_detail["Title"] + "\n" +
                          "打卡时间:" + datetime.now().strftime("%m-%d") + "\n" +
                          "分享链接:" + share_url + "\n" +
                          "打卡名称:" + task_detail["Title"] + "\n"
                          , img)
            else:
                print_and_log_failed("[-]" + user['name'] + task_detail["Title"] + " 打卡失败")


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
    print_and_log("**************开启打卡**************")
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
    print_and_log("**************结束打卡**************")
    
    msg2me = ""
    for i in LOG:
        msg2me += i
    mail.mail(MY_ADMIN, "易班打卡详细日志", msg2me)
    
    msg2me = ""
    for i in LOG_FAILED:
        msg2me += i
    if msg2me != "":
        mail.mail(MY_ADMIN, "易班打卡失败记录", msg2me)
    
    mail.quit()
    exit(0)
