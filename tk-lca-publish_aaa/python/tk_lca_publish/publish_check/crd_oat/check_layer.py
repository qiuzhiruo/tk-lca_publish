# -*- coding: utf-8 -*-
# @Time    : 18-5-16 下午4:56
# @Author  : zhangzheng
__author__ = 'zhangzheng'
__maintainer__ = 'zhangzheng'

import traceback
import pymel.core as pm


# All system check classes will use StdCheck as the class name.
class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查文件内有没有多余的显示，动画，渲染层"
        self.description = u"文件内不应该有默认层之外的层"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return
    
    def run_check(self):
        try:
            defuals_layer = ['defaultLayer', 'defaultRenderLayer', 'BaseAnimation']
            pm.delete([i for i in pm.ls(type=['displayLayer', 'renderLayer']) if i not in defuals_layer])
            layers = [i.name() for i in pm.ls(type=['displayLayer', 'renderLayer', 'animLayer']) if i not in defuals_layer]
            if len(layers) != 0:
                return u'场景中含有自定义层\n\t%s' % ''.join(layers)
            else:
                return ''
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

