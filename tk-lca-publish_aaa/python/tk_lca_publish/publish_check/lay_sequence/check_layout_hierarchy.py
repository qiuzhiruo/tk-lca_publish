# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.06
#
# Description: Check layout hierarchy
#
############################################
import traceback
import os
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查是否存在assets|lay组及该组下的子层级'
        self.description = u'详见 <a href="http://shotgun.zhuiguang.com/detail/Ticket/2412">Ticket</a>'
        self.auto_fix = False
        self.duty = u'艺术家本人。'
        return

    def run_check(self):
        try:
            top_level_nodes = pm.ls(assemblies=True)
            invalid_nodes = []
            for node in top_level_nodes:
                if node.name() not in ('assets', 'cameras', 'persp', 'top', 'front', 'side'):
                    invalid_nodes.append(node)

            if invalid_nodes:
                pm.select(invalid_nodes)
                node_names = [node.name() for node in invalid_nodes]
                return u'以下节点在大纲中的层级不正确：\n%s'%'\n'.join(node_names)

            layout_null = '|assets|lay'
            temp_assets_null = layout_null + '|temp_assets'
            vfx_null = layout_null + '|VFX'
            light_null = vfx_null + '|light'
            efx_null = vfx_null + '|EFX'
            for null in [layout_null, temp_assets_null, vfx_null, light_null, efx_null]:
                if not pm.objExists(null):
                    return u'%s不存在。'%null

            null = pm.nt.Transform(temp_assets_null)
            if self.dialog.publish_mode == 1 and null.getChildren():
                pm.select(null)
                return u'%s组不是空的。'%temp_assets_null

            lights = pm.ls(type='light')
            for light in lights:
                if not light.isChildOf(light_null):
                    light = light.getParent()
                    pm.select(light)
                    return u'%s没有放到%s组内。'%(light, light_null)

            return ""
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

