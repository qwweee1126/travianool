# -*- coding: utf-8 -*-
import sys, os.path, threading, random, time, re
from datetime import datetime
from Queue import Queue
from Queue import Empty

#put common/ in sys.path
import sys, os.path
sys.path.append(os.path.normpath(os.getcwd()+'/..'))

from common.TravianClient import TravianClient
from common.TravianConfig import TravianConfig

class Producer(threading.Thread):
    """ The main purpose is to input gridID into a queue. """
    def __init__(self, threadname, scaner):
        threading.Thread.__init__(self, name = threadname)
        self.scaner = scaner
        
    def run(self):
        #Note: self.scaner.config.rect = [x1, y1, x2, y2]. x1<x2, y1<y2
        x=self.scaner.config.rect[0]+3
        while x+3<=self.scaner.config.rect[2]:
            y=self.scaner.config.rect[1] +3
            while y+3<=self.scaner.config.rect[3]:
                tmpx, tmpy = x, y
                if tmpx > self.scaner.config.ServerScale:
                    tmpx = x - self.scaner.config.ServerScale * 2 - 1
                if tmpy > self.scaner.config.ServerScale:
                    tmpy = y - self.scaner.config.ServerScale * 2 - 1
                #gridID=320801+tmpx-801*tmpy
                tmp = self.scaner.config.ServerScale
                gridID = (tmp - tmpy) * (2 * tmp + 1) + tmpx + tmp + 1
                self.scaner.queue.put(str(gridID), 1)
                print "Scan area(7x7) center: (%s, %s, %s)"%(x, y, gridID)    #扫描区域
                y += 7
            x += 7
            
        self.scaner.endflag = True
        print self.getName(),'Finished'

class KarteZThread(threading.Thread):
    """Read the karte?z=GID and retrieve karte?d=GID&c=xx"""
    def __init__(self, threadname, scaner):
        threading.Thread.__init__(self, name=threadname)
        self.scaner = scaner
    def run(self):
        try:
            while True:
                try:
                    gridID = self.scaner.queue.get(False)
                    fetchFlag = True
                except Empty:
                    fetchFlag = False
                
                if fetchFlag:
                    strHtml = self.scaner.tclient.getKarteZHtml(gridID)
                    self.parseKarteZHtml(strHtml)
                elif self.scaner.endflag:
                    print self.getName() + ' Finished'
                    return
                else:
                    time.sleep(random.randrange(10)/10.0)
        except:
            print 'exception catched in ' + self.getName()
            return
    
    def parseKarteZHtml(self, strHtml):
        """The use: """
        regObj = re.compile(r'<area id="a_[0-6]_[0-6]" shape="poly" coords="\d+, \d+, \d+, \d+, \d+, \d+, \d+, \d+" href="karte.php\?d=(\d{6})&c=([0-9a-z]{2})"/>')
        for matObj in regObj.finditer(strHtml):
            self.scaner.queueD.put([matObj.group(1), matObj.group(2)])    #the main purpose of this function. to get d=350470&c=7f

class KarteDThread(threading.Thread):
    def __init__(self, threadname, scaner):
        threading.Thread.__init__(self, name = threadname)
        self.scaner = scaner
        
    def run(self):
        try:
            while True:
                try:
                    gridID, cCode = self.scaner.queueD.get(False)
                    fetchFlag = True
                except Empty:
                    fetchFlag = False
                
                if fetchFlag:
                    strHtml = self.scaner.tclient.getKarteDHtml(gridID, cCode)
                    self.parseKarteDHtml(gridID, strHtml)
                elif self.scaner.endflagD:
                    print self.getName() + ' Finished'
                    return
                else:
                    time.sleep(random.randrange(10)/10.0)
        except:
            print 'exception catched in ' + self.getName()
            return
        
    def parseKarteDHtml(self, gridID, html):
        tempx, tempy = [int(gridID)%(self.scaner.config.ServerScale * 2 + 1) - (self.scaner.config.ServerScale + 1), self.scaner.config.ServerScale - int(gridID)/(self.scaner.config.ServerScale * 2 + 1)]
        dest = calcDestination(self.scaner.config.home[0], self.scaner.config.home[1], tempx, tempy)
          
        if html.find('资源分配') > 0:  #farm
            #farm
            Info = ['','','','','[%s:%s]:%s'%(tempx,tempy,gridID), '%f'%dest]
            for idx, matObj in enumerate(re.findall(r'<td class="s7 b">(\d+)</td>', html)):
                Info[idx] = matObj
            self.scaner.FarmWriter.write(",".join(Info) + '\n')
        elif html.find('种族') > 0:   #village
            #村庄名
            pattern = '<div class="ddb">([^<]*)</div>'
            matObj = re.search(pattern, html)
            village = matObj.group(1).decode('utf8').encode('cp936')    #村庄名
            
            #所有者
            pattern = r'<td><a href="spieler.php\?uid=\d+"> *<b>([^<]*)</b></a></td>'
            matObj = re.search(pattern, html)
            owner = matObj.group(1).decode('utf8').encode('cp936')
            
            #种族
            pattern = r'<td>种族:</td><td> <b>([^<]*)</b></td>'
            matObj = re.search(pattern, html)
            type = matObj.group(1).decode('utf8').encode('cp936')
            
            #联盟
            pattern = r'<td>联盟:</td><td><a href="allianz.php\?aid=\d+">([^<]*)</a></td>'
            matObj = re.search(pattern, html)
            alliance = matObj.group(1).decode('utf8').encode('cp936')
            
            #居民
            pattern = r'<td>居民:</td><td><b> (\d+)</b></td>'
            matObj = re.search(pattern, html)
            residen = matObj.group(1)
            
            #写入, (u'村庄,玩家,种族,联盟,居民,x,y\n'.encode('cp936'))
            self.scaner.VillageWriter.write(",".join([village, owner, type, alliance, residen, '[%s:%s]:%s'%(tempx,tempy,gridID), '%f'%dest]) + '\n')
        elif html.find('军队') > 0:   #Oasis
            #oasis
            reresult = re.search(r'<img src="img/un/m/w(?P<id>\d+).jpg" id="resfeld">', html)
            if reresult:
                strOasisType = reresult.group('id')
            else:
                strOasisType = ''
            Info = ['','','','','','','','','','','',strOasisType,'[%s:%s]:%s'%(tempx,tempy,gridID), '%f'%dest]
            
            #animal amount
            animals = ['老鼠', '蜘蛛', '野猪', '蛇', '蝙蝠', '狼', '熊', '鳄鱼', '老虎', '大象']
            pattern = r'<td align="right">&nbsp;<b>(\d+)</b></td><td>%s</td>'
            sum = 0
            for idx, animal in enumerate(animals):
                rslist = re.findall(pattern%animal, html)
                if rslist:
                    Info[idx] = rslist[0]
                    sum += int(Info[idx])
            Info[len(animals)] = str(sum)
            self.scaner.OasisWriter.write(",".join(Info) + '\n')
        else:
            print 'Invalid'

