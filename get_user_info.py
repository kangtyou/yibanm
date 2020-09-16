#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
import csv
import json
import yiban.mail
import yiban.YiBan
from datetime import timedelta
from yiban.utils import *
from yiban.config import *
from yiban.mail import mail


def grab_info(user):
    yb = yiban.YiBan.YiBan({
        'account': user[0],
        'password': user[1],
        'email': user[2],
    })
    if yb.login() is None:
        print_and_log_failed("[-]账号密码错误,打卡失败")
        print_and_log_failed("[-]账号:" + user['account'])
        print_and_log_failed("[-]密码:" + user['password'])
        return None
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
    completed_list = yb.get_completed_list()
    grap_map = {}
    wf_form_list = []
    for form in WF_FORM_INFO:
        if form[2] == user[3]:
            grap_map[form[0]] = False
            wf_form_list.append(form[0])
    res = {}
    cnt = 0
    date = datetime.now()
    while not all_true(grap_map):
        if cnt > 10:
            break
        form_list = []
        for form in WF_FORM_INFO:
            if form[2] == user[3]:
                form_list.append(form[1].format(make_date(date, form[2])))
        for i in completed_list["data"]:
            if i['Title'] not in form_list:
                continue
            task_detail = yb.get_task_detail(i["TaskId"])["data"]
            if task_detail["WFId"] not in wf_form_list:
                print("出现新的表单,终止打卡")
                print_and_log_failed('[-]出现新的表单,终止打卡')
                print_and_log_failed('[-]' + "WFId: " + task_detail["WFId"])
                print_and_log_failed("[-]账号:" + str(user[0]))
                print_and_log_failed("[-]学校:" + str(user[3]))
                return
            if grap_map[task_detail["WFId"]]:
                continue
            submit_detail = yb.get_upload_data(task_detail["InitiateId"])
            res[task_detail["WFId"]] = submit_detail['data']['Initiate']['FormDataJson']
            grap_map[task_detail["WFId"]] = True
            print_and_log("[+] 成功抓取 "+i['Title'])
        date = date + timedelta(days=-1)
        cnt += 1
    return res


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
    
    data_main = []
    data_input = []
    data_add = []
    with open(DATA_PATH + 'data.json', "r", encoding='utf-8')as fp:
        data_main = json.load(fp)
    
    with open(DATA_PATH + 'input.csv', "r", encoding='utf-8')as fp:
        reader = csv.reader(fp, delimiter=';')
        for row in reader:
            data_input.append(row)
    if data_input[0][0] == 'account':
        data_input = data_input[1:]
    print_and_log('[+]增加' + str(len(data_input)) + '个条目')
    
    print_and_log("**************开启抓取**************")
    for user in data_input:
        print('开始抓取:', user[0])
        usermap = {
            "account": user[0],
            "password": user[1],
            "email": user[2],
            "school": user[3],
        }
        buf = grab_info(user)
        usermap['name']="null"
        if buf is not None:
            usermap["info"] = buf
            for i in buf:
                for j in buf[i]:
                    if j['label'] == '姓名':
                        usermap['name'] = j['value']
                        break
            data_add.append(usermap)
        print('结束抓取', user[0])
    data_main = data_main + data_add
    print_and_log("**************结束抓取**************")
    
    with open(DATA_PATH + 'add.json', "w", encoding='utf-8')as fp:
        json.dump(data_add, fp, indent=4)
    with open(DATA_PATH + 'data.json', "w", encoding='utf-8')as fp:
        json.dump(data_main, fp, indent=4)
    print('处理完成,已经将', DATA_PATH + 'input.scv', '中的条目添加到', DATA_PATH + 'data.json', '中')
    print('附加信息放在', DATA_PATH + 'add.json', '中')
    mail.quit()
    exit(0)
