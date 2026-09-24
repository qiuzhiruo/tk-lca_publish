# -*- coding:utf-8 -*-

import traceback

import os
import re
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"rra内的组名称必须以_grp结尾"
        self.description = u"rra内如果有自定义的组，则组名称必须以_grp结尾"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def getTransform(self, top='|master|rra'):
        children = pm.listRelatives(top, type='transform')
        trans = []
        for c in children:
            if pm.referenceQuery(c, inr=True):
                continue
            elif c.name().endswith(':master') and pm.referenceQuery(c, inr=True):
                continue
            elif pm.mel.eval('nodeType ' + c.name()) == 'assemblyReference':
                continue
            else:
                trans.append(c)
                trans.extend( self.getTransform(c) )
        return trans

    def run_check(self):

        try:
            if not pm.objExists("|master"):
                return u"没有找到最高层的 |master 组。"

            if not pm.objExists("|master|rra"):
                return u"没有找到次高层的 |master|rra 组。"

            groups = self.getTransform()
            illegal_grp = []
            for g in groups:
                try:
                    if not g.name().endswith('_grp'):
                        illegal_grp.append(g.name())
                except:
                    pass

            if len(illegal_grp)>0:
                return u"发现不已_grp结尾的组: \n" + '\n'.join(illegal_grp)

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


