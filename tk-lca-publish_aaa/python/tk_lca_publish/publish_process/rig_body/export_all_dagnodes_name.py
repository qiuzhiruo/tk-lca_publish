# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2014 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.01
#
# Description: Record model mesh info
#
############################################

import os
import traceback
import hashlib
from xml.dom.minidom import Document
import pymel.core as pm
import maya.api.OpenMaya as om
import maya.cmds as cmds



# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"记录所有DAG节点名称。"
        self.description = u"记录所有DAG节点名称，为做对比找出重名节点做准备。"
        return

    def get_all_dagnodes_name(self):
        cmds.select('|master',hi=1)
        alldags=cmds.ls(sl=1)
        alldagtx=''
        for dag in alldags:
            alldagtx=alldagtx+dag+'\n'
        cmds.select(cl=1)
        return alldagtx[:-1]


    def proceed(self):
        try:
            master_dags_name = self.dialog.version_dir + '/master_all_dagname.dag'
            alldags=self.get_all_dagnodes_name()
            print alldags
            f = open(master_dags_name, 'w')
            f.write(alldags)
            f.close()
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


