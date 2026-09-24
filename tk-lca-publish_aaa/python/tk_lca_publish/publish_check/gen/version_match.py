# -*- coding:utf-8 -*-

import traceback
import os

from proc.function_running_time import record_time


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查工程文件版本(Version)号是否和publish版本号一致。"
        self.description = u"task版本必须和publish版本一致，否则请使用shotgun菜单的Shotgun Save As或Version Up Current Scene升级版本。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):

        try:
            if self.dialog.step['name'] == 'dmt':
                import nuke
                nk_version = nuke.root()['name'].getValue()[-6:-3]
                if not nk_version.isdigit():
                    return u"nuke文件名不规范，应该yi三位数版本号结尾"

                print 'dialog.version_num: '+self.dialog.version_num
                if self.dialog.version_num != nk_version:
                    return u"nuke版本号和publish版本号不一致！请使用shotgun菜单的Shotgun Save As或Version Up Current Scene升级当前nuke版本，再publish。"
            else:
                import pymel.core as pm
                maya_version = os.path.basename( pm.system.sceneName() )[-6:-3]
                if not maya_version.isdigit():
                    return u"maya文件名不规范，应该以三位数版本号结尾"

                print 'dialog.version_num: '+self.dialog.version_num
                if self.dialog.version_num != maya_version:
                    return u"maya版本号和publish版本号不一致！请使用shotgun菜单的Shotgun Save As或Version Up Current Scene升级当前maya版本，再publish。"

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

