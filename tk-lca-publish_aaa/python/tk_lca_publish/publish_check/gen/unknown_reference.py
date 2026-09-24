# -*- coding:utf-8 -*-

import traceback

import os
import re
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查asb资产内的unknown reference节点。"
        self.description = u"检查asb资产内的unknown reference节点，手动或自动删除。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            ref = pm.ls(type='reference')
            unknw = []
            for r in ref:
                # _UNKNOWN_REF_NODE_
                if 'UNKNOWN' in str(r):
                    unknw.append(str(r))
            if len(unknw)>0:
                return u"发现unknown reference节点：" + '\n'.join(unknw)

            return ""

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        try:
            ref = pm.ls(type='reference')
            remain = []
            for r in ref:
                # _UNKNOWN_REF_NODE_
                if 'UNKNOWN' in str(r):
                    try:
                        try:
                            pm.lockNode(r, lock=False)
                        except:
                            pass
                        pm.delete(r)
                    except:
                        remain.append(str(r))
            if len(remain)>0:
                return 'The following unknown reference node can not be deleted: '+'\n'.join(remain)

            return ''

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


