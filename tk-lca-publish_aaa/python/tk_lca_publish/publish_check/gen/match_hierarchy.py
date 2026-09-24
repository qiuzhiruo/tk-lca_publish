# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: 
#
############################################

import traceback
import os
import sys
import re
from xml.etree import ElementTree
import pymel.core as pm
from proc.mod_diff import Mod_Diff

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"对比模型版本层级拓扑。"
        self.description = u"和模型版本进行比较，如果层级结构或者拓扑不同提出警示。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def get_trans(self, root):
        l_nodes = pm.listRelatives(root, type='transform')
        for node in l_nodes:
            if node.type() == 'transform':
                self.l_new_trans.append(node.fullPath())
                self.l_new_trans_name.append(node.fullPath().split('|')[-1])
                self.get_trans(node)
        return


    def run_check(self):
        self.dialog.md_msg = ''
        try:
            step = self.dialog.step['name']
            if step == 'mod':
                desp = u"和上一版 Downstream 模型相比:"
                mesh_xml = self.dialog.publish_root + '/' + self.dialog.version_key + '/mesh.xml'
                if not os.path.isfile(mesh_xml):
                    return ""
            else:
                desp = u"和模型相比:"
                l_attrs = pm.listAttr('|master')
                if not ('modVersion' in l_attrs and 'modPath' in l_attrs):
                    return u"没有找到 Mod Version 和 Mod Path 属性，无法对比模型层级。"

                mod_version = pm.getAttr('|master.modVersion')
                mod_path = pm.getAttr('|master.modPath').replace('\\', '/')

                if mod_version == '000':
                    return ""

                if self.dialog.task['name'] == 'layout_rigging':
                    return ""

                tokens = mod_path.split('/')
                if tokens[-1] != self.dialog.entity['name'] + '.ma':
                    return u"使用的模型文件不是 " + self.dialog.entity['name'] + '.ma'

                mesh_xml = os.path.dirname(mod_path) + '/mesh.xml'
                if sys.platform.startswith('linux'):
                    mesh_xml = mesh_xml.replace('Z:/', '/mnt/proj/')
                if mod_path.startswith('Z:/'):
                    last_proj = mod_path.split('/')[2]
                    asset_name = mod_path.split('/')[5]
                else:
                    last_proj = mod_path.split('/')[2]
                    asset_name = mod_path.split('/')[5]
                if last_proj != self.dialog.project['name'].lower():
                    desp = '复用{}：{}，{}'.format(last_proj,asset_name,desp)
                if not os.path.isfile(mesh_xml):
                    return u"没有找到模型对应的 xml 文件: " + mesh_xml

            md = Mod_Diff()
            if step == 'cfx':
                md.parse_xml(mesh_xml, ignore_deform=True)
            else:
                md.parse_xml(mesh_xml)

            # write model diff description
            err_missing = u''
            err_new = u''
            err_moved = u''
            err_topology_changed = u''

            if len(md.l_missing) !=0:
                err_missing += u'\n有 ' + str(len(md.l_missing)) + u" 个mesh被删除了: "
                self.dialog.md_msg += err_missing+u' '.join(md.l_missing)
                
                if len(md.l_missing) > 5:
                    err_missing += u' '.join(md.l_missing[:5]) + u" ..."
                else:
                    err_missing += u' '.join(md.l_missing)

            if len(md.l_new) !=0:
                err_new += u'\n有 ' + str(len(md.l_new)) + u" 个mesh被创建了: "
                self.dialog.md_msg += err_new + u' '.join(md.l_new)
                if len(md.l_new) > 5:
                    err_new += u' '.join(md.l_new[:5]) + u" ..."
                else:
                    err_new += u' '.join(md.l_new)

            if len(md.l_moved) !=0:
                err_moved += u'\n有 ' + str(len(md.l_moved)) + u" 个mesh被改变了层级: "
                self.dialog.md_msg += err_moved + u' '.join(md.l_moved)
                if len(md.l_moved) > 5:
                    err_moved += u' '.join(md.l_moved[:5]) + u" ..."
                else:
                    err_moved += u' '.join(md.l_moved)

            if len(md.l_topology_changed) !=0:
                
                err_topology_changed += u'\n有 ' + str(len(md.l_topology_changed)) + u" 个mesh被改变了拓扑: "
                self.dialog.md_msg += err_topology_changed + u' '.join(md.l_topology_changed)
                if len(md.l_topology_changed) > 5:
                    err_topology_changed += u' '.join(md.l_topology_changed[:5]) + u" ..."
                else:
                    err_topology_changed += u' '.join(md.l_topology_changed)

            # Fill the description field for mod publish
            if step == 'mod':
                if err_missing == u'' and err_new == u'' and err_moved == u'' and err_topology_changed == u'':
                    self.dialog.w_publish.plainTextEdit_auto_description.setPlainText(desp + u" 本版本无层级拓扑变化。")
                    self.dialog.md_msg += desp + u" 本版本无层级拓扑变化。"
                else:
                    desp += err_missing + err_new + err_moved + err_topology_changed
                    desp = desp.replace('Shape', '')
                    self.dialog.w_publish.plainTextEdit_auto_description.setPlainText(desp)

            # The order of errors: missing > new > moved > topology changed
            else:
                if len(md.l_missing) > 0:
                    return desp + err_missing

                if len(md.l_new) > 0:
                    return desp + err_new

                if len(md.l_moved) > 0:
                    return desp + err_moved

                if len(md.l_topology_changed) > 0:
                    return desp + err_topology_changed

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


