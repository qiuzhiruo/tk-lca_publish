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

import ani.lca_layer_manager.functions as functions_lm;reload(functions_lm)

# lookPassName = '.lookPass'
# rigPassName = '.rigPass'
# vixCtrlName = 'visibility_ctrl'

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"在服务器上版本文件夹里创建 extra_data，输出必要信息"
        self.description = u"在服务器上版本文件夹里创建 extra_data，输出 seq_shot_start/end_frame，输出 shot 内的 asset "
        return


    def proceed(self):
        '''
            extra_data_dir_shot =
                /mnt/proj/projects/lrs/shot/z99/z99997/lay/publish/z99997.lay.rough_layout.v064/extra_data
            ### seq_shot_start_end_frame.json ### only pub : daily ds
            extra_data_shot =
                {
                    "z99997": {
                        "seq_end_frame": 117.0, 
                        "seq_start_frame": 18.0
                    }
                }
            ### seq_shot_assets_pass.json ### only pub : ds
            extra_data_pass_shot = 
                {
                    "z99997": {
                        "wang_wife": {
                            "lookPass": "default", 
                            "rigPass": "\u89d2\u8272 \u65e0 rigPass \u6548\u679c"
                        }, 
                        "nxq_niexiaoqian": {
                            "lookPass": "h30_darn_hurt | h50_slap", 
                            "rigPass": "suture", 
                            "lookPass_frame": "67.0 | 75.0"
                        }
                    }
                }
            
            extra_data_dir_seq = 
                /mnt/proj/projects/lrs/preproduction/z99/story/lay/publish/z99.lay.rough_layout_a.v064/extra_data
            ### seq_shot_assets.json ### only pub : daily ds
            extra_data_seq = 
                {
                    "z99996": {
                        "chr": [
                            "wang_wife", 
                            "nxq_niexiaoqian"
                        ]
                    }, 
                    "z99997": {
                        "chr": [
                            "wang_wife", 
                            "nxq_niexiaoqian"
                        ], 
                        "prp": [
                            "bazaar_pear_pits"
                        ]
                    }
                }
            ### seq_shot_assets_pass.json ### only pub : ds
            extra_data_pass_seq =
                {
                    "z99996": {
                        "wang_wife": {
                            "lookPass": "default", 
                            "rigPass": "\u89d2\u8272 \u65e0 rigPass \u6548\u679c"
                        }, 
                        "nxq_niexiaoqian": {
                            "rigPass": "default | suture", 
                            "lookPass": "h30_darn_hurt", 
                            "rigPass_frame": "2.0 | 4.0"
                        }
                    }, 
                    "z99997": {
                        "wang_wife": {
                            "lookPass": "default", 
                            "rigPass": "\u89d2\u8272 \u65e0 rigPass \u6548\u679c"
                        }, 
                        "nxq_niexiaoqian": {
                            "lookPass": "h30_darn_hurt | h50_slap", 
                            "rigPass": "suture", 
                            "lookPass_frame": "67.0 | 75.0"
                        }
                    }
                }
        '''
        try:
            # 创建 rough lay 的版本文件夹
            self.dialog.version_dir = self.dialog.publish_root + '/' + self.dialog.version_name
            if not os.path.isdir(self.dialog.version_dir):
                os.makedirs(self.dialog.version_dir)
            
            # 创建 seq 的 extra_data_dirs
            extra_data_dir_seq = medd.make_rough_lay_extra_data_dirs(self.dialog.version_dir)

            extra_data_seq = {} # 新增记录 rough lay 阶段输出每个镜头内的 资产 信息

            extra_data_pass_seq = {} # 新增记录 rough lay 阶段输出每个镜头内的 资产的 pass 信息

            # 循环每一个镜头 输出 shot 在 seq 里面的 seq_shot_start/end_frame，并记录，shot 内的 asset
            for data in self.dialog.shots_preview_data:
                data['version_name'] = '%s.lay.rough_layout.v%s' % (data['shot_info']['code'],
                                                                    self.dialog.version_num)
                data['version_dir'] = os.path.join(data['publish_root'],
                                                   data['version_name'])
                if not os.path.isdir(data['version_dir']):
                    os.makedirs(data['version_dir'])

                
                shot_node = pm.nt.Shot(data['shot_node'])
                shot_name = data['shot_info']['code']

                # 创建 shot 的 extra_data_dirs
                print
                print '   start make_rough_lay_shot_extra_data_dirs',shot_name
                extra_data_dir_shot = medd.make_rough_lay_extra_data_dirs(data['version_dir'])
                print '   end make_rough_lay_shot_extra_data_dirs',shot_name
                print

                # 新增记录 rough lay 阶段输出每个 shot 在 lay 文件里面的原始帧范围的 起始 和 结束 帧（这里无论lay趴多少镜头，只写趴出来的镜头就好
                self.write_seq_shot_start_end_frame(shot_node,shot_name,extra_data_dir_shot)

                #################
                # 增加判定，rough lay，pub daily 不进行写出 单个镜头 角色 pass 信息，只有 pub ds 时才写出
                #################
                if self.dialog.step['name'] == 'lay' and self.dialog.ui.comboBox_publish_mode.currentIndex()==1:
                    # 新增记录 rough lay 阶段输出每个镜头内的 资产的 pass 信息:此处针对 rough lay 每一个镜头
                    extra_data_pass_shot = {}
                    extra_data_pass_shot[shot_name] = {}
                    extra_data_pass_shot = self.write_seq_shot_assets_pass(shot_node,shot_name,extra_data_dir_shot,extra_data_pass_shot)
                    self.write_rough_lay_extra_data(extra_data_dir_shot,extra_data_pass_shot,'seq_shot_assets_pass.json')

                    # 新增记录镜头内摆位置的asb紫环信息
                    extra_data_asb_move = self.get_asb_root_con()
                    self.write_rough_lay_extra_data(extra_data_dir_shot, extra_data_asb_move, 'asb_root_con.json')
                
                # 新增记录 rough 阶段输出镜头内的 sceneAssembly 的 显示隐藏 信息
                extra_data_sceneAssembly_shot = {}
                extra_data_sceneAssembly_shot = self.write_shot_sceneAssembly_visibility(shot_name,extra_data_dir_shot,extra_data_sceneAssembly_shot)
                self.write_rough_lay_extra_data(extra_data_dir_shot,extra_data_sceneAssembly_shot,'shot_sceneAssembly_visibility.json')

            # 此处写出所有镜头，避免lay只趴一个镜头，输出的信息不全，影响后面检测镜头内角色的pass
            for shot_node in pm.general.ls(exactType='shot'):
                shot_name = shot_node.name().split('_')[0]
                if cmds.objExists(shot_name+'_cam'):
                    # 新增记录 rough lay 阶段输出每个镜头内的 资产 信息
                    extra_data_seq[shot_name] = {}
                    extra_data_seq = self.write_seq_shot_assets(shot_node,shot_name,extra_data_dir_seq,extra_data_seq)
                    #################
                    # 增加判定，rough lay，pub daily 不进行写出 所有镜头 角色 pass 信息，只有 pub ds 时才写出
                    #################
                    if self.dialog.step['name'] == 'lay' and self.dialog.ui.comboBox_publish_mode.currentIndex()==1:
                        # 新增记录 rough lay 阶段输出每个镜头内的 资产的 pass 信息:此处针对 rough lay 所有镜头
                        extra_data_pass_seq[shot_name] = {}
                        extra_data_pass_seq = self.write_seq_shot_assets_pass(shot_node,shot_name,extra_data_dir_seq,extra_data_pass_seq)

            # 输出 seq 内 shot 内的 asset 信息
            # print extra_data_seq # {u'z99996': {'chr': [u'wangcheng']}, u'z99997': {'chr': [u'wangcheng']}}
            self.write_rough_lay_extra_data(extra_data_dir_seq,extra_data_seq,'seq_shot_assets.json')

            #################
            # 增加判定，rough lay，pub daily 不进行写出 所有镜头 角色 pass 信息，只有 pub ds 时才写出
            #################
            if self.dialog.step['name'] == 'lay' and self.dialog.ui.comboBox_publish_mode.currentIndex()==1:
                # 输出 seq 内 shot 内的 asset 的 pass 信息
                self.write_rough_lay_extra_data(extra_data_dir_seq,extra_data_pass_seq,'seq_shot_assets_pass.json')
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

    # 新增记录 rough lay 阶段输出每个 shot 在 lay 文件里面的原始帧范围的 起始 和 结束 帧（这里无论lay趴多少镜头，只写趴出来的镜头就好
    def write_seq_shot_start_end_frame(self,shot_node,shot_name,extra_data_dir_shot):
        extra_data_shot = {}
        extra_data_shot[shot_name] = {}
        seq_start_frame = shot_node.getSequenceStartTime()
        seq_end_frame = shot_node.getSequenceEndTime()
        extra_data_shot[shot_name]['seq_start_frame'] = seq_start_frame
        extra_data_shot[shot_name]['seq_end_frame'] = seq_end_frame
        
        print
        print '   start write_rough_lay_shot_extra_data',shot_name
        self.write_rough_lay_extra_data(extra_data_dir_shot,extra_data_shot,'seq_shot_start_end_frame.json')
        print '   end write_rough_lay_shot_extra_data',shot_name
        print

    # 新增记录 rough lay 阶段输出每个镜头内的 资产 信息
    def write_seq_shot_assets(self,shot_node,shot_name,extra_data_dir_seq,extra_data_seq):
        
        seq_start_frame = shot_node.getSequenceStartTime()
        seq_end_frame = shot_node.getSequenceEndTime()

        # print shot_node,shot_name,seq_start_frame,seq_end_frame # z99997_shot z99997 18.0 117.0

        # 加载 插件
        if not pm.pluginInfo('frustumSelection', query=True, loaded=True):
            pm.loadPlugin('frustumSelection')
        # 获取 shot 在 自己帧范围内的 asset
        shot_cam = shot_name+'_cam'
        pm.select(shot_cam)
        items = pm.frustumSelection(viewportWidth=2048, viewportHeight=858,
                                    startFrame=seq_start_frame, endFrame=seq_end_frame, invert=False)
        items = list(set(items))
        masters_in_frustum = functions_lm.getMastersFromNodes(items, verbose = False)
        masters_in_frustum = pm.ls(masters_in_frustum, referencedNodes=True)
        # 将每一个 shot 内的 asset 组装进 字典
        if masters_in_frustum != []:
            asset_types = []
            asset_namespaces = []

            # assets = list(set([m.split(':')[0].rstrip(string.digits) for m in masters_in_frustum]))
            for m in masters_in_frustum:
                asset_namespace = m.split(':')[0]
                asset_name = asset_namespace.rstrip(string.digits)

                aseet_type = self.dialog.sg.find_one("Asset",[['project', 'is', self.dialog.project],
                                                                            ['code', 'is', asset_name]],['sg_asset_type'])['sg_asset_type']
                # z99997_shot z99997 z99997_cam 18.0 117.0 wangcheng {'sg_asset_type': 'chr', 'type': 'Asset', 'id': 26641}
                # print shot_node,shot_name,shot_cam,seq_start_frame,seq_end_frame,asset_name,aseet_type
                asset_namespaces.append(asset_namespace)
                asset_types.append(aseet_type)
            # 
            for i in set(asset_types):
                extra_data_seq[shot_name][i]=[]
            # 
            for r in range(len(asset_namespaces)):
                extra_data_seq[shot_name][asset_types[r]].append(asset_namespaces[r])

        return extra_data_seq

    # 新增记录 rough lay 阶段输出每个镜头内的 资产的 pass 信息
    def write_seq_shot_assets_pass(self,shot_node,shot_name,extra_data_dir_seq,extra_data_pass_seq):
        shot_cam = shot_name+'_cam'
        allAttrs = cmds.listAttr(shot_cam)
        print 'lca_shot_chr_pass' in allAttrs
        # 此处增加判定，防止 rough 第一次 publish 时如果不选择所有镜头，有些镜头相机上是没有记录信息的
        if 'lca_shot_chr_pass' in allAttrs:
            shot_pass_dict = eval(cmds.getAttr(shot_cam+'.lca_shot_chr_pass'))
        else:
            shot_pass_dict = {}
        extra_data_pass_seq[shot_name] = shot_pass_dict
        return extra_data_pass_seq

    # 写出 extra_data 到 json
    def write_rough_lay_extra_data(self,extra_data_dir,extra_data,json_name):
        
        extra_data_json = os.path.join(extra_data_dir,json_name).replace('\\','/')

        self._writeJson(extra_data_json,extra_data)

    def _writeJson(self, jsonPath, json_dict):
        try:
            extra_data_dir = os.path.dirname(jsonPath)
            os.system("chmod 777 -R %s" % extra_data_dir)
            os.chmod(extra_data_dir, 0777)
            #[NOTE]:publish经常有无权限的错误，这里给jsonpath 解锁
            os.system("chmod 777 -R %s" % jsonPath)
            os.chmod(jsonPath, 0777)
        except Exception as e:
            print(e)
        with open(jsonPath, 'w') as json_file:
            json_file.write(json.dumps(json_dict, indent=4))

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
                            asb_move_json[c.split('|')[-1]] = {'asbname': asb_name, 'purple_con_name': c,
                                                'transform': {'t': c_t, 'r': c_r, 's': c_s, 'm': c_m}}
        return asb_move_json

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
