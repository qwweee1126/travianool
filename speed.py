# -*- coding: utf-8 -*-
"""计算到达需要时间以及什么时候出发才能按时到达"""
import unittest
S_GB = 6    #古罗马
S_JB = 5    #禁卫兵
S_DB = 7    #帝国兵
S_DQ = 14   #帝国骑士
S_JQ = 10   #将军骑士
S_CC = 4    #冲撞车
S_HC = 3    #火焰投石器

class Coordinate:
    def __init__(self, x, y):
        self.x = x
        self.y = y

def distance(c1, c2):
    """计算c1, c2的距离, 分两部分: 30 & >30"""
    d = ((c1.x-c2.x)**2 + (c1.y-c2.y)**2)**0.5
    if d>30:
        return [30, d-30]
    else:
        return [d, 0]

def timeNeeded(dis, arenaLevel, sp):
    """dis 距离, arenaLevel竞技场等级, sp速度
    返回秒
    """
    t1 = dis[0]/sp
    sp = (1+arenaLevel/10)*sp
    t2 = dis[1]/sp
    return round((t1+t2)*3600)
    

###########################################
## 测试
class SpeedTest(unittest.TestCase):
    def setUp(self):
        pass
    
    def testDistance(self):
        c1 = Coordinate(0, 0)
        c2 = Coordinate(3, 4)
        self.assertEqual([5,0], distance(c1, c2))
        
        c1 = Coordinate(35, -34)
        c2 = Coordinate(-70, 19)
        d = distance(c1, c2)
        self.assertAlmostEqual(30, d[0])
        self.assertAlmostEqual(87.618025829377018, d[1], 6)
        
        t = timeNeeded(d, 5.0, S_GB)
        self.assertEqual(53047, t)
        
if __name__ == '__main__':
    unittest.main()
