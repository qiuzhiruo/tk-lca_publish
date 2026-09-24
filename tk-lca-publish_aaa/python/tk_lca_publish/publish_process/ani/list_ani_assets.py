# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: XiangQuan
#
# Date: 2015.08
#
# Description:
#
############################################

import os
# import sys
import traceback
# import shutil
import json
from xml.dom.minidom import Document, parse

import pymel.core as pm
import maya.cmds as cmds
import maya.OpenMaya as OpenMaya
import maya.app.general.editUtils as editUtils
from maya.maya_to_py_itr import PyEditItr

import production.CacheUtils.FilterCacheObjects as cf

reload(cf)
# import maya.cmds as cmds

# sys.path.append('P:/home/liulu/td_dev_zone/sgtk/tk-lca-publish/python/tk_lca_publish')
from proc import scene_assets

reload(scene_assets)

try:
    cmds.loadPlugin('sceneAssembly', quiet=True)
except:
    pass

class AssetData:
    def __init__(self, namespace='', type='', name='', step='', transform=None, constrained=False,
                 status='', project=''):
        # Example:
        self.namespace = namespace  # inspector1
        self.type = type  # chr
        self.name = name  # inspector
        self.step = step  # cfx
        self.transform = pm.PyNode(str(transform))  # PyNode('inspector:master')
        self.constrained = constrained  # if the assset is constrained with other element
        self.status = status  # constrained/animated/edited/static
        self.project = project


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.l_assets = []

        self.process_name = u"记录带动画的资产和残影数据"
        self.description = u"将镜头的起始结束帧和带动画的资产记录到版本文件夹内一个文本文件中，为自动Cache做准备。"
        return

    def proceed(self):
        try:
            # write result to ani_assets.xml, should consider whether the file exists or not,
            # cause this script will work with list_ani_assets.py, which may create the xml first

            if hasattr(self.dialog, 'assetDatas'):
                self.write_to_xml(self.dialog.assetDatas)
            else:
                self.get_reference_assets()
                self.get_assembly_assets()
                self.write_to_xml(self.l_assets)

            # check and write ghost data
            self.record_ani_ghosts_data()
            return ""
        except:
            return traceback.format_exc()

    def record_ani_ghosts_data(self):
        ani_ghost_grp = 'ANI_GHOSTS'
        data = {}
        if cmds.objExists(ani_ghost_grp):
            children = cmds.listRelatives(ani_ghost_grp, c=True)
            if children:
                for i in sorted(children):
                    asset_ns = cmds.getAttr('{}.asset_ns'.format(i))
                    frame = i.split('_')[-1]
                    data.setdefault(asset_ns, {})
                    ac = cmds.listConnections('{}.visibility'.format(i), s=True, d=False, type='animCurve')[0]
                    indexes = cmds.keyframe(ac, q=True, tc=True)
                    data[asset_ns]['ghost_{}'.format(frame)] = {'start': indexes[1], 'end': indexes[2]}
            if data:
                ghost_data_file = os.path.join(self.dialog.version_dir, 'ghost_data.json')
                with open(ghost_data_file, 'w') as fw:
                    fw.write(json.dumps(data, indent=4, encoding='utf-8'))

    def get_latest_ani_assets_from_ani(self):
        """
        get the ani_asset.xml from the latest ani ver, if it does not exist, return ''
        :return:
        """
        vers = self.dialog.sg.find('Version', [['project', 'is', self.dialog.project],
                                               ['entity.Shot.code', 'is', self.dialog.entity['name']],
                                               ['code', 'contains', 'animation']], ['code', 'sg_version_folder'])
        ani_assets_xml = ''
        if vers:
            # e.g. 'Z:\\projects\\nza\\shot\\e30\\e30120\\ani\\publish\\e30120.ani.animation.v037\\'
            ani_assets_xml = sorted(vers)[-1]['sg_version_folder']['local_path'].replace('\\', '/') + 'ani_assets.xml'

        return ani_assets_xml

    def check_ref_constrain(self, asset):
        asset_ns = asset.namespace()
        constrained = False
        non_transform_constrained = False
        asset_constrained_anim = False
        start = cmds.playbackOptions(q=True, minTime=True)
        end = cmds.playbackOptions(q=True, maxTime=True)
        for constrain in pm.listRelatives(asset, ad=True, type='constraint'):
            # exclude referenced constrain:
            if constrain.isReferenced():
                continue
            if asset.nodeType() == 'assemblyReference' and constrain.name().startswith(asset_ns):
                continue
            ctrl_name = constrain.getParent().nodeName().split(':')[-1]
            for c in pm.listConnections(constrain, c=True, d=True, s=False, p=True):
                constrained = True
                attr = c[0].name().split('.')[-1]
                if not ((attr.startswith('constraintTranslate') or attr.startswith(
                        'constraintRotate')) and ctrl_name in ['global_ctrl' or 'root_ctrl']):
                    non_transform_constrained = True

            # 判断约束后, 控制器有没有数值的变化
            # 这个判断是存在一些问题的，比如一个chr大环被约束，但大环本身没动画，但是胳膊(或身体其他部位)有动画，此处判断就有bug
            for trans in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
                value_list = []
                if asset_constrained_anim:
                    break
                for i in range(int(start), int(end) + 1):
                    if asset_constrained_anim:
                        break
                    value = cmds.getAttr(constrain.getParent().nodeName() + '.' + trans, time=i)
                    if not value_list:
                        value_list.append(value)
                    if value_list and value not in value_list:
                        asset_constrained_anim = True

        if constrained:
            if non_transform_constrained:
                return 'constrained', asset_constrained_anim
            else:
                return 'constrained_trans', asset_constrained_anim
        else:
            return '', asset_constrained_anim

    def check_ar_ref_constrain(self, asset_ar, l_constrained_dg):
        for dg in l_constrained_dg:
            if dg.isParentOf(asset_ar):
                return 'constrained_trans'
        return ''

    def check_ref_edits(self, asset):

        is_child_ref = False

        if asset.nodeType() == 'transform':
            # l_failed = cmds.referenceQuery(asset.name(), editStrings = True, successfulEdits=False, failedEdits = True)
            # l_edits = cmds.referenceQuery(asset.name(), editStrings = True)
            ref_node = cmds.referenceQuery(asset.name(), rfn=True)
            # 此处 碰到 rra 直接 返回，防止 获取 操作历史 直接导致 卡死
            if '_rra' in ref_node:
                return 'constrained'
            l_failed = []
            l_edits = cmds.referenceQuery(ref_node, failedEdits=False, successfulEdits=True, showDagPath=True,
                                          showNamespace=True, editStrings=True)
            is_child_ref = bool(cmds.referenceQuery(ref_node, parent=True, referenceNode=True))

        elif asset.nodeType() == 'assemblyReference':
            l_failed = []
            selectedAssembly = editUtils.makeDependNode(asset.nodeName())
            curAssembly = selectedAssembly
            assemblies = []
            while not curAssembly.isNull():
                assemblies.append(curAssembly)
                assemblyMFn = OpenMaya.MFnAssembly(curAssembly)
                curAssembly = assemblyMFn.getParentAssembly()

            curAssembly = assemblies[-1]

            l_edits = [edt.getString() for edt in PyEditItr(
                OpenMaya.MItEdits(curAssembly, selectedAssembly, OpenMaya.MItEdits.ALL_EDITS,
                                  OpenMaya.MItEdits.kReverse))]

        for edt in l_edits:

            if edt in l_failed:
                continue

            # multi level reference edits doesn't have the full namespace, so we just check setAttr key words
            if is_child_ref and 'setAttr' in edt:
                return 'constrained'  # "edited" means use flo cache for downstream, we use "constrained"

            for token in edt.replace('"', '').split(' ')[1:]:
                node_path = token.split('.')[0]
                if not pm.objExists(node_path):
                    continue  # Not exists/ unload

                try:
                    if not asset.isParentOf(node_path):
                        continue
                except:
                    continue  # None DAG node/ invalid

                if pm.nodeType(node_path) in ['mesh', 'transform']:
                    return 'edited'

                node_name = node_path.split('|')[-1].split(':')[-1]
                if node_name.endswith('_ctrl') and not node_name in ['global_ctrl', 'root_ctrl']:
                    return 'edited'

        return ''

    def is_rra_ref(self, asset):
        '''
        check the reference asset whether is the rra asset
        '''

        ref_node = cmds.referenceQuery(asset.name(), rfn=True)
        return bool(cmds.referenceQuery(ref_node, parent=True, referenceNode=True))

    def find_static_obj(self, objs, assembly=True):
        obj_data = {}
        start = cmds.playbackOptions(q=True, minTime=True)
        end = cmds.playbackOptions(q=True, maxTime=True)
        for frame in [start, int((end - start) / 4 + start), int((end - start) / 2 + start),
                      int(end - (end - start) / 4), end]:
            cmds.currentTime(frame)
            for o in objs:
                name = o.name()
                if assembly:
                    mesh_grp = '{}{}:mesh_grp'.format(o.namespace(), cmds.assembly(name, q=True, rns=True))
                else:
                    mesh_grp = '{}mesh_grp'.format(o.namespace())
                obj_data.setdefault(name, {})
                if cmds.objExists(mesh_grp):
                    if len(cmds.ls(mesh_grp, long=1)) != 1:
                        mesh_grp = [i for i in cmds.ls(mesh_grp, long=1) if ':lo|' not in i and ':md|' not in i][0]
                    # check all mesh children whether moved
                    child_mesh = cmds.listRelatives(mesh_grp, ad=True, type='mesh')
                    children = [mesh_grp] + [cmds.listRelatives(i, parent=True)[0] for i in
                                             child_mesh] if child_mesh else [mesh_grp]
                    for child in children:
                        obj_data[name].setdefault(child, set())
                        obj_data[name][child].add(str(cmds.xform(child, q=True, bb=True, ws=True)))
                else:
                    # unexpand AR, check the AR node whether moved
                    obj_data[name].setdefault(name, set())
                    obj_data[name][name].add(str(cmds.xform(name, q=True, bb=True, ws=True)))

        static_objs = set()
        for k, v in obj_data.iteritems():
            is_static = True
            for i in v:
                if len(v[i]) > 1:
                    is_static = False
                    break
            if is_static:
                static_objs.add(k)

        return static_objs

    def get_reference_assets(self):
        '''
        comes from list_ani_assets.py, check traditional reference nodes
        '''

        l_ref_asset = scene_assets.getReferenceAssets('|assets')
        # e.g. [nt.Transform(u'doctor_surgery:master'), nt.Transform(u'doctor_surgery1:master')]

        # 添加这个主要是为了应对prp
        # eg1: flo添加了道具, 但是用了约束, 不过没动画, 此处应该标记为edited (如果不加此判断, 会被标记为constrained, 就需要来回返动画)
        # eg2: ani约束了prp, 但是约束节点被p到了组外, 此处应该标记为constrained (如果不加此判断, 会被标记为edited)
        check_static_grp = '|assets|prp'
        static_reference_prp_objs = []

        if cmds.objExists(check_static_grp):
            check_static_grp_list = cmds.listRelatives(check_static_grp, children=True)
            if check_static_grp_list:
                l_ref_prp_asset = [obj for obj in l_ref_asset if obj.name() in check_static_grp_list]
                static_reference_prp_objs = self.find_static_obj(l_ref_prp_asset, assembly=False)

        for trans in l_ref_asset:
            if not pm.objExists(trans.namespace() + 'poly'):
                continue

            # skip mash prp
            if '|assets|prp|' in trans.fullPath() and cmds.ls('%s:*' % trans.name().split(':')[0], type='MASH_Waiter') and trans.name().startswith('crow_cluster'):
                continue
            # asset_name = trans.name().split(":")[-2]
            asset_name = '.'.join(trans.name().split(":")[:-1])
            if pm.referenceQuery(trans, isNodeReferenced=True):
                ref_path = pm.referenceQuery(trans, filename=True)
                tokens = ref_path.split('/')
                if 'asset' in tokens:
                    i = tokens.index('asset')
                    asset_type = tokens[i + 1]
                    ref_asset_name = tokens[i + 2]
                    asset_src = tokens[i + 3]
                    asset_project = tokens[i - 1]
                else:
                    asset_type = '-'
                    ref_asset_name = '-'
                    asset_src = '-'
                    asset_project = '-'
            else:
                asset_type = '-'
                ref_asset_name = '-'
                asset_src = '-'
                asset_project = '-'

            is_rra = self.is_rra_ref(trans)
            constrain_status, constrained_anim = self.check_ref_constrain(trans)
            anim_status = cf.isAnimation(trans)
            prp_ref_static_status = trans.name() in static_reference_prp_objs

            if is_rra:  # normally rra asset is constrained, so we set the rra asset status to "constrained"
                status = 'constrained'
            elif constrain_status == 'constrained':
                if prp_ref_static_status and not constrained_anim:
                    status = 'edited'
                else:
                    status = 'constrained'
            elif constrain_status == 'constrained_trans':
                if anim_status:
                    status = 'animated'
                elif prp_ref_static_status and not constrained_anim:
                    status = 'edited'
                else:
                    status = 'constrained'
            else:
                if anim_status:
                    status = 'animated'
                elif self.check_ref_edits(trans) == 'constrained':
                    status = 'constrained'
                # 添加此处判断的目的是, 如果有prp下的约束节点跑到了大纲根目录下, 就会有bug
                elif asset_type == 'prp' and not prp_ref_static_status:
                    status = 'constrained'
                elif self.check_ref_edits(trans) == 'edited':
                    status = 'edited'
                else:
                    status = 'edited'

            if status == '':
                continue

            if constrain_status:
                constrained = True
            else:
                constrained = False

            asset_data = AssetData(asset_name, asset_type, ref_asset_name, asset_src, trans, constrained, status,
                                   asset_project)
            self.l_assets.append(asset_data)

        return

    def get_assembly_assets(self):
        l_asset_ar, l_unload_ar, l_asb_ar = scene_assets.getAssemblyReferenceAssets('|assets')

        l_constrained_dg = []

        if l_asset_ar:
            for c in pm.ls(type='constraint'):
                if not c.isReferenced():
                    if c.getParent() is not None:
                        l_constrained_dg.append(c.getParent())

            static_assembly_objs = self.find_static_obj(l_asset_ar)
            print 'Static Assembly Objects:\n', '\n'.join(static_assembly_objs)
            for trans in l_asset_ar:
                # asset_data = self.create_assetData(asset_ar)
                constrain_status, constrained_anim = self.check_ref_constrain(trans)
                if constrain_status == '':
                    constrain_status = self.check_ar_ref_constrain(trans, l_constrained_dg)

                anim_status = cf.isAnimation(trans)
                assembly_static_status = trans.name() in static_assembly_objs

                if constrain_status == 'constrained':
                    if trans.name() in static_assembly_objs and not constrained_anim:
                        status = 'edited'
                    else:
                        status = 'constrained'
                elif constrain_status == 'constrained_trans':
                    if anim_status:
                        status = 'animated'
                    elif trans.name() in static_assembly_objs and not constrained_anim:
                        status = 'edited'
                    else:
                        status = 'constrained'
                else:
                    if anim_status:
                        status = 'animated'
                    # 添加此处判断的目的是, 如果有AR下的约束节点跑到了大纲根目录下, 就会有bug
                    elif not assembly_static_status:
                        status = 'constrained'
                    elif self.check_ref_edits(trans) == 'edited':
                        status = 'edited'
                    else:
                        status = ''

                if status == '':
                    continue

                if constrain_status:
                    constrained = True
                else:
                    constrained = False
                asset_data = self.create_assetData(trans, constrained, status)
                self.l_assets.append(asset_data)

        return

    def read_from_xml(self, xml_file):
        """
        :param xml_file: e.g. 'Z:/projects/nza/shot/e30/e30120/ani/publish/e30120.ani.animation.v037/ani_assets.xml'
        :return: a list
        """
        dom = parse(xml_file)
        asset_elems = dom.getElementsByTagName("asset")

        assets = []
        for asset_elem in asset_elems:
            asset_name = asset_elem.getAttribute('transform')
            if pm.objExists(asset_name):
                assets.append(pm.PyNode(asset_name))  # e.g. nt.Transform(u'doctor_surgery:master')
            else:
                print 'Warning:', asset_name, 'does not exist in the current file.'

        return assets

    def find_extra_sampled_node(self, assetname, asset_project=''):
        '''支持跨项目资产查询'''
        # [NOTE]: 202510 因为z88场次测试镜头可能会用别的项目的资产，所以这里允许查找别的项目资产的sample。正式镜头不允许出现别的项目资产，检查项会卡住

        asset_target_project = (self.dialog.sg.find_one('Project', [['name', 'is', asset_project]])
                                if asset_project else self.dialog.project)  # type:dict
        extra_sampled_node = []
        shot_extra_sampled_node = self.dialog.sg.find_one('Shot', [['code', 'is', self.dialog.entity['name']],
                                                                   ['project', 'is', self.dialog.project]],
                                                          ['sg_asset_in_shot_sample'])['sg_asset_in_shot_sample']
        asset_data = self.dialog.sg.find_one('Asset',
                                             [['project', 'is', asset_target_project],
                                              ['code', 'is', assetname]], ['sg_asset_sample'])

        asset_extra_sampled_node = asset_data.get('sg_asset_sample') if asset_data else None

        if shot_extra_sampled_node and assetname in shot_extra_sampled_node:
            shot_extra_sampled_node = eval(shot_extra_sampled_node)[assetname]
            extra_sampled_node += shot_extra_sampled_node.keys()
        if asset_extra_sampled_node:
            asset_extra_sampled_node = eval(asset_extra_sampled_node)
            extra_sampled_node += asset_extra_sampled_node.keys()
        if extra_sampled_node:
            extra_sampled_node = ','.join(list(set(extra_sampled_node)))
        return extra_sampled_node

    def write_to_xml(self, assetDatas):
        '''
        write result to ani_assets.xml, should consider whether the file exists or not
        if the xml file exists, write after old info; else create a new file
        TODO: does not consider the situation that the existing file cannot be parsed, like it is an empty file
        '''
        shot = self.dialog.sg.find_one('Shot', [['id', 'is', self.dialog.entity['id']]],
                                       ['sg_cut_in', 'sg_cut_out', 'sg_ani_cut_in', 'sg_ani_cut_out'])
        cut_in = shot['sg_cut_in']
        cut_out = shot['sg_cut_out']
        if shot['sg_ani_cut_in'] and shot['sg_ani_cut_out']:
            cut_in = shot['sg_ani_cut_in']
            cut_out = shot['sg_ani_cut_out']

        xml_path = self.dialog.version_dir + '/ani_assets.xml'

        dom = Document()
        root_dom = dom.createElement('anim')
        root_dom.setAttribute('start', str(int(cut_in)))
        root_dom.setAttribute('end', str(int(cut_out)))
        dom.appendChild(root_dom)

        # 预先检查 assetDatas 中是否存在 assembly 类型资产
        # has_assembly_asset = any(a for a in assetDatas if a.type == 'assemblyReference') # 先返回旧功能，可以让 assembly 形态的 flg 列入到 ani assets xml 里面，后续再打开

        d_assets = {}
        for asset in assetDatas:
            if not d_assets.has_key(asset.type):
                d_assets[asset.type] = {}
            d_assets[asset.type][asset.namespace] = asset

        for a_type in sorted(d_assets.keys()):
            for a_name in sorted(d_assets[a_type].keys()):
                asset = d_assets[a_type][a_name]

                # # 新增判断逻辑： # 先返回旧功能，可以让 assembly 形态的 flg 列入到 ani assets xml 里面，后续再打开
                # if asset.type == 'flg' and has_assembly_asset:
                #     continue
                # node_name = asset.transform.split(':')[-1]
                # if asset.type == 'flg' and '_AR' in node_name:
                #     continue

                dom_elem = dom.createElement('asset')
                dom_elem.setAttribute('type', asset.type)
                dom_elem.setAttribute('name', asset.name)
                dom_elem.setAttribute('namespace', asset.namespace)
                dom_elem.setAttribute('transform', asset.transform)
                dom_elem.setAttribute('constrained', str(asset.constrained))
                dom_elem.setAttribute('status', str(asset.status))

                if asset.type == 'chr':
                    if pm.attributeQuery('asm_info', n=asset.transform, ex=1):
                        asm_info = pm.PyNode(asset.transform).asm_info.get()
                        dom_elem.setAttribute('asm_info', str(asm_info))

                if asset.type == 'chr' or asset.type == 'crd' or asset.type == 'prp':
                    extra_sampled_node = self.find_extra_sampled_node(asset.name, asset.project)
                    if extra_sampled_node:
                        dom_elem.setAttribute('extra_sampled_node', str(extra_sampled_node))

                if asset.type == 'chr':
                    if pm.attributeQuery('cycleCache', node=asset.transform, exists=True):
                        dom_elem.setAttribute('cycle_cache', cmds.getAttr(asset.transform + '.cycleShotName'))
                root_dom.appendChild(dom_elem)

        # just formatting output xml
        pretty_text = dom.toprettyxml(indent='    ', newl='')
        final_text = pretty_text.replace('        ', '    ')
        final_text = final_text.replace('>    <', '>\n    <')
        final_text = final_text.replace('><', '>\n<')
        f = open(xml_path, 'w')
        f.write(final_text)
        f.close()
        return

    def append_to_list(self, assem_node, constraint, status, data_list):
        '''
        '''
        assetData = self.create_assetData(assem_node)
        assetData.constrained = constraint
        assetData.flag = True
        assetData.status = status
        # import maya.cmds as cmds
        # assetData.type = cmds.ls(str(assem_node), long = True)[0].split('|')[2]
        data_list.append(assetData)

    def create_assetData(self, assem_node, constrained, status):
        assem_splits = assem_node.split(':')
        real_namespace = assem_splits[:-1]
        ar_prefix_ns = assem_splits[-1].replace('_AR', '')
        real_namespace.append(ar_prefix_ns)
        namespace = '.'.join(real_namespace)
        assem_def_path = pm.getAttr(assem_node + '.definition').replace('\\', '/')
        def_path_tokens = assem_def_path.split('/')
        if 'asset' in def_path_tokens:
            i = def_path_tokens.index('asset')
            asset_type = def_path_tokens[i + 1]  # read type from reference path
            asset_name = def_path_tokens[i + 2]
            asset_step = def_path_tokens[i + 3]
        else:
            asset_type = '-'
            asset_name = '-'
            asset_step = '-'

        return AssetData(namespace, asset_type, asset_name, asset_step, assem_node, constrained, status)

    def get_all_assemblies(self, start_node=''):
        '''
        list all assemblyReference nodes under start_node
        '''
        if start_node == '':
            assemblies = pm.ls(type='assemblyReference')
        else:
            assemblies = pm.listRelatives(start_node, allDescendents=True, type='assemblyReference')

        return assemblies

    def get_current_representation(self, assembly_name):
        '''
        '''
        return pm.assembly(assembly_name, query=True, active=True)

    def is_scene(self, assem, assem_repr):
        '''
        when representation is a scene, handle it like what 'list_ani_assets.py' does:
        only check constraints under 'poly' hierarchy
        '''
        if assem_repr.endswith('.ma') or assem_repr.endswith('.mb'):
            assem_children = pm.listRelatives(assem, c=True, pa=True)
            if not assem_children:
                return False

            master = [assem_c for assem_c in assem_children if str(assem_c).endswith('master')][0]
            if not master:
                return False

            children = pm.listRelatives(master, c=True, pa=True)
            if not children:
                return False

            has_poly = False
            for child in children:
                if child.endswith(':poly'):
                    has_poly = True
                    break
            return has_poly  # if repr is ma or mb, and hierarchy has poly, then it is a scene
        else:
            return False

    def is_scene_meshShown(self, assem):
        '''
        '''
        # cause is_scene check happens first, master must exists
        assem_children = pm.listRelatives(assem, c=True, pa=True)
        master = [assem_c for assem_c in assem_children if str(assem_c).endswith('master')][0]

        namespace = master.rsplit(':', 1)[0]
        hi_level = namespace + ':hi'
        if not pm.objExists(hi_level):
            return False

        # we only count on meshes in hi group
        trans = pm.listRelatives(hi_level, allDescendents=True, path=True, type='transform')
        for t in trans:
            if pm.getAttr(t + '.visibility'):
                meshes = pm.listRelatives(t, allDescendents=True, path=True,
                                          type=['mesh', 'subdiv', 'nurbsSurface'])
                if meshes:
                    return True

        return False

    def is_gpuCache(self, assem_repr):
        if assem_repr.endswith('.abc'):
            return True
        else:
            return False

    def is_locator(self, assem_repr):
        if assem_repr.endswith('.locator'):
            return True
        else:
            return False

    def is_bottom_assemblyReference(self, assem):
        is_bottom = False
        sub_assem = pm.listRelatives(assem, type='assemblyReference', allDescendents=True)
        if not sub_assem:
            is_bottom = True
        return is_bottom

    def is_transform_attrs_locked(self, node):
        is_locked = True
        locked_transformation = []
        locked_transformation.append(pm.getAttr(node + '.translateX', lock=True))
        locked_transformation.append(pm.getAttr(node + '.translateY', lock=True))
        locked_transformation.append(pm.getAttr(node + '.translateZ', lock=True))

        locked_transformation.append(pm.getAttr(node + '.rotateX', lock=True))
        locked_transformation.append(pm.getAttr(node + '.rotateX', lock=True))
        locked_transformation.append(pm.getAttr(node + '.rotateX', lock=True))

        locked_transformation.append(pm.getAttr(node + '.scaleX', lock=True))
        locked_transformation.append(pm.getAttr(node + '.scaleY', lock=True))
        locked_transformation.append(pm.getAttr(node + '.scaleZ', lock=True))

        if False in locked_transformation:
            is_locked = False

        return is_locked

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
