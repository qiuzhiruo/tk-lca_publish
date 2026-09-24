# -*- coding:utf-8 -*-

import traceback
import os
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查位于水平面以下的资产"
        self.description = u"检查位于水平面以下的资产, 如果这些资产不需要，应该unload，而不是拖拽到地面下"
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
            underground = []
            for m in masters:
                poly = str(m).replace(':master', ':poly')
                if not pm.objExists(poly):
                    continue
                node = pm.PyNode(poly)
                bbox = node.getBoundingBox(space='world')
                if bbox.max().y < 0:
                    underground.append( str(m) )

            if underground:
                try:
                    pm.select(underground, r=True)
                except:
                    pass
                return u"以下资产位于水平面以下, 如果这些资产不需要, 请unload: \n" + '\n'.join( underground )

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

