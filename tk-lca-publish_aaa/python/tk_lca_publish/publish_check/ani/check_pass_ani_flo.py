# -*- coding: utf-8 -*-
import pymel.core as pm
import maya.mel as mel
import maya.cmds as cmds
import json
import platform
import platform
import os
from sgtk.platform.qt import QtCore, QtGui

import string


class TposeFrame():
    def __init__(self):
        self.__debug = False
        self.lca_shot_lookPass_attr = 'lca_lookPass_%s'
        self.lca_shot_rigPass_attr = 'lca_rigPass_%s'

        self.lca_sure_lookPass_attr = 'lca_sure_lookPass_%s'
        self.lca_sure_rigPass_attr = 'lca_sure_rigPass_%s'

        self.lca_shot_pass_attr = 'lca_shot_chr_pass'
    # 实例化各个控件
    def aa(self,grp_tab,allRoughShotAssetDict,key,dialog,buttonKeys):
        self.dialog = dialog
        self.proj = self.dialog.project['name'].lower()
        self.seq = self.dialog.entity['name'][:3]
        
        if key:
            print '[key --- ]',key

            # 创建 shot 内 每个角色 的 look pass 控件显示
            if '_asset_lookpass' in key:
                asset_name = key.split('_asset_')[0]
                shot_name = key.split('_')[-1]

                #角色按钮
                self.look_pass_chr_button = QtGui.QPushButton(grp_tab)
                self.look_pass_chr_button.setText(asset_name)
                self.look_pass_chr_button.setGeometry(QtCore.QRect(10, 20+30*(buttonKeys.index(key)), 140, 25))
                
                #注释按钮
                self.look_pass_button = QtGui.QPushButton(grp_tab)
                self.look_pass_button.setText(u"文件内 lookPass ->")
                self.look_pass_button.setGeometry(QtCore.QRect(155, 20+30*(buttonKeys.index(key)),100, 25))
                self.look_pass_button.setStyleSheet("background:rgba(0,0,0,0);border:0px solid rgba(0,0,0,0);color:rgb(170,170,170)")
                # pass lineEdit
                self.look_pass_lineEdit = QtGui.QLineEdit(grp_tab)
                self.look_pass_lineEdit.setAlignment(QtCore.Qt.AlignHCenter)

                self.look_pass_lineEdit.setText(allRoughShotAssetDict[shot_name][asset_name]['lookPass']['name'])
                self.look_pass_lineEdit.setGeometry(QtCore.QRect(260, 20+30*(buttonKeys.index(key)), 140, 25))
                self.look_pass_lineEdit.setEnabled(False)
                self.look_pass_lineEdit.setStyleSheet("color:rgb(255,255,0)")
                self.look_pass_lineEdit.setValidator(QtGui.QIntValidator())

                if ' not find' in allRoughShotAssetDict[shot_name][asset_name]['lookPass']['name']:
                    self.look_pass_lineEdit.setText(u'角色 无 lookPass 效果')
                    self.look_pass_lineEdit.setStyleSheet("color:rgb(255,0,0)")
                
                #注释按钮
                self.look_pass_button_sg = QtGui.QPushButton(grp_tab)
                self.look_pass_button_sg.setText(u"SG lookPass ->")
                self.look_pass_button_sg.setGeometry(QtCore.QRect(405, 20+30*(buttonKeys.index(key)),90, 25))
                self.look_pass_button_sg.setStyleSheet("background:rgba(0,0,0,0);border:0px solid rgba(0,0,0,0);color:rgb(170,170,170)")
                # pass lineEdit
                self.look_pass_lineEdit_sg = QtGui.QLineEdit(grp_tab)
                self.look_pass_lineEdit_sg.setAlignment(QtCore.Qt.AlignHCenter)

                if allRoughShotAssetDict[shot_name][asset_name]['sg_lookPass']:
                    self.look_pass_lineEdit_sg.setText(allRoughShotAssetDict[shot_name][asset_name]['sg_lookPass'])
                    self.look_pass_lineEdit_sg.setStyleSheet("color:rgb(255,255,0)")
                else:
                    self.look_pass_lineEdit_sg.setText(u'角色 无 lookPass link')
                    self.look_pass_lineEdit_sg.setStyleSheet("color:rgb(255,0,0)")
                self.look_pass_lineEdit_sg.setGeometry(QtCore.QRect(500, 20+30*(buttonKeys.index(key)), 140, 25))
                self.look_pass_lineEdit_sg.setEnabled(False)
                self.look_pass_lineEdit_sg.setValidator(QtGui.QIntValidator())

                # 点击角色按钮，更新界面内 单个角色的 lookPass，并更改界面颜色显示
                self.look_pass_chr_button.clicked.connect(lambda : self.updateAssetLookPass(self.look_pass_chr_button,self.look_pass_button,self.look_pass_lineEdit,self.look_pass_button_sg,self.look_pass_lineEdit_sg,self.dialog,self.proj,shot_name))
                
                return self.look_pass_chr_button,self.look_pass_button,self.look_pass_lineEdit,self.look_pass_button_sg,self.look_pass_lineEdit_sg
            # 创建 shot 内 每个角色 的 rig pass 控件显示
            if '_asset_rigpass' in key:
                asset_name = key.split('_asset_')[0]
                shot_name = key.split('_')[-1]

                #角色按钮
                self.rig_pass_chr_button = QtGui.QPushButton(grp_tab)
                self.rig_pass_chr_button.setText(asset_name)
                self.rig_pass_chr_button.setGeometry(QtCore.QRect(10, 20+30*(buttonKeys.index(key)), 140, 25))
                
                #注释按钮
                self.rig_pass_button = QtGui.QPushButton(grp_tab)
                self.rig_pass_button.setText(u"文件内 rigPass  ->")
                self.rig_pass_button.setGeometry(QtCore.QRect(155, 20+30*(buttonKeys.index(key)),100, 25))
                self.rig_pass_button.setStyleSheet("background:rgba(0,0,0,0);border:0px solid rgba(0,0,0,0);color:rgb(170,170,170)")

                # pass lineEdit
                self.rig_pass_lineEdit = QtGui.QLineEdit(grp_tab)
                self.rig_pass_lineEdit.setAlignment(QtCore.Qt.AlignHCenter)

                self.rig_pass_lineEdit.setText(allRoughShotAssetDict[shot_name][asset_name]['rigPass']['name'])
                self.rig_pass_lineEdit.setGeometry(QtCore.QRect(260, 20+30*(buttonKeys.index(key)), 140, 25))
                self.rig_pass_lineEdit.setEnabled(False)
                self.rig_pass_lineEdit.setStyleSheet("color:rgb(255,255,0)")
                self.rig_pass_lineEdit.setValidator(QtGui.QIntValidator())

                if ' not find' in allRoughShotAssetDict[shot_name][asset_name]['rigPass']['name']:
                    self.rig_pass_lineEdit.setText(u'角色 无 rigPass 效果')
                    self.rig_pass_lineEdit.setStyleSheet("color:rgb(255,0,0)")

                #注释按钮
                self.rig_pass_button_sg = QtGui.QPushButton(grp_tab)
                self.rig_pass_button_sg.setText(u"SG rigPass ->")
                self.rig_pass_button_sg.setGeometry(QtCore.QRect(405, 20+30*(buttonKeys.index(key)),90, 25))
                self.rig_pass_button_sg.setStyleSheet("background:rgba(0,0,0,0);border:0px solid rgba(0,0,0,0);color:rgb(170,170,170)")
                # pass lineEdit
                self.rig_pass_lineEdit_sg = QtGui.QLineEdit(grp_tab)
                self.rig_pass_lineEdit_sg.setAlignment(QtCore.Qt.AlignHCenter)
                if allRoughShotAssetDict[shot_name][asset_name]['sg_rigPass']:
                    self.rig_pass_lineEdit_sg.setText(allRoughShotAssetDict[shot_name][asset_name]['sg_rigPass'])
                    self.rig_pass_lineEdit_sg.setStyleSheet("color:rgb(255,255,0)")
                else:
                    self.rig_pass_lineEdit_sg.setText(u'角色 无 rigPass link')
                    self.rig_pass_lineEdit_sg.setStyleSheet("color:rgb(255,0,0)")
                self.rig_pass_lineEdit_sg.setGeometry(QtCore.QRect(500, 20+30*(buttonKeys.index(key)), 140, 25))
                self.rig_pass_lineEdit_sg.setEnabled(False)
                self.rig_pass_lineEdit_sg.setValidator(QtGui.QIntValidator())

                # 点击角色按钮，更新界面内 单个角色的 rigPass，并更改界面颜色显示
                self.rig_pass_chr_button.clicked.connect(lambda : self.updateAssetRigPass(self.rig_pass_chr_button,self.rig_pass_button,self.rig_pass_lineEdit,self.rig_pass_button_sg,self.rig_pass_lineEdit_sg,self.dialog,self.proj,shot_name))

                return self.rig_pass_chr_button,self.rig_pass_button,self.rig_pass_lineEdit,self.rig_pass_button_sg,self.rig_pass_lineEdit_sg
        # 创建 全部确认 控件显示
        else:
            # 添加 全部确认 按钮
            self.sure_button = QtGui.QPushButton(grp_tab)
            self.sure_button.setText(u"全部确认")
            self.sure_button.setGeometry(QtCore.QRect(10, 20+30*0,80, 25))
            self.sure_button.setStyleSheet("color:rgb(0,255,255)")

            self.sure_chr_button = QtGui.QPushButton(grp_tab)
            self.sure_chr_button.setText(u"!!! 请 确认 全部的 资产 pass 使用情况 !!!")
            self.sure_chr_button.setGeometry(QtCore.QRect(95, 20+30*0,533, 25))
            self.sure_chr_button.setStyleSheet("background:rgba(0,0,0,0);border:0px solid rgba(0,0,0,0);color:rgb(255,255,0)")

            return self.sure_button,self.sure_chr_button,None,None,None
        
    # 用来获取所有 ref node
    def all_refs(self):
        allRefNodes_ = pm.ls(rf=1)
        allRefNodes = []
        for ref in allRefNodes_:
            if ref.referenceFile():
                if ref.isLoaded():
                    ref_name = ref.name()
                    allRefNodes.append(ref_name)
        return allRefNodes

    # 点击角色按钮，更新界面内 单个角色的 lookPass，并更改界面颜色显示
    def updateAssetLookPass(self,look_pass_chr_button,look_pass_button,look_pass_lineEdit,look_pass_button_sg,look_pass_lineEdit_sg,dialog,proj_name,shot_name):
        print 'shot_name >>>',shot_name
        shotAsset = look_pass_chr_button.text()

        visib_Ctrl = shotAsset+':visibility_ctrl' # wangcheng:visibility_ctrl
        # 判断角色是否有 visibility_ctrl
        if pm.objExists(visib_Ctrl):
            cmds.select(visib_Ctrl)
        
        shot_entity = dialog.sg.find_one('Shot', [['project', 'name_is', proj_name], ['code', 'is', shot_name]], ['code','sg_cut_in','sg_cut_out','sg_ani_cut_in','sg_ani_cut_out'])
        # 再 重新获取 角色 的 lookPass 写在控件上
        new_look_pass_dict = self.getAssetPass(shot_entity,shotAsset,'lookPass')
        # print new_look_pass_dict
        look_pass_lineEdit.setText(new_look_pass_dict['name'])
        look_pass_lineEdit.setStyleSheet("color:rgb(255,255,0)")
        if ' not find' in new_look_pass_dict['name']:
            look_pass_lineEdit.setText(u'角色 无 lookPass 效果')
            look_pass_lineEdit.setStyleSheet("color:rgb(255,0,0)")
            new_look_pass_dict['name'] = u'角色 无 lookPass 效果'
        # 同步更新 shot 节点下的 pass 属性信息
        self.write_shot_pass_mes(shot_name,shotAsset,'lookPass',new_look_pass_dict,dialog)
        
        # 设置重新检查后的颜色，并更新 visibility_ctrl 里面的属性值
        look_pass_chr_button.setStyleSheet("color:rgb(255,255,255)")
        look_pass_button.setStyleSheet("background:rgba(0,0,0,0);border:0px solid rgba(0,0,0,0);color:rgb(170,170,170)")
        look_pass_button_sg.setStyleSheet("background:rgba(0,0,0,0);border:0px solid rgba(0,0,0,0);color:rgb(170,170,170)")
        
        visib_Ctrl = shotAsset+':visibility_ctrl'
        allAttrs = cmds.listAttr(visib_Ctrl)

        shot_lookPass_attr = self.lca_shot_lookPass_attr % shot_name
        sure_lookPass_attr = self.lca_sure_lookPass_attr % shot_name
        if shot_lookPass_attr not in allAttrs:
            cmds.addAttr(visib_Ctrl, ln=shot_lookPass_attr, dt='string')
        if sure_lookPass_attr not in allAttrs:
            cmds.addAttr(visib_Ctrl, ln=sure_lookPass_attr, dt='string')
        cmds.setAttr(visib_Ctrl+'.'+shot_lookPass_attr,look_pass_lineEdit.text(),type='string')
        cmds.setAttr(visib_Ctrl+'.'+sure_lookPass_attr,'0',type='string')

    # 点击角色按钮，更新界面内 单个角色的 rigPass，并更改界面颜色显示
    def updateAssetRigPass(self,rig_pass_chr_button,rig_pass_button,rig_pass_lineEdit,rig_pass_button_sg,rig_pass_lineEdit_sg,dialog,proj_name,shot_name):

        shotAsset = rig_pass_chr_button.text()

        visib_Ctrl = shotAsset+':visibility_ctrl' # wangcheng:visibility_ctrl
        # 判断角色是否有 visibility_ctrl
        if pm.objExists(visib_Ctrl):
            cmds.select(visib_Ctrl)
        
        shot_entity = dialog.sg.find_one('Shot', [['project', 'name_is', proj_name], ['code', 'is', shot_name]], ['code','sg_cut_in','sg_cut_out','sg_ani_cut_in','sg_ani_cut_out'])
        # 再 重新获取 角色 的 rigpass 写在控件上
        new_rig_pass_dict = self.getAssetPass(shot_entity,shotAsset,'rigPass')
        # print new_rig_pass_dict
        rig_pass_lineEdit.setText(new_rig_pass_dict['name'])
        rig_pass_lineEdit.setStyleSheet("color:rgb(255,255,0)")
        if ' not find' in new_rig_pass_dict['name']:
            rig_pass_lineEdit.setText(u'角色 无 rigPass 效果')
            rig_pass_lineEdit.setStyleSheet("color:rgb(255,0,0)")
            new_rig_pass_dict['name'] = u'角色 无 rigPass 效果'
        # 同步更新 shot 节点下的 pass 属性信息
        self.write_shot_pass_mes(shot_name,shotAsset,'rigPass',new_rig_pass_dict,dialog)

        rig_pass_chr_button.setStyleSheet("color:rgb(255,255,255)")
        rig_pass_button.setStyleSheet("background:rgba(0,0,0,0);border:0px solid rgba(0,0,0,0);color:rgb(170,170,170)")
        rig_pass_button_sg.setStyleSheet("background:rgba(0,0,0,0);border:0px solid rgba(0,0,0,0);color:rgb(170,170,170)")

        visib_Ctrl = shotAsset+':visibility_ctrl'
        allAttrs = cmds.listAttr(visib_Ctrl)
        
        shot_rigPass_attr = self.lca_shot_rigPass_attr % shot_name
        sure_rigPass_attr = self.lca_sure_rigPass_attr % shot_name

        if shot_rigPass_attr not in allAttrs:
            cmds.addAttr(visib_Ctrl, ln=shot_rigPass_attr, dt='string')
        if sure_rigPass_attr not in allAttrs:
            cmds.addAttr(visib_Ctrl, ln=sure_rigPass_attr, dt='string')

        cmds.setAttr(visib_Ctrl+'.'+shot_rigPass_attr,rig_pass_lineEdit.text(),type='string')
        cmds.setAttr(visib_Ctrl+'.'+sure_rigPass_attr,'0',type='string')
    
    # 更新界面内 单个角色的 sg lookPass，并更改界面颜色显示
    def updateAssetLookPass_sg(self,look_pass_chr_button,look_pass_button,look_pass_lineEdit,look_pass_button_sg,look_pass_lineEdit_sg,dialog,proj_name,shot_name):
        # shot_name = look_pass_shot_button.text()
        shotAsset = look_pass_chr_button.text()
        shotAsset_nsp = shotAsset.rstrip(string.digits)

        shot_entity_look_passes_link_dict = {}

        shot_entity = dialog.sg.find_one('Shot', [['project', 'name_is', proj_name], ['code', 'is', shot_name]], ['code','sg_rig_passes','sg_look_passes_link'])
        shot_entity_look_passes_link = shot_entity['sg_look_passes_link']
        print '*'*20,shot_name,shotAsset_nsp,shot_entity_look_passes_link
        if shot_entity_look_passes_link!=[]:
            for look_pass in shot_entity_look_passes_link:
                look_pass_link_entity = dialog.sg.find_one('CustomEntity12', [['id', 'is', int(look_pass['id'])]], ['code','shot_sg_look_passes_link_shots'])
                look_pass_assetName = look_pass_link_entity['code'].split('.')[0]
                look_pass_name = look_pass_link_entity['code'].split('.')[-1]
                shot_entity_look_passes_link_dict[look_pass_assetName]=[]
            for look_pass in shot_entity_look_passes_link:
                look_pass_link_entity = dialog.sg.find_one('CustomEntity12', [['id', 'is', int(look_pass['id'])]], ['code','shot_sg_look_passes_link_shots'])
                look_pass_assetName = look_pass_link_entity['code'].split('.')[0]
                look_pass_name = look_pass_link_entity['code'].split('.')[-1]
                shot_entity_look_passes_link_dict[look_pass_assetName].append(look_pass_name)

            if shotAsset_nsp in shot_entity_look_passes_link_dict.keys():
                if shot_entity_look_passes_link_dict[shotAsset_nsp]!=[]:
                    shot_asset_look_pass =  ''
                    for i in shot_entity_look_passes_link_dict[shotAsset_nsp]:
                        shot_asset_look_pass = shot_asset_look_pass+i+' | '
                    new_sg_lookPass = shot_asset_look_pass[:-3]

                    if new_sg_lookPass!='':
                        look_pass_lineEdit_sg.setText(new_sg_lookPass)
                        look_pass_lineEdit_sg.setStyleSheet("color:rgb(255,255,0)")
                    else:
                        look_pass_lineEdit_sg.setText(u'角色 无 lookPass link')
                        look_pass_lineEdit_sg.setStyleSheet("color:rgb(255,0,0)")
                else:
                    look_pass_lineEdit_sg.setText(u'角色 无 lookPass link')
                    look_pass_lineEdit_sg.setStyleSheet("color:rgb(255,0,0)")
            else:
                look_pass_lineEdit_sg.setText(u'角色 无 lookPass link')
                look_pass_lineEdit_sg.setStyleSheet("color:rgb(255,0,0)")
        else:
            look_pass_lineEdit_sg.setText(u'角色 无 lookPass link')
            look_pass_lineEdit_sg.setStyleSheet("color:rgb(255,0,0)")
        print '*'*20,shot_name,shotAsset_nsp,shot_entity_look_passes_link_dict
    # 更新界面内 单个角色的 rigPass，并更改界面颜色显示
    def updateAssetRigPass_sg(self,rig_pass_chr_button,rig_pass_button,rig_pass_lineEdit,rig_pass_button_sg,rig_pass_lineEdit_sg,dialog,proj_name,shot_name):
        # shot_name = rig_pass_shot_button.text()
        shotAsset = rig_pass_chr_button.text()
        shotAsset_nsp = shotAsset.rstrip(string.digits)

        shot_entity_rig_passes_dict = {}

        shot_entity = dialog.sg.find_one('Shot', [['project', 'name_is', proj_name], ['code', 'is', shot_name]], ['code','sg_rig_passes','sg_look_passes_link'])
        shot_entity_rig_passes = shot_entity['sg_rig_passes']
        print '*'*20,shot_name,shotAsset_nsp,shot_entity_rig_passes
        if shot_entity_rig_passes!=[]:
            for rig_pass in shot_entity_rig_passes:
                rig_pass_link_entity = dialog.sg.find_one('CustomEntity10', [['id', 'is', int(rig_pass['id'])]], ['code','shot_sg_rig_passes_shots','sg_attribute','sg_asset'])
                rig_pass_assetName = rig_pass_link_entity['sg_asset']['name']
                rig_pass_name = rig_pass_link_entity['sg_attribute'].split('.')[-1]
                shot_entity_rig_passes_dict[rig_pass_assetName]=[]
            for rig_pass in shot_entity_rig_passes:
                rig_pass_link_entity = dialog.sg.find_one('CustomEntity10', [['id', 'is', int(rig_pass['id'])]], ['code','shot_sg_rig_passes_shots','sg_attribute','sg_asset'])
                rig_pass_assetName = rig_pass_link_entity['sg_asset']['name']
                rig_pass_name = rig_pass_link_entity['sg_attribute'].split('.')[-1]
                shot_entity_rig_passes_dict[rig_pass_assetName].append(rig_pass_name)
            
            if shotAsset_nsp in shot_entity_rig_passes_dict.keys():
                if shot_entity_rig_passes_dict[shotAsset_nsp]!=[]:
                    shot_asset_rig_pass =  ''
                    for i in shot_entity_rig_passes_dict[shotAsset_nsp]:
                        shot_asset_rig_pass = shot_asset_rig_pass+i+' | '
                    new_sg_rigPass = shot_asset_rig_pass[:-3]

                    if new_sg_rigPass!='':
                        rig_pass_lineEdit_sg.setText(new_sg_rigPass)
                        rig_pass_lineEdit_sg.setStyleSheet("color:rgb(255,255,0)")
                    else:
                        rig_pass_lineEdit_sg.setText(u'角色 无 rigPass link')
                        rig_pass_lineEdit_sg.setStyleSheet("color:rgb(255,0,0)")
                else:
                    rig_pass_lineEdit_sg.setText(u'角色 无 rigPass link')
                    rig_pass_lineEdit_sg.setStyleSheet("color:rgb(255,0,0)")
            else:
                rig_pass_lineEdit_sg.setText(u'角色 无 rigPass link')
                rig_pass_lineEdit_sg.setStyleSheet("color:rgb(255,0,0)")
        else:
            rig_pass_lineEdit_sg.setText(u'角色 无 rigPass link')
            rig_pass_lineEdit_sg.setStyleSheet("color:rgb(255,0,0)")
        print '*'*20,shot_name,shotAsset_nsp,shot_entity_rig_passes_dict
    
    # 获取文加内 shot 内的 asset 
    def get_shot_assets(self,dialog,shot_name,extra_data_seq,all_ref_nodes):

        # 将 shot 内的 asset 组装进 字典
        if all_ref_nodes != []:
            asset_types = []
            asset_namespaces = []

            for m in all_ref_nodes:
                # 此处考虑到测试镜头会引用别的项目资产，防止查找出错
                ref_filename = pm.referenceQuery(m,f=1).replace('\\','/')
                ref_proj = ref_filename.split('/projects/')[1].split('/asset/')[0]
                ref_proj_entity = dialog.sg.find_one('Project', [['name', 'is', ref_proj.upper()]], ['name'])

                asset_namespace = pm.referenceQuery(m,ns=1)[1:]
                asset_name = asset_namespace.rstrip(string.digits)
                #[NOTE]：获取文件内的pass rra asset has namespaces
                if ":" in asset_name:
                    asset_name = str(asset_name).split(":")[-1]
                aseet_type = dialog.sg.find_one("Asset",[['project', 'is', ref_proj_entity],
                                                                            ['code', 'is', asset_name]],['sg_asset_type'])['sg_asset_type']
                # z99997_shot z99997 z99997_cam 18.0 117.0 wangcheng {'sg_asset_type': 'chr', 'type': 'Asset', 'id': 26641}
                # print shot_node,shot_name,shot_cam,seq_start_frame,seq_end_frame,asset_name,aseet_type
                if aseet_type == 'chr' or aseet_type == 'prp':
                    asset_namespaces.append(asset_namespace)
                    asset_types.append(aseet_type)
            # 
            for i in set(asset_types):
                extra_data_seq[shot_name][i]=[]
            # 
            for r in range(len(asset_namespaces)):
                extra_data_seq[shot_name][asset_types[r]].append(asset_namespaces[r])
        if self.__debug:
            print("[extra_data_seq]",extra_data_seq)
        return extra_data_seq
    # 获取当前镜头里所有角色信息
    def getShotAsset(self,dialog,all_ref_nodes,all_ref_nsps):

        try:
            pm.mel.RNdeleteUnused()
        except:
            pass
        
        proj_name = dialog.project['name'].lower() # lrs
        seq_name = dialog.entity['name'][:3] # z99
        shot_name = dialog.entity['name'] # z99996
        task_name = dialog.task['name'] # animation
        
        ###########################
        
        extra_data_seq = {}
        extra_data_seq[shot_name] = {}
        # 获取文加内 shot 内的 asset 
        extra_data_seq = self.get_shot_assets(dialog,shot_name,extra_data_seq,all_ref_nodes)

        allRoughShotAssetDict = extra_data_seq # {'z99996': {'chr': [u'nxq_niexiaoqian', u'wang_wife'], 'prp': [u'bazaar_pear_pits']}}
        # print
        # print 'allRoughShotAssetDict >',allRoughShotAssetDict
        # print
        ###########################
        # 依次获取镜头内角色的 pass 使用情况，然后重组一个字典
        new_allRoughShotAssetDict = {}
        # 重构字典，并获取 shot 内 asset 的 pass 信息
        for shotName in allRoughShotAssetDict.keys():
            shot_entity = dialog.sg.find_one('Shot', [['project', 'name_is', proj_name], ['code', 'is', shot_name]], ['code','sg_cut_in','sg_cut_out','sg_ani_cut_in','sg_ani_cut_out'])

            new_allRoughShotAssetDict[shotName]={}
            if allRoughShotAssetDict[shotName].has_key('chr'):
                shotAsstes = allRoughShotAssetDict[shotName]['chr']
                for shotAsset in shotAsstes:
                    new_allRoughShotAssetDict[shotName][shotAsset] = {}
                    new_allRoughShotAssetDict[shotName][shotAsset]['rigPass'] = self.getAssetPass(shot_entity,shotAsset,'rigPass')
                    new_allRoughShotAssetDict[shotName][shotAsset]['lookPass'] = self.getAssetPass(shot_entity,shotAsset,'lookPass')
            if allRoughShotAssetDict[shotName].has_key('prp'):
                shotAsstes = allRoughShotAssetDict[shotName]['prp']
                for shotAsset in shotAsstes:
                    new_allRoughShotAssetDict[shotName][shotAsset] = {}
                    new_allRoughShotAssetDict[shotName][shotAsset]['rigPass'] = self.getAssetPass(shot_entity,shotAsset,'rigPass')
                    new_allRoughShotAssetDict[shotName][shotAsset]['lookPass'] = self.getAssetPass(shot_entity,shotAsset,'lookPass')
            if not allRoughShotAssetDict[shotName].has_key('chr') and not allRoughShotAssetDict[shotName].has_key('prp'):
                new_allRoughShotAssetDict[shotName]=None
        # print
        # print new_allRoughShotAssetDict # {'z99996': {u'bazaar_pear_pits': {'rigPass': {'name': u'Incomplete_1', 'value': 1, 'rigPass_name': 'pear_state'}, 'lookPass': {'name': u'default', 'value': 0, 'lookPass_name': 'lookPass'}}, u'wang_wife': {'rigPass': {'name': 'pear_state attr not find', 'value': 'pear_state attr not find'}, 'lookPass': {'name': 'lookPass attr not find', 'value': 'lookPass attr not find'}}, u'nxq_niexiaoqian': {'rigPass': {'frame': '1002.0 | 1004.0', 'name': u'default | suture', 'value': '0 | 1', 'rigPass_name': 'rigPass'}, 'lookPass': {'name': u'h30_darn_hurt', 'value': 6, 'lookPass_name': 'lookPass'}}}}
        # print
        

        # 对应每一个角色，增加 LCA Pass 属性信息，记录每一个镜头的pass使用情况
        # 对应镜头，增加 LCA Pass 属性信息，记录镜头内角色的pass使用情况
        for rough_shot in new_allRoughShotAssetDict.keys():
            shot_pass_attr_dict = {}
            rough_shot_assets = new_allRoughShotAssetDict[rough_shot]
            if rough_shot_assets:
                for shot_asset in rough_shot_assets.keys():
                    print 'shot_asset ----------------',shot_asset

                    visib_Ctrl = shot_asset+':visibility_ctrl'
                    shot_pass_attr_dict[shot_asset]={}
                    if cmds.objExists(visib_Ctrl):
                        allAttrs = cmds.listAttr(visib_Ctrl)

                        shot_lookPass_attr = self.lca_shot_lookPass_attr % rough_shot
                        shot_rigPass_attr = self.lca_shot_rigPass_attr % rough_shot
                        sure_lookPass_attr = self.lca_sure_lookPass_attr % rough_shot
                        sure_rigPass_attr = self.lca_sure_rigPass_attr % rough_shot

                        if shot_lookPass_attr not in allAttrs:
                            cmds.addAttr(visib_Ctrl, ln=shot_lookPass_attr, dt='string')
                        if shot_rigPass_attr not in allAttrs:
                            cmds.addAttr(visib_Ctrl, ln=shot_rigPass_attr, dt='string')
                        if sure_lookPass_attr not in allAttrs:
                            cmds.addAttr(visib_Ctrl, ln=sure_lookPass_attr, dt='string')
                        if sure_rigPass_attr not in allAttrs:
                            cmds.addAttr(visib_Ctrl, ln=sure_rigPass_attr, dt='string')
                        
                        cmds.setAttr(visib_Ctrl+'.'+shot_lookPass_attr,new_allRoughShotAssetDict[rough_shot][shot_asset]['lookPass'],type='string')
                        cmds.setAttr(visib_Ctrl+'.'+shot_rigPass_attr,new_allRoughShotAssetDict[rough_shot][shot_asset]['rigPass'],type='string')
                        cmds.setAttr(visib_Ctrl+'.'+sure_lookPass_attr,'0',type='string')
                        cmds.setAttr(visib_Ctrl+'.'+sure_rigPass_attr,'0',type='string')
                        
                        
                        shot_pass_attr_dict[shot_asset]['lookPass'] = new_allRoughShotAssetDict[rough_shot][shot_asset]['lookPass']['name']
                        shot_pass_attr_dict[shot_asset]['rigPass'] = new_allRoughShotAssetDict[rough_shot][shot_asset]['rigPass']['name']

                        if new_allRoughShotAssetDict[rough_shot][shot_asset]['lookPass'].has_key('frame'):
                            shot_pass_attr_dict[shot_asset]['lookPass_frame'] = new_allRoughShotAssetDict[rough_shot][shot_asset]['lookPass']['frame']
                        if new_allRoughShotAssetDict[rough_shot][shot_asset]['rigPass'].has_key('frame'):
                            shot_pass_attr_dict[shot_asset]['rigPass_frame'] = new_allRoughShotAssetDict[rough_shot][shot_asset]['rigPass']['frame']

                        if ' not find' in new_allRoughShotAssetDict[rough_shot][shot_asset]['lookPass']['name']:
                            shot_pass_attr_dict[shot_asset]['lookPass'] = u'角色 无 lookPass 效果'
                        if ' not find' in new_allRoughShotAssetDict[rough_shot][shot_asset]['rigPass']['name']:
                            shot_pass_attr_dict[shot_asset]['rigPass'] = u'角色 无 rigPass 效果'
                        
                        if new_allRoughShotAssetDict[rough_shot][shot_asset]['lookPass'].has_key('lookPass_name'):
                            shot_pass_attr_dict[shot_asset]['lookPass_name'] = new_allRoughShotAssetDict[rough_shot][shot_asset]['lookPass']['lookPass_name']
                        if new_allRoughShotAssetDict[rough_shot][shot_asset]['rigPass'].has_key('rigPass_name'):
                            shot_pass_attr_dict[shot_asset]['rigPass_name'] = new_allRoughShotAssetDict[rough_shot][shot_asset]['rigPass']['rigPass_name']
                    # 这里是给道具留空，有些道具直接拿的mod，没有名牌的
                    else:
                        shot_pass_attr_dict[shot_asset]['lookPass'] = u'角色 无 lookPass 效果'
                        shot_pass_attr_dict[shot_asset]['rigPass'] = u'角色 无 rigPass 效果'

            shot_cam = rough_shot+'_cam'
            # 解锁相机，为了增加属性
            cmds.select(shot_cam)
            tops = pm.ls(sl = True)
            for top in tops:
                all = pm.listRelatives(top, allDescendents = True)
                all.append(top)
                for c in all:
                    pm.lockNode(c, lock = False)
            
            shot_allAttrs = cmds.listAttr(shot_cam)
            shot_pass_attr = self.lca_shot_pass_attr
            if shot_pass_attr not in shot_allAttrs:
                cmds.addAttr(shot_cam, ln=shot_pass_attr, dt='string')
            cmds.setAttr(shot_cam+'.'+shot_pass_attr,str(shot_pass_attr_dict),type='string')
            # 赋予 dialog 初始所有角色的 pass 信息
            dialog.shot_pass_dict = shot_pass_attr_dict
        return new_allRoughShotAssetDict
    # 获取角色在当前镜头，当前镜头时间范围内的一个key帧情况
    def getAssetPass(self,shot_entity,shotAsset,passName):

        # rig pass 可能是 rigPass 或者 rig_pass,后续统一规范为 rigPass

        # 获取 shot 节点的 起始结束帧
        if shot_entity['sg_ani_cut_in'] and shot_entity['sg_ani_cut_out']:
            seq_start_frame = shot_entity['sg_ani_cut_in'] # 18
            seq_end_frame = shot_entity['sg_ani_cut_out'] # 117
        elif shot_entity['sg_cut_in'] and shot_entity['sg_cut_out']:
            seq_start_frame = shot_entity['sg_cut_in'] # 18
            seq_end_frame = shot_entity['sg_cut_out'] # 117
        else:
            seq_start_frame = cmds.playbackOptions(q=True, min=True) # 18
            seq_end_frame = cmds.playbackOptions(q=True, max=True) # 117

        passDict = {'name':None,'value':None}
        visib_Ctrl = shotAsset+':visibility_ctrl' # wangcheng:visibility_ctrl
        print '>>> ',shotAsset
        # 判断角色是否有 visibility_ctrl
        if not pm.objExists(visib_Ctrl):
            print visib_Ctrl,'不存在'
            passDict = {'name':(visib_Ctrl +' ctrl not find'),'value':(visib_Ctrl +' ctrl not find')}
            return passDict

        visib_Ctrl_Attrs = pm.listAttr(visib_Ctrl)
        # 判断 角色是否有 传进来的 rigPass / lookPass 属性
        if passName not in visib_Ctrl_Attrs:
            if passName == 'rigPass':
                # passName = 'rig_pass'
                # if passName not in visib_Ctrl_Attrs:
                #     passName = 'pear_state'
                #     if passName not in visib_Ctrl_Attrs:
                #         passName = 'Book_open'
                #         if passName not in visib_Ctrl_Attrs:
                #             passName = 'handle_bar_state'
                #             if passName not in visib_Ctrl_Attrs:
                #                 print passName,'不存在'
                #                 passDict = {'name':(passName +' attr not find'),'value':(passName +' attr not find')}
                #                 return passDict
                
                other_passName_exists = False
                for pn in ['rigPass','rig_pass','pear_state','Book_open','handle_bar_state','RigPass','Rigpass','rig_Pass','Rig_Pass','Rig_pass','rigpass']:
                    if pn in visib_Ctrl_Attrs:
                        passName = pn
                        other_passName_exists = True
                if not other_passName_exists:
                    print passName,'不存在'
                    passDict = {'name':(passName +' attr not find'),'value':(passName +' attr not find')}
                    return passDict

            elif passName == 'lookPass':
                print passName,'不存在'
                passDict = {'name':(passName +' attr not find'),'value':(passName +' attr not find')}
                return passDict

        # 如果 是 rigPass
        if passName in ['rigPass','rig_pass','pear_state','Book_open','handle_bar_state','RigPass','Rigpass','rig_Pass','Rig_Pass','Rig_pass','rigpass']:
            passDict['rigPass_name']=passName
            # 返回 rigPass 的所有属性
            pass_Attrs = cmds.attributeQuery(passName, node=visib_Ctrl, listEnum=True)[0].split(':') # [u'default',u'fantasy',u'gourd',u'c30020',u'c90630',u'c90680',u'c90700',u'c90730',u'c10140']
            # 返回 rigPass 全称
            visib_Ctrl_pass = visib_Ctrl+'.'+passName # wangcheng:visibility_ctrl.rigPass
            # 获取 rigPass 的 父级连接，看是否是 key 帧，还是 被连接了，还是没有 key 帧 
            pass_parent = cmds.listConnections(visib_Ctrl_pass,s=1,d=0,p=1) # [u'visibility_ctrl_lookPass.output']
            # 没有 父级连接，直接获取 rigPass 的属性值
            if not pass_parent:
                print '没有 父级连接，直接获取 rigPass 属性值'
                passDict['value'] = pm.getAttr(visib_Ctrl_pass)
                passDict['name'] = pass_Attrs[passDict['value']]
                # passDict = {'name': u'c30020', 'value': 3}
            # 有 父级连接
            if pass_parent:
                print '有 父级连接'
                # 获取 父级连接 是 animCurve 类型，用来判定是否有 key 帧
                pass_parent_keyType = list(set([i for i in pass_parent if 'animCurve' in str(pm.nodeType(i))]))
                # 获取 父级连接 是否包含 lookPass，用来判定是否有 link
                pass_parent_linkType = list(set([i for i in pass_parent if 'visibility_ctrl.lookPass' in i]))
                if pass_parent_keyType!=[]:
                    print '有 父级连接，是 key 帧'
                    ctrl_parentNodes = {}
                    # 返回 rig pass key帧节点
                    if len(pass_parent_keyType) >=1:
                        for i in pass_parent:
                            if 'animCurve' in str(pm.nodeType(i)):
                                ctrl_parentNodes[i] = cmds.listConnections(i,p=1,c=1)[-1] # {u'visibility_ctrl_lookPass.output': u'wangcheng:visibility_ctrl.lookPass'}
                    key_node = [i.split('.')[0] for i in ctrl_parentNodes.keys() if ctrl_parentNodes[i]==visib_Ctrl_pass][0] # u'visibility_ctrl_lookPass'
                    # 返回当前 shot 节点 起始结束帧 之内的 key 帧
                    visib_Ctrl_pass_keyFrames = cmds.keyframe(key_node,q=1,ev=0) # [18.0, 55.0]
                    visib_Ctrl_pass_keyFrames_new = [i for i in visib_Ctrl_pass_keyFrames if i >= seq_start_frame and i <= seq_end_frame] # [55.0]
                    # 如果 当前 shot 节点 起始结束帧 之内没有 key 帧
                    if len(visib_Ctrl_pass_keyFrames_new)==0:
                        print 'shot 帧范围内没有一个 key 帧'
                        # 此时 获取 shot 起始帧的 pass 值
                        keyFrame_value = cmds.getAttr(visib_Ctrl_pass,time=seq_start_frame)
                        passDict['value'] = keyFrame_value
                        passDict['name'] = pass_Attrs[passDict['value']]
                        # passDict = {'name': u'c90680', 'value': 5}
                    # 如果 当前 shot 节点 起始结束帧 之内有 一个key 帧
                    if len(visib_Ctrl_pass_keyFrames_new)==1:
                        print 'shot 帧范围内只有一个 key 帧'
                        # 此时 获取 shot 内 key 帧的 pass 值
                        keyFrame_value = cmds.getAttr(visib_Ctrl_pass,time=visib_Ctrl_pass_keyFrames_new[0])
                        passDict['value'] = keyFrame_value
                        passDict['name'] = pass_Attrs[passDict['value']]
                        # passDict = {'name': u'c90630', 'value': 4}
                    # 如果 当前 shot 节点 起始结束帧 之内有 多个key 帧
                    if len(visib_Ctrl_pass_keyFrames_new)>1:
                        print 'shot 帧范围内有多个 key 帧'
                        values = ''
                        names = ''
                        frames = ''
                        # 此时 获取 shot 内每一个 key 帧的数值
                        for keyFrame in visib_Ctrl_pass_keyFrames_new:
                            print keyFrame
                            # keyFrame_value = cmds.getAttr(key_node+'.keyTimeValue[%s]' % visib_Ctrl_pass_keyFrames.index(keyFrame))[0] # 此处也可以获取，但是不需要获取动画曲线的，而是直接获取属性的 key 帧数值
                            keyFrame_value = cmds.getAttr(visib_Ctrl_pass,time=keyFrame)
                            print keyFrame_value
                            values = values+str(keyFrame_value)+' | '
                            names = names+pass_Attrs[keyFrame_value]+' | '
                            frames = frames+str(keyFrame) + ' | '
                        passDict['value'] = values[:-3]
                        passDict['name'] = names[:-3]
                        passDict['frame'] = frames[:-3]
                        # passDict = {'name': u'c90700 c90730', 'value': '6 7'}
                elif pass_parent_linkType!=[]:
                    print '有 父级连接，是 lookPass'
                    if '.lookPass' in pass_parent_linkType[0]:
                        print '被 lookPass link'
                        lookPass_visib_Ctrl_pass = pass_parent_linkType[0]
                        # 获取 look Pass 的 父级连接，看是否是 key 帧，还是没有 key 帧 (注意：此处与检测rigpass不同，无需再检测 lookpass 是否被关联)
                        lookPass_pass_parent = cmds.listConnections(lookPass_visib_Ctrl_pass,s=1,d=0,p=1) # [u'visibility_ctrl_lookPass.output']
                        # look pass 没有 key 帧
                        if not lookPass_pass_parent:
                            print '被 lookPass link，lookPass 没有 key 帧'
                            passDict['value'] = pm.getAttr(visib_Ctrl_pass)
                            passDict['name'] = pass_Attrs[passDict['value']]
                            # passDict = {'name': u'c30020', 'value': 3}
                        if lookPass_pass_parent:
                            # 获取 look pass parent 是 animCurve 类型，用来判定是否有 key 帧
                            lookPass_pass_parent_keyType = list(set([i for i in lookPass_pass_parent if 'animCurve' in str(pm.nodeType(i))]))
                            if lookPass_pass_parent_keyType!=[]:
                                print '被 lookPass link，lookPass 有 key 帧'
                                ctrl_parentNodes = {}
                                # 返回 look pass key帧节点
                                if len(lookPass_pass_parent_keyType) >=1:
                                    for i in lookPass_pass_parent:
                                        if 'animCurve' in str(pm.nodeType(i)):
                                            ctrl_parentNodes[i] = cmds.listConnections(i,p=1,c=1)[-1] # {u'visibility_ctrl_lookPass.output': u'wangcheng:visibility_ctrl.lookPass'}
                                key_node = [i.split('.')[0] for i in ctrl_parentNodes.keys() if ctrl_parentNodes[i]==lookPass_visib_Ctrl_pass][0] # u'visibility_ctrl_lookPass'
                                # 返回当前 shot 节点 起始结束帧 之内的 key 帧
                                visib_Ctrl_pass_keyFrames = cmds.keyframe(key_node,q=1,ev=0) # [18.0, 55.0]
                                visib_Ctrl_pass_keyFrames_new = [i for i in visib_Ctrl_pass_keyFrames if i >= seq_start_frame and i <= seq_end_frame] # [55.0]
                                # 如果 当前 shot 节点 起始结束帧 之内没有 key 帧
                                if len(visib_Ctrl_pass_keyFrames_new)==0:
                                    print '被 lookPass link，shot 帧范围内没有一个 key 帧'
                                    # 此时 获取 shot 起始帧的 pass 值
                                    keyFrame_value = cmds.getAttr(visib_Ctrl_pass,time=seq_start_frame)
                                    passDict['value'] = keyFrame_value
                                    passDict['name'] = pass_Attrs[passDict['value']]
                                    # passDict = {'name': u'c90680', 'value': 5}
                                # 如果 当前 shot 节点 起始结束帧 之内有 一个key 帧
                                if len(visib_Ctrl_pass_keyFrames_new)==1:
                                    print '被 lookPass link，shot 帧范围内只有一个 key 帧'
                                    # 此时 获取 shot 内 key 帧的 pass 值
                                    keyFrame_value = cmds.getAttr(visib_Ctrl_pass,time=visib_Ctrl_pass_keyFrames_new[0])
                                    passDict['value'] = keyFrame_value
                                    passDict['name'] = pass_Attrs[passDict['value']]
                                    # passDict = {'name': u'c90630', 'value': 4}
                                # 如果 当前 shot 节点 起始结束帧 之内有 多个key 帧
                                if len(visib_Ctrl_pass_keyFrames_new)>1:
                                    print '被 lookPass link，shot 帧范围内有多个 key 帧'
                                    values = ''
                                    names = ''
                                    frames = ''
                                    # 此时 获取 shot 内每一个 key 帧的数值
                                    for keyFrame in visib_Ctrl_pass_keyFrames_new:
                                        keyFrame_value = cmds.getAttr(visib_Ctrl_pass,time=keyFrame)
                                        values = values+str(keyFrame_value)+' | '
                                        names = names+pass_Attrs[keyFrame_value]+' | '
                                        frames = frames+str(keyFrame) + ' | '
                                    passDict['value'] = values[:-3]
                                    passDict['name'] = names[:-3]
                                    passDict['frame'] = frames[:-3]
                                    # passDict = {'name': u'c90700 c90730', 'value': '6 7'}
                            else:
                                print '被 lookPass link，lookPass 没有 key 帧'
                                passDict['value'] = pm.getAttr(visib_Ctrl_pass)
                                passDict['name'] = pass_Attrs[passDict['value']]
                                # passDict = {'name': u'c30020', 'value': 3}

                else:
                    print '有 父级 连接，无 key 帧，也不是 lookPass'
                    passDict['value'] = pm.getAttr(visib_Ctrl_pass)
                    passDict['name'] = pass_Attrs[passDict['value']]
                    # passDict = {'name': u'c30020', 'value': 3}
        # 如果 是 lookPass
        if passName == 'lookPass':
            passDict['lookPass_name']=passName
            # 返回 lookPass 的所有属性
            pass_Attrs = cmds.attributeQuery(passName, node=visib_Ctrl, listEnum=True)[0].split(':') # [u'default',u'fantasy',u'gourd',u'c30020',u'c90630',u'c90680',u'c90700',u'c90730',u'c10140']
            # 返回 lookPass 全称
            visib_Ctrl_pass = visib_Ctrl+'.'+passName # wangcheng:visibility_ctrl.lookPass
            # 获取 lookPass 的 父级连接，看是否是 key 帧，还是 被连接了，还是没有 key 帧 
            pass_parent = cmds.listConnections(visib_Ctrl_pass,s=1,d=0,p=1) # [u'visibility_ctrl_lookPass.output']
            # 没有 父级连接，直接获取 lookPass 的属性值
            if not pass_parent:
                print '没有 父级连接，直接获取 lookPass 属性值'
                passDict['value'] = pm.getAttr(visib_Ctrl_pass)
                passDict['name'] = pass_Attrs[passDict['value']]
                # passDict = {'name': u'c30020', 'value': 3}
            # 有 父级连接
            if pass_parent:
                print '有 父级连接'
                # 获取 父级连接 是 animCurve 类型，用来判定是否有 key 帧
                pass_parent_keyType = list(set([i for i in pass_parent if 'animCurve' in str(pm.nodeType(i))]))
                # 获取 父级连接 是否包含 rigPass，用来判定是否有 link
                pass_parent_linkType = list(set([i for i in pass_parent if 'visibility_ctrl.rigPass' in i or 'visibility_ctrl.rig_pass' in i ]))
                if pass_parent_keyType!=[]:
                    print '有 父级连接，是 key 帧'
                    ctrl_parentNodes = {}
                    # 返回 look pass key帧节点
                    if len(pass_parent_keyType) >=1:
                        for i in pass_parent:
                            if 'animCurve' in str(pm.nodeType(i)):
                                ctrl_parentNodes[i] = cmds.listConnections(i,p=1,c=1)[-1] # {u'visibility_ctrl_lookPass.output': u'wangcheng:visibility_ctrl.lookPass'}
                    key_node = [i.split('.')[0] for i in ctrl_parentNodes.keys() if ctrl_parentNodes[i]==visib_Ctrl_pass][0] # u'visibility_ctrl_lookPass'
                    # 返回当前 shot 节点 起始结束帧 之内的 key 帧
                    visib_Ctrl_pass_keyFrames = cmds.keyframe(key_node,q=1,ev=0) # [18.0, 55.0]
                    visib_Ctrl_pass_keyFrames_new = [i for i in visib_Ctrl_pass_keyFrames if i >= seq_start_frame and i <= seq_end_frame] # [55.0]
                    # 如果 当前 shot 节点 起始结束帧 之内没有 key 帧
                    if len(visib_Ctrl_pass_keyFrames_new)==0:
                        print 'shot 帧范围内没有一个 key 帧'
                        # 此时 获取 shot 起始帧的 pass 值
                        keyFrame_value = cmds.getAttr(visib_Ctrl_pass,time=seq_start_frame)
                        passDict['value'] = keyFrame_value
                        passDict['name'] = pass_Attrs[passDict['value']]
                        # passDict = {'name': u'c90680', 'value': 5}
                    # 如果 当前 shot 节点 起始结束帧 之内有 一个key 帧
                    if len(visib_Ctrl_pass_keyFrames_new)==1:
                        print 'shot 帧范围内只有一个 key 帧'
                        # 此时 获取 shot 内 key 帧的 pass 值
                        keyFrame_value = cmds.getAttr(visib_Ctrl_pass,time=visib_Ctrl_pass_keyFrames_new[0])
                        passDict['value'] = keyFrame_value
                        passDict['name'] = pass_Attrs[passDict['value']]
                        # passDict = {'name': u'c90630', 'value': 4}
                    # 如果 当前 shot 节点 起始结束帧 之内有 多个key 帧
                    if len(visib_Ctrl_pass_keyFrames_new)>1:
                        print 'shot 帧范围内有多个 key 帧'
                        values = ''
                        names = ''
                        frames = ''
                        # 此时 获取 shot 内每一个 key 帧的数值
                        for keyFrame in visib_Ctrl_pass_keyFrames_new:
                            print keyFrame
                            # keyFrame_value = cmds.getAttr(key_node+'.keyTimeValue[%s]' % visib_Ctrl_pass_keyFrames.index(keyFrame))[0] # 此处也可以获取，但是不需要获取动画曲线的，而是直接获取属性的 key 帧数值
                            keyFrame_value = cmds.getAttr(visib_Ctrl_pass,time=keyFrame)
                            print keyFrame_value
                            values = values+str(keyFrame_value)+' | '
                            names = names+pass_Attrs[keyFrame_value]+' | '
                            frames = frames+str(keyFrame) + ' | '
                        passDict['value'] = values[:-3]
                        passDict['name'] = names[:-3]
                        passDict['frame'] = frames[:-3]
                        # passDict = {'name': u'c90700 c90730', 'value': '6 7'}
                elif pass_parent_linkType!=[]:
                    print '有 父级连接，是 rigPass'
                    if '.rigPass' in pass_parent_linkType[0]:
                        print '被 rigPass link'
                        rigPass_visib_Ctrl_pass = pass_parent_linkType[0]
                        # 获取 rig Pass 的 父级连接，看是否是 key 帧，还是没有 key 帧 (注意：此处与检测rigpass不同，无需再检测 rigpass 是否被关联)
                        rigPass_pass_parent = cmds.listConnections(rigPass_visib_Ctrl_pass,s=1,d=0,p=1) # [u'visibility_ctrl_lookPass.output']
                        # rig pass 没有 key 帧
                        if not rigPass_pass_parent:
                            print '被 rigPass link，rigPass 没有 key 帧'
                            passDict['value'] = pm.getAttr(visib_Ctrl_pass)
                            passDict['name'] = pass_Attrs[passDict['value']]
                            # passDict = {'name': u'c30020', 'value': 3}
                        if rigPass_pass_parent:
                            # 获取 rig pass parent 是 animCurve 类型，用来判定是否有 key 帧
                            rigPass_pass_parent_keyType = list(set([i for i in rigPass_pass_parent if 'animCurve' in str(pm.nodeType(i))]))
                            if rigPass_pass_parent_keyType!=[]:
                                print '被 rigPass link，rigPass 有 key 帧'
                                ctrl_parentNodes = {}
                                # 返回 rig pass key帧节点
                                if len(rigPass_pass_parent_keyType) >=1:
                                    for i in rigPass_pass_parent:
                                        if 'animCurve' in str(pm.nodeType(i)):
                                            ctrl_parentNodes[i] = cmds.listConnections(i,p=1,c=1)[-1] # {u'visibility_ctrl_rigPass.output': u'wangcheng:visibility_ctrl.lookPass'}
                                key_node = [i.split('.')[0] for i in ctrl_parentNodes.keys() if ctrl_parentNodes[i]==rigPass_visib_Ctrl_pass][0] # u'visibility_ctrl_lookPass'
                                # 返回当前 shot 节点 起始结束帧 之内的 key 帧
                                visib_Ctrl_pass_keyFrames = cmds.keyframe(key_node,q=1,ev=0) # [18.0, 55.0]
                                visib_Ctrl_pass_keyFrames_new = [i for i in visib_Ctrl_pass_keyFrames if i >= seq_start_frame and i <= seq_end_frame] # [55.0]
                                # 如果 当前 shot 节点 起始结束帧 之内没有 key 帧
                                if len(visib_Ctrl_pass_keyFrames_new)==0:
                                    print '被 rigPass link，shot 帧范围内没有一个 key 帧'
                                    # 此时 获取 shot 起始帧的 pass 值
                                    keyFrame_value = cmds.getAttr(visib_Ctrl_pass,time=seq_start_frame)
                                    passDict['value'] = keyFrame_value
                                    passDict['name'] = pass_Attrs[passDict['value']]
                                    # passDict = {'name': u'c90680', 'value': 5}
                                # 如果 当前 shot 节点 起始结束帧 之内有 一个key 帧
                                if len(visib_Ctrl_pass_keyFrames_new)==1:
                                    print '被 rigPass link，shot 帧范围内只有一个 key 帧'
                                    # 此时 获取 shot 内 key 帧的 pass 值
                                    keyFrame_value = cmds.getAttr(visib_Ctrl_pass,time=visib_Ctrl_pass_keyFrames_new[0])
                                    passDict['value'] = keyFrame_value
                                    passDict['name'] = pass_Attrs[passDict['value']]
                                    # passDict = {'name': u'c90630', 'value': 4}
                                # 如果 当前 shot 节点 起始结束帧 之内有 多个key 帧
                                if len(visib_Ctrl_pass_keyFrames_new)>1:
                                    print '被 rigPass link，shot 帧范围内有多个 key 帧'
                                    values = ''
                                    names = ''
                                    frames = ''
                                    # 此时 获取 shot 内每一个 key 帧的数值
                                    for keyFrame in visib_Ctrl_pass_keyFrames_new:
                                        keyFrame_value = cmds.getAttr(visib_Ctrl_pass,time=keyFrame)
                                        values = values+str(keyFrame_value)+' | '
                                        names = names+pass_Attrs[keyFrame_value]+' | '
                                        frames = frames+str(keyFrame) + ' | '
                                    passDict['value'] = values[:-3]
                                    passDict['name'] = names[:-3]
                                    passDict['frame'] = frames[:-3]
                                    # passDict = {'name': u'c90700 c90730', 'value': '6 7'}
                            else:
                                print '被 rigPass link rigPass 没有 key 帧'
                                passDict['value'] = pm.getAttr(visib_Ctrl_pass)
                                passDict['name'] = pass_Attrs[passDict['value']]
                                # passDict = {'name': u'c30020', 'value': 3}

                else:
                    print '有 父级 连接，无 key 帧，也不是 rigPass'
                    passDict['value'] = pm.getAttr(visib_Ctrl_pass)
                    passDict['name'] = pass_Attrs[passDict['value']]
                    # passDict = {'name': u'c30020', 'value': 3}
        print '========================================'
        print passDict
        print '========================================'
        return passDict

    # 针对 ani 角色 pass 检查，如果没有全部确认，则无法进入下一个 pub 页面
    def getSurePassChecked(self,dialog):
        
        # shot_names = list(dialog.entity['name'])
        shot_names = dialog.entity['name']
        allVisibiCtrls = {}
        allRefNodes = self.all_refs()
        for refNode in allRefNodes:
            if cmds.referenceQuery(refNode,il=1):
                refNodeName = cmds.referenceQuery(refNode,rfn=1)
                refNodeFile = cmds.referenceQuery(refNode,f=1)
                refNodeNamespace = cmds.referenceQuery(refNode,ns=1)
                # 判定，只有1级,2级角色才符合，并且勾选 sg_is_reference_one_time
                aseet_difficulty = dialog.sg.find_one("Asset",[['project', 'is', dialog.project],
                                                                            ['code', 'is', refNodeNamespace[1:]]],['sg_diffculty2','sg_is_reference_one_time','sg_asset_type'])
                # print '>>>>>>>>>>>>>>>>>>>>>>>>>'
                # print refNodeNamespace,aseet_difficulty
                # print '>>>>>>>>>>>>>>>>>>>>>>>>>'
                if aseet_difficulty:
                    if aseet_difficulty['sg_asset_type']=='chr':
                        if aseet_difficulty['sg_diffculty2']=='1' or aseet_difficulty['sg_diffculty2']=='2':
                            if aseet_difficulty['sg_is_reference_one_time']:
                                if '/asset/chr/' in refNodeFile:
                                    visib_Ctrl = refNodeNamespace[1:]+':visibility_ctrl'

                                    allAttrs = cmds.listAttr(visib_Ctrl)
                                    lca_sure_pass_attr = [i for i in allAttrs if 'lca_sure_rigPass_' in i or 'lca_sure_lookPass_' in i]
                                    allVisibiCtrls[visib_Ctrl]={}
                                    for sure_pass_attr in lca_sure_pass_attr:
                                        # for sht_name in shot_names:
                                        if shot_names in sure_pass_attr:
                                            if 'lca_sure_rigPass_' in sure_pass_attr:
                                                allVisibiCtrls[visib_Ctrl][sure_pass_attr]=cmds.getAttr(visib_Ctrl+'.'+sure_pass_attr)
                                            if 'lca_sure_lookPass_' in sure_pass_attr:
                                                allVisibiCtrls[visib_Ctrl][sure_pass_attr]=cmds.getAttr(visib_Ctrl+'.'+sure_pass_attr)
        # print 
        # print 'allVisibiCtrls  >',allVisibiCtrls
        # print 
        return allVisibiCtrls

    # 点击全部检查：重新检查 chr-shot-pass之间的关联，并更改界面颜色显示
    def checkAllChrPass(self,all_button,dialog,proj,shot_name,sure_chr_button):

        sure_chr_button_text = ''
        sure_chr_button.setText(sure_chr_button_text)

        for key in all_button.keys():
            chr_button=all_button[key]['chr_button']
            file_pass_button=all_button[key]['file_pass_button']
            file_pass_lineEdit=all_button[key]['file_pass_lineEdit']
            sg_pass_button=all_button[key]['sg_pass_button']
            sg_pass_lineEdit=all_button[key]['sg_pass_lineEdit']

            if chr_button:

                if 'lookPass' in file_pass_button.text() and 'lookPass' in sg_pass_button.text():
                    self.updateAssetLookPass(chr_button,file_pass_button,file_pass_lineEdit,sg_pass_button,sg_pass_lineEdit,dialog,proj,shot_name)
                    self.updateAssetLookPass_sg(chr_button,file_pass_button,file_pass_lineEdit,sg_pass_button,sg_pass_lineEdit,dialog,proj,shot_name)
                if 'rigPass' in file_pass_button.text() and 'rigPass' in sg_pass_button.text():
                    self.updateAssetRigPass(chr_button,file_pass_button,file_pass_lineEdit,sg_pass_button,sg_pass_lineEdit,dialog,proj,shot_name)
                    self.updateAssetRigPass_sg(chr_button,file_pass_button,file_pass_lineEdit,sg_pass_button,sg_pass_lineEdit,dialog,proj,shot_name)
                    
                chr_button.setStyleSheet("color:rgb(0,255,255)")
                file_pass_button.setStyleSheet("background:rgba(0,0,0,0);border:0px solid rgba(0,0,0,0);color:rgb(0,255,255)")
                sg_pass_button.setStyleSheet("background:rgba(0,0,0,0);border:0px solid rgba(0,0,0,0);color:rgb(0,255,255)")

                shot_asset = chr_button.text()
                visib_Ctrl = shot_asset+':visibility_ctrl'
                allAttrs = cmds.listAttr(visib_Ctrl)

                shot_lookPass_attr = self.lca_shot_lookPass_attr % shot_name
                shot_rigPass_attr = self.lca_shot_rigPass_attr % shot_name
                sure_lookPass_attr = self.lca_sure_lookPass_attr % shot_name
                sure_rigPass_attr = self.lca_sure_rigPass_attr % shot_name

                if shot_lookPass_attr not in allAttrs:
                    cmds.addAttr(visib_Ctrl, ln=shot_lookPass_attr, dt='string')
                if shot_rigPass_attr not in allAttrs:
                    cmds.addAttr(visib_Ctrl, ln=shot_rigPass_attr, dt='string')
                if sure_lookPass_attr not in allAttrs:
                    cmds.addAttr(visib_Ctrl, ln=sure_lookPass_attr, dt='string')
                if sure_rigPass_attr not in allAttrs:
                    cmds.addAttr(visib_Ctrl, ln=sure_rigPass_attr, dt='string')

                self.compare_pass(chr_button,file_pass_button,file_pass_lineEdit,sg_pass_button,sg_pass_lineEdit,sure_chr_button,shot_asset,sure_lookPass_attr,sure_rigPass_attr)
                
    
    def compare_pass(self,chr_button,file_pass_button,file_pass_lineEdit,sg_pass_button,sg_pass_lineEdit,sure_chr_button,shot_asset,sure_lookPass_attr,sure_rigPass_attr):
         
        file_pass = file_pass_lineEdit.text().split(' | ')
        sg_pass = sg_pass_lineEdit.text().split(' | ')

        cp_file_pass = list(set(file_pass))
        cp_sg_pass = list(set(sg_pass))

        # if 'default' in file_pass:
        #     cp_file_pass.remove('default')
        # elif 'Default' in file_pass:
        #     cp_file_pass.remove('Default')
        
        for cfp in cp_file_pass:
            if cfp == 'default' or cfp == 'Default' or u'无' in cfp:
                cp_file_pass.remove(cfp)
        for csp in cp_sg_pass:
            if csp == 'default' or csp == 'Default' or u'无' in csp:
                cp_sg_pass.remove(csp)
        
        visib_Ctrl = shot_asset+':visibility_ctrl'

        if cp_file_pass != cp_sg_pass:
            chr_button.setStyleSheet("color:rgb(255,0,0)")

            sure_chr_button.setText(u'注意：请确认 标红色 的角色，文件内 pass 和 shotgun 是否一致，如有疑问，请联系 制片 和 组长')
            sure_chr_button.setStyleSheet("background:rgba(0,0,0,0);border:0px solid rgba(0,0,0,0);color:rgb(255,0,0)")
            
            if 'rigPass' in file_pass_button.text():
                cmds.setAttr(visib_Ctrl+'.'+sure_rigPass_attr,'0',type='string')
            if 'lookPass' in file_pass_button.text():
                cmds.setAttr(visib_Ctrl+'.'+sure_lookPass_attr,'0',type='string')
        else:
            if 'rigPass' in file_pass_button.text():
                cmds.setAttr(visib_Ctrl+'.'+sure_rigPass_attr,'1',type='string')
            if 'lookPass' in file_pass_button.text():
                cmds.setAttr(visib_Ctrl+'.'+sure_lookPass_attr,'1',type='string')
            


    # 同步更新 shot 节点下的 pass 属性信息
    def write_shot_pass_mes(self,shot_name,asset_name,pass_name,new_look_pass_dict,dialog):
        
        shot_cam = shot_name +'_cam'
        
        shot_pass_attr = self.lca_shot_pass_attr
        shot_allAttrs = cmds.listAttr(shot_cam)
        # 判定相机是否有 lca_shot_chr_pass 属性
        # 没有，则增加，并设置为 初始所有角色的 pass 信息
        if shot_pass_attr not in shot_allAttrs:
            # 解锁相机，为了增加属性
            cmds.select(shot_cam)
            tops = pm.ls(sl = True)
            for top in tops:
                all = pm.listRelatives(top, allDescendents = True)
                all.append(top)
                for c in all:
                    pm.lockNode(c, lock = False)
            cmds.addAttr(shot_cam, ln=shot_pass_attr, dt='string')
            cmds.setAttr(shot_cam+'.'+shot_pass_attr,str(dialog.shot_pass_dict),type='string')

        shot_pass_attr_dict = eval(cmds.getAttr(shot_cam+('.%s' % shot_pass_attr)))
        
        shot_pass_attr_dict[asset_name][pass_name] = new_look_pass_dict['name']
        if new_look_pass_dict.has_key('frame'):
            shot_pass_attr_dict[asset_name][pass_name+'_frame'] = new_look_pass_dict['frame']
        
        cmds.setAttr(shot_cam+'.'+shot_pass_attr,str(shot_pass_attr_dict),type='string')
        # 赋予 dialog 最新所有角色的 pass 信息
        dialog.shot_pass_dict = shot_pass_attr_dict
    # 增加返回角色 shotgun 上 和 shot 的 link
    def getSgAssetPassLink(self,dialog,allRoughShotAssetDict):
        
        new_allRoughShotAssetDict = allRoughShotAssetDict
        proj_name = dialog.project['name'].lower() # lrs

        for rough_shot in new_allRoughShotAssetDict.keys():
            shot_entity = dialog.sg.find_one('Shot', [['project', 'name_is', proj_name], ['code', 'is', rough_shot]], ['code','sg_rig_passes','sg_look_passes_link'])
            shot_entity_rig_passes = shot_entity['sg_rig_passes']
            shot_entity_look_passes_link = shot_entity['sg_look_passes_link']
            if self.__debug:
                print("[shot_entity_look_passes_link]",shot_entity_look_passes_link)
            shot_entity_rig_passes_dict = {}
            shot_entity_look_passes_link_dict = {}

            ###### find rig pass ######
            if shot_entity_rig_passes!=[]:
                for rig_pass in shot_entity_rig_passes:
                    rig_pass_link_entity = dialog.sg.find_one('CustomEntity10', [['id', 'is', int(rig_pass['id'])]], ['code','shot_sg_rig_passes_shots','sg_attribute','sg_asset'])
                    rig_pass_assetName = rig_pass_link_entity['sg_asset']['name']
                    rig_pass_name = rig_pass_link_entity['sg_attribute'].split('.')[-1]
                    shot_entity_rig_passes_dict[rig_pass_assetName]=[]
                for rig_pass in shot_entity_rig_passes:
                    rig_pass_link_entity = dialog.sg.find_one('CustomEntity10', [['id', 'is', int(rig_pass['id'])]], ['code','shot_sg_rig_passes_shots','sg_attribute','sg_asset'])
                    rig_pass_assetName = rig_pass_link_entity['sg_asset']['name']
                    rig_pass_name = rig_pass_link_entity['sg_attribute'].split('.')[-1]
                    shot_entity_rig_passes_dict[rig_pass_assetName].append(rig_pass_name)
            ###### find look pass ######
            if shot_entity_look_passes_link!=[]:
                for look_pass in shot_entity_look_passes_link:
                    look_pass_link_entity = dialog.sg.find_one('CustomEntity12', [['id', 'is', int(look_pass['id'])]], ['code','shot_sg_look_passes_link_shots'])
                    look_pass_assetName = look_pass_link_entity['code'].split('.')[0]
                    look_pass_name = look_pass_link_entity['code'].split('.')[-1]
                    shot_entity_look_passes_link_dict[look_pass_assetName]=[]
                for look_pass in shot_entity_look_passes_link:
                    look_pass_link_entity = dialog.sg.find_one('CustomEntity12', [['id', 'is', int(look_pass['id'])]], ['code','shot_sg_look_passes_link_shots'])
                    look_pass_assetName = look_pass_link_entity['code'].split('.')[0]
                    look_pass_name = look_pass_link_entity['code'].split('.')[-1]
                    shot_entity_look_passes_link_dict[look_pass_assetName].append(look_pass_name)
                    
                    

            rough_shot_assets = new_allRoughShotAssetDict[rough_shot]
            if rough_shot_assets:
                for shot_asset in rough_shot_assets.keys():
                    if self.__debug:
                        print("[shot_asset]",shot_asset)
                    shot_asset_nsp = shot_asset.rstrip(string.digits)
                    #[NOTE]: remove rra namespaces
                    if ":" in shot_asset:
                        shot_asset_remove_namespace = str(shot_asset).split(":")[-1]
                        shot_asset_nsp = shot_asset_remove_namespace.rstrip(string.digits)
                    
                    if shot_asset_nsp in shot_entity_rig_passes_dict.keys():
                        if shot_entity_rig_passes_dict[shot_asset_nsp]!=[]:
                            shot_asset_rig_pass =  ''
                            for i in shot_entity_rig_passes_dict[shot_asset_nsp]:
                                shot_asset_rig_pass = shot_asset_rig_pass+i+' | '
                            new_allRoughShotAssetDict[rough_shot][shot_asset]['sg_rigPass'] = shot_asset_rig_pass[:-3]
                    else:
                        new_allRoughShotAssetDict[rough_shot][shot_asset]['sg_rigPass'] = None
                    if shot_asset_nsp in shot_entity_look_passes_link_dict.keys():
                        if self.__debug:
                            print("[shot_asset_nsp]",shot_asset_nsp)
                        if shot_entity_look_passes_link_dict[shot_asset_nsp]!=[]:
                            shot_asset_look_pass =  ''
                            for i in shot_entity_look_passes_link_dict[shot_asset_nsp]:
                                shot_asset_look_pass = shot_asset_look_pass+i+' | '
                            new_allRoughShotAssetDict[rough_shot][shot_asset]['sg_lookPass'] = shot_asset_look_pass[:-3]
                    else:
                        new_allRoughShotAssetDict[rough_shot][shot_asset]['sg_lookPass'] = None

        return new_allRoughShotAssetDict
                            


