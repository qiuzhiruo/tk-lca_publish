# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: chen gang
#
# Date: 2017.10
#
# Description: 
#
############################################
import os
import traceback
import shutil
import pymel.core as pm
from sgtk.platform.qt import QtGui
import maya.cmds as mc
import maya.mel as mel
from xml.etree import ElementTree
import hashlib,re

from production.shotgun_connection import Connection
import production.pipeline.lcProdProj as clpp
from assetsystem_sgl.tools.common.publish.setmessage import setmessage


class Mod_Diff():

    def __init__(self):
        self.l_moved = []
        self.l_missing = []
        self.l_new = []
        self.l_topology_changed = []
        return


    def xml_to_dict(self, mesh_xml,root_node='|master|poly|hi|'):
        d_meshes = {}
        l_order = []
        tree = ElementTree.parse(mesh_xml)
        root = tree.getroot()
        l_meshes = root.getiterator("mesh")
        for mesh in l_meshes:
            full_path = mesh.attrib['name']
            if not root_node in full_path:
                continue
            mesh_name = full_path.split('|')[-1]
            topology = mesh.attrib['topology']
            d_meshes[mesh_name] = {'path': full_path, 'topology':topology}
            l_order.append(mesh_name)
        return d_meshes, l_order


    def parse_xml(self, mesh_xml, root_node='|master|poly|hi',filt=''):
        import pymel.core as pm
        import maya.api.OpenMaya as om
        d_old_meshes, l_old_order = self.xml_to_dict(mesh_xml,root_node=root_node)
        d_new_meshes = {}
        l_new_mesh = pm.listRelatives(root_node, ad=True, type='mesh', noIntermediate=True)
        for i, mesh in enumerate(l_new_mesh):
            mesh_name = mesh.name().split('|')[-1]
            d_new_meshes[mesh_name] = ''
            if not d_old_meshes.has_key(mesh_name):
                if filt:
                    skin_grp = [mesh.name().split('|')[-1]  for mesh in pm.listRelatives(filt, ad=True, type='mesh', noIntermediate=True) or []]
                    if mesh_name not in skin_grp:
                        self.l_new.append(mesh_name)
                else:
                    self.l_new.append(mesh_name)
            else:
                full_path = mesh.fullPath()

                if full_path != d_old_meshes[mesh_name]['path']:
                    self.l_moved.append(mesh_name)

                sl = om.MSelectionList()
                sl.add(full_path)
                mesh_dag = sl.getDagPath(0)
                mesh_mfn = om.MFnMesh(mesh_dag)
                v = mesh_mfn.getVertices()
                v_str0 = '[' + ', '.join([str(i) for i in v[0]]) + ']'
                v_str1 = '[' + ', '.join([str(i) for i in v[1]]) + ']'
                topology = hashlib.md5( v_str0 + ' ' + v_str1).hexdigest()
                if topology != d_old_meshes[mesh_name]['topology']:
                    self.l_topology_changed.append(mesh_name)

        for mesh_name in d_old_meshes.keys():
            if not d_new_meshes.has_key(mesh_name):
                self.l_missing.append(mesh_name)

        return


def diff_md(md):
    err_missing = u''
    err_new = u''
    err_moved = u''
    err_topology_changed = u''
    if len(md.l_missing) != 0:
        err_missing += u'\n有 ' + str(len(md.l_missing)) + u" 个mesh被删除了: "
        err_missing += u' '.join(md.l_missing)
    if len(md.l_new) != 0:
        err_new += u'\n有 ' + str(len(md.l_new)) + u" 个mesh被创建了: "
        err_new += u' '.join(md.l_new)

    if len(md.l_moved) != 0:
        err_moved += u'\n有 ' + str(len(md.l_moved)) + u" 个mesh被改变了层级: "
        err_moved += u' '.join(md.l_moved)

    if len(md.l_topology_changed) != 0:
        err_topology_changed += u'\n 有' + str(len(md.l_topology_changed)) + u" 个mesh被改变了拓扑: "
        err_topology_changed += u' '.join(md.l_topology_changed)
    desp = ''
    if err_missing == u'' and err_new == u'' and err_moved == u'' and err_topology_changed == u'':
        return desp
    else:
        desp += err_missing + err_new + err_moved + err_topology_changed
        desp = desp.replace('Shape', '')
        return desp




