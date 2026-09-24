# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Yu Huazhuo
#
# Date: 2019.04
#

########################################################################################
import sys
import os
import traceback
import pymel.core as pm
from xml.etree import ElementTree
from proc.function_running_time import record_time

class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查发光物体命名是否含(light)。"
        self.description = u"如果模型的材质是发光的,则命名需要加上light,mesh的命名包含light,或组包含light的物体,材质球的incandescence必须大于0.1"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    @record_time(__file__)
    def run_check(self):
        try:
            light_mesh_list=[]

            for sg in pm.ls(type='shadingEngine'):
                shader_list = []
                shader_list.extend(pm.listConnections(sg, type='lambert'))
                shader_list.extend(pm.listConnections(sg, type='blinn'))
                shader_list.extend(pm.listConnections(sg, type='phong'))
                shader_list.extend(pm.listConnections(sg, type='phongE'))
                for shader in shader_list:
                    light = pm.getAttr(shader + '.incandescence')
                    if max(light) > 0.1:
                        mesh_list = sg.members()
                        for mesh in mesh_list:
                            if 'light' not in mesh.name() and pm.objExists(mesh):
                                light_mesh_list.append(mesh)

            t_mesh=list(set(light_mesh_list))
            if len(t_mesh) > 0:
                pm.select(t_mesh)
                return u"下列 mesh 的材质是发光的,命名需要加上light。:\n" + u' '.join([t.name() for t in t_mesh])

            for mesh in pm.listRelatives('|master|poly', ad=1, type='mesh'):
                if 'light' not in mesh.name():
                    continue
                    
                ses = pm.listConnections(mesh.name(), d=True, s=False, type='shadingEngine')
                for se in ses:
                    shader = se.surfaceShader.listConnections(d=True, s=True)[0]
                    if shader.hasAttr('incandescence') and max(shader.getAttr('incandescence')) < 0.1:
                        print mesh
                        light_mesh_list.append(mesh)

            t_mesh = list(set(light_mesh_list))
            
            if len(t_mesh) > 0:
                pm.select(t_mesh)
                return u"下列 mesh 的命名包含light ,材质需要是发光的,。:\n" + u' '.join([t.name() for t in t_mesh])

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