# import sys,os,shutil,platform,time,json,subprocess,csv,getpass,re,threading
# sys.path.insert(0,r'W:\shome\hanbo\Zz_Zz_Zz\hhhhh\lca\shotgun_api3')

# from shotgun_api3 import *
# import os,platform
# import csv
# import subprocess

# script_name = ''
# api_key = ''
# base_url = 'http://shotgun.zhuiguang.com'
# login = 'hanbo'
# password = 'Hb123456789'

# sg = Shotgun(base_url,login = login,password=password)

# shot_entity_look_passes_link_dict = {}

# proj_name = 'SGL' 
# shot_name = 'z99993'
# shot_entity = sg.find_one('Shot', [['project', 'name_is', proj_name], ['code', 'is', shot_name]], ['code','sg_rig_passes','sg_look_passes_link'])
# shot_entity_look_passes_link = shot_entity['sg_look_passes_link']
# print shot_entity_look_passes_link
# if shot_entity_look_passes_link!=[]:
#     for look_pass in shot_entity_look_passes_link:
#         look_pass_link_entity = sg.find_one('CustomEntity12', [['id', 'is', int(look_pass['id'])]], ['code','shot_sg_look_passes_link_shots'])
#         look_pass_assetName = look_pass_link_entity['code'].split('.')[0]
#         look_pass_name = look_pass_link_entity['code'].split('.')[-1]
#         shot_entity_look_passes_link_dict[look_pass_assetName]=[]
#     for look_pass in shot_entity_look_passes_link:
#         look_pass_link_entity = sg.find_one('CustomEntity12', [['id', 'is', int(look_pass['id'])]], ['code','shot_sg_look_passes_link_shots'])
#         look_pass_assetName = look_pass_link_entity['code'].split('.')[0]
#         look_pass_name = look_pass_link_entity['code'].split('.')[-1]
#         shot_entity_look_passes_link_dict[look_pass_assetName].append(look_pass_name)
# print shot_entity_look_passes_link_dict


