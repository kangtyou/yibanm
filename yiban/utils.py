#!/usr/bin/python3
# -*- coding: utf-8 -*-

import random
import js2py
import json
import time
from datetime import datetime

LOG = []
LOG_FAILED = []


def print_and_log(msg):
    print(msg)
    LOG.append(msg)
    LOG.append("\n")


def get_all_log():
    return LOG


def print_and_log_failed(msg):
    print(msg)
    LOG.append(msg)
    LOG.append("\n")


def get_all_log_failed():
    return LOG


def random_temperature(low=3, high=8):
    return "36." + str(random.randrange(low, high, 1))


def make_csrf():
    js = """
        function r() {return Math.floor(65536 * (1 + Math.random())).toString(16).substring(1)}
        function o() {return r() + r() + r() + r() + r() + r() + r() + r()}
        """
    csrf_token = js2py.eval_js(js)()
    return csrf_token


def make_from(user, task_detail, task_ex):
    data = {}
    extend = {}
    data_template = {}
    info_template = {}
    for i in user["info"]:
        if i == task_detail["data"]["Id"]:
            data_template = task_detail["data"]["Form"]
            # info_template=user["info"][i]
            for j in user["info"][i]:
                info_template[j["id"]] = j["value"]
    for i in data_template:
        try:
            
            if i["props"]["label"] == "体温" or i["props"]["label"] == "当前具体体温":
                data[i["id"]] = random_temperature()
                pass
            elif i["props"]["label"] == "检测时间":
                data[i["id"]] = str(datetime.fromtimestamp(int(time.time())).strftime("%Y-%m-%d %H:%M"))
                pass
            elif i["props"]["label"] == "1":
                pass
            elif i["props"]["label"] == "2":
                pass
            elif i["props"]["label"] == "3":
                pass
            else:
                data[i["id"]] = info_template[i["id"]]
        except:
            pass
    if user["school"] == "长沙理工大学":
        extend = {"TaskId": task_ex["Id"],
                  "title": "任务信息",
                  "content": [{"label": "任务名称", "value": task_ex["Title"]},
                              {"label": "发布机构", "value": task_ex["PubOrgName"]},
                              {"label": "发布人", "value": task_ex["PubPersonName"]}
                              ]
                  }
    elif user["school"] == "**学院":
        extend = {"TaskId": task_ex["Id"],
                  "title": "任务信息",
                  "content": [{"label": "任务名称", "value": task_ex["Title"]},
                              {"label": "发布机构", "value": task_ex["PubOrgName"]}
                              ]
                  }
    
    params = {
        "data": json.dumps(data),
        "extend": json.dumps(extend)
    }
    return params


def make_date(date, school="长沙理工大学"):
    if school == "长沙理工大学":
        return str(date.month) + "月" + str(date.day) + "日"
    elif school == "**学院":
        return str(date.year) + "-" + str(date.month).rjust(2, "0") + "-" + str(date.day).rjust(2, "0")


def getimage(driver, url, img_path=None):
    driver.get(url)
    driver.refresh()
    time.sleep(5)
    if img_path is not None:
        driver.get_screenshot_as_file(img_path)
        print("已完成一次打卡，截图保存为：" + img_path)
    return driver.get_screenshot_as_png()


def all_true(map):
    res = True
    for i in map:
        res = res and map[i]
    return res
