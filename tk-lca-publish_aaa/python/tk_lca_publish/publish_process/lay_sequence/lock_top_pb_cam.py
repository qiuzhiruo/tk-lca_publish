# -*- coding:utf-8 -*-

__author__ = 'xiangquan'

import os
import traceback
import shutil
import pymel.core as pm

IGNORE_LIST = ['FreeBlockCam', 'top_pb_cam']

# All publish process will use StdProcess as the class name.
class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"锁定top_pb_cam"
        self.description = u"锁定top_pb_cam节点和相关属性"
        return
    
    def proceed(self):
        check_root = 'assets|lay|top_pb_cam'
        try:
            #lock attribute
            pm.setAttr(check_root + '.tx', lock = True)
            pm.setAttr(check_root + '.ty', lock = True)
            pm.setAttr(check_root + '.tz', lock = True)
            pm.setAttr(check_root + '.rx', lock = True)
            pm.setAttr(check_root + '.ry', lock = True)
            pm.setAttr(check_root + '.rz', lock = True)
            pm.setAttr(check_root + '|top_pb_camShape' + '.hfa', lock = True)
            pm.setAttr(check_root + '|top_pb_camShape' + '.vfa', lock = True)
            #lock node
            pm.lockNode(check_root, lock = True)
            
            return ""
        except:
            return traceback.format_exc()
    
    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
