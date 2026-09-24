# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Edward Sun
#
# Date: 2013.10
#
# Description: 
#
########################################################################################

import traceback
import pymel.core as pm
import maya.cmds as cmds
import os

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查是是否有DAG节点与rigging_body的最新publish文件重名"
        self.description = u"所有DAG节点的命名不能与rigging_body文件里的DAG节点重名，避免合并rigging_body文件时重名。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            grps=['facial_modules_grp', "facial_controls_grp", "facial_skeletons_grp", 'facial_model_grp']
            dagnamespath = self.dialog.publish_root + '/' + self.dialog.version_key.replace('.rigging_facial','.rigging_body')+'/master_all_dagname.dag'
            if not os.path.exists(dagnamespath):
                return ''
            print dagnamespath
            f = open(dagnamespath,'r')
            ftx = f.read()
            f.close()
            #print ftx
            otherdags=ftx.split('\n')
            #print otherdags
            err_msg=''
            cmds.select(grps,hi=1)
            alldags=cmds.ls(sl=1)
            cmds.select(cl=1)
            for dag in alldags:
                #print dag
                if dag in otherdags:
                    err_msg=err_msg+dag+u'  与身体设置rigging_body publish 文件里的DAG 节点重名，请检查。\n'
            return err_msg
        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        return ''

    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


