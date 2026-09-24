# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.10
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


# All system check classes will use StdCheck as the class name.
class StdCheck():
    
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"植被资产提前检测mesh/curve节点的名称。"
        self.description = u"清除历史记录。\n一个transform下最多只能有一个 mesh/nurbsCurve节点。如果有intermediate object就删除掉。\n在|master|poly组下的mesh节点命名符合如下规范:节点名=transform名+Shape;\n所有节点名都不能带命名空间。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return
    
    def run_check(self):
        try:
            asset = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]],
                                            ['sg_asset_type'])
            if not asset:
                #print 'not find sg asset',self.dialog.entity['id']
                return ""
            
            if asset['sg_asset_type'] != 'flg':
                #print 'continue not flg asset',asset['sg_asset_type']
                return ""
            
            root = '|master'
            if not pm.objExists('|master'):
                return u'没有找到 |master'
            
            error_info = ''
            # Freeze transoform - 坐标清零
            node_poly = pm.PyNode('|master|poly')
            pm.select(node_poly, r=True)
            #pm.mel.eval('DeleteHistory;')
            pm.select(cl=True)
            
            # Clean intermediate objects
            l_meshes = pm.listRelatives(root, ad=True, type='mesh', fullPath=True)
            for mesh_node in l_meshes:
                if pm.getAttr(mesh_node.name() + '.intermediateObject'):
                    pm.delete(mesh_node)
                    l_meshes.remove(mesh_node)
            
            # No sibling mesh nodes TODO
            l_render_nodes = pm.listRelatives(root, ad=True, type='mesh', fullPath=True)
            l_render_nodes.extend(pm.listRelatives(root, ad=True, type='nurbsCurve', fullPath=True))
            
            maya_poly_name = [u'polyshape', u'pplane', u'pcylinder', u'pcone', u'pcube', u'ptorus', u'psphere',
                              u'pcircle', u'phelix', u'ppyramid', u'pprism', u'polySurface']
            error_name_list = []
            
            for render_node in l_render_nodes:
                trans_node = pm.listRelatives(render_node, parent=True, fullPath=True)[0]
                l_children = pm.listRelatives(trans_node, fullPath=True, type='mesh')
                l_children.extend(pm.listRelatives(trans_node, fullPath=True, type='nurbsCurve'))
                if len(l_children) > 1:
                    error_info+= u'Transform节点 ' + trans_node.name() + u' 之下有多个mesh/curve节点。需要模型师手动找到并删除。（无法使用自动修复）\n'
                
                transName = trans_node.fullPath().split('|')[-1]
                if render_node.fullPath() != trans_node.fullPath() + '|' + transName + 'Shape':
                    error_info+= u'命名错误: ' + render_node.name() + u' 符合规范的命名应该是: ' + trans_node.fullPath() + '|' + transName + 'Shape \n'
                
                for m_name in maya_poly_name:
                    if m_name in render_node.name():
                        error_name_list.append(render_node.name())
                
                # No namespace
                l_ns_nodes = []
                l_nodes = pm.listRelatives(root, ad=True, path=True)
                for node in l_nodes:
                    node_name = node.split('|')[-1]
                    if ':' in node_name:
                        l_ns_nodes.append(node.name())
                
                if len(l_ns_nodes) > 0:
                    error_info+= u"模型节点名中不能有命名空间: " + ' '.join(l_ns_nodes) +'\n'
                
                if len(error_name_list) > 0:
                    error_info+= u"模型节点名中不能有maya默认名字: " + ' '.join(error_name_list) + u" （无法使用自动修复）\n"
            
            if error_info:
                return error_info
            
            return ""
        
        except:
            return traceback.format_exc()
    
    def run_fix(self):
        '''Auto Fix'''
        try:
            root = '|master'

            if not pm.objExists(root):
                return u'没有找到 ' + root.name()
            
            l_render_nodes = pm.listRelatives(root, ad=True, type='mesh', fullPath=True)
            l_render_nodes.extend(pm.listRelatives(root, ad=True, type='nurbsCurve', fullPath=True))
            
            for render_node in l_render_nodes:
                trans_node = pm.listRelatives(render_node, parent=True, fullPath=True)[0]
                transName = trans_node.split('|')[-1]
                if render_node != trans_node + '|' + transName + 'Shape':
                    print 'Rename:', render_node, '>', transName + 'Shape'
                    pm.rename(render_node, transName + 'Shape')
            
            l_nodes = pm.listRelatives(root, ad=True, path=True)
            for node in l_nodes:
                node_name = node.split('|')[-1]
                if ':' in node_name:
                    node.rename(node_name.split(':')[-1])
            
            return ''
        
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


