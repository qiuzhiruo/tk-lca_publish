# -*- coding:utf-8 -*-

import traceback
import os
import pymel.core as pm
import maya.cmds as cmds
import production.mayautils.assembly as assutils
import maya
import re
import maya.OpenMaya as OpenMaya
import maya.app.general.editUtils as editUtils



# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查 Assembly Reference 节点底下是否 有 层级 p 了出来"
        self.description = u"Assembly Reference 节点底下 层级 不能 p 出来"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            cmds.select(cl=1)
            wrong_ars = []
            for ar in pm.ls(type='assemblyReference'):
                ass = self.getOpenMayaAssemblyNode(ar.name())
                #print ass,ass.fullPathName()
                full_path = ass.fullPathName()
                
                editList = []
                targetNode = self.makeDependNode(full_path)
                curOwner = targetNode
                while not curOwner.isNull():
                    editList = editList + self.getEdits(curOwner, targetNode)
                    assemblyFn = OpenMaya.MFnAssembly(curOwner)
                    curOwner = assemblyFn.getParentAssembly()
                
                if editList != []:
                    for edit in editList:
                        editStr = edit.getString()
                        if edit.isTopLevel():
                            if editStr.startswith('parent'):
                                if ar.name() not in wrong_ars:
                                    #print ar.name(),len(editList)
                                    #print editStr
                                    cmds.select(full_path,add=1)
                                    wrong_ars.append(ar.name())
                                    continue
            
            if wrong_ars!=[]:
                message = u'以下AR节点层级有节点p出，大纲内已经选中，请点击自动修复进行修复：\n%s' % str(wrong_ars)
                return message
            return ""

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        
        try:
            import lay.lca_remove_parent_edit.remove_list_assembly_edits_parent as rlae;reload(rlae);rlae.main()
            return ''
        except:
            return traceback.format_exc()


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty

    def getOpenMayaAssemblyNode(self,refNodeName):
        assemblyNode = editUtils.makeDependNode(refNodeName)
        assemblyFn = OpenMaya.MFnAssembly(assemblyNode)
        return assemblyFn
    def makeDependNode(self,name):
        selList = OpenMaya.MSelectionList()
        selList.add(name)
        node = OpenMaya.MObject()
        selList.getDependNode(0, node)
        return node
    def getEdits(self,owner, target):
        """
        Query edits that are stored on the given owner node.
        
        If target is not empty, we will only list
        edits that affect nodes in this assembly.
        
        If target is empty, we will list all edits
        stored on the given node
        """
        
        editList = []
        useStringTarget = False
        # err = maya.stringTable['y_editUtils.kInvalidNode' ]
        err = 'y_editUtils.kInvalidNode'
        try:
            ownerNode = self.makeDependNode(owner)
        except:
            msg = cmds.format(err, stringArg=owner)
            print msg
            raise
        
        try:
            targetNode = self.makeDependNode(target)
        except:
            useStringTarget = True
            pass
        
        if useStringTarget:
            it = OpenMaya.MItEdits(ownerNode, target)
        else:
            it = OpenMaya.MItEdits(ownerNode, targetNode)

        while not it.isDone():
            edit = it.edit()
            # if an edit was removed, it will be NULL
            if edit is not None:
                editList.append(it.edit())
            it.next()

        return editList 