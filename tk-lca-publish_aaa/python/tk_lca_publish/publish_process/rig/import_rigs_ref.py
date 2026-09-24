# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Edward Sun
#
# Date: 2014.08
#
# Description: 
#
############################################

import os
import traceback
import shutil
import pymel.core as pm
import maya.cmds as cmds

def importAllRefs():
    'import file form refs'
    refs = cmds.ls(references=1)
    for x in refs:
        #x=refs[0]
        try:
            filePath = cmds.referenceQuery(x,filename=True )
            cmds.file(filePath,importReference=1)
        except:
            pass
        if cmds.objExists(x):
            cmds.lockNode(x,lock=False)
            cmds.delete(x)
    return ""

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"将工程文件中reference的模型变成import。"
        self.description = u"非chr类资产中如果直接reference了模型，在最终下游组使用文件中把模型import进来，减少reference层级。"
        return


    def proceed(self):
        try:
            #print '<import_ref>'
            #print asset_info
            if self.dialog.asset_type != 'chr':
                # asset's locking relies on this condition, any asset who failed to meet this condition will not be locked neither
                importAllRefs()
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description



