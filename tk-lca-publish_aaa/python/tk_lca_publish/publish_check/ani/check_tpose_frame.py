# -*- coding: utf-8 -*-
import pymel.core as pm
import maya.mel as mel
import maya.cmds as cmds
import json
import platform
import platform
import os
from sgtk.platform.qt import QtCore, QtGui
import ZvParentMaster
from ani.lca_t_pose import tposeWidget_publish_show as tps
reload(tps)

class TposeFrame():
    def __init__(self):
        # self.tsRtList = ['translateX','translateY','translateZ','rotateX','rotateY','rotateZ']
        self.bodyCtrlList = [u'hip', u'shoulder', u'head', u'neck', u'leg', u'global', u'body', u'foot', u'root', u'arm']
        
        self.lca_nameSpace_attr = 'lca_nameSpace'
        self.lca_chr_frame_attr = 'lca_chr_frame'
        self.lca_sure_tpose_attr = 'lca_sure_tpose'
    # 实例化各个控件
    def aa(self,grp_tab,allTposeData,key,dialog,buttonKeys):
        self.dialog = dialog
        self.proj = self.dialog.project['name'].lower()
        self.seq = self.dialog.entity['name'][:3]
        self.shot = self.dialog.entity['name']
        if key:
            print 'key --- ',key
            visib_Ctrl = key+':visibility_ctrl'
            self.sure_button = QtGui.QPushButton(grp_tab)
            self.sure_button.setText(u"确认")
            self.sure_button.setGeometry(QtCore.QRect(10, 20+30*(buttonKeys.index(key)),40, 25))
            self.sure_button.setStyleSheet("color:rgb(255,0,0)")
            #角色按钮
            self.chr_button = QtGui.QPushButton(grp_tab)
            self.chr_button.setText(key)
            self.chr_button.setGeometry(QtCore.QRect(65, 20+30*(buttonKeys.index(key)), 230, 25))
            self.chr_button.setEnabled(False)
            
            #注释按钮
            self.tpose_button = QtGui.QPushButton(grp_tab)
            self.tpose_button.setText(u"-> -> Tpose 做在了 -> ->")
            self.tpose_button.setGeometry(QtCore.QRect(300, 20+30*(buttonKeys.index(key)),160, 25))
            self.tpose_button.setStyleSheet("background:rgba(0,0,0,0);border:0px solid rgba(0,0,0,0);};color:rgb(170,170,170)")
            #帧数按钮
            self.frame_lineEdit = QtGui.QLineEdit(grp_tab)
            self.frame_lineEdit.setAlignment(QtCore.Qt.AlignHCenter)
            self.frame_lineEdit.setText(allTposeData[key]['TposeFrame'])
            self.frame_lineEdit.setGeometry(QtCore.QRect(475, 20+30*(buttonKeys.index(key)), 100, 25))
            self.frame_lineEdit.setEnabled(False)
            self.frame_lineEdit.setStyleSheet("color:rgb(255,255,0)")
            self.frame_lineEdit.setValidator(QtGui.QIntValidator())
            
            #修改帧数按钮
            self.change_button = QtGui.QPushButton(grp_tab)
            self.change_button.setText(u"修改")
            self.change_button.setGeometry(QtCore.QRect(590, 20+30*(buttonKeys.index(key)),40, 25))
            self.change_button.setStyleSheet("color:rgb(255,255,170)")
            #信号事件
            self.sure_button.clicked.connect(lambda : self.sureChrTpose())
            self.chr_button.clicked.connect(lambda : self.checkChrTpose())
            self.change_button.clicked.connect(lambda : self.setFrameLineEdit())
            self.frame_lineEdit.textChanged.connect(lambda : self.changeFrameLineEdit())
        else:
            # 添加 全部确认 和 全部修改 按钮
            self.sure_button = QtGui.QPushButton(grp_tab)
            self.sure_button.setText(u"全部确认")
            self.sure_button.setGeometry(QtCore.QRect(10, 20+30*0,80, 25))
            self.sure_button.setStyleSheet("color:rgb(0,255,255)")

            self.change_button = QtGui.QPushButton(grp_tab)
            self.change_button.setText(u"全部修改")
            self.change_button.setGeometry(QtCore.QRect(550, 20+30*0,80, 25))
            self.change_button.setStyleSheet("color:rgb(255,255,170)")

            return self.sure_button,self.change_button,None,None
            
        return self.sure_button,self.change_button,self.chr_button,self.frame_lineEdit


    def all_refs(self):
        all_ref_Nodes = pm.ls(rf=1)
        allRefNodes = []
        for ref in all_ref_Nodes:
            if ref.referenceFile():
                if ref.isLoaded():
                    ref_name = ref.name()
                    allRefNodes.append(ref_name)

        return allRefNodes

    #根据每一个角色的ref node,得到对应的visibility_ctrl。返回一个字典
    def getVisCtrls(self,allRefNodes,chrNamespace=False,single = False):
        nodes_dict = {}
        for refNode in allRefNodes:
            if cmds.referenceQuery(refNode,il=1):
                refNodeName = cmds.referenceQuery(refNode,rfn=1)
                refNodeFile = cmds.referenceQuery(refNode,f=1)
                refNodeNamespace = cmds.referenceQuery(refNode,ns=1)[1:]
                # skip unused rra
                # print 'refNodeFile: ', refNodeFile
                if '/asset/chr/' in refNodeFile or '/asset/crd/' in refNodeFile:
                    long_name = cmds.ls('{}:master'.format(refNodeNamespace), long=True)
                    if not long_name:
                        pass
                    elif '|assets|rra|' in long_name[0]:
                        continue

                if not single:
                    if '/asset/chr/' in refNodeFile or '/asset/crd/' in refNodeFile:
                        print '-------------------------------------'
                        # print refNodeNamespace
                        nodes_dict[refNodeNamespace]={}
                        visCtrl = refNodeNamespace+':visibility_ctrl'
                        nodes_dict[refNodeNamespace]['visibilityCtrl']=visCtrl
                elif single:
                    if '/asset/chr/' in refNodeFile and refNodeNamespace == chrNamespace:
                        print '-------------------------------------'
                        # print refNodeNamespace
                        nodes_dict[refNodeNamespace]={}
                        visCtrl = refNodeNamespace+':visibility_ctrl'
                        nodes_dict[refNodeNamespace]['visibilityCtrl']=visCtrl
                    if '/asset/crd/' in refNodeFile and refNodeNamespace == chrNamespace:
                        print '-------------------------------------'
                        # print refNodeNamespace
                        nodes_dict[refNodeNamespace]={}
                        visCtrl = refNodeNamespace+':visibility_ctrl'
                        nodes_dict[refNodeNamespace]['visibilityCtrl']=visCtrl
        return nodes_dict
    #根据每个角色的命名空间，结合bodyCtrlList，得到对应的body控制器，继续在原先字典里加
    def getBodyCtrls(self,nodes_dict):
        for chrNameSpace in nodes_dict.keys():
            nodes_dict[chrNameSpace]['ctrls']=[]
            for i in self.bodyCtrlList:
                for c in cmds.ls('{}:{}*{}'.format(chrNameSpace, i+'_','_ctrl'), type=['transform', 'joint']):
                    if '_sec_' not in c:
                        ph_grp = ZvParentMaster._getParentHandle(c)
                        sn_grp = ZvParentMaster._getSnapGroup(c)
                        if cmds.objExists(ph_grp) and ph_grp not in nodes_dict[chrNameSpace]['ctrls']:
                            nodes_dict[chrNameSpace]['ctrls'].append(ph_grp)
                        if cmds.objExists(sn_grp) and sn_grp not in nodes_dict[chrNameSpace]['ctrls']:
                            nodes_dict[chrNameSpace]['ctrls'].append(sn_grp)
                        if c not in nodes_dict[chrNameSpace]['ctrls']:
                            nodes_dict[chrNameSpace]['ctrls'].append(c)
                for c in cmds.ls('{}:*{}*{}'.format(chrNameSpace, '_'+i+'_','_ctrl'), type=['transform', 'joint']):
                    if '_sec_' not in c:
                        ph_grp = ZvParentMaster._getParentHandle(c)
                        sn_grp = ZvParentMaster._getSnapGroup(c)
                        if cmds.objExists(ph_grp) and ph_grp not in nodes_dict[chrNameSpace]['ctrls']:
                            nodes_dict[chrNameSpace]['ctrls'].append(ph_grp)
                        if cmds.objExists(sn_grp) and sn_grp not in nodes_dict[chrNameSpace]['ctrls']:
                            nodes_dict[chrNameSpace]['ctrls'].append(sn_grp)
                        if c not in nodes_dict[chrNameSpace]['ctrls']:
                            nodes_dict[chrNameSpace]['ctrls'].append(c)
            # print len(nodes_dict[chrNameSpace]['ctrls'])
        return nodes_dict
    # 检测所有角色的tpose起始帧,返回一个字典
    def getAllRefNodeTpose(self,dialog):
        self.dialog = dialog
        self.proj = self.dialog.project['name'].lower()
        self.seq = self.dialog.entity['name'][:3]
        self.shot = self.dialog.entity['name']

        try:
            pm.mel.RNdeleteUnused()
        except:
            pass

        allRefTposeDict = {}
        # allRefNodes = cmds.ls(rf=1)
        allRefNodes = self.all_refs()

        #根据每一个角色的ref node,得到对应的visibility_ctrl。返回一个字典
        nodes_dict=self.getVisCtrls(allRefNodes)
        #根据每个角色的命名空间，结合bodyCtrlList，得到对应的body控制器，继续在原先字典里加
        nodes_dict_new = self.getBodyCtrls(nodes_dict)
        for refNodeNamespace in nodes_dict_new:
            # print refNode
            allFrames = []
            # print '-------------------------------------'
            # print refNodeNamespace
            # 给visibility添加四个属性
            visib_Ctrl = refNodeNamespace+':visibility_ctrl'
            allAttrs = cmds.listAttr(visib_Ctrl)
            if self.lca_nameSpace_attr not in allAttrs:
                cmds.addAttr(visib_Ctrl, ln=self.lca_nameSpace_attr, dt='string')
            if self.lca_chr_frame_attr not in allAttrs:
                cmds.addAttr(visib_Ctrl, ln=self.lca_chr_frame_attr, dt='string')
            if self.lca_sure_tpose_attr not in allAttrs:
                cmds.addAttr(visib_Ctrl, ln=self.lca_sure_tpose_attr, dt='string')
                
            # nameSpace_value = cmds.getAttr(visib_Ctrl+'.'+self.lca_nameSpace_attr)
            
            cmds.setAttr(visib_Ctrl+'.'+self.lca_nameSpace_attr,refNodeNamespace,type='string')
            cmds.setAttr(visib_Ctrl+'.'+self.lca_sure_tpose_attr,'0',type='string')

            for i in nodes_dict_new[refNodeNamespace]['ctrls']:
                try:
                    for ii in sorted(cmds.keyframe(i,q=1,a=1)):
                        if ii not in allFrames:
                            allFrames.append(ii)
                except:
                    pass
            #print sorted(allFrames)
            if allFrames != []:
                allRefTposeDict[refNodeNamespace]={}
                allRefTposeDict[refNodeNamespace]['TposeFrame']=str(int(sorted(allFrames)[0]))
                allRefTposeDict[refNodeNamespace]['SureTpose'] = '0'
                visib_Ctrl = refNodeNamespace+':visibility_ctrl'
                cmds.setAttr(visib_Ctrl+'.'+self.lca_chr_frame_attr,str(int(sorted(allFrames)[0])),type='string')
            else:
                allRefTposeDict[refNodeNamespace]={}
                allRefTposeDict[refNodeNamespace]['TposeFrame']=None
                allRefTposeDict[refNodeNamespace]['SureTpose'] = '0'

        return allRefTposeDict
    # 重新检测单个角色的tpose起始帧
    def getRefNodeTpose(self,chrNamespace):
        allRefTposeDict = {}
        # allRefNodes = cmds.ls(rf=1)
        allRefNodes = self.all_refs()
        #根据每一个角色的ref node,得到对应的visibility_ctrl。返回一个字典
        nodes_dict=self.getVisCtrls(allRefNodes,chrNamespace,single = True)
        #根据每个角色的命名空间，结合bodyCtrlList，得到对应的body控制器，继续在原先字典里加
        nodes_dict_new = self.getBodyCtrls(nodes_dict)
        for refNodeNamespace in nodes_dict_new:
            # print refNode
            allFrames = []
            for i in nodes_dict_new[refNodeNamespace]['ctrls']:
                try:
                    for ii in sorted(cmds.keyframe(i,q=1,a=1)):
                        if ii not in allFrames:
                            #print i
                            allFrames.append(ii)
                except:
                    pass
            #print sorted(allFrames)
            if allFrames != []:
                allRefTposeDict[refNodeNamespace]=str(int(sorted(allFrames)[0]))
                return str(int(sorted(allFrames)[0]))
            else:
                allRefTposeDict[refNodeNamespace]=None
                return None
    # 得到所有角色的visb ctrl，并获得对应的lca属性值，返回一个字典
    def getAllVisibCtrl(self):
        allVisibiCtrls = {}
        # allRefNodes = cmds.ls(rf=1)
        allRefNodes = self.all_refs()
        for refNode in allRefNodes:
            if cmds.referenceQuery(refNode,il=1):
                refNodeName = cmds.referenceQuery(refNode,rfn=1)
                refNodeFile = cmds.referenceQuery(refNode,f=1)
                refNodeNamespace = cmds.referenceQuery(refNode,ns=1)

                # skip rra asset
                if '/asset/chr/' in refNodeFile or '/asset/crd/' in refNodeFile:
                    long_name = cmds.ls('{}:master'.format(refNodeNamespace), long=True)
                    if not long_name:
                        pass
                    elif '|assets|rra|' in long_name[0]:
                        continue

                if '/asset/chr/' in refNodeFile or '/asset/crd/' in refNodeFile:
                    visib_Ctrl = refNodeNamespace[1:]+':visibility_ctrl'
                    # 考虑到打开publish页面，又ref进新的角色，所以加了try，但是一般不这样操作，趴的时候是不可能再ref新的角色的，就算ref新的角色，也需要重新打开publish页面
                    try:
                        allVisibiCtrls[visib_Ctrl]={}
                        allVisibiCtrls[visib_Ctrl]['lca_nameSpace']=cmds.getAttr(visib_Ctrl+'.'+self.lca_nameSpace_attr)
                        allVisibiCtrls[visib_Ctrl]['lca_chr_frame']=cmds.getAttr(visib_Ctrl+'.'+self.lca_chr_frame_attr)
                        allVisibiCtrls[visib_Ctrl]['lca_sure_tpose']=cmds.getAttr(visib_Ctrl+'.'+self.lca_sure_tpose_attr)

                        allVisibiCtrls[visib_Ctrl]['new_name_space'] = refNodeNamespace[1:]
                    except:
                        allAttrs = cmds.listAttr(visib_Ctrl)
                        if self.lca_nameSpace_attr not in allAttrs:
                            cmds.addAttr(visib_Ctrl, ln=self.lca_nameSpace_attr, dt='string')
                        if self.lca_chr_frame_attr not in allAttrs:
                            cmds.addAttr(visib_Ctrl, ln=self.lca_chr_frame_attr, dt='string')
                        if self.lca_sure_tpose_attr not in allAttrs:
                            cmds.addAttr(visib_Ctrl, ln=self.lca_sure_tpose_attr, dt='string')
                        cmds.setAttr(visib_Ctrl+'.'+self.lca_nameSpace_attr,refNodeNamespace[1:],type='string')
                        cmds.setAttr(visib_Ctrl+'.'+self.lca_sure_tpose_attr,'0',type='string')
                        chrTpose = self.getRefNodeTpose(refNodeNamespace[1:])
                        if chrTpose:
                            cmds.setAttr(visib_Ctrl+'.'+self.lca_chr_frame_attr,chrTpose,type='string')
                        allVisibiCtrls[visib_Ctrl]={}
                        allVisibiCtrls[visib_Ctrl]['lca_nameSpace']=cmds.getAttr(visib_Ctrl+'.'+self.lca_nameSpace_attr)
                        allVisibiCtrls[visib_Ctrl]['lca_chr_frame']=cmds.getAttr(visib_Ctrl+'.'+self.lca_chr_frame_attr)
                        allVisibiCtrls[visib_Ctrl]['lca_sure_tpose']=cmds.getAttr(visib_Ctrl+'.'+self.lca_sure_tpose_attr)

                        allVisibiCtrls[visib_Ctrl]['new_name_space'] = refNodeNamespace[1:]
        return allVisibiCtrls
    # 根据参数 设置visb ctrl确认属性为0/1，以及修改frame attr，设置lca_nameSpace_attr的值
    def setVisbCtrlAttr(self,chrNameSpcae,sure=False,change=False,changeFrame=False,nameSpace=False):
        visib_Ctrl = chrNameSpcae+':visibility_ctrl'
        if sure:
            cmds.setAttr(visib_Ctrl+'.'+self.lca_sure_tpose_attr,'1',type='string')
        if change:
            cmds.setAttr(visib_Ctrl+'.'+self.lca_sure_tpose_attr,'0',type='string')
        if changeFrame:
            cmds.setAttr(visib_Ctrl+'.'+self.lca_chr_frame_attr,self.frame_lineEdit.text(),type='string')
        if nameSpace:
            cmds.setAttr(visib_Ctrl+'.'+self.lca_nameSpace_attr,chrNameSpcae,type='string')


    #点击 确认 按钮，设置点击角色的lca_sure_tpose_attr为1，chr_button不可点击，frame_lineEdit不可修改
    def sureChrTpose(self):
        # print 'sureChrTpose---'
        self.resetChrButton(self.chr_button)

        self.setVisbCtrlAttr(self.chr_button.text(),sure=True)
        self.sure_button.setStyleSheet("color:rgb(0,255,255)")
        self.chr_button.setEnabled(False)
        self.frame_lineEdit.setEnabled(False)
    # 点击 chr button，重新检测chr的tpose起始帧，并设置到visibi ctrl上,修改frame_lineEdit的值
    def checkChrTpose(self):
        self.resetChrButton(self.chr_button)

        chrTpose = self.getRefNodeTpose(self.chr_button.text())
        if chrTpose:
            self.frame_lineEdit.setText(chrTpose)
        else:
            self.frame_lineEdit.clear()
    # 点击 change button，设置点击角色的lca_sure_tpose_attr为0,chr_button可点击，frame_lineEdit可修改
    def setFrameLineEdit(self):
        self.resetChrButton(self.chr_button)

        self.setVisbCtrlAttr(self.chr_button.text(),change=True)
        self.sure_button.setStyleSheet("color:rgb(255,0,0)")
        self.chr_button.setEnabled(True)
        self.frame_lineEdit.setEnabled(True)
    # 修改 frame_lineEdit 会出发修改lca_chr_frame_attr的值
    def changeFrameLineEdit(self):
        self.resetChrButton(self.chr_button)

        self.setVisbCtrlAttr(self.chr_button.text(),changeFrame=True)

    # def writeSureChrFrameJson(self,proj,seq,shot,chr_button,frame_lineEdit,sureOrNot):
    #     jsonDirPath = self.mkdirTpose(proj,seq,shot)
    #     jsonPath = os.path.join(jsonDirPath,'chr_tpose.json')

    #     jsonData = self.readJson(jsonPath)

    #     chrNamespace = chr_button.text()
    #     chrTpose = frame_lineEdit.text()

    #     jsonData[chrNamespace]['SureTpose'] = str(sureOrNot)

    #     self.writeToJson(jsonPath,jsonData)


    # 点击 全部确认 确认所有
    def sureAllChrTpose(self,all_button,dialog):
        #获取现在所有的visb ctrl及其所加属性的值
        allVisbCtrls = self.getAllVisibCtrl()

        for key in all_button.keys():
            sure_button=all_button[key]['sure_button']
            chr_button=all_button[key]['chr_button']
            frame_lineEdit=all_button[key]['frame_lineEdit']
            # 先更改button状态
            sure_button.setStyleSheet("color:rgb(0,255,255)")
            chr_button.setEnabled(False)
            frame_lineEdit.setEnabled(False)
            # 判断visb 的lca_nameSpace是否和chr button一样，一样就把最新的nameSpace给到chr button
            for keyy in allVisbCtrls.keys():
                if allVisbCtrls[keyy]['lca_nameSpace'] == chr_button.text():
                    chr_button.setText(allVisbCtrls[keyy]['new_name_space'])
            # 先修改visb 的lca_sure_tpose_attr为1
            self.setVisbCtrlAttr(chr_button.text(),sure=True)
        # 再修改visb 的lca_chr_frame_attr为chr button的值
        for key in all_button.keys():
            sure_button=all_button[key]['sure_button']
            chr_button=all_button[key]['chr_button']
            frame_lineEdit=all_button[key]['frame_lineEdit']

            self.setVisbCtrlAttr(chr_button.text(),nameSpace = True)
        tpose_use_tool_chrs = []
        tpose_nouse_tool_chrs = []
        for visib_Ctrl in allVisbCtrls.keys():
            if cmds.objExists(visib_Ctrl):
                nsp = visib_Ctrl.split(':')[0]
                allAttrs = cmds.listAttr(visib_Ctrl)
                if 'lca_tpose_use_tool' in allAttrs:
                    if cmds.getAttr((visib_Ctrl+'.lca_tpose_use_tool'))=='1':
                        if nsp not in tpose_use_tool_chrs:
                            tpose_use_tool_chrs.append(nsp)
                    else:
                        if nsp not in tpose_nouse_tool_chrs:
                            tpose_nouse_tool_chrs.append(nsp)
                else:
                    if nsp not in tpose_nouse_tool_chrs:
                        tpose_nouse_tool_chrs.append(nsp)
        print 'tpose_use_tool_chrs >',tpose_use_tool_chrs
        print 'tpose_nouse_tool_chrs >',tpose_nouse_tool_chrs
        if tpose_nouse_tool_chrs!=[]:
            tps.main()

    # 点击 全部修改 修改所有
    def changeAllChrTpose(self,all_button,dialog):
        #获取现在所有的visb ctrl及其所加属性的值
        allVisbCtrls = self.getAllVisibCtrl()

        for key in all_button.keys():
            sure_button=all_button[key]['sure_button']
            chr_button=all_button[key]['chr_button']
            frame_lineEdit=all_button[key]['frame_lineEdit']

            # 先更改button状态
            sure_button.setStyleSheet("color:rgb(255,0,0)")
            chr_button.setEnabled(True)
            frame_lineEdit.setEnabled(True)
            # 判断visb 的lca_nameSpace是否和chr button一样，一样就把最新的nameSpace给到chr button
            for keyy in allVisbCtrls.keys():
                if allVisbCtrls[keyy]['lca_nameSpace'] == chr_button.text():
                    chr_button.setText(allVisbCtrls[keyy]['new_name_space'])
            # 先修改visb 的lca_sure_tpose_attr为0
            self.setVisbCtrlAttr(chr_button.text(),change=True)
        # 再修改visb 的lca_chr_frame_attr为chr button的值
        for key in all_button.keys():
            sure_button=all_button[key]['sure_button']
            chr_button=all_button[key]['chr_button']
            frame_lineEdit=all_button[key]['frame_lineEdit']

            self.setVisbCtrlAttr(chr_button.text(),nameSpace = True)


    # 点击但个 确认/修改 按钮，修改全部的角色命名空间button的值
    def resetAllChrButton(self,all_button,dialog=None):
        # print '--------------- resetAllChrButton'
        #获取现在所有的visb ctrl及其所加属性的值
        allVisbCtrls = self.getAllVisibCtrl()
        for key in all_button.keys():
            sure_button=all_button[key]['sure_button']
            chr_button=all_button[key]['chr_button']
            frame_lineEdit=all_button[key]['frame_lineEdit']

            # 先更改button状态
            # sure_button.setStyleSheet("color:rgb(255,0,0)")
            # chr_button.setEnabled(True)
            # frame_lineEdit.setEnabled(True)
            # 判断visb 的lca_nameSpace是否和chr button一样，一样就把最新的nameSpace给到chr button
            for keyy in allVisbCtrls.keys():
                if allVisbCtrls[keyy]['lca_nameSpace'] == chr_button.text():
                    chr_button.setText(allVisbCtrls[keyy]['new_name_space'])
            # 先修改visb 的lca_sure_tpose_attr为0
            # self.setVisbCtrlAttr(chr_button.text(),change=True)
        # 再修改visb 的lca_chr_frame_attr为chr button的值
        for key in all_button.keys():
            sure_button=all_button[key]['sure_button']
            chr_button=all_button[key]['chr_button']
            frame_lineEdit=all_button[key]['frame_lineEdit']

            self.setVisbCtrlAttr(chr_button.text(),nameSpace = True)
    # 点击单个 确认/修改 按钮，只修改这一行的
    def resetChrButton(self,chr_button):
        allVisbCtrls = self.getAllVisibCtrl()
        for keyy in allVisbCtrls.keys():
            if allVisbCtrls[keyy]['lca_nameSpace'] == chr_button.text():
                chr_button.setText(allVisbCtrls[keyy]['new_name_space'])
        # 先修改visb 的lca_sure_tpose_attr为0
        # self.setVisbCtrlAttr(chr_button.text(),change=True)
        # 再修改visb 的lca_chr_frame_attr为chr button的值
        self.setVisbCtrlAttr(chr_button.text(),nameSpace = True)