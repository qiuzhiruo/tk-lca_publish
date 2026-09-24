# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
############################################

import os
import sys
from xml.etree import ElementTree

from sgtk.platform.qt import QtCore, QtGui

import sys

import check
reload(check)
from check import Check

try:
    # import platform
    # if platform.system().lower() == 'windows':
    #     sys.path.insert(0,'U:/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/publish_check/ani/')
    # elif platform.system().lower() == 'linux':
    #     sys.path.insert(0,'/mnt/utility/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/publish_check/ani/')

    import tk_lca_publish.publish_check.ani.check_tpose_frame as check_tpose_frame
    import tk_lca_publish.publish_check.ani.check_pass as check_pass
    reload(check_tpose_frame)
    reload(check_pass)

    import tk_lca_publish.publish_check.mod.reuse_asset_sg_description as reuse_asset_sg_description
    reload(reuse_asset_sg_description)
except:
    pass

def build(form, check_xml, dialog):

    l_release_check = []

    tabWidget_sys_check = QtGui.QTabWidget(form)
    tabWidget_sys_check.setGeometry(QtCore.QRect(10, 50, 680, 370))

    f = open(check_xml, 'r')
    xml_text = f.read()
    f.close()
    root = ElementTree.fromstring(xml_text)

    l_grps = root.getiterator("check_group")

    grp_tab_rough_pass = None

    for i in range(len(l_grps)):
        if l_grps[i].attrib['name'] == 'Chr Tpose Checks':

            # if dialog.ui.comboBox_publish_mode.currentIndex()>0 and dialog.task['name'] == 'animation' and dialog.step['name'] == 'ani':
            # 读取xml返回所有的group
            grp = l_grps[i]
            # 实例化滑杆
            grp_tab_sa = QtGui.QScrollArea()
            # 实例化 QWidget
            grp_tab = QtGui.QWidget()
            # 把 QWidget 加到滑杆里面
            grp_tab_sa.setWidget(grp_tab)
            # 返回场景内所有角色的tpose数据
            allTposeData = check_tpose_frame.TposeFrame().getAllRefNodeTpose(dialog)
            grp_tab.setMinimumSize(630, ((len(allTposeData.keys())+2)*30))
            # 循环每个角色的数据并创建一行控件，包括：确认button，角色button，提示button，帧Linedit，修改button
            # key为角色命名空间
            if len(allTposeData.keys())>0:
                sureButtonGroup = QtGui.QButtonGroup(grp_tab)
                changeButtonGroup = QtGui.QButtonGroup(grp_tab)
                # print 'buttonGroup 111- - - ',buttonGroup
                # 给 QTabWidget 添加 Chr Tpose Checks 的 tab
                tabWidget_sys_check.addTab(grp_tab_sa, grp.attrib['name'])
                # 依次循环 把每个角色及其对应的tpose所在帧显示出来
                # 这里为了留余添加 ‘全部确认‘ 按钮
                buttonKeys = [None]
                # 返回一个列表
                for i in sorted(allTposeData.keys()):
                    buttonKeys.append(i)
                all_button = {}
                # 以角色为key，加入字典
                for key in buttonKeys:
                    sure_button,change_button,chr_button,frame_lineEdit=check_tpose_frame.TposeFrame().aa(grp_tab,allTposeData,key,dialog,buttonKeys)
                    if not key:
                        sureAllButton = sure_button
                        changeAllButton = change_button
                    else:
                        all_button[key]={}
                        all_button[key]['sure_button']=sure_button
                        all_button[key]['chr_button']=chr_button
                        all_button[key]['frame_lineEdit']=frame_lineEdit
                        sureButtonGroup.addButton(sure_button)
                        changeButtonGroup.addButton(change_button)
                # 调用自定义tab的界面布局 及其 信号事件
                # print 'sureButtonGroup- - - ',sureButtonGroup.buttons()
                # print 'changeButtonGroup- - - ',changeButtonGroup.buttons()

                sureButtonGroup.buttonClicked.connect(lambda : check_tpose_frame.TposeFrame().resetAllChrButton(all_button,dialog))
                changeButtonGroup.buttonClicked.connect(lambda : check_tpose_frame.TposeFrame().resetAllChrButton(all_button,dialog))

                sureAllButton.clicked.connect(lambda : check_tpose_frame.TposeFrame().sureAllChrTpose(all_button,dialog))
                changeAllButton.clicked.connect(lambda : check_tpose_frame.TposeFrame().changeAllChrTpose(all_button,dialog))
                
                
            else:
                pass
        elif l_grps[i].attrib['name'] == 'Chr Pass Checks':
            # print '============================='
            # print 'dialog.ui.comboBox_publish_mode.currentIndex() >',dialog.ui.comboBox_publish_mode.currentIndex() # 0
            # print "dialog.step['name'] >",dialog.step['name'] # lay
            # print "dialog.entity_type >",dialog.entity_type # Sequence
            # print '============================='
            # 读取xml返回所有的group
            grp = l_grps[i]
            # 实例化滑杆
            grp_tab_sa = QtGui.QScrollArea()
            # 实例化 QWidget
            grp_tab_rough_pass = QtGui.QWidget()
            # 把 QWidget 加到滑杆里面
            grp_tab_sa.setWidget(grp_tab_rough_pass)
            # 给 QTabWidget 添加 Chr Tpose Checks 的 tab
            tabWidget_sys_check.addTab(grp_tab_sa, grp.attrib['name'])

            # if dialog.ui.comboBox_publish_mode.currentIndex() == 1 and dialog.step['name'] == 'lay' and dialog.entity_type == 'Sequence':
            # # 返回场景内所有镜头内角色的数据
            # allRoughShotAssetDict = check_pass.TposeFrame().getAllRoughShotAsset(dialog) # {u'z99996': {u'wangcheng': {'rigPass': {'name': None, 'value': None}, 'lookPass': {'name': None, 'value': None}}}, u'z99997': {u'wangcheng': {'rigPass': {'name': None, 'value': None}, 'lookPass': {'name': None, 'value': None}}}}
            # allRoughShots = sorted(allRoughShotAssetDict.keys()) # [u'z99996', u'z99997']
            # allRoughShotAssets = []
            # for ii in allRoughShots:
            #     if allRoughShotAssetDict[ii]:
            #         for iii in allRoughShotAssetDict[ii].keys():
            #             allRoughShotAssets.append(iii) # [u'wangcheng', u'wangcheng']
            # # 设置行数
            # grp_tab_rough_pass.setMinimumSize(630, ((len(allRoughShots)+(len(allRoughShotAssets))*2+2)*30))

            # # 循环每个镜头每个角色的数据并创建一行控件，包括：确认button，角色button，提示button，帧Linedit，修改button
            # # key为角色命名空间
            
            # checkButtonGroup = QtGui.QButtonGroup(grp_tab_rough_pass)
            # uploadButtonGroup = QtGui.QButtonGroup(grp_tab_rough_pass)
            
            # # # 给 QTabWidget 添加 Chr Tpose Checks 的 tab
            # # tabWidget_sys_check.addTab(grp_tab_sa, grp.attrib['name'])
            # # 依次循环 把每个角色及其对应的 pass 显示出来
            # # 这里为了留余添加 ‘全部确认‘ 按钮
            # buttonKeys = [None]
            # # 返回一个列表
            # for i in sorted(allRoughShotAssetDict.keys()):
            #     buttonKeys.append(i+'_shot')
            #     if allRoughShotAssetDict[i]:
            #         for ii in sorted(allRoughShotAssetDict[i].keys()):
            #             buttonKeys.append(ii+'_asset_lookpass_'+i)
            #             buttonKeys.append(ii+'_asset_rigpass_'+i)
            # all_button = {}
            # # 以角色为key，加入字典
            # for key in buttonKeys:
            #     shot_button,upload_button,chr_button,pass_button,pass_lineEdit = check_pass.TposeFrame().aa(grp_tab_rough_pass,allRoughShotAssetDict,key,dialog,buttonKeys)
            # #     sure_button,change_button,chr_button,frame_lineEdit=check_pass.TposeFrame().aa(grp_tab_rough_pass,allRoughShotAssetDict,key,dialog,buttonKeys)
            #     if not key:
            #         checkAllButton = shot_button
            #         uploadAllButton = upload_button
            #     else:
            #         all_button[key]={}
            #         all_button[key]['shot_button']=shot_button
            #         all_button[key]['upload_button']=upload_button
            #         all_button[key]['chr_button']=chr_button
            #         all_button[key]['pass_button']=pass_button
            #         all_button[key]['pass_lineEdit']=pass_lineEdit

            # # 信号事件
            # # 点击全部检查：打断 chr-shot-pass之间的关联，并更改界面颜色显示
            # # 点击全部上传：做 chr-shot-pass之间的关联，并更改界面颜色显示
            
            # checkAllButton.clicked.connect(lambda : check_pass.TposeFrame().checkAllChrPass(all_button,dialog))
            # uploadAllButton.clicked.connect(lambda : check_pass.TposeFrame().uploadAllChrPass(all_button,dialog))
            # else:
            #     print '==============================+++++++++++++++++++++++++'
            #     # tabWidget_sys_check.setTabEnabled(i,False)
            #     tabWidget_sys_check.clear()
        elif l_grps[i].attrib['name'] == 'reuse asset description':
            grp = l_grps[i]
            grp_tab_rough_pass = reuse_asset_sg_description.ReuseAssetWin()
            grp_tab_sa = QtGui.QScrollArea()
            grp_tab_sa.setWidget(grp_tab_rough_pass)
            tabWidget_sys_check.addTab(grp_tab_sa, grp.attrib['name'])

        else:
            grp = l_grps[i]
            grp_tab = QtGui.QWidget()
            tabWidget_sys_check.addTab(grp_tab, grp.attrib['name'])
            #tabWidget_sys_check.setTabText(i, )
            
            l_checks = grp.getiterator("check")
            for j in range(len(l_checks)):
                check = l_checks[j]
                module_type = check.attrib['type']
                module_name = check.attrib['name']
                allow_skip  = check.attrib['allow_skip']
                chk = Check( grp_tab, grp.attrib['name'], 'publish_check.' + module_type, module_name, allow_skip, j, dialog)
                l_release_check.append(chk)

    return l_release_check,tabWidget_sys_check,grp_tab_rough_pass