# All publish process will use StdProcess as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查模型拓扑"
        self.description = u"检查模型拓扑"
        self.auto_fix = False
        self.duty = u"艺术家本人 或 TD。"

        return

    def run_check(self):
        try:
            current_file_path = mc.file(sn=1, q=1)
            sg = Connection('get_project_info').get_sg()
            path = os.path.normpath(mc.getAttr("master.modPath"))
            c_project_name = re.findall('(?<=projects\\\\)\w+', path)[0]
            c_proj_info = sg.find_one('Project', [['name', 'is', c_project_name]])

            mod_version = pm.getAttr('|master.modVersion')
            mod_path = pm.getAttr('|master.modPath').replace('\\', '/')
            if mod_path.split('/')[-1][-3:] == ".ma" or mod_path.split('/')[-1][-3:] == ".mb":
                tokens = mod_path.split('/')[-1][:-3]
            else:
                pm.warning("file not ending with .ma or .mb")

            modvs = sg.find('Version', [['project','is',c_proj_info],['entity', 'name_is', str(tokens)],['sg_task.Task.content','is','model'],['sg_version_type','is','Downstream']],['code'])
            modVersion = modvs[-1]['code'][-3:]
            oldversion = re.findall('(?<=v)\d+', path)[0]
            newversion = path.replace(oldversion, str(modVersion))
            mesh_xml = os.path.dirname(newversion) + '\\mesh.xml'

            if not os.path.isfile(mesh_xml):
                listdir = mc.getAttr("master.modPath")
                listdira = os.path.dirname(os.path.dirname(listdir))
                maxlist = []
                list_new = os.listdir(listdira)
                for hh in list_new:
                    if ".mod.model." in hh:
                        maxlist.append(hh.split(".v")[1])
                MAX = max(maxlist)
                oldversion = re.findall('(?<=v)\d+', listdir)[0]
                newversion = listdir.replace(oldversion, str(MAX))
                mesh_xml = os.path.dirname(newversion) + '/mesh.xml'


            if os.path.isfile(mesh_xml):
                results=re.findall(r"/projects/(\w+)/asset/\w+/(\w+)/\w+/",mesh_xml.replace("\\","/"))
                project_name=results[0][0]
                asset_name=results[0][1]
                sg = Connection('get_project_info').get_sg()
                proj_info = sg.find_one('Project', [['name', 'is', project_name]])
                asset_entity = sg.find_one('Asset', [['project', 'is', proj_info], ['code', 'is', asset_name]])
                parent_info = sg.find_one('Asset', [['id', 'is', asset_entity['id']]], ['parents'])
                parent_asset = [sub_asset['name'] for sub_asset in parent_info['parents']] or []
                if parent_asset:
                    parent_asset_name = parent_asset[0]
                    cp = clpp.lcProdProj()
                    cp.setProj(project_name)
                    parent_mesh_xml = cp.getAssetLatestVersion(parent_asset_name, 'mod').replace("\\","/") + '/mesh.xml'
                    md = Mod_Diff()
                    md.parse_xml(parent_mesh_xml,root_node='|master|poly|hi|mesh_grp|skin_grp')
                    parent_diff = diff_md(md)
                    md = Mod_Diff()
                    md.parse_xml(mesh_xml,root_node='|master|poly|hi|mesh_grp',filt='|master|poly|hi|mesh_grp|skin_grp')
                    mesh_diff = diff_md(md)
                    all_diff = parent_diff+mesh_diff
                    if all_diff:
                        return all_diff
                    else:
                        return ""
                else:
                    md = Mod_Diff()
                    md.parse_xml(mesh_xml)
                    desp = diff_md(md)
                    if desp:
                        return desp
                    else:
                        return ""
            else:

                setmessage(u'{} 模型路径错误'.format(mesh_xml), ['chengang'])
                return u'{} mesh_xml路径错误,联系TD'.format(mesh_xml)

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

