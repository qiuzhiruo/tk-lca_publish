# -*- coding:utf-8 -*-

import traceback

import os
import re
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"asb内的组名不能重名"
        self.description = u"asb内如果有自定义的组，则组名称必须不能重名"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def getTransform(self, top='all'):
        if top=='all':
            children = pm.ls(type='transform')
        else:
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
                #trans.extend( self.getTransform(c) )
        return trans

    def run_check(self):

        try:
            if not pm.objExists("|master"):
                return u"没有找到最高层的 |master 组。"

            if not pm.objExists("|master|asb"):
                return u"没有找到次高层的 |master|asb 组。"

            groups =[g.name().split('|')[-1]  for g in  self.getTransform()]

            if len(groups)==len(set(groups)):
                return ""


            import collections
            counter_grp=collections.Counter(groups)

            same_grp=[]
            for k,v in counter_grp.items():
                if v!=1:
                    same_grp.append(k)
                    
            pm.select(clear=1)
            for grp in same_grp:
                pm.select('*'+grp,add=1)

            if len(same_grp)>0:
                return u"发现重名的组: \n" + '\n'.join(same_grp)

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


