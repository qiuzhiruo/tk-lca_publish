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

import os,sys
import traceback
import pymel.core as pm
import maya.cmds as cmds
import json
import string
import production.make_extra_data_dirs.make_extraData_dirs as medd;reload(medd)
sys.path.insert(0, os.path.join(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')), 'ani'))
import flg_note_to_gas_artist as fntga;reload(fntga)
import publish_process.ani.create_write_extra_data as pass_helper
reload(pass_helper)
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
                /mnt/proj/projects/lrs/shot/z99/z99996/flo/publish/z99996.flo.final_layout.v007/extra_data
            ### shot_assets_pass.json ### only pub : check,ds
            extra_data_pass_shot = 
                {
                    "z99996": {
                        "wang_wife": {
                            "lookPass": "lookPass not find", 
                            "rigPass": "rig_pass not find"
                        }, 
                        "nxq_niexiaoqian": {
                            "rigPass": "default | suture", 
                            "lookPass": "h30_darn_hurt", 
                            "rigPass_frame": "1002.0 | 1004.0"
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
            # 创建 flo 的版本文件夹
            self.dialog.version_dir = self.dialog.publish_root + '/' + self.dialog.version_name
            if not os.path.isdir(self.dialog.version_dir):
                os.makedirs(self.dialog.version_dir)
            
            print 
            print 
            # 创建 flo 的 extra_data_dirs
            try:
                os.chmod(self.dialog.version_dir, 0777)
            except:
                pass
            extra_data_dir_shot = medd.make_rough_lay_extra_data_dirs(self.dialog.version_dir)

            if self.dialog.step['name'] == 'flo' and self.dialog.entity_type == 'Shot' and self.dialog.task['name'] == 'final_layout' and self.dialog.ui.comboBox_publish_mode.currentIndex() == 1:
                
                shot_name = self.dialog.entity['name']

                extra_data_pass_shot = {} # 新增记录 ani 阶段输出镜头内的 资产的 pass 信息

                extra_data_hair_pass_info = pass_helper.InfoHelper.get_hair_pass_info() #type:dict
                self.write_extra_data(extra_data_dir_shot,extra_data_hair_pass_info,'lookdiff_3_hair_info.json')

                extra_data_pass_shot[shot_name] = {}

                extra_data_pass_shot = self.write_shot_assets_pass(shot_name,extra_data_dir_shot,extra_data_pass_shot)

                self.write_extra_data(extra_data_dir_shot,extra_data_pass_shot,'shot_assets_pass.json')

                extra_data_sceneAssembly_shot = {} # 新增记录 ani 阶段输出镜头内的 sceneAssembly 的 显示隐藏 信息

                extra_data_sceneAssembly_shot = self.write_shot_sceneAssembly_visibility(shot_name,extra_data_dir_shot,extra_data_sceneAssembly_shot)

                self.write_extra_data(extra_data_dir_shot,extra_data_sceneAssembly_shot,'shot_sceneAssembly_visibility.json')
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