# -*- coding:utf-8 -*-

import traceback

import os
import re
import pymel.core as pm

from proc.function_running_time import record_time


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"文件中不能有 TEXTURE。"
        self.description = u"文件中不能有常规的 texture"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):

        try:
            tex = pm.ls(type='file')
            if len(tex) > 0:
                tex_paths = []
                for i in tex:
                    tex_paths.append('{}:{}\n'.format(i.name(), pm.getAttr(i.name() + '.fileTextureName')))
                # l_names = [n.name() for n in tex]
                # # for i in l_names:
                # tex_path = [pm.getAttr(i + '.fileTextureName') for i in l_names]
                return u"文件中有常规的 texture 节点：\n" + '\n'.join(tex_paths)
            return ""

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        for tex in pm.ls(type='file'):
            pm.delete(tex)
        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


