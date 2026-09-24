# -*-coding:utf-8-*-
"""
 @Time : 4/19/23 10:57 AM
 @Author : Taka(xutao)
"""


import traceback
import os
import maya.cmds as cmds
try:
    import xgenm as xgm
    import xgenm.xgGlobal as xgg
except:
    pass


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查给植被分布用的flg资产的hair的正确性"
        self.description = u"检查collection命名问题,description命名问题"
        self.auto_fix = False
        self.duty = u"艺术家本人"
        return

    def run_check(self):
        try:
            task = self.dialog.task['name']
            task_key = {'hair': '_hi_',
                        'mid_hair': '_md_',
                        'low_hair': '_lo_'}

            if 'cloth' in task:
                return ''

            bad_str = ''
            if self.dialog.asset_type == 'flg':
                collections = xgm.palettes()
                if not collections:
                    return u'这个文件没有collection!'

                for collection in collections:
                    if task_key[task] not in collection:
                        bad_str += u'collection %s 的命名不正确, 请检查, hair任务要有_hi_关键字，其他同理\n' % collection

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