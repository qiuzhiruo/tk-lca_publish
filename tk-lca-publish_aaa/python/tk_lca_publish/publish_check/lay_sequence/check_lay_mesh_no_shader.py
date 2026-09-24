# -*- coding:utf-8 -*-


import traceback
import pymel.core as pm


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"lay组下无材质模型"
        self.description = u"检查lay组下无材质的模型（无材质影响预渲染）"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            empty_list = []

            sels = pm.ls("|assets|lay", dag=True, type='mesh')
            objs = []
            for sel in sels:
                if "|assets|lay|ars" in sel.longName():
                    continue
                objs += pm.listRelatives(sel, p=True)
            objs = list(set(objs))
            for o in objs:
                shape = pm.listRelatives(o, s=True)[0]
                shader_list = set(pm.listConnections(shape, type='shadingEngine'))
                if not shader_list:
                    empty_list.append(o.longName())
            if empty_list:
                return_string = ''
                return_string += u'以下物体无材质:\n' + '\n'.join(empty_list)
                return return_string
            else:
                return ''
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


