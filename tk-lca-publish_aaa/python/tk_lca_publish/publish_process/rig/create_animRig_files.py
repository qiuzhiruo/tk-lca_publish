# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Edward Sun
#
# Date: 2014.05
#
# Description: 
#
############################################
import os
import traceback
import shutil
import pymel.core as pm
from sgtk.platform.qt import QtGui
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import sys

def create_animRig_files():
    fixdeformer=['deltaMush','stretchMesh']
    print 'create_animRig_files...'

    if cmds.objExists('tech_rig'):
        print 'delete ... tech_rig'
        cmds.lockNode('tech_rig', lock=False)
        cmds.delete('tech_rig')
    else:
        print 'tech_rig is not existed'

    if cmds.objExists('tech_model'):
        print 'delete ... tech_model'
        cmds.lockNode('tech_model', lock=False)
        cmds.delete('tech_model')
    else:
        print 'tech_model is not existed'

    if cmds.objExists('Facial_tech_model'):
        print 'delete ... Facial_tech_model'
        cmds.lockNode('Facial_tech_model', lock=False)
        cmds.delete('Facial_tech_model')
    else:
        print 'Facial_tech_model   is not existed'

    deletedeformers=[]
    for tp in fixdeformer:
        nodes=cmds.ls(type=tp)
        if nodes:
            deletedeformers=deletedeformers+nodes

    print 'delete all fix deformer:\n'
    print deletedeformers

    try:
        cmds.delete(deletedeformers)
    except:
        print 'delete fix deformer failed'
    
def set_attr_value(attr,v):
    try:
        cmds.setAttr(attr,v)
    except:
        None

def set_attr_lock(attr,lv):
    try:
        cmds.setAttr(attr,e=1,l=lv)
    except:
        None


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"导出提供给animation环节使用的rig版本。"
        self.description = u"注意所有tech_rig下的设置和tech_asset下的部件将被清除并导出文件到shotGun数据库！"
        return


    def proceed(self):
        #print self.dialog.project['name'].upper()
        #self.dialog.anim_file=self.dialog.version_dir+'/anim_rig/'
        
        print 'create anim rig.'
        #task=self.dialog.task['name'].lower()
        #finalrigpath=self.dialog.publish_root+'/'+self.dialog.version_name
        #version=finalrigpath.split('.')[-1]
        #finalrigpath=finalrigpath.replace('.'+version,'')
        #finalRigging=finalrigpath.replace(task,'rigging')
        #filename=finalRigging.split('/')[-1].split('.')[0]
        filename=self.dialog.entity['name']
        self.dialog.anim_file=self.dialog.version_dir+'/anim_rig/'
        self.dialog.blok_rig=self.dialog.version_dir+'/blok_rig/'

        blocking_path = os.path.normpath(self.dialog.version_dir.split("rigging")[0]+"rigging_blocking" + os.sep + filename + '.ma')
        print "blocking_path",blocking_path

        if os.path.isfile(blocking_path):
            if not os.path.exists(self.dialog.blok_rig):
                print 'create blok rig folder'
                os.mkdir(self.dialog.blok_rig)
            shutil.copyfile(blocking_path,self.dialog.blok_rig+os.sep+filename+'.ma')
            shutil.copyfile(blocking_path,self.dialog.blok_rig+os.sep+filename+'.mb')

        elif cmds.objExists('master.blok_rig_path'):
            if os.path.isfile(os.path.normpath(cmds.getAttr("master.blok_rig_path")or"")):
                file_path = os.path.normpath(cmds.getAttr("master.blok_rig_path")or"")
                if not os.path.exists(self.dialog.blok_rig):
                    print 'create blok rig folder'
                    os.mkdir(self.dialog.blok_rig)
                shutil.copyfile(file_path,self.dialog.blok_rig+os.sep+filename+'.ma')
                shutil.copyfile(file_path,self.dialog.blok_rig+os.sep+filename+'.mb')
                print 'copy blok rig to folder'

        if not self.dialog.project['name'].upper() == 'GOD':
            if not os.path.exists(self.dialog.anim_file):
                print 'create anim rig folder'
                os.mkdir(self.dialog.anim_file)
            try:
                set_attr_value('visibility_ctrl.proxy_vis',1)
                set_attr_value('visibility_ctrl.tech_rig_vis',0)
                set_attr_value('visibility_ctrl.anim_rig_vis',1)
                set_attr_value('visibility_ctrl.proxy_type_vis',1)
                set_attr_value('visibility_ctrl.special_deformer_state',0)
                # set_attr_lock('visibility_ctrl.proxy_vis',1)
                set_attr_lock('visibility_ctrl.tech_rig_vis',1)
                set_attr_lock('visibility_ctrl.anim_rig_vis',1)
                set_attr_lock('visibility_ctrl.proxy_type_vis',1)
                set_attr_lock('visibility_ctrl.special_deformer_state',1)

                self.dialog.facial_points = []
                if pm.objExists("facial_CtrlGrp") and pm.objExists("facial_head_geo"):
                    head_geo = pm.PyNode("facial_head_geo")
                    head_geo_shape = head_geo.getShape()
                    attr_list = [["jaw_M_ctrl.rotateX", 30],
                    ["mouth_L_up_1_ctrl.translateY", 1],
                    ["mouth_R_up_2_ctrl.translateY", 1],
                    ["mouth_L_dn_1_ctrl.translateY", -1],
                    ["mouth_R_dn_1_ctrl.translateY", -1],
                    ["brow_R_all_ctrl.translateY", -1],
                    ["brow_L_all_ctrl.translateY", -1]]
                    for attr,value in attr_list:
                        # Modified by Sheng Liao on 2021/11/11 ------------------
                        # Note that special characters may not have some facial controllers,
                        # like the "three ass monster" of the NYJ project.
                        if not cmds.objExists(attr):
                            continue
                        if cmds.getAttr(attr, lock=True):
                            continue
                        # ------------------ Modified by Sheng Liao on 2021/11/11
                        pm.setAttr(attr,value)
                        points_length = sum(head_geo_shape.getPoints()).length()
                        pm.setAttr(attr,0)
                        self.dialog.facial_points.append(points_length)

                pm.select("|master", r=True)
                assets = cmds.ls(type='container')
                if assets:
                    pm.select(assets, add=True)
                # pm.exportSelected(self.dialog.anim_file + filename + '.ma', force=True, options="v=0;", type="mayaAscii", pr=True, es=True)
                # pm.exportSelected(self.dialog.anim_file + filename + '.mb', force=True, options="v=0;", type="mayaBinary", pr=True, es=True)
                pm.saveAs(self.dialog.anim_file + filename + '.ma', type='mayaAscii', force=True)
                pm.saveAs(self.dialog.anim_file + filename + '.mb', type='mayaBinary', force=True)
                pm.select(cl=True)
                return ""
            except:
                return traceback.format_exc()

        else:
            return ""


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
