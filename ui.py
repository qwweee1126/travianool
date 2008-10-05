# -*- coding: utf-8 -*-
#include parent path in sys.path
import os.path, threading, time, random, datetime
from Tkinter import *
from tkMessageBox import *

sys.path.append(os.path.normpath(os.getcwd()+'/..'))

from common.TravianConfig import TravianConfig
from common.TravianClient import TravianClient
from datetime import datetime, timedelta
import common.util as util

#global
AUTOLIST = 'autolist.txt'

#The main window    
class AutoAttackWindow(Tk):    
    """从autolist.txt读取攻击列表"""
    def __init__(self):
        Tk.__init__(self)
        
        #登陆信息 
        f1 = Frame(self)
        Label(f1, text=u'用户名').pack(side=LEFT)
        self.userEnt = Entry(f1, width=15)
        self.userEnt.insert(END, u'灶君')
        self.userEnt.pack(side=LEFT)
        
        Label(f1, text=u'密码').pack(side=LEFT)
        self.passEnt = Entry(f1, width=15)
        self.passEnt.pack(side=LEFT)
        
        f1.pack()
        
        Button(self, text=u'发兵', command=self.go).pack(side=LEFT)
        Button(self, text=u'暂停', command=self.stop).pack(side=LEFT)
    
    #登陆
    def login(self):
        self.config = TravianConfig(self.userEnt.get().encode('cp936'), self.passEnt.get())
        self.config.ReLogin = True
        
        self.tclient = TravianClient(self.config)
        if not self.tclient.login():
            return False
        return True
    
    def go(self):
        #先登陆
        if not self.login():
            showerror('无法登陆', '请确认用户名和密码正确')
            return
        
        #读取列表
        autolists = parseAttackList()
        if autolists:
            for p in autolists:
                thread = AutoThread(self.tclient, p) #需要用params.copy(), 一个线程一份参数
                thread.start()
                
    def stop(self):
        sys.exit(0)     #退出所有线程

#返回解析autolist.txt解析结果   
def parseAttackList(fname=AUTOLIST):
    try:
        auto = open(fname)
    except:
        showerror('打开autolist.txt错误', '打开autolist.txt错误')
        return False
    
    attacks = []
    idx = 1
    for line in auto:
        if line.startswith('#'):
            continue
        line = line[:line.index('#')].strip()   #kid=347270;sleep=364
        toks = line.split(';')
        params = {'id': 39}
        for tok in toks:
            if tok.startswith('#'):
                continue
            key, value = tok.split('=')
            if key in ['sleep', 'times']:
                value = int(value)
            if key == 'wait':
                value = int(value)+idx*3
            
            params[key] = value          #村庄id
            
        attacks.append(params)
        idx += 1
    return attacks

def _format(dt):
    """Format datetime"""
    return str(dt)[:19]

class AutoThread(threading.Thread):
    def __init__(self, tclient, params):
        threading.Thread.__init__(self, name=u'TD-%s'%params['kid'])
        self.tclient = tclient
        self.params = params
        self.sleep = self.params.pop('sleep')*2+20
        self.wait = self.params.pop('wait')
        self.times = self.params.pop('times')
        self.URL = 'http://scn1.travian.cn/a2b.php'
        
    def run(self):
        #等待时间
        now = datetime.now()
        d = timedelta(seconds=self.wait)
        util.info(u'现在时间%s 等待%s, 在%s出兵'%(_format(now), d, _format(now+d)))
        time.sleep(self.wait)
        
        for i in range(self.times):
            #can login?
            if not self.tclient.login():
                util.error(u'你没有登陆')
                break
            
            self.params['a'] = random.randint(1, 60000)     #某个随机数
            #post
            self.tclient.doPost(self.URL, self.params)
            util.info(u'%s 完成出兵%s任务, 等待%s秒开始下一轮。'%(self.getName(), self.params['kid'], self.sleep))
            time.sleep(self.sleep)
        util.info(u'%s任务完成, 退出.'%self.getName())

if __name__ == '__main__':
    win = AutoAttackWindow()
    win.mainloop()
#    for p in parseAttackList():
#        print p
