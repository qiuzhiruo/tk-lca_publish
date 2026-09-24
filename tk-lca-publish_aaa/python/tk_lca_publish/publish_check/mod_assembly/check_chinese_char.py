# -*- coding:utf-8 -*-

import re

import pymel.core as pm


class StdCheck:

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查中文贴图"
        self.description = u"检查中文贴图"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        error_info = {}
        for file_node in pm.ls(typ='file'):
            tex_path = pm.getAttr(file_node + '.fileTextureName')
            pattern = re.compile(u'[\u4e00-\u9fff\u3400-\u4dbf\u3000-\u303f]')
            if pattern.findall(tex_path) or str('?') in str(tex_path):
                error_info.update({file_node: tex_path})

        if error_info:
            pm.select(error_info.keys())
            return u'这些贴图中包含中文路径\n{}'.format('\n'.join(error_info.values()))

        return ''

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


