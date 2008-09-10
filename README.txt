=====================================================================================
说明:
travian网页游戏的多线程扫田工具
注意：扫描范围最好不要太大，会造成网络堵塞

有问题请email: xushaoxun@gmail.com
=====================================================================================
需求:
python 2.5 
下载地址:http://www.python.org/ftp/python/2.5.2/python-2.5.2.msi


=====================================================================================
安装:

无需安装，下载使用即可。
下载地址: http://travianscanner2.googlecode.com/svn/trunk/

=====================================================================================
命令行参数:
python scanner.py [-options] startX:startY endX:endY

where options include:
    -h, --help   	使用帮助.
    -l, --login  	是否重新登陆.
    -s, --server=HostNameOrIP
                 	服务器地址(scn1.travian.cn, 无需'http://').
    -u, --user=username
                 	用户名.
    -p, --pass=password
                 	密码.

=====================================================================================
使用UI：
1. 安装python. http://www.python.org/ftp/python/2.5.2/python-2.5.2.msi
2. 点击scannerui.py, 然后查看result目录下的报表

=====================================================================================
使用命令行：
1. 安装python. http://www.python.org/ftp/python/2.5.2/python-2.5.2.msi
2. 打开命令窗口: 在开始->运行键入cmd.
3. cd到travianscanner目录.
4. 键入命令: python scanner.py -u 用户名 -p password -l 0:0 7:7
5. 到目录result下查看结果