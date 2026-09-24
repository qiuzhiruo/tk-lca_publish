# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Yu HuaZhuo
#
# Date: 2017.03
#
# Description: One and only one mesh node under it's associated transform node, no sibling mesh.
#              Clean the intermediate nodes if they exists);
#              mesh name = transform name + 'Shape'.
#              Note: This check needs to be executed after clean all instances
#
########################################################################################
import sys
import os
import traceback
import pymel.core as pm
from xml.etree import ElementTree
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查透明物体命名是否含(glass或water)。。"
        self.description = u"如果模型是玻璃且的材质是透明的,则命名需要加上glass或water,不是可以忽略检查。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    @record_time(__file__)
    def run_check(self):
        try:
            self.dialog.mod_asset = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]],
                                                            ['sg_asset_type'])
            
            if self.dialog.mod_asset['sg_asset_type'] in ['chr', 'crd','asm']:
                return ""

            transparency_mesh_list=[]

            for sg in pm.ls(type='shadingEngine'):
                shader_list = []
                shader_list.extend(pm.listConnections(sg, type='lambert'))
                shader_list.extend(pm.listConnections(sg, type='blinn'))
                for shader in shader_list:
                    transparency = pm.getAttr(shader + '.transparency')
                    if max(transparency) > 0.3:
                        mesh_list = sg.members()
                        for mesh in mesh_list:
                            if 'glass' not in mesh.name() and 'eyeball' not in mesh.name() and 'water' not in mesh.name() and 'efx' not in mesh.name():
                                if '.f' in str(mesh):
                                    transparency_mesh_list.append(mesh)
                                else:
                                    transparency_mesh_list.append(mesh.getTransform())

            t_mesh=list(set(transparency_mesh_list))
            if len(t_mesh) > 0:
                pm.select(t_mesh)
                return u"下列 mesh 的材质是透明,当模型是玻璃时命名需要加上glass或water,不是可以忽略检查。:\n" + u' '.join([t.name() for t in t_mesh])

            need_transparency_mesh_list = []
            for mesh in pm.listRelatives('|master|poly', ad=1, type='mesh'):
                if 'glass' in mesh.name() or 'water' in mesh.name() and 'efx' not in mesh.name():
                    ses = pm.listConnections(mesh.name(), d=True, s=False, type='shadingEngine')
                    for se in ses:
                        shader = se.surfaceShader.listConnections(d=True, s=True)[0]
                        if shader.hasAttr('transparency') and max(shader.getAttr('transparency')) < 0.5:
                            print mesh
                            need_transparency_mesh_list.append(mesh.getTransform())

                if 'efx' in mesh.name():
                    ses_efx = pm.listConnections(mesh.name(), d=True, s=False, type='shadingEngine')
                    for se_w in ses_efx:
                        shader_w = se_w.surfaceShader.listConnections(d=True, s=True)[0]
                        if shader_w.hasAttr('transparency') and max(shader_w.getAttr('transparency')) < 0.3:
                            print mesh
                            need_transparency_mesh_list.append(mesh.getTransform())

            t_mesh = list(set(need_transparency_mesh_list))

            if len(t_mesh) > 0:
                pm.select(t_mesh)
                return u"命名包含_glass _water ,材质需要是透明的 ( 至少大于 0.5 ):\n"+u"命名包含_efx ,材质需要是透明的 ( 至少大于 0.3 ):\n" + u"请检测以下文件: \n" + u' '.join([t.name() for t in t_mesh])


            return ""

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        try:
            return
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


