# -*- coding:utf-8 -*-

import traceback

import os
import re
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查组装资产里的空组。"
        self.description = u"|master|asb组下如果有空组就直接删除。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def findEmptyGrp(self, obj):
        '''
        returned bool is used as self checking internally, therefore has no meaning as return function
        '''
        empty = []
        c = pm.listRelatives(obj, c=True, pa=True, type='transform')
        if len(c)>0:
            for item in c:
                if ':master' in str(item):
                    continue
                empty.extend( self.findEmptyGrp(item) )
        else:
            if pm.mel.eval('nodeType ' + obj.name())=='transform' and not obj.getShape() and not obj.isReferenced():
                empty.append(obj)
        return empty

    def run_check(self):
        try:
            l_empty_trans = self.findEmptyGrp('|master|asb')

            if len(l_empty_trans) > 0:
                return u'发现空组:\n' + '\n'.join([str(i) for i in l_empty_trans])

            return ""

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        try:
            l_empty_trans = self.findEmptyGrp('|master|asb')

            for trans in l_empty_trans:
                if pm.objExists(trans):
                    pm.delete(trans)

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


