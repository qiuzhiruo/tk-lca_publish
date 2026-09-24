# -*- coding: utf-8 -*-

import traceback
import re
import pymel.core as pm



    
# All system check classes will use StdCheck as the class name.
class StdCheck():
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查文件命名是否符合规范"
        self.description = u"检查文件命名是否符合规范，确保命名格式为：{镜头名}.crd.crowd_people.{版本}.{后缀}。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return



    def run_check(self):
        try:
            filename = pm.sceneName().split('/')[-1]

            match = re.match(r'%s\.v\d{3}\.ma'%self.dialog.version_key.replace('.','\.'),filename)
            if match:
                return ''
            else:
                return filename+u'不符合命名标准！\n请参考规范:b20500.crd.crowd_people.v001.ma'
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

