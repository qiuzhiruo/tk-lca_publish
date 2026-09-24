# -*- coding:utf-8 -*-

__author__ = 'xiangquan'

import traceback

import os
import re
import sys
import shutil

import pymel.core as pm
import maya.cmds as cmds

import production.translate_os_path as tra_path
reload(tra_path)


class StdCheck():
    """
    """
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是否有非work/publish盘的reference资源"
        self.description = u"检查是否有非work/publish盘的reference资源"
        self.auto_fix = True
        self.duty = u"自动修复"
        self.illegal_refs = {}
        self.illegal_abc = {}
        return

    def run_check(self):
        self.illegal_refs = {}
        self.illegal_abc = {}
        try:
            ref_nodes = pm.listReferences()
            loaded_refs = []
            for ref_node in ref_nodes:
                try:
                    if ref_node.isLoaded():
                        loaded_refs.append(ref_node)
                except:
                    pass
            
            proj_path_prefix = os.path.join(os.environ['LC_PROJ'] + '/', 'projects', self.dialog.project['name'].lower()).replace('\\', '/')
            work_path_prefix = os.path.join(os.environ['LC_WORK'] + '/', 'projects', self.dialog.project['name'].lower()).replace('\\', '/')
            cam_rig_path = os.path.join(os.environ['LC_WORK'] + '/', 'projects', 'lib/publish/asset/camera').replace('\\', '/')
            work_lay_proj_path = os.path.join(os.environ['LC_WORK'] + '/', 'layProjects').replace('\\', '/')
            print 'proj_path_prefix', proj_path_prefix
            print 'work_path_prefix', work_path_prefix
            print 'cam_rig_path', cam_rig_path
            print 'work_lay_proj_path', work_lay_proj_path
            for loaded_ref in loaded_refs:
                file_path = str(loaded_ref.path).replace('\\', '/')
                if proj_path_prefix not in file_path and \
                   work_path_prefix not in file_path and \
                   cam_rig_path not in file_path:
                    self.illegal_refs[loaded_ref.namespace] = loaded_ref

            for i in cmds.ls(type='AlembicNode'):
                if cmds.referenceQuery(i, inr=True):
                    continue
                path = cmds.getAttr('{}.abc_File'.format(i))
                if not path:
                    continue
                path = tra_path.osPathConvert(path)
                if not path.startswith(proj_path_prefix) and not path.startswith(work_path_prefix) and not path.startswith(work_lay_proj_path):
                    self.illegal_abc[i] = path
            
            msg = ''
            if self.illegal_refs:
                msg += u'以下reference的引用路径不合法，可能导致下游读取不到正确文件：\n'
                
                msg += '\n'.join(sorted(self.illegal_refs.keys()))
                msg += u'\n选择"自动修复"可将这些资产改为import.\n'

            if self.illegal_abc:
                msg += u'以下abc节点的引用路径不合法，可能导致下游读取不到正确文件：\n'
                msg += '\n'.join(sorted(self.illegal_abc.keys()))
                msg += u'\n选择"自动修复"可将这些abc修复到work盘路径.\n'
            print self.illegal_refs
            print self.illegal_abc
            return msg

        except:
            return traceback.format_exc()


    def run_fix(self):
        '''Auto Fix'''
        # fix bad ref path
        for ref_node_ns in self.illegal_refs:
            self.illegal_refs[ref_node_ns].importContents()

        # fix bad abc path
        work_root = os.path.join(os.path.join(os.environ['LC_WORK'], 'projects', self.dialog.project['name'].lower(),
                                              'preproduction', self.dialog.entity['name'], 'story/lay/task/maya/cache')).replace('\\', '/')
        copied_abc = []
        for k, v in self.illegal_abc.iteritems():
            attr = '{}.abc_File'.format(k)
            cmds.lockNode(k, lock=False)
            cmds.setAttr(attr, lock=False)
            v = tra_path.osPathConvert(v)

            if not os.path.isfile(v):
                cmds.setAttr(attr, '', type='string')
                print 'clean not exist abc: {} : {}'.format(k, v)
                continue
            to_file = os.path.join(work_root, os.path.basename(v))
            if v not in copied_abc:
                shutil.copyfile(v, to_file)
                copied_abc.append(v)
                print 'copy abc: {} --> {}'.format(v, to_file)
            cmds.setAttr('{}.abc_File'.format(k), to_file, type='string')
            print 'set node:', k, to_file

        self.illegal_refs = {}
        self.illegal_abc = {}
        
        return ''

    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


