#!/usr/bin/python3
# -*- coding: utf-8 -*-
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.header import Header
from email.utils import formataddr
from yiban.config import *
from yiban.utils import *


class Mail:
    def __init__(self):
        # 登录邮箱
        self.server = smtplib.SMTP_SSL("smtp.qq.com", 465)  # 用发件人邮箱的SMTP服务器地址和端口创建一个新的连接实例
        self.server.login(MY_SENDER, MY_PASS)  # 登录
    
    def mail(self, my_user, title, body, img=None):
        # 发邮件
        try:
            self.msg = MIMEMultipart()
            self.msg['To'] = formataddr(["AutoClockUser", my_user])
            self.msg['From'] = formataddr(["yiban_Auto_Clock_Bot", MY_SENDER])
            self.msg['Subject'] = Header(title, 'utf-8').encode()
            
            # 文本
            msg_text = MIMEText(body, 'plain', 'utf-8')
            msg_text["Accept-Language"] = "zh-CN"
            msg_text["Accept-Charset"] = "ISO-8859-1,utf-8"
            self.msg.attach(msg_text)
            
            # 截图
            if img is not None:
                img = MIMEImage(img)
                img.add_header('Content-ID', '<0>')
                img.add_header('Content-Disposition', 'attachment', filename="打卡截图.png")
                img.add_header('X-Attachment-Id', '0')
                self.msg.attach(img)
            # 括号中对应的是发件人邮箱账号、收件人邮箱账号、发送邮件
            self.server.sendmail(MY_SENDER, [my_user, ], self.msg.as_string())
            print('[+]已经向{}发送邮箱'.format(my_user))
        except Exception as e:
            print_and_log("[-]邮箱发送失败")
            print_and_log("[-]" + self.msg.as_string())
    
    def quit(self):
        self.server.quit()
        print('[+] 已经正常退出邮箱')


mail = Mail()
