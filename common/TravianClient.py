# -*- coding: utf-8 -*- 
import os.path, re, time, sys
import urllib, urllib2, cookielib
import util

class TravianClient(object):
	def __init__(self, config):
		object.__init__(self)
		# the path and filename to save your cookies in
		self.COOKIEFILE = 'log/travian.cookie'
		
		# handle cookie
		self.cj = cookielib.LWPCookieJar()
		if os.path.isfile(self.COOKIEFILE):   #if we have a cookie file already saved then load it into
			self.cj.load(self.COOKIEFILE)    
		
		# get the HTTPCookieProcessor &  HTTPHandler and install the opener in urllib2
		self.HTTP_HANDLER=urllib2.HTTPHandler(debuglevel=0)    #debug msg
		self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj), self.HTTP_HANDLER)
		urllib2.install_opener(self.opener)

		self.txheaders = {'User-agent':'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.0.1) Gecko/2008070208 Firefox/3.0.1'}
		self.config = config
		
		#logging config
		if not os.path.exists('log'):
			os.mkdir('log')
		
	def login(self):
		if not self.cookieExpire() and not self.config.ReLogin:
			util.debug(u'不需重新登陆(Cookie未过期或ReLogin=False)')
			return True
		
		'''Retriving the cookie and save in COOKIEFILE.'''
		util.debug(u'取登陆表单.......')
		
		# get login form to retrive input name
		theurl = 'http://%s/login.php'%self.config.ServerName
		txdata = None     #if txdata==None, request use get
		
		#get login page and form item names
		try:
			req = urllib2.Request(theurl, txdata, self.txheaders)
			handle = urllib2.urlopen(req)
		except IOError, e:
			print e; return False
		else:
			strForm = handle.read()
			#here we got login web form
			userPat = ur'<input class="fm fm110" type="text" name="([0-9a-z]{7})"'
			userfield = re.findall(userPat, strForm)[0]

			passPat = ur'<input class="fm fm110" type="password" name="([0-9a-z]{7})"'
			passfield = re.findall(passPat, strForm)[0]
			
			extraPat = ur'<input type="hidden" name="([0-9a-z]{7})" value="(.*)">'
			extrafield, extravalue = re.findall(extraPat, strForm)[0]
			#loginvalue=1220424384, userfield=e4fb1ab, passfield=e99fa06, extrafield=ed4052c
		
		#login using user info
		self.HTTP_HANDLER._debuglevel = 0
		theurl = 'http://%s/dorf1.php'%self.config.ServerName
		# an example url that sets a cookie,
		# try different urls here and see the cookie collection you can make !
		params = {'w': '1024:768',
				  'login': int(time.time()),
				  userfield: self.config.UserName.decode('cp936').encode('utf8'),
				  passfield: self.config.PassWord,
				  extrafield: extravalue}
		txdata = urllib.urlencode(params) #the params that will be posted
		
		try:
			#txdata = None
			# if we were making a POST type request,
			# we could encode a dictionary of values here,
			# using urllib.urlencode(somedict)
			req = urllib2.Request(theurl, txdata, self.txheaders)
			handle = urllib2.urlopen(req)        #self.opener.open(req)
		except IOError, e:
			print e
			return False
		else:
			strHtml = handle.read()
			if strHtml.find('login') > 0 and strHtml.find('用户名:') > 0 and strHtml.find('密码:') > 0 :
				util.info(u'登陆失败, 请输入正确的用户名和密码')
				return False
			
#			for index, cookie in enumerate(self.cj):
#				print index, '  :  ', cookie
			self.cj.save(self.COOKIEFILE)                     # save the cookies again
		util.info(u'登陆成功, Cookie已被保存。')
		return True
	
	def cookieExpire(self):
		if not os.path.exists(self.COOKIEFILE):
			print 'cookie file not exist'
			return True
		for cookie in self.cj:
			if cookie.is_expired():return True
			
		return False
		
	def getKarteZHtml(self,gridID):
		theurl = 'http://%s/karte.php?z=%s'%(self.config.ServerName, gridID)
		return self.getHtmlByURL(theurl)
		
	def getKarteDHtml(self,gridID,cCode):
		theurl = 'http://%s/karte.php?d=%s&c=%s'%(self.config.ServerName, gridID, cCode)
		return self.getHtmlByURL(theurl)
		
	def getHtmlByURL(self,theurl):
		succ = False
		for i in range(self.config.RetryNum):
			if not succ:
				print 'Getting [%s] -- %s try.'%(theurl, i+1)
				try:
					req = urllib2.Request(theurl, None, self.txheaders)
					# create a request object
					
					handle = urllib2.urlopen(req)
					# and open it to return a handle on the url
				except IOError, e:
					print e
				else:
					succ = True
					strHtml = handle.read();
					#here we got web page http://s1.travian.cn/karte.php
					util.debug(u'成功取得 %s 的内容.'%theurl)
		return strHtml
	
	def doPost(self, theurl, params):
		self.HTTP_HANDLER._debuglevel = 0
		try:
			# create a request object
			req = urllib2.Request(theurl, urllib.urlencode(params), self.txheaders)
			
			# and open it to return a handle on the url
			handle = urllib2.urlopen(req)
#			handle.read()
		except IOError, e:
			print e
			sys.exit()
	
	
def save(content, fname):
	fsock = open(fname, 'w')
	print >> fsock, content
	fsock.close() 

if __name__ == '__main__':
	import TravianConfig as cfg
	
	client = TravianClient(cfg.TravianConfig())
	client.login()

#	w = client.getKarteZHtml(348070)
#	save(w, '348070.html')