# -*- coding:utf-8 -*-
import os
import re
import maya.cmds as cmds
import pymel.core as pm
from proc.function_running_time import record_time


class MG:
    windows_limit = 230


class StdCheck:

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查shader的名字的长度"
        self.description = u"windows系统对文件路径的长度有要求，文件路径过长会导致无法保存文件。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def get_all_materials(self):
        shading_engines = cmds.ls(type='shadingEngine')

        materials = set()

        for shading_engine in shading_engines:
            connections = cmds.listConnections(shading_engine + ".surfaceShader", source=True, destination=False)
            if connections:
                for mat in connections:
                    materials.add(mat)

        return list(materials)

    @record_time(__file__)
    def run_check(self):
        self.err_shader_list = []
        shader_list = self.get_all_materials()
        asset_name = os.path.basename(pm.sceneName()).split('.')[0]
        version_dir = self.dialog.d_assets_info[asset_name]['version_dir']
        shader_dir = os.path.join(version_dir, 'maya_shaders')
        for shader_name in shader_list:
            if len(os.path.join(shader_dir,  (shader_name + '.mb'))) > MG.windows_limit:
                shader_len = len(os.path.join(shader_dir,  (shader_name + '.mb'))) - MG.windows_limit
                print(shader_name)
                self.err_shader_list.append([shader_name, shader_len])

        if self.err_shader_list:
            msg = '下面这些shader的名字过长，缩短即可。\n {}'.format('\n'.join([i[0] for i in self.err_shader_list]))
            cmds.select([i[0] for i in self.err_shader_list])
            return msg

        return ''

    def run_fix(self):
        '''Auto Fix'''
        for err_shader_info in self.err_shader_list:
            new_name = err_shader_info[0][err_shader_info[1]:]
            cmds.rename(err_shader_info[0], new_name)

        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty


