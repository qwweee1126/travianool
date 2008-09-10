# -*- coding: utf-8 -*-
import getopt

class TravianConfig:
    def __init__(self):
        #Some default settings
        self.ServerName = 'scn1.travian.cn'
        self.UserName = '用户名'
        self.PassWord = '密码'
        self.ReLogin = False

        self.ThreadNum = 32
        self.RetryNum = 5
        
        self.ServerScale = 400  #地图坐标最大值
        self.cityId = '348070'      #你城市的id
        self.home = [35, -34]  #你的村庄，用来计算和其它村庄距离 
        self.rect = [25, -44, 45, -24]   #[x1, y1, x2, y2]. x1<x2, y1<y2 and x2-x1>=6, y2-y1>=6
        
    def getConfig(self ,argv):
        try:
            #短命令和长命令不需要按照顺序
            opts, arg = getopt.getopt(argv[1:], 'hls:u:p:t:r:m:', 
                                      ['help', 'login','server=', 'user=','pass=','thread=','retry=','version', 'home='])
        except getopt.GetoptError:
            # print help information and exit:
            self.usage()
            return False
        try:
            for o, a in opts:
                if o in ("-h", "--help"):
                    self.usage()
                    return False
                if o in ("-l", "--login"):
                    self.ReLogin = True
                if o in ("-s", "--server"):
                    self.ServerName = a
                if o in ("-u", "--user"):
#                    self.UserName = a.decode('GB18030')     #decode
                    self.UserName = a
                    print "Username:", a
                if o in ("-p", "--pass"):
                    self.PassWord = a
                if o in ("-t", "--thread"):
                    if int(a) < 2 :
                        raise OptionException, 'thread number should more than 1'
                    self.ThreadNum = int(a)
                if o in ("-r", "--retry"):
                    if int(a) < 1 :
                        raise OptionException, 'retrys should more than 0'
                    self.RetryNum = int(a)
                if o in ('--version',):
                    self.printVersion()
                    return False
                if o in ('-m', '--home'):
                    home = a.split(':')
                    try:
                        self.home[0] = int(home[0])
                        self.home[1] = int(home[1])
                    except:
                        raise OptionException, 'home should be in x:y format'
                        return False
                
            # 33:12 44:52
            if len(arg) == 2:
                x1,y1 = [int(k) for k in arg[0].split(':')]
                x2,y2 = [int(k) for k in arg[1].split(':')]
                if not self.inScale(x1, y1, x2, y2) :
                    raise OptionException, 'start and end coordinate should be in map'
                #x1<x2, y1<y2. 总是从左下往右上扫描
                if x1>x2:
                    x1, x2 = x2, x1
                if y1>y2:
                    y1, y2 = y2, y1
                self.rect = [x1,y1,x2,y2]
            else:
                raise OptionException, 'coordinate option error'
                
            return True
        except OptionException, e:
            print e
            self.usage()
            return False
                
    def inScale(self, *coordinate):
        for c in coordinate:
            if not (-self.ServerScale < c < self.ServerScale):
                return False
        return True
        
    def printVersion(self):
        print 'Travian scaner 0.0.6 (2007/09/07)'
        print 'Written by sevenever.'
        print 'Copyright (C) 2007 Sevenever.'
        print 'This is free software; see the source for copying conditions.  There is NO'
        print 'warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.'
    
    def usage(self):
        print '''Usage: scan [-options] startX:startY endX:endY

Scan travian(http://www.travian.cn) server for map infomation.
where options include:
    -h, --help  Show this help message.
    -l, --login Relogin with username and password given.
    -s, --server=HostNameOrIP
                The travian server host name or IP address(without 'http://' prefix).
    -c, --scale=value
                The scale of map on this server, 400 usually.
    -u, --user=username
                Username to login.
    -p, --pass=password
                Password to login.
    -t, --thread=value
                Max thread to fetch webpages(not exactly).
    -r, --retry=value
                Max retrys while fetch webpages(not exactly).
    -m, --home=x:y
                your home's coordinate.
    
    Report bugs to <xushaoxun@gmail.com>.'''

class OptionException(Exception):pass
        
if __name__ == '__main__':
    import sys
    cfg = TravianConfig()
    cfg.getConfig(sys.argv)