# shot_entity_rig_passes_dict = {}

# proj_name = 'SGL' 
# shot_name = 'z99993'
# shot_entity = sg.find_one('Shot', [['project', 'name_is', proj_name], ['code', 'is', shot_name]], ['code','sg_rig_passes','sg_look_passes_link'])
# shot_entity_rig_passes = shot_entity['sg_rig_passes']
# print shot_entity_rig_passes
# if shot_entity_rig_passes!=[]:
#     for rig_pass in shot_entity_rig_passes:
#         rig_pass_link_entity = sg.find_one('CustomEntity10', [['id', 'is', int(rig_pass['id'])]], ['code','shot_sg_rig_passes_shots','sg_attribute','sg_asset'])
#         rig_pass_assetName = rig_pass_link_entity['sg_asset']['name']
#         rig_pass_name = rig_pass_link_entity['sg_attribute'].split('.')[-1]
#         shot_entity_rig_passes_dict[rig_pass_assetName]=[]
#     for rig_pass in shot_entity_rig_passes:
#         rig_pass_link_entity = sg.find_one('CustomEntity10', [['id', 'is', int(rig_pass['id'])]], ['code','shot_sg_rig_passes_shots','sg_attribute','sg_asset'])
#         rig_pass_assetName = rig_pass_link_entity['sg_asset']['name']
#         rig_pass_name = rig_pass_link_entity['sg_attribute'].split('.')[-1]
#         shot_entity_rig_passes_dict[rig_pass_assetName].append(rig_pass_name)
# print shot_entity_rig_passes_dict
