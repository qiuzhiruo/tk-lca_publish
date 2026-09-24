# -*- coding:utf-8 -*-
__author__ = 'xiangquan'
import os
import traceback
import pymel.core as pm
import pymel.core.nodetypes as nt

import production.mayautils as mutils


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查model_layout。"
        self.description = u"如果场景中使用资产是mod.model_layout, 则需要换成mod.model"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def get_model_layout(self):
        d_model_layout = {}
        for n in pm.ls(type='assemblyReference'):
            path = str(n.getAttr("definition")).replace('\\', '/')
            v_dir = path.split('/publish/')[-1].split('/')[0]             #e.g.  'toys_police_car.mod.model_layout'
            tokens = v_dir.split('.')
            if tokens[1] == 'mod' and tokens[-1] == 'model_layout':
                correct_path = path.replace('model_layout', 'model')
                if os.path.isfile(correct_path):
                    d_model_layout[n.name()] = correct_path
        return d_model_layout

    def run_check(self):

        try:
            l_model_layout = self.get_model_layout().keys()
            if len(l_model_layout)>0:
                return u'有些资产在使用 model_layout: ' + u'\n'.join(l_model_layout)

            return ''

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        try:
            d_model_layout = self.get_model_layout()
            for ar_name, ar_file in d_model_layout.iteritems():
                ar_node = nt.Assembly(ar_name)
                ar_node.setActive('')
                ar_node.setAttr('definition', ar_file)
            return ''
        except:
            return traceback.format_exc()


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