class Scaner(object):
    def __init__(self, config, tclient):
        object.__init__(self)
        self.config = config
        self.tclient = tclient
        
        self.queue = Queue(128)     #contain gridId
        self.endflag = False
        self.queueD = Queue(1024)
        self.endflagD = False
        
        #csv file
        dt = datetime.now()
        self.VillageWriter = ScanWriter('result' + os.path.sep + dt.strftime('%Y%m%d_%H%M%S') + 'Village.csv')
        self.FarmWriter = ScanWriter('result' + os.path.sep + dt.strftime('%Y%m%d_%H%M%S') + 'Farm.csv')
        self.OasisWriter = ScanWriter('result' + os.path.sep + dt.strftime('%Y%m%d_%H%M%S') + 'Oasis.csv')
        
        self.VillageWriter.write(u'村庄,玩家,种族,联盟,居民,(x:y):id,距离\n'.encode('cp936'))   #保证可以在excel中读取中文。
        self.FarmWriter.write(u'伐木场,泥坑,铁矿场,农场,(x:y):id,距离\n'.encode('cp936'))
        self.OasisWriter.write(u'老鼠,蜘蛛,野猪,蛇,蝙蝠,狼,熊,鳄鱼,老虎,大象,总数,绿洲类型,(x:y):id,距离\n'.encode('cp936'))
        
    def scan(self):
        print 'Starting threads ...'
        producer = Producer('Producer', self)
        producer.start()
        
        threadNum = self.config.ThreadNum / 8           #4
        if threadNum <= 0 :
            threadNum = 1
        threadNumD = self.config.ThreadNum - threadNum  #28
        if threadNumD <= 0 :
            threadNumD = 1
        
        threadlist = []
        for i in range(threadNum):
            thread = KarteZThread('Z Thread '+str(i+1), self)
            threadlist.append(thread)
            thread.start()
        
        threadlistD = []
        for i in range(threadNumD):
            thread = KarteDThread('D Thread '+str(i+1), self)
            threadlistD.append(thread)
            thread.start()
        
        for i in threadlist:
            i.join()
        self.endflagD = True
        print 'all Get Z thread finished'
        
        for i in threadlistD:
            i.join()
        print 'all Get D thread finished'

class ScanWriter(object):
    """保存log"""
    def __init__(self,filename):
        self.fs = open(filename,'w')    #open for append
    def __del__(self):
        self.fs.close()
    def write(self,str):
        self.fs.write(str)
    
def calcDestination(x1, y1, x2, y2):
    return ((x1-x2)**2 + (y1-y2)**2)**0.5

def main():
    init()
    config = TravianConfig()
    if not config.getConfig(sys.argv):
        sys.exit()
    
   
    
    #process login
    tclient = TravianClient(config)
    if config.ReLogin:
        if not tclient.login():
            print 'Invalid username or password'
            sys.exit()
    else:
        #cookie check
        strHtml = tclient.getKarteZHtml(config.cityId)
        if strHtml.find('login') > 0 and strHtml.find('用户名:') > 0 and strHtml.find('密码:') > 0 :
            print 'Cookie time out, relogin needed. Please use -l option or try --help option.'
            sys.exit()
    
    scaner = Scaner(config, tclient)
    scaner.scan()
    
def init():
    """ Make two dirs """
    for n in ['log','result']:
        if os.path.exists(n):
            if os.path.isfile(n):
                os.remove(n)
                os.mkdir(n)
        else:
            os.mkdir(n)

if __name__ == '__main__':
    main()
