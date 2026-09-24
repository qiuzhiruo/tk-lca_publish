# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2016.04
#
# Description: 
#
############################################

import traceback
import hashlib
import os
import re
import subprocess

from proc.mod_diff import Mod_Diff

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"根据abc输出mesh.xml，并和publish的mod任务最新版对比"
        self.description = u"根据abc输出mesh.xml，并和publish的mod任务最新版对比层级，拓扑"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):

        try:
            if self.dialog.os == 'win':
                MAYAPY = '"C:/Program Files/Autodesk/Maya2015/bin/mayapy.exe"'
            else:
                MAYAPY = '{}/lca_launchers/maya/mayapy2015'.format(os.getenv('LC_UTILITY'))

            tokens = os.path.dirname(__file__).replace('\\', '/').split('/')
            mesh_xml_py = '/'.join(tokens[:-2]) + '/proc/mesh_xml_cmd.py'
            self.dialog.dynamic_mesh_xml = os.path.dirname(self.dialog.dynamic_file) + '/mesh.xml'
            self.dialog.dynamic_scene_xml = os.path.dirname(self.dialog.dynamic_file) + '/' + self.dialog.entity['name'] +'.xml'
            if os.path.isfile(self.dialog.dynamic_mesh_xml):
                os.remove(self.dialog.dynamic_mesh_xml)

            if os.path.isfile(self.dialog.dynamic_scene_xml):
                os.remove(self.dialog.dynamic_scene_xml)

            cmd = MAYAPY + ' ' + mesh_xml_py + ' -a ' + self.dialog.dynamic_file + ' -m ' + self.dialog.dynamic_mesh_xml + ' -s ' + self.dialog.model_scene_xml + ' ' + self.dialog.dynamic_scene_xml
            #p = subprocess.Popen(cmd, shell = self.dialog.process_shell )
            os.system(cmd)

            if not os.path.isfile(self.dialog.dynamic_mesh_xml):
                self.dialog.print_log(cmd)
                return u"通过 ABC 文件生成 mesh.xml 失败。"

            if not os.path.isfile(self.dialog.dynamic_scene_xml):
                self.dialog.print_log(cmd)
                return u"通过 ABC 文件生成 scene graph xml 失败。"

            # compare mesh.xml
            md = Mod_Diff()
            md.diff_xml(self.dialog.model_mesh_xml, self.dialog.dynamic_mesh_xml)
            err_str = ''
            if len(md.l_missing) > 0:
                err_str += u'有 ' + str(len(md.l_missing)) + u" 个mesh被删除了:\n    "  + '\n    '.join(md.l_missing) + '\n'

            if len(md.l_new) > 0:
                err_str += u'有 ' + str(len(md.l_new)) + u" 个mesh被创建了:\n    "  + '\n    '.join(md.l_new) + '\n'

            if len(md.l_moved) > 0:
                err_str += u'有 ' + str(len(md.l_moved)) + u" 个mesh改变了层级:\n    "  + '\n    '.join(md.l_moved) + '\n'

            if err_str != '':
                err_str = u'和mesh文件: ' + self.dialog.model_mesh_xml + u' 对比，动态abc的模型有变化:\n' + err_str

            return err_str

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


        if len(md.l_missing) > 0:
            QtGui.QMessageBox.critical(self, "Failed!", u'有 ' + str(len(md.l_missing)) + u" 个mesh被删除了:\n    "  + '\n    '.join(md.l_missing))
            return

        if len(md.l_new) > 0:
            QtGui.QMessageBox.critical(self, "Failed!", u'有 ' + str(len(md.l_new)) + u" 个mesh被创建了:\n    "  + '\n    '.join(md.l_new))
            return

        if len(md.l_moved) > 0:
            QtGui.QMessageBox.critical(self, "Failed!", u'有 ' + str(len(md.l_moved)) + u" 个mesh改变了层级:\n    "  + '\n    '.join(md.l_moved))
            return

        if len(md.l_topology_changed) > 0:
            QtGui.QMessageBox.critical(self, "Failed!", u'有 ' + str(len(md.l_topology_changed)) + u" 个mesh改变了拓扑:\n    "  + '\n    '.join(md.l_topology_changed))
            return

