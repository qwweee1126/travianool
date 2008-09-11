# -*- coding: utf-8 -*-
import logging

#config logging
logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(levelname)s %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S')

def unicode2cp936(ustr):
    if isinstance(ustr, unicode):
        ustr = ustr.encode('cp936')
    return ustr

def debug(ustr):
    logging.debug(unicode2cp936(ustr))

def info(ustr):
    logging.info(unicode2cp936(ustr))

def error(ustr):
    logging.error(unicode2cp936(ustr))
    
    
    
if __name__ == '__main__':
    debug(u'我')