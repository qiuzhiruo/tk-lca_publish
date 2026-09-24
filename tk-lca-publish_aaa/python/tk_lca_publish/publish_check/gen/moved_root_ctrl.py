# -*- coding:utf-8 -*-

import traceback
import os
import pymel.core as pm


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"Root Ctrl不可以有任何位移"
        self.description = u"Root Ctrl不可以有任何位移"
        self.auto_fix = True
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
                obj = str(m).replace(':master', ':root_ctrl')
                if pm.objExists(obj):
                    pynode = pm.PyNode(obj)
                    if not pynode.getTranslation().isEquivalent(pm.dt.Vector.zero, 0.001) or not pynode.getRotation().isEquivalent(pm.dt.Vector.zero, 0.001):
                        moved.append(str(pynode))

            if moved:
                return u"以下Root Ctrl有位移：\n" + '\n'.join(moved)

            return ""

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        try:
            masters = self.getMasters()
            failed = []
            for m in masters:
                obj = str(m).replace(':master', ':root_ctrl')
                if pm.objExists(obj):
                    pynode = pm.PyNode(obj)
                    if not pynode.getTranslation().isEquivalent(pm.dt.Vector.zero, 0.001) or not pynode.getRotation().isEquivalent(pm.dt.Vector.zero, 0.001):
                        try:
                            pynode.setTranslation(pm.dt.Vector.zero)
                            pynode.setRotation(pm.dt.Vector.zero)
                        except:
                            failed.append(str(pynode))

            if failed:
                return u"以下资产无法自动将位移归零:\n" + '\n'.join(failed)

            return ""

        except:
            return traceback.format_exc()

        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty

