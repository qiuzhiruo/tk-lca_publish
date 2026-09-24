# -*- coding:utf-8 -*-
__author__ = 'xiangquan'


import traceback
import os
import pymel.core as pm


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查 |assets|lay 下面是否有AR节点。'
        self.description = u'检查 |assets|lay 下面是否有AR节点，如果有，由艺术家判断是否需要保留。'
        self.auto_fix = False
        self.duty = u'艺术家本人。'
        return

    def run_check(self):
        try:
            # e.g. nt.AssemblyReference(u'iron_frame_a59_AR')]
            ars = pm.ls(type = 'assemblyReference')
            if ars:
                suspecious_ars = [str(pm.PyNode(ar).fullPath()) for ar in ars
                              if '|assets|lay' in pm.PyNode(ar).fullPath()
                                  and '|assets|lay|ars' not in pm.PyNode(ar).fullPath()]
                if suspecious_ars:
                    msg = u'以下AR节点位于 |assets|lay 组下，非ARs组内；请艺术家手动将需要保留的AR节点移到 |assets|lay|ars，将不需要的删除：\n'
                    msg += '\n'.join(suspecious_ars)
                    return msg

            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty

