# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.05
#
# Description: 
#
############################################
import os
import traceback
import shutil
import pymel.core as pm
from sgtk.platform.qt import QtGui
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import sys
import pprint
import time
from xml.etree import ElementTree
import maya.cmds as mc
from pymel.core import *
TXT_DEFAULT = QtGui.QColor(200, 200, 200)
TXT_ORANGE = QtGui.QColor(255, 150, 30)
TXT_RED = QtGui.QColor(255, 50, 50)
TXT_BLUE = QtGui.QColor(150, 150, 255)
TXT_WHITE = QtGui.QColor(255, 255, 255)
#root_path = os.path.dirname(assetsystem_sgl.__file__)
root_path ='D:\\program\\git\\lca_rig\\assetsystem_sgl'
rig_mod_Path = root_path + "\\tools\\mod\\rig_mod"
if rig_mod_Path not in sys.path:
    sys.path.insert(0, rig_mod_Path)
from assetsystem_sgl.utils.maya import handler
# @handler.undo_info
# import shotgun_rig_mod as sm
# reload(sm)


# All publish process will use StdProcess as the class name.
class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拆分asm资产"
        self.description = u"拆分asm资产"
        return


    @handler.undo_info
    def delete_chr(self,c_asset_names,c_asset_name):
        """
        c_asset_names = ['set1','set2','set3']
        c_asset_name = 'set1'

        """
        try:
            c_asset_names = [a+"_cloth" for a in c_asset_names]
            c_asset_name += "_cloth"
            old_list = mc.sets(c_asset_name, q=1)
            del_list =[]
            for a in c_asset_names:
                if c_asset_name != a:
                   other_list = mc.sets(a, q=1)
                   # print other_list
                   for b in other_list:
                       if b not in old_list:
                            del_list.append(b)
            mc.delete(list(set(del_list)))

        except:
            pass

    def proceed(self):
        ast_info = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_asset_type'])
        # #if ast_info['sg_asset_type'] == 'chr':
        # asset = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_asset_type', 'sg_manual_lod'] )
        # print "asset: \n", asset
        # print "sg_asset_type: \n", ast_info['sg_asset_type'], '\n'
        # print "dialog.d_assets_info: \n", self.dialog.d_assets_info
        # print "dialog.entity: \n", self.dialog.entity

        if ast_info['sg_asset_type'] == 'asm':
            asset_info = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['assets'])
            c_asset_names = [sub_asset['name'] for sub_asset in asset_info['assets']]
            print "c_asset_names", c_asset_names
            if not c_asset_names:
                return ""
            get_char_name = mc.addAttr("visibility_ctrl.char_name", q=1, enumName=1).split(":")


            # check = ",".join([str(a) for a in c_asset_names if a not in get_char_name])
            # if check != "":
            #     return u"visibility_ctrl.char_name 和任务子资产不匹配"

            # for a in c_asset_names:
            #     if not mc.objExists(a):
            #         return u"任务子资产不匹配"

            self.dialog.c_master_tank_file = self.dialog.tank_file
            # groups = mc.listRelatives("|master|poly", c=1, ni=1)
            # remove_list = ['proxy', 'hi', 'share']
            # c_asset_names = [a for a in groups if a not in remove_list]
            for c_asset_name in get_char_name:
            # for c_asset_name in c_asset_names:
                if c_asset_name in c_asset_names:
                    self.dialog.current_chr_file = c_asset_name
                    c_project_name = self.dialog.project['name']
                    c_task_name = self.dialog.task['name']
                    c_project_name_lower = c_project_name.lower()
                    # init functions
                    # 1.get project info
                    c_proj_info = self.dialog.sg.find_one('Project', [['name', 'is', c_project_name]])
                    c_proj_info["name"] = c_project_name
                    # 2.get asset info
                    c_asset_entity = self.dialog.sg.find_one('Asset',
                                                             [['project', 'is', c_proj_info], ['code', 'is', c_asset_name]])
                    c_asset_entity["name"] = c_asset_name
                    # 3.get task id
                    c_task_info_rig = self.dialog.sg.find('Task',
                                                          [['entity', 'is', c_asset_entity],
                                                           ['content', 'is', c_task_name]],
                                                          ["step"])
                    # 4 get asset_type
                    c_asset_type = self.dialog.sg.find_one('Asset', [['id', 'is', c_asset_entity['id']]], ['sg_asset_type'])[
                        'sg_asset_type']
                    # init vars
                    c_task = {'type': 'Task', 'name': c_task_name, 'id': c_task_info_rig[0]["id"]}
                    c_versions = self.dialog.sg.find('Version', [['project', 'is', c_proj_info], ['sg_task', 'is', c_task]],
                                                     ['code', 'user', 'created_at', 'description'])
                    c_versions.reverse()
                    if c_versions:
                        c_MAX = int(max([a['code'][-3:] for a in c_versions])) + 1
                        c_version = '.v%03d' % c_MAX
                        c_version_name = '%s.rig.%s%s' % (c_asset_name, c_task_name, c_version)
                    else:
                        c_version_name = '%s.rig.%s.v001' % (c_asset_name, c_task_name)
                    c_file_path = r'Z:/projects/%s/asset/%s/%s/rig/publish/%s' % (c_project_name_lower,
                                                                                  c_asset_type, c_asset_name, c_version_name)

                    self.dialog.project = c_proj_info
                    self.dialog.entity = c_asset_entity
                    self.dialog.task = c_task
                    self.dialog.version_dir = c_file_path
                    self.dialog.version_name = c_version_name
                    self.dialog.publish_root = r'Z:/projects/%s/asset/%s/%s/rig/publish' % (c_project_name_lower,
                                                                                            c_asset_type, c_asset_name)
                    # print 'project:\n', c_proj_info['name'], '\n'
                    # print 'entity:\n', c_asset_entity['name'], '\n'
                    # print 'task:\n', c_task['name'], '\n'
                    # print 'version_dir:\n', c_file_path, '\n'
                    # print 'version_name:\n', c_version_name, '\n'
                    # print 'asset_type:\n', c_asset_type, '\n'
                    # print 'tank_file:\n', self.dialog.publish_root + '/' + self.dialog.version_name + '/' + self.dialog.entity['name'] + '.ma', '\n'
                    # print 'publish_root:\n', self.dialog.publish_root ,'\n'

                    asset = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]],
                                                    ['sg_asset_type', 'sg_manual_lod'])
                    self.dialog.d_assets_info = {}
                    self.dialog.d_assets_info = {self.dialog.entity['name']: {'node': pm.PyNode('|master'),
                                                                              'node_name': 'master',
                                                                              'parent': None,
                                                                              'asset': self.dialog.entity,
                                                                              'task': self.dialog.task,
                                                                              'type': asset['sg_asset_type'],
                                                                              'lod': asset['sg_manual_lod'],
                                                                              'publish_dir': self.dialog.publish_root,
                                                                              'version_name': self.dialog.version_name,
                                                                              'version_dir': self.dialog.publish_root + '/' + self.dialog.version_name,
                                                                              'tank_file': self.dialog.publish_root + '/' + self.dialog.version_name + '/' + self.dialog.entity['name'] + '.ma',
                                                                              'translation': (0.0, 0.0, 0.0),
                                                                              'rotation': (0.0, 0.0, 0.0),
                                                                              'v_info': None}}
                    self.dialog.tank_file = self.dialog.publish_root + '/' + self.dialog.version_name + '/' + self.dialog.entity['name'] + '.ma'
                    pm.openFile(self.dialog.c_master_tank_file, f=True)
                    self.dialog.d_assets_info[self.dialog.entity['name']]['node']=pm.PyNode('|master')
                    self.processes(c_asset_names, c_asset_name, get_char_name)
                    self.dialog.sg.update('Version',self.dialog.v_info['id'] , {'description': self.dialog.w_publish.plainTextEdit_auto_description.toPlainText() })

                    # mc.undo()
        return ""

    @handler.undo_info
    def processes(self, c_asset_names=None, c_asset_name=None, get_char_name=None):
        self.delete_chr(c_asset_names,c_asset_name)
        for a in c_asset_names:
            if c_asset_name != a:
                try:
                    mc.delete(a+"_other_ctrl_grp")
                except:
                    pass
                try:
                    mc.delete(list(set(mc.sets(a+"_delete", q=1))))
                except:
                    pass
                try:
                    mc.delete(a+"*")
                except:
                    pass
        char_index = get_char_name.index(c_asset_name)
        # print "c_asset_name: ", c_asset_name, "char_index: ", char_index
        mc.lockNode("visibility_ctrl", l=0)
        mc.setAttr("visibility_ctrl.char_name", lock=0)
        mc.setAttr("visibility_ctrl.char_name", char_index, lock=1)
        # mc.lockNode("visibility_ctrl", l=1)
        process_xml = os.path.dirname(self.dialog.publish_processes_xml) + '/publish_processes_asm.xml'
        c_publish_processes = build(process_xml, self.dialog)
        for i in range(len(c_publish_processes)):
            process = c_publish_processes[i]
            print "c_publish_processes:\n", process.module_name, '\n'
            if not process.run_process():
                self.dialog.print_log(u"Publish停止。", txt_color=TXT_RED)
                return

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description

class cProcess:
    def __init__(self, module_type, module_name, module_mode, id, dialog):

        self.module_type = module_type
        self.module_mode = module_mode
        self.module_name = module_name
        print module_type + '.' + module_name
        proc_module = my_import(module_type + '.' + module_name)
        reload(proc_module)
        self.process = proc_module.StdProcess(dialog)
        self.process_name = self.process.get_process_name()
        self.description = self.process.get_description()
        self.id = id
        self.dialog = dialog
        return

    def run_process(self):
        t = time.time()
        result = self.process.proceed()
        print 'Process Time Cost:', self.module_type + '.' + self.module_name, ("%.2f sec" % (time.time() - t))
        if result == '':
            self.dialog.print_log(self.module_name + u' 完成\n')
            return True
        else:
            if isinstance(result, str):
                result = result.decode('utf-8')
            self.dialog.print_log(self.module_name + u' 失败:\n' + result, txt_color=QtGui.QColor(255, 50, 50))
            self.dialog.print_log(u"解决问题请找 TD\n", txt_color=QtGui.QColor(255, 160, 50))
            return False
        return


def my_import(name):
    m = __import__(name)
    for n in name.split(".")[1:]:
        m = getattr(m, n)
    return m


def build(process_xml, dialog):
    l_publish_process = []
    f = open(process_xml, 'r')
    xml_text = f.read()
    f.close()
    root = ElementTree.fromstring(xml_text)
    l_processes = root.getiterator("process")

    for i in range(len(l_processes)):
        process = l_processes[i]
        module_type = process.attrib['type']
        module_name = process.attrib['name']
        module_mode = process.attrib['mode']
        proc = cProcess('publish_process.' + module_type, module_name, module_mode, i, dialog)
        l_publish_process.append(proc)
    return l_publish_process
