# -*- coding: utf-8 -*-
#include parent path in sys.path
import os.path, threading
from Tkinter import *
from tkMessageBox import *

sys.path.append(os.path.normpath(os.getcwd()+'/..'))

import scanner
from common.TravianConfig import TravianConfig
from common.TravianClient import TravianClient
from common.uicomp import LabelEntry

ENTRY_WIDTH = 15
SERVERS = ['scn1', 'speed', 's1', 's2', 's3', 's4', 's5', 's6', 's7', 's8', 's9']

class ScannerWindow(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.serverField = LabelEntry(self, u'服务器', 'scn1.travian.cn')
        self.userField = LabelEntry(self, u'用户名', '灶君')
        self.passwordField = LabelEntry(self, u'密   码')
        self.co1Field = LabelEntry(self, u'坐标 1', '25:-44')
        self.co2Field = LabelEntry(self, u'坐标 2', '45:-24')
        self.homeField = LabelEntry(self, u'主村坐标', '35:-34')
        
        repBtn = Button(self, text=u'扫描', command=self.do)
        repBtn.pack()
        
        #make some dirs
        scanner.init()
        
    def do_inthread(self):
        t = threading.Thread(target=self.do, args=())  #生成线程
        t.start()
        
    def do(self):
        if self.getConfig():
            self.scan()
            showinfo(u"扫描完成", u'请至result目录下查看报表')
        
    def getConfig(self):
        server = self.serverField.getValue()
        co1 = self.co1Field.getValue()
        co2 = self.co2Field.getValue()
        username = self.userField.getValue()
#        print username, type(username)
        password = self.passwordField.getValue()
        home = self.homeField.getValue()
        
        #验证
        try:
            self.validateServer(server)
            self.validateCoordinate(co1)
            self.validateCoordinate(co2)
            self.validateCoordinate(home)
            self.validateNotNull(username, u'用户名')
            self.validateNotNull(password, u'密码')
        except ValidateException, x:
            showerror(x.title, x.message)
            return False
            
        #Config, 传过去的字符串是<type str>
        self.config = TravianConfig()
        argv = 'rubbish -s %s -u %s -p %s -m %s -l %s %s'%(server, username.encode('cp936'), password, home, co1, co2)
        return self.config.getConfig(argv.split())
    
# some validator    
    def validateServer(self, server):
        #Validate server
        servers = [s+'.travian.cn' for s in SERVERS]
        if server not in servers:
            raise ValidateException(u'服务器错误.', "请从以下服务器列表选择:\n" + "\n".join(servers))
        
        
    def validateCoordinate(self, s):
        xy = s.split(':')
        if len(xy) != 2:
            raise ValidateException(u'坐标错误.', "坐标格式 x:y");
        try:
            for i in xy:
                if not -400<=int(i)<=400:
                    raise Exception
        except:
            raise ValidateException(u'坐标错误.', "坐标格式 x:y\n且坐标值要在-400~400之间")
        else:
            return [int(c) for c in s.split(':')]
    
    def validateNotNull(self, s, msg):
        if not s:
            raise ValidateException(u'%s不能为空.'%msg, u'%s不能为空.'%msg)
    
    #do scan
    def scan(self):
        #process login
        tclient = TravianClient(self.config)
        if not tclient.login():
            showerror(u"登陆错误", u"错误的用户名和密码")
            return
        
        sc = scanner.Scaner(self.config, tclient)
        sc.scan()
        
class ValidateException(Exception):
    def __init__(self, title, message):
        Exception.__init__(self)
        self.title = title
        self.message = message

        
if __name__ == '__main__':
    win = ScannerWindow()
    win.mainloop()