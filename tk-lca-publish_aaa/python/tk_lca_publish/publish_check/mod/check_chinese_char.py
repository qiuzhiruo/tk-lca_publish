# -*- coding:utf-8 -*-
import os
import re
import maya.OpenMaya as om
import maya.cmds as cmds
import maya.mel as mel
import getpass
import re
import sys
import pymel.core as pm
import shutil
import traceback
from proc.function_running_time import record_time
from proc import get_materials_info
reload(get_materials_info)
from proc.get_materials_info import is_file_node_texture_exists

class StdCheck:

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查中文贴图"
        self.description = u"检查中文贴图"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    @record_time(__file__)
    def run_check(self):
        mel.eval("MLdeleteUnused;")
        tex_info = {}
        need_manually_rename = []
        no_tex_list = []
        for file_node in pm.ls(typ='file'):
            tex_path = pm.getAttr(file_node + '.fileTextureName')
            if not is_file_node_texture_exists(file_node.name()):
                no_tex_list.append(file_node.name())
            pattern = re.compile(u'[\u4e00-\u9fff\u3400-\u4dbf\u3000-\u303f]')
            if pattern.findall(os.path.basename(tex_path)) or str('?') in str(os.path.basename(tex_path)):
                tex_info.setdefault(len(os.path.basename(tex_path).replace(' ', '')), []).append(tex_path)

        for k, v in tex_info.items():
            if len(v) > 1:
                need_manually_rename.extend(v)
        if no_tex_list:
            err_msg = u'下面这些节点的贴图不存在\n{}'.format('\n'.join(no_tex_list))
            return err_msg
        if need_manually_rename:
            err_msg = u'下面这些贴图命名是中文且无法自动修改，需要手动改成英文命名\n{}'.format('\n'.join(need_manually_rename))
            return err_msg

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


