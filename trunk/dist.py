# -*- coding: utf-8 -*-
#清理log, result目录
#发布
import os, tarfile, glob

def visit(arg, dirname, names):
    if os.path.split(dirname)[1] in arg:
        os.system('RMDIR %s /s /q'%dirname)
        print dirname, 'removed!'

def distAutoAttack(version):
    """打包autoattack"""
    files = ['COPYLEFT', u'autoattack使用说明.doc'.encode('cp936')]
    gifs = glob.glob('autoattack/img/*.gif')
    for gif in gifs:
        files.append(gif)
    
    __fillFiles(['autoattack', 'common'], 'py', files)

    fname = 'autoattack-%s.tar.gz'%version
    __tarFiles(fname, files)

def distScanner(version):    
    """打包scanner"""
    files = ['COPYLEFT', u'scanner使用说明.doc'.encode('cp936')]
    
    __fillFiles(['scanner', 'common'], 'py', files)
    
    fname = 'scanner-%s.tar.gz'%version
    __tarFiles(fname, files)

def distRecalc(version):
    """打包Recalc"""
    files = ['COPYLEFT', u'recalc使用说明.doc'.encode('cp936')]
    
    __fillFiles(['recalc', 'common'], 'py', files)
    __fillFiles(['recalc/img'], 'gif', files)
    
    fname = 'recalc-%s.tar.gz'%version
    __tarFiles(fname, files)
    
#######################################
def __fillFiles(dirs, suffix, files):
    for d in dirs:
        for f in glob.glob('%s/*.%s'%(d, suffix)):
            files.append(f)

def __tarFiles(tarName, files):
    tar = tarfile.open(tarName, 'w:gz')
    for f in files:
        tar.add(f)
    tar.close()
    
if __name__ == '__main__':
    #clean rubbish
    os.path.walk('.', visit, ['log', 'result'])
    for f in glob.glob('*.tar.gz'):
        os.remove(f)
        
    #####distribute
#    distAutoAttack("0.1")
#    distScanner(0.1)
#    distRecalc(0.2)