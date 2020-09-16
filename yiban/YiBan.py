#!/usr/bin/python3
# -*- coding: utf-8 -*-

from yiban.config import *
from yiban.utils import *
import requests
import re
import json


class YiBan:
    name: object
    access_token: object
    detial_info = ''
    CSRF = make_csrf()
    COOKIES = {"csrf_token": CSRF}
    HEADERS = {"Origin": "https://c.uyiban.com", "User-Agent": UserAgent}
    
    def __init__(self, info):
        self.info = info
        self.account = info['account']
        self.passwd = info['password']
        
        self.session = requests.session()
    
    def request(self, url, method="get", params=None, cookies=None):
        if method == "get":
            req = self.session.get(url, params=params, timeout=10, headers=self.HEADERS, cookies=cookies)
        else:
            req = self.session.post(url, data=params, timeout=10, headers=self.HEADERS, cookies=cookies)
        if req.cookies.get_dict():  # 保持cookie有效
            self.session.cookies.update(req.cookies)
        try:
            return req.json()
        except:
            return None
    
    def login(self):
        params = {
            "account": self.account,
            "ct": 2,
            "identify": 0,
            "v": "4.7.4",
            "passwd": self.passwd
        }
        r = self.request(url='https://mobile.yiban.cn/api/v2/passport/login', params=params)
        
        if r is not None and str(r["response"]) == "100":
            self.access_token = r["data"]["access_token"]
            self.name = r["data"]["user"]["name"]
            return r
        else:
            return None
    
    def auth(self):
        location = self.session.get("http://f.yiban.cn/iapp/index?act=iapp7463&v=%s" % self.access_token,
                                    allow_redirects=False).headers["Location"]
        verifyRequest = re.findall(r"verify_request=(.*?)&", location)[0]
        # print(verifyRequest)
        return self.request(
            "https://api.uyiban.com/base/c/auth/yiban?verifyRequest=%s&CSRF=%s" % (verifyRequest, self.CSRF),
            cookies=self.COOKIES)
    
    def get_uncompleted_list(self):
        return self.request("https://api.uyiban.com/officeTask/client/index/uncompletedList?CSRF=%s" % self.CSRF,
                            cookies=self.COOKIES)
    
    def get_completed_list(self):
        return self.request("https://api.uyiban.com/officeTask/client/index/completedList?CSRF=%s" % self.CSRF,
                            cookies=self.COOKIES)
    
    def get_task_detail(self, taskId):
        return self.request(
            "https://api.uyiban.com/officeTask/client/index/detail?TaskId=%s&CSRF=%s" % (taskId, self.CSRF),
            cookies=self.COOKIES)
    
    def get_form(self, WFId):
        return self.request(
            "https://api.uyiban.com/workFlow/c/my/form/%s?CSRF=%s" % (WFId, self.CSRF),
            cookies=self.COOKIES)
    
    def submit(self, WFId, params):
        return self.request(
            "https://api.uyiban.com/workFlow/c/my/apply/%s?CSRF=%s" % (WFId, self.CSRF), method="post",
            params=params,
            cookies=self.COOKIES)
    
    def get_share_url(self, initiateId):
        return self.request(
            "https://api.uyiban.com/workFlow/c/work/share?InitiateId=%s&CSRF=%s" % (initiateId, self.CSRF),
            cookies=self.COOKIES)
    
    def get_upload_data(self, initiateId):
        return self.request(
            "https://api.uyiban.com/workFlow/c/work/show/view/%s?CSRF=%s" % (initiateId, self.CSRF),
            cookies=self.COOKIES)
    
    def get_screenshot(self, share_url, title):
        try:
            DRIVER.get(share_url)
            DRIVER.refresh()
            time.sleep(5)
            file_name = "%s-%s-%s.png" % (time.strftime("%Y-%m-%d"), title, self.info['name'])
            if NEED_SAVE_IMG:
                DRIVER.get_screenshot_as_file(IMG_SAVE_PATH + file_name)
            img = DRIVER.get_screenshot_as_png(IMG_SAVE_PATH + file_name)
            return img
        except Exception as e:
            print_and_log(str(e))
            return None
