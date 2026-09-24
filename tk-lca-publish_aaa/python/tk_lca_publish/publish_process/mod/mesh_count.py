# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2014 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.08
#
# Description: 
#
############################################

import os
import traceback
from xml.dom.minidom import Document
import pymel.core as pm
import maya.cmds as cmds
import re
from proc.function_running_time import record_time

# All publish process will use StdProcess as the class name.
class StdProcess():
    
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"记录模型高/低模面数和模型高度。"
        self.description = u"将模型的高/低模面数和高度记录到 shotgun 资产信息。"
        return
    
    def get_mesh_count(self, root_node):
        if not pm.objExists(root_node):
            return 0
        
        l_meshes = pm.listRelatives(root_node, ad=True, type='mesh')
        if len(l_meshes) == 0:
            return 0
        
        pm.select(l_meshes, r=True)
        cnt = pm.polyEvaluate(f=True)
        pm.select(cl=True)
        return cnt
    
    def get_mesh_height(self, root_node):
        if not pm.objExists(root_node):
            return 0
        mesh_poly_list = pm.listRelatives(root_node, ad=True, type='mesh')
        
        if len(mesh_poly_list) == 0:
            return 0
        
        mesh_boundingbox = pm.exactWorldBoundingBox(mesh_poly_list)
        mesh_height = mesh_boundingbox[4] - mesh_boundingbox[1]
        
        return float(mesh_height)



    @record_time(__file__)
    def proceed(self):
        try:
            for asset_name in self.dialog.d_assets_info.keys():
                root = self.dialog.d_assets_info[asset_name]['node']
                node_name = self.dialog.d_assets_info[asset_name]['node_name']

                if not (len(self.dialog.d_assets_info.keys()) == 1 and node_name == 'master'):
                    asset_id = self.dialog.sg.find_one('Asset',
                                                       [['project','name_is',self.dialog.project.get('name').lower()],['code','is',asset_name]],
                                                       ['id'])['id']
                else:
                    asset_id = self.dialog.entity['id']
                # make a master if necessary
                if self.dialog.d_assets_info[asset_name]['parent']:
                    pm.parent(root, world=True)
                
                root.rename('master')
                
                hi_cnt = self.get_mesh_count('|master|poly|hi')
                lo_cnt = self.get_mesh_count('|master|poly|lo')
                
                hi_height = self.get_mesh_height('|master')
                
                if lo_cnt == 0:
                    self.dialog.sg.update('Asset', asset_id,
                                          {'sg_poly_count_hi': hi_cnt, 'sg_ctrl_poly': hi_height})
                else:
                    self.dialog.sg.update('Asset', asset_id,
                                          {'sg_poly_count_hi': hi_cnt, 'sg_poly_count_lo': lo_cnt,
                                           'sg_ctrl_poly': hi_height})
                
                # recovery root node
                if self.dialog.d_assets_info[asset_name]['parent']:
                    pm.parent(root, self.dialog.d_assets_info[asset_name]['parent'])
                
                root.rename(node_name)
            
                if len(self.dialog.d_assets_info.keys()) == 1 and node_name == 'master':
                    txt = self.dialog.w_publish.plainTextEdit_auto_description.toPlainText()
                    if self.dialog.version_tag == u"粗模":
                        txt += u'\n粗模面数：' + str(hi_cnt)
                    else:
                        txt += u'\n高模面数：' + str(hi_cnt)
                    self.dialog.w_publish.plainTextEdit_auto_description.setPlainText(txt)
                asset_type = self.dialog.d_assets_info[asset_name]['type']
                if asset_type.lower() in ['chr']:
                    return ''
                reuse_info = ''
                if root.hasAttr('reuse_info'):
                    MayasenceName = root.getAttr('reuse_info').replace('\\', '/')
                    ProjectStr = r"/projects/lib/publish/asset/(\w+)/(\w{3}).(\w+)/"
                    ProjectStrC = re.compile(ProjectStr)
                    results = ProjectStrC.findall(MayasenceName.replace("\\", "/"))
                    if results:
                        reuse_info = results[0][1] + '.' + results[0][2]

                if reuse_info == '' and root.hasAttr('modPath'):
                    MayasenceName = root.getAttr('modPath').replace('\\', '/')
                    ProjectStr = r"/projects/(\w{3})/asset/(\w+)/(\w+)/(\w{3})/"
                    ProjectStrC = re.compile(ProjectStr)
                    results = ProjectStrC.findall(MayasenceName.replace("\\", "/"))
                    if results:
                        reuse_info = results[0][0] + '.' + results[0][2]

                if reuse_info:
                    if reuse_info.split('.')[0] != self.dialog.project.get('name').lower():

                        if not self.dialog.d_assets_info[asset_name].has_key('description'):
                            if len(self.dialog.d_assets_info.keys()) == 1 and node_name == 'master':
                                return ""
                            else:
                                self.dialog.d_assets_info[asset_name]['description'] = ''

                        if self.dialog.d_assets_info[asset_name]['description']:
                            description = self.dialog.d_assets_info[asset_name]['description'].decode('utf-8')
                        else:
                            description = ''
                        if reuse_info not in description:
                            description += u'  复用:' + reuse_info
                            self.dialog.sg.update('Asset', asset_id,
                                                  {'description': description})
                    else:
                        print self.dialog.project.get('name').lower() + '.' + asset_name,reuse_info

            return ""
        
        except:
            return traceback.format_exc()
    
    def get_process_name(self):
        return self.process_name
    
    def get_description(self):
        return self.description
