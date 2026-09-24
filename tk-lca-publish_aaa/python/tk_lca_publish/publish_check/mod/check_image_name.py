# -*- coding:utf-8 -*-
import os
import re
import sys
import maya.cmds as cmds
import pymel.core as pm
import shutil
from proc.function_running_time import record_time

# if sys.platform.startswith("win"):
#     sys.path.insert(0, r'W:\shome\PLETEMP\TD_MOD\python_pinyin_master')
# else:
#     sys.path.insert(0, '/mnt/work/shome/PLETEMP/TD_MOD/python_pinyin_master')

lib_repo = os.getenv('LC_LIB_REPO')
sys.path.insert(0, lib_repo + '/3rd_party/python_pinyin_master')

from pypinyin import lazy_pinyin

class StdCheck:

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查贴图中文名字，点击自动修复会转换成拼音"
        self.description = u"将贴图的中文名字转成拼音。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def has_chinese(self, text):
        pattern = re.compile(ur'[\u4e00-\u9fa5]')  # py2中需要明确使用 unicode 正则表达式
        return bool(pattern.search(text))

    @record_time(__file__)
    def run_check(self):

        self.error_file = {}
        for file_node in cmds.ls(typ='file'):
            tex_path = cmds.getAttr(file_node + '.fileTextureName')
            if self.has_chinese(os.path.basename(tex_path)):
                self.error_file.update({file_node: tex_path})
        if self.error_file:
            return '贴图名字中含有中文， 点击自动修复会变成拼音。'

        return ''

    def run_fix(self):
        '''Auto Fix'''
        if self.error_file:
            for node_name, file_path in self.error_file.items():
                new_path = os.path.join(os.path.dirname(file_path), ''.join(lazy_pinyin(os.path.basename(file_path))))
                if not os.path.exists(new_path):
                    shutil.copyfile(file_path, new_path)
                pm.setAttr(node_name + '.fileTextureName', new_path)

        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty


