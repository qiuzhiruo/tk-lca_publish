# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Create version dir on the server
#
############################################

import os
import traceback
import pymel.core as pm

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"将输出的子资产 reference 进入当前文件。"
        self.description = u"将输出的子资产 reference 进入当前文件。"
        return


    def proceed(self):
        try:
            pm.loadPlugin('sceneAssembly', quiet=True)
            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']
                tank_file = self.dialog.d_assets_info[asset_name]['tank_file']
                #translation = self.dialog.d_assets_info[asset_name]['translation']
                #rotation = self.dialog.d_assets_info[asset_name]['rotation']
                parent = self.dialog.d_assets_info[asset_name]['parent']
                assembly_file = self.dialog.d_assets_info[asset_name]['assembly_file']

                translation = root.getTranslation()
                rotation = root.getRotation()
                scale = root.getScale()

                pm.delete(root)
                ar = pm.createNode("assemblyReference")
                hl = pm.createNode("hyperLayout", n= "hyperLayout_" + asset_name)
                pm.connectAttr(hl.name()+".msg", ar.name()+".hl")
                ar.setAttr("definition", assembly_file)
                pm.mel.eval('AEassemblyChangeAttrNamespace "'+ar.name()+'.repNamespace" "'+asset_name+'";')

                ar.rename(asset_name + '_AR')

                # pm.setAttr(ar.name()+'.translateX', translation[0])
                # pm.setAttr(ar.name()+'.translateY', translation[1])
                # pm.setAttr(ar.name()+'.translateZ', translation[2])
                # pm.setAttr(ar.name()+'.rotateX', rotation[0])
                # pm.setAttr(ar.name()+'.rotateY', rotation[1])
                # pm.setAttr(ar.name()+'.rotateZ', rotation[2])
                # pm.setAttr(ar.name()+'.scaleX', scale[0])
                # pm.setAttr(ar.name()+'.scaleY', scale[1])
                # pm.setAttr(ar.name()+'.scaleZ', scale[2])

                pm.parent(ar, parent)

                '''ref = pm.createReference( tank_file, namespace = asset_name )
                l_nodes = ref.nodes()

                n_master = n_global_ctrl = None
                for node in l_nodes:
                    if node.name().endswith(':master'):
                        n_master = node
                    if node.name().endswith(':global_ctrl'):
                        n_global_ctrl = node

                if n_master and n_global_ctrl:
                    #pm.xform(n_global_ctrl, r=True, translation=(translation[0],  translation[1], translation[2]))
                    n_global_ctrl.setTranslation(tralslation)
                    n_global_ctrl.setRotation(rotation)
                    if parent:
                        pm.parent(n_master, parent)'''

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

