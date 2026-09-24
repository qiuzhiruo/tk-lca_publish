# -*- coding:utf-8 -*-

import traceback
import os
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查大环的中心点是否在圆心位置"
        self.description = u"如果大环位置不在圆心，则publish结果将会与work文件不一致"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def getMasters(self, level='*:'):
        masters = pm.ls(level+'master')
        if masters:
            masters.extend( self.getMasters(level+level) )
        return masters

    def run_check(self):
        try:
            masters = self.getMasters()
            moved = []
            for m in masters:
                obj = str(m).replace(':master', ':global_ctrl')
                if pm.objExists(obj):
                    pynode = pm.PyNode(obj)
                    if not all([p.isEquivalent(pm.dt.Vector.zero, 0.001) for p in pynode.getPivots(objectSpace=True)]):
                        moved.append(str(pynode))

            if moved:
                return u"以下global_ctrl的轴心点有位移：\n" + '\n'.join(moved)

            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty

