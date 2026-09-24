# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Han Bo
#
# Date: 2024.4.15
#
# Description: create_write_extra_data
#
############################################

import os
import traceback
import pymel.core as pm
import maya.cmds as cmds
import json
import string
import production.make_extra_data_dirs.make_extraData_dirs as medd;reload(medd)
import flg_note_to_gas_artist as fntga;reload(fntga)
# All publish process will use StdProcess as the class name.


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"在服务器上版本文件夹里创建 extra_data，输出必要信息"
        self.description = u"在服务器上版本文件夹里创建 extra_data，输出 shot 内的 asset 的 pass 信息；输出 sceneAssembly 的显示隐藏 信息"
        return

    def proceed(self):
        '''
            extra_data_dir_shot = 
                /mnt/proj/projects/lrs/shot/z99/z99997/ani/publish/z99997.ani.animation.v014/extra_data
            ### shot_assets_pass.json ### only pub : check,ds
            extra_data_pass_shot = 
                {
                    "z99997": {
                        "bazaar_pear_pits": {
                            "rigPass_frame": null, 
                            "lookPass": "default", 
                            "rigPass_name": "pear_state", 
                            "lookPass_frame": null, 
                            "rigPass": "Full", 
                            "lookPass_name": "lookPass"
                        }, 
                        "wang_wife": {
                            "lookPass": "default", 
                            "rigPass_frame": null, 
                            "rigPass": null, 
                            "lookPass_frame": null, 
                            "lookPass_name": "lookPass"
                        }, 
                        "nxq_niexiaoqian": {
                            "rigPass_frame": null, 
                            "lookPass": "h30_darn_hurt | h50_slap", 
                            "rigPass_name": "rigPass", 
                            "lookPass_frame": {
                                "1050.0": "h30_darn_hurt", 
                                "1058.0": "h50_slap"
                            }, 
                            "rigPass": "suture", 
                            "lookPass_name": "lookPass"
                        }
                    }
                }
            extra_data_sceneAssembly_shot = 
                /mnt/proj/projects/lrs/shot/z99/z99997/ani/publish/z99997.ani.animation.v014/extra_data
            ### shot_sceneAssembly_visibility.json ### only pub : check,ds
            extra_data_sceneAssembly_shot = 
                {
                    "|assets|scn": {
                        "|assets|scn|......:L_window_break_b_window_grp": {
                            "frame": [
                                1001.0, 
                                1010.0
                            ]
                        }, 
                        "|assets|scn|......:nxq_ningroom_wall_a:wall_a_1": {
                            "frame": []
                        }
                    }, 
                    "|assets|flg": {}, 
                    "|assets|asb": {}
                }
        '''
        try:
            # 创建 ani 的版本文件夹
            self.dialog.version_dir = self.dialog.publish_root + '/' + self.dialog.version_name
            if not os.path.isdir(self.dialog.version_dir):
                os.makedirs(self.dialog.version_dir)
            
            print 
            print 
            # 创建 ani 的 extra_data_dirs
            extra_data_dir_shot = medd.make_rough_lay_extra_data_dirs(self.dialog.version_dir)

            if self.dialog.step['name'] == 'ani' and self.dialog.entity_type == 'Shot' and self.dialog.task['name'] == 'animation' and self.dialog.ui.comboBox_publish_mode.currentIndex()>=1:

                shot_name = self.dialog.entity['name']
                extra_data_pass_shot = {} # 新增记录 ani 阶段输出镜头内的 资产的 pass 信息
                
                extra_data_hair_pass_info = InfoHelper.get_hair_pass_info() #type:dict
                self.write_extra_data(extra_data_dir_shot,extra_data_hair_pass_info,'lookdiff_3_hair_info.json')

                extra_data_pass_shot[shot_name] = {}

                extra_data_pass_shot = self.write_shot_assets_pass(shot_name,extra_data_dir_shot,extra_data_pass_shot)

                self.write_extra_data(extra_data_dir_shot,extra_data_pass_shot,'shot_assets_pass.json')

                extra_data_sceneAssembly_shot = {} # 新增记录 ani 阶段输出镜头内的 sceneAssembly 的 显示隐藏 信息

                extra_data_sceneAssembly_shot = self.write_shot_sceneAssembly_visibility(shot_name,extra_data_dir_shot,extra_data_sceneAssembly_shot)

                self.write_extra_data(extra_data_dir_shot,extra_data_sceneAssembly_shot,'shot_sceneAssembly_visibility.json')
            # print 88888, self.dialog.step['name']
            # if self.dialog.step['name'] in ['ani', 'lay', 'flo']:
            #     extra_data_asb_move = {} # 新增记录镜头内摆位置的asb信息

            #     extra_data_asb_move = self.get_asb_root_con()

            #     self.write_extra_data(extra_data_dir_shot, extra_data_asb_move,'asb_root_con.json')
            # 增加发送 flg 显示&位移 情况给 GAS
            fntga.main(self.dialog)
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


    def get_node_visibility(self,node,node_visibility_dict):
        node_vis_attr = node+'.visibility'
        # 先获取 visibility 属性值
        node_vis_value = pm.getAttr(node_vis_attr)
        # 获取父级连接
        node_parents = cmds.listConnections(node_vis_attr,s=1,d=0,p=1)
        # print node_parents
        # 如果有父级连接
        if node_parents:
            # 获取 animCurve 类型父级连接
            node_parents_keyType = list(set([i for i in node_parents if 'animCurve' in str(pm.nodeType(i))]))
            # print node_parents_keyType
            # 如果有 animCurve 类型父级连接
            if len(node_parents_keyType)==1:
                keyframes = cmds.keyframe(node_parents_keyType[0].split('.')[0], query=True, timeChange=True)
                # 如果是 key 帧 的 animCurve
                if keyframes:
                    # keyframes_dict = {}
                    key_f_list=[]
                    key_v=[]
                    for key_f in keyframes:
                        node_vis_value = cmds.getAttr(node_vis_attr,time=key_f)
                        # keyframes_dict[key_f]=node_vis_value
                        key_v.append(node_vis_value)
                        if not node_vis_value:
                            key_f_list.append(key_f)
                    key_v_list = list(set(key_v))
                    if len(key_v_list)==1:
                        if key_v_list[0]:
                            pass
                        else:
                            node_visibility_dict[node]={}
                            node_visibility_dict[node]['frame']=[]
                    else:
                        node_visibility_dict[node]={}
                        node_visibility_dict[node]['frame']=key_f_list
                # 如果不是 key 帧 的 animCurve，则跳过，
                else:
                    pass
            # 如果没有 animCurve 类型父级连接，则跳过，这种情况是资产做的隐藏连接
            else:
                pass
        # 如果没有父级连接，则直接获取 visibility
        else:
            if not node_vis_value:
                node_visibility_dict[node]={}
                node_visibility_dict[node]['frame']=[]
        
        return node_visibility_dict

    def get_invisible_nodes(self,sceneAssembly_layer):
        node_visibility_dict={}
        all_nodes = cmds.ls(allPaths=True, dag=True, l=True)
        for node in all_nodes:
            # 找 |assets|scn 下面对象
            if node.startswith(sceneAssembly_layer):
                node_type = cmds.nodeType(node)
                # 看节点类型 是不是 transform 或者 assemblyReference
                if node_type in ["transform", "assemblyReference"]:
                    # 看节点 是不是 AR，一般指的是 assemblyReference 类型
                    if node.endswith('_AR'):
                        # print 'is _AR'
                        node_visibility_dict = self.get_node_visibility(node,node_visibility_dict)
                    # 看节点 是不是 master，asb，poly，hi，mesh_grp 层级，一般指的是 transform 类型
                    elif node.endswith(':master') or node.endswith(':asb') or node.endswith(':poly') or node.endswith(':hi') or node.endswith(':mesh_grp'):
                        print 'is master,asb,poly,hi,mesh_grp'
                        node_visibility_dict = self.get_node_visibility(node,node_visibility_dict)
                    # 看节点 是不是 mesh_grp 下面的，一般指的是 transform 类型
                    elif ':mesh_grp|' in node:
                        print 'is mesh_grp'
                        node_visibility_dict = self.get_node_visibility(node,node_visibility_dict)
        return node_visibility_dict

    # 新增记录 ani 阶段输出镜头内的 sceneAssembly 的 显示隐藏 信息
    def write_shot_sceneAssembly_visibility(self,shot_name,extra_data_dir_seq,sceneAssembly_visibility_dict):
        sceneAssembly_layers = ['|assets|scn','|assets|asb','|assets|flg']
        for sceneAssembly_layer in sceneAssembly_layers:
            sceneAssembly_visibility_dict[sceneAssembly_layer]={}
            node_visibility_dict = self.get_invisible_nodes(sceneAssembly_layer)
            sceneAssembly_visibility_dict[sceneAssembly_layer]=node_visibility_dict
        
        return sceneAssembly_visibility_dict

    # 新增记录 ani 阶段输出镜头内的 资产的 pass 信息
    def write_shot_assets_pass(self,shot_name,extra_data_dir_seq,extra_data_pass_seq):
        shot_cam = shot_name+'_cam'
        shot_pass_dict = eval(cmds.getAttr(shot_cam+'.lca_shot_chr_pass'))
        if shot_pass_dict != {}:
            for asset_key in shot_pass_dict.keys():
                for pass_key in shot_pass_dict[asset_key].keys():
                    # print shot_pass_dict[asset_key][pass_key]
                    if u'无' in shot_pass_dict[asset_key][pass_key]:
                        shot_pass_dict[asset_key][pass_key] = None
                
                rigPass_name = 'rigPass'
                rigPass_frame_name = 'rigPass_frame'
                if shot_pass_dict[asset_key][rigPass_name]:
                    rigPass_name_list = shot_pass_dict[asset_key][rigPass_name].split(' | ')
                    if len(rigPass_name_list) >1 :
                        rigPass_frame_list = shot_pass_dict[asset_key][rigPass_frame_name].split(' | ')
                        shot_pass_dict[asset_key][rigPass_frame_name]={}
                        for r in range(len(rigPass_name_list)):
                            shot_pass_dict[asset_key][rigPass_frame_name][rigPass_frame_list[r]]=rigPass_name_list[r]
                    else:
                        shot_pass_dict[asset_key][rigPass_frame_name]=None
                else:
                    shot_pass_dict[asset_key][rigPass_frame_name]=None
                
                lookPass_name = 'lookPass'
                lookPass_frame_name = 'lookPass_frame'
                if shot_pass_dict[asset_key][lookPass_name]:
                    lookPass_name_list = shot_pass_dict[asset_key][lookPass_name].split(' | ')
                    if len(lookPass_name_list) >1 :
                        lookPass_frame_list = shot_pass_dict[asset_key][lookPass_frame_name].split(' | ')
                        shot_pass_dict[asset_key][lookPass_frame_name]={}
                        for r in range(len(lookPass_name_list)):
                            shot_pass_dict[asset_key][lookPass_frame_name][lookPass_frame_list[r]]=lookPass_name_list[r]
                    else:
                        shot_pass_dict[asset_key][lookPass_frame_name]=None
                else:
                    shot_pass_dict[asset_key][lookPass_frame_name]=None
                
        extra_data_pass_seq[shot_name] = shot_pass_dict
        return extra_data_pass_seq

    def get_asb_root_con(self):
        asb_move_json = {}
        if cmds.objExists('|assets|lay|ctrl'):
            c_list = cmds.listRelatives('|assets|lay|ctrl', ad=1, f=1, type='transform')
            if c_list:
                for c in c_list:
                    if '_asb_' in c.split('|')[-1]:
                        if c.split('_')[-2] == 'asb':
                            asb_name = cmds.getAttr('%s.asbname' % c)
                            c_t = cmds.getAttr('%s.t' % c)[0]
                            c_r = cmds.getAttr('%s.r' % c)[0]
                            c_s = cmds.getAttr('%s.s' % c)[0]
                            c_m = cmds.xform(c, q=True, m=True, ws=True)
                            asb_move_json[c] = {'asbname': asb_name, 'purple_con_name': c,
                                                'transform': {'t': c_t, 'r': c_r, 's': c_s, 'm': c_m}}
        return asb_move_json

    # 写出 extra_data 到 json
    def write_extra_data(self,extra_data_dir,extra_data,json_name):
        
        extra_data_json = os.path.join(extra_data_dir,json_name).replace('\\','/')

        self._writeJson(extra_data_json,extra_data,extra_data_dir)

    def _writeJson(self, jsonPath, json_dict,extra_data_dir):
        try:
            os.system("chmod 777 -R %s" % extra_data_dir)
            os.chmod(extra_data_dir, 0777)
            #[NOTE]:publish经常有无权限的错误，这里给jsonpath 解锁
            os.system("chmod 777 -R %s" % jsonPath)
            os.chmod(jsonPath, 0777)
        except Exception as e:
            print(e)
        with open(jsonPath, 'w') as json_file:
            json_file.write(json.dumps(json_dict, indent=4))


class InfoHelper(object):

    @staticmethod
    def get_selected_references():
        """获取已勾选的引用文件"""
        selected_refs = []
        
        all_refs = cmds.file(query=True, reference=True) or []
        
        for ref_path in all_refs:
            try:
                is_deferred = cmds.file(ref_path, query=True, deferReference=True)
                if not is_deferred:
                    selected_refs.append(ref_path)
            except:
                continue
        
        return selected_refs
    @staticmethod
    def extract_namespace_from_node(node_path):
        """从节点路径提取名称空间"""
        if not node_path:
            return ""
        
        short_name = node_path.split('|')[-1]
        
        if ':' in short_name:
            return short_name.split(':')[0]
        
        return ""
    @staticmethod
    def get_reference_namespaces(ref_path):
        """获取引用中非相机节点的名称空间"""
        namespaces = set()
        
        try:
            ref_nodes = cmds.referenceQuery(ref_path, nodes=True, dagPath=True) or []
            
            for node in ref_nodes:
                node_type = cmds.nodeType(node)
                if node_type == 'camera':
                    continue
                
                shapes = cmds.listRelatives(node, shapes=True, fullPath=True) or []
                is_camera = False
                for shape in shapes:
                    if cmds.nodeType(shape) == 'camera':
                        is_camera = True
                        break
                
                if not is_camera:
                    namespace = InfoHelper.extract_namespace_from_node(node)
                    if namespace:
                        namespaces.add(namespace)
        
        except Exception as e:
            print("获取引用名称空间时出错: {}".format(str(e)))
        
        return list(namespaces)

    @staticmethod
    def get_transform_nodes_in_group(group_name, check_group=False):
        """获取组下所有transform节点的显示隐藏信息"""
        result = []
        
        if not cmds.objExists(group_name):
            return result
        
        # [NOTE]:获取组下的所有直接子transform节点
        child_transforms = cmds.listRelatives(group_name, 
                                              children=True,
                                              type='transform',
                                              fullPath=True) or []
        if check_group:
            child_transforms = [group_name]
        
        for child in child_transforms:
            # [NOTE]:获取显示状态
            visibility = True
            child_shapes = cmds.listRelatives(child, shapes=True, noIntermediate=True) or []
            child_check_vis = child if not child_shapes else child_shapes[0]
            try:
                if cmds.attributeQuery('visibility', node=child_check_vis, exists=True):
                    vis_attr = "{}.visibility".format(child_check_vis)
                    visibility = bool(cmds.getAttr(vis_attr))
            except:
                visibility = True
            
            node_info = {
                "transform_node": child,
                "visibility": visibility
            }
            
            result.append(node_info)
        
        return result

    @staticmethod
    def get_transform_all_nodes_in_group(group_name, name_filter=None, muggle=False):
        """获取组下所有transform节点的显示隐藏信息"""
        result = []

        if not cmds.objExists(group_name):
            return result

        # [NOTE]:获取组下的所有直接子transform节点
        child_transforms = cmds.listRelatives(group_name,
                                              ad=True,
                                              type='transform',
                                              fullPath=True) or []

        for transform in child_transforms:
            # [NOTE]:获取显示状态
            short_name = transform.rsplit('|', 1)[-1]
            transform_shapes = cmds.listRelatives(transform, shapes=True, noIntermediate=True) or []
            transform_check_vis = transform if not transform_shapes else transform_shapes[0]
            try:
                if name_filter and not short_name.startswith(name_filter):
                    continue
                if muggle:
                    group_name = transform_check_vis
                visibility = InfoHelper.is_visible_under_root(transform_check_vis, group_name)
            except:
                visibility = True

            node_info = {
                "transform_node": transform,
                "visibility": visibility
            }

            result.append(node_info)

        return result

    @staticmethod
    def get_node_type_in_outliner(node):
        if cmds.nodeType(node) != 'transform':
            return cmds.nodeType(node)

        shapes = cmds.listRelatives(node, shapes=True, noIntermediate=True) or []

        if not shapes:
            return 'group'

        shape_type = cmds.nodeType(shapes[0])

        if shape_type == 'mesh':
            return 'mesh'

        return shape_type

    @staticmethod
    def is_visible_under_root(node, root_grp):
        current = node

        while current:
            if not cmds.getAttr(current + '.visibility'):
                return False

            if current == root_grp:
                break

            parent = cmds.listRelatives(current, p=True, f=True)
            current = parent[0] if parent else None

        return True

    @staticmethod
    def get_RiggingSystemType(namespace):
        RiggingType = "lca"
        global_ctrl = "{}:global_ctrl".format(namespace)
        if pm.objExists(global_ctrl):
            if pm.objExists(global_ctrl + ".rig_system"):
                RiggingType = pm.getAttr(global_ctrl + ".rig_system")
                # RiggingType == "adv"/"muggle"
        return RiggingType

    @staticmethod
    def get_group_info_by_namespace(namespace):
        """获取指定名称空间的组信息（包含所有transform节点）"""
        result = {}
        rig_type = InfoHelper.get_RiggingSystemType(namespace)
        muggle = True if rig_type == "muggle" else False
        
        # [NOTE]:处理face_hair组 - 获取所有transform节点
        face_hair_group = "{}:face_hair".format(namespace) if namespace else "face_hair"
        if cmds.objExists(face_hair_group):
            face_hair_group = cmds.ls(face_hair_group, long=True)[0]
            face_hair_transforms = InfoHelper.get_transform_all_nodes_in_group(face_hair_group, muggle=muggle)
            face_hair_transforms = [i for i in face_hair_transforms
                                    if InfoHelper.get_node_type_in_outliner(i['transform_node']) == 'mesh']
            if face_hair_transforms:
                result["face_hair"] = face_hair_transforms
        
        # [NOTE]:处理head_hair组 - 获取所有transform节点
        head_hair_group = "{}:head_hair".format(namespace) if namespace else "head_hair"
        if cmds.objExists(head_hair_group):
            head_hair_group = cmds.ls(head_hair_group, long=True)[0]
            head_hair_transforms = InfoHelper.get_transform_all_nodes_in_group(head_hair_group, muggle=muggle)
            head_hair_transforms = [i for i in head_hair_transforms
                                    if InfoHelper.get_node_type_in_outliner(i['transform_node']) == 'mesh']
            if head_hair_transforms:
                result["head_hair"] = head_hair_transforms

        # [NOTE]:处理face_pass_grp组 - 获取所有transform节点
        face_pass_group = "{}:face_pass_grp".format(namespace) if namespace else "face_pass_grp"
        if cmds.objExists(face_pass_group):
            face_pass_transforms = InfoHelper.get_transform_nodes_in_group(face_pass_group)
            if face_pass_transforms:
                face_pass_result = []
                for fp in face_pass_transforms:
                    if not fp['visibility']:
                        continue
                    fp_result = InfoHelper.get_transform_all_nodes_in_group(fp['transform_node'],
                                                                            '{}:shell_'.format(namespace),
                                                                            muggle=muggle)
                    grp_vis_status = [i for i in fp_result if i['visibility']]
                    if grp_vis_status:
                        face_pass_result.extend(fp_result)
                if face_pass_result:
                    result["face_pass"] = face_pass_result

        # [NOTE]:处理cloth_pass_grp组 - 获取所有transform节点
        cloth_pass_group = cmds.ls("{}:CLT_*_grp".format(namespace) if namespace else "cloth_pass_group", long=True)
        if cloth_pass_group:
            cloth_pass_result = []
            for child in cloth_pass_group:
                node_info = InfoHelper.get_transform_all_nodes_in_group(child, muggle=muggle)
                child_grp_vis = [i for i in node_info if i['visibility'] and
                                 InfoHelper.get_node_type_in_outliner(i['transform_node']) == 'mesh']
                cloth_pass_result.append({"transform_node": child, "visibility": bool(child_grp_vis)})

            if cloth_pass_result:
                result["cloth_pass"] = cloth_pass_result
        
        # [NOTE]:只有当有face_hair或head_hair信息时才返回
        if result:
            return result
        
        return None
    @staticmethod
    def process_all_namespaces(namespaces):
        """处理所有名称空间，获取组信息"""
        #type: list[str]-> dict
        namespace_data = {}
        
        for namespace in namespaces:
            namespace_key = namespace if namespace else "global"
            group_info = InfoHelper.get_group_info_by_namespace(namespace)
            if group_info:
                namespace_data[namespace_key] = group_info
        
        return namespace_data
    
    @staticmethod
    def get_hair_pass_info():
        #type:(...)->dict
        loaded_refs = InfoHelper.get_selected_references()
        
        if not loaded_refs:
            print("未找到已勾选的引用")
            return {}

        all_namespaces = set()
        for ref_path in loaded_refs:
            try:
                ref_name = os.path.basename(ref_path)
                print("\n处理引用: {}".format(ref_name))

                namespaces = InfoHelper.get_reference_namespaces(ref_path)
                if namespaces:
                    print("  找到名称空间: {}".format(", ".join(namespaces)))
                    all_namespaces.update(namespaces)
                else:
                    print("  未找到有效的名称空间")
                    
            except Exception as e:
                print("  处理引用时出错: {}".format(str(e)))
                continue
        
        all_data = InfoHelper.process_all_namespaces(list(all_namespaces))
        
        return all_data
