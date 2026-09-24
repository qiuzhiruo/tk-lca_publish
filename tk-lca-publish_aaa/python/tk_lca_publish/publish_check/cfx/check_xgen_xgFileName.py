# -*-coding:utf-8-*-
"""
 @Time : 4/18/23 8:52 PM
 @Author : Taka(xutao)
"""

import traceback
import os
import maya.cmds as cmds
import pymel.core as pm
try:
    import xgenm as xg
    import xgenm.xgGlobal as xgg
except:
    pass


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查xgen file name"
        self.description = u"检查xgen collection xgFileName 是否正确"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return

    def run_check(self):
        try:
            if 'cloth' in self.dialog.task['name']:
                return ''

            file_name = os.path.basename(cmds.file(q=True, sn=True))
            bad_str = ''
            for palette in pm.ls(type='xgmPalette'):
                file_xgen = palette.xgFileName.get()
                if file_xgen != file_name[:-3]+ '__'+  palette+'.xgen':
                    bad_str += palette + ':' + file_xgen + '\n'
            if bad_str:
                bad_str = u'\n以下collection的xgen文件不在正常work路径下,请检查!.\n' + bad_str

            return bad_str
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