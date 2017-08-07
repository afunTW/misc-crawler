# 參考 https://github.com/twtrubiks/PttAutoLoginPost

import re
import sys
import time
import telnetlib
import json
import csv

from pprint import pprint


class Ptt(object):
    def __init__(self, host, user, password):
        self._host = host
        self._user = user.encode('big5')
        self._password = password.encode('big5')
        self._telnet = telnetlib.Telnet(host)
        self._content = ''

    @property
    def is_success(self):
        if u"密碼不對" in self._content:
            print("密碼不對或無此帳號。程式結束")
            sys.exit()
        if u"您想刪除其他重複登入" in self._content:
            print("刪除其他重複登入的連線....")
            self._telnet.write(b"y\r\n")
            time.sleep(5)
            self._content = self._telnet.read_very_eager().decode('big5', 'ignore')
        if u"請按任意鍵繼續" in self._content:
            print("資訊頁面，按任意鍵繼續...")
            self._telnet.write(b"\r\n")
            time.sleep(2)
        if u"您要刪除以上錯誤嘗試" in self._content:
            print("刪除以上錯誤嘗試...")
            self._telnet.write(b"y\r\n")
            time.sleep(2)
            self._content = self._telnet.read_very_eager().decode('big5', 'ignore')
        if u"您有一篇文章尚未完成" in self._content:
            print('刪除尚未完成的文章....')
            # 放棄尚未編輯完的文章
            self._telnet.write(b"q\r\n")
            time.sleep(2)
            self._content = self._telnet.read_very_eager().decode('big5', 'ignore')
        return True

    @property
    def input_user_password(self):
        if u"請輸入代號" in self._content:
            print('輸入帳號中...')
            self._telnet.write(self._user + b'\r\n')
            print('輸入密碼中...')
            self._telnet.write(self._password + b'\r\n')
            time.sleep(2)
            self._content = self._telnet.read_very_eager().decode('big5', 'ignore')
            return self.is_success
        return False

    def is_connect(self):
        self._content = self._telnet.read_very_eager().decode('big5', 'ignore')
        # print(self._content)
        if u"系統過載" in self._content:
            print('系統過載, 請稍後再來')
            sys.exit(0)
        return True

    def login(self):
        if self.input_user_password:
            print("----------------------------------------------")
            print("------------------ 登入完成 ------------------")
            print("----------------------------------------------")
            return True
        print("沒有可輸入帳號的欄位，網站可能掛了")
        return False

    def logout(self):
        print("登出中...")
        # q = 上一頁，直到回到首頁為止，g = 離開，再見
        self._telnet.write(b"qqqqqqqqqg\r\ny\r\n")
        time.sleep(1)
        self._telnet.close()
        print("----------------------------------------------")
        print("------------------ 登出完成 ------------------")
        print("----------------------------------------------")

    def post(self, board, title, content):
        print("發文中...")
        # s 進入要發文的看板
        self._telnet.write(b's')
        self._telnet.write(board.encode('big5') + b'\r\n')
        time.sleep(1)
        self._telnet.write(b'q')
        time.sleep(2)
        # 請參考 http://donsnotes.com/tech/charsets/ascii.html#cntrl
        # Ctrl+P
        self._telnet.write(b'\x10')
        # 發文類別
        self._telnet.write(b'1\r\n')
        self._telnet.write(title.encode('big5') + b'\r\n')
        time.sleep(1)
        # Ctrl+X
        self._telnet.write(content.encode('big5') + b'\x18')
        time.sleep(1)
        # 儲存文章
        self._telnet.write(b's\r\n')
        # 不加簽名檔
        self._telnet.write(b'0\r\n')
        print("----------------------------------------------")
        print("------------------ 發文成功 ------------------")
        print("----------------------------------------------")

    def query_by_id(self, user_id):
        print('查詢網友中 - {}'.format(user_id))
        self._telnet.write(b'qqqqqqqqqqt\r\nq\r\n')
        time.sleep(1)
        self._telnet.write(user_id.encode('big5', 'ignore') + b'\r\n')
        time.sleep(1)
        content = self._telnet.read_very_eager().decode('big5', 'ignore')
        self._telnet.write(b'qqqqqqq\r\n')
        return content

    def query_and_parse(self, user_id):
        result = self.query_by_id(user_id)
        lines = [re.sub('(\\x1b[^m]*m|\\x1b.*H|\\r\\n.*|\\n.*|▄.*▄)', '', i) for i in result.split('《') if '》' in i]
        lines = [line.strip(' ').strip('\r\n') for line in lines]
        data = {}

        for i, line in enumerate(lines):
                k, v = line.split('》')
                if k.strip() == u'個人名片':
                    continue
                data[k.strip(' ')] = v.strip(' ')

        return data

def main():
    host = 'ptt.cc'
    user = ''
    password = ''
    query_id = sys.argv[1:]
    data = []

    ptt = Ptt(host, user, password)
    time.sleep(1)
    if ptt.is_connect():
        if ptt.login():
            for id in query_id:
                query_data = ptt.query_and_parse(id)
                if query_data:
                    data.append(query_data)

    time.sleep(1)
    ptt.logout()
    print('length of data:', len(data))

    with open('monitor_data.csv', 'w+', encoding='utf-8') as f:
        writer = csv.DictWriter(f, data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        print('saved in monitor_data.csv')

if __name__ == "__main__":
    main()
