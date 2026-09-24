# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.05
#
# Description: 
#
# Maintainer: by guo 2016.8.16
############################################
import os
import traceback
import shutil
import pymel.core as pm
from sgtk.platform.qt import QtGui
import maya.cmds as cmds
import maya.mel as mel
import maya.OpenMaya as om
import math
import edo_publishListUI.edo_autoCombineFacialRigging_shotgun as edo_autoCombineFacialRigging_shotgun;reload(edo_autoCombineFacialRigging_shotgun)

import rigsystem.tools.tyh_autoCombineFacialRigging as combine_facial_rigging


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"===========自动上传RIGGING TASK============"
        self.description = u"如果第一页publish时是成品: 那么便自动合并上传final_rigging。"
        return

    def getRiggingWorkVersion(self):
        currentfilename=cmds.file(q=1,sn=1)
        currentfileshnname=cmds.file(q=1,sn=1,shn=1)
        currentpath=currentfilename.replace(currentfileshnname,'')
        riggingfilename=currentfilename.replace('.rigging_body.','.rigging.').replace('.rigging_facial.','.rigging.')
        version=riggingfilename.split('.')[-2]
        riggingfilename=riggingfilename.split(version)[0]
        riggingfilesname=riggingfilename.split('/')[-1]
        allfiles=os.listdir(currentpath)
        maxversion=''
        maxid=0
        for f in allfiles:
            #f=allfiles
            #f='golden_pig.rig.rigging.v001.ma'
            ff=currentpath+f
            if riggingfilename in ff:
                #print f
                version=f.split(riggingfilesname)[-1].split('.')[0].replace('v','')
                versionid=int(version)
                #print versionid
                if versionid>maxid:
                    maxid=versionid
                    maxversion=version
        newid=maxid+1
        newversion=maxversion.replace(str(maxid),str(newid))[-3:]
        newriggingfilepath=riggingfilename+'v'+newversion+'.ma'
        cmds.file(rn=newriggingfilepath)
        cmds.file( force=True, type='mayaAscii', save=True )
        newriggingfileversion=riggingfilesname+'v'+newversion
        return newriggingfileversion


    def proceed(self):
        #print self.dialog.project['name'].upper()
        try:
            tag=self.dialog.version_tag
            #print tag
            if not tag==u"成品":
                self.dialog.close()
                self.dialog.destroy()
                cmds.confirmDialog( title=u"上传成功", message=u"    上传成功    ", button=[u"确定"],dismissString='No')
                return u"publish 已经成功，UI即将关闭"

            print u"自动导入合并身体设置和表情设置上传rigging task ..."
            # edo_autoCombineFacialRigging_shotgun.edo_combineFcialRigging(0,0)
            edo_autoCombineFacialRigging_shotgun.edo_importFacialAndBodyRig(0,0)
            combine_facial_rigging.combineFacialBodyRiging()

            #set dialig variable
            #
            self.dialog.task = self.dialog.sg.find_one('Task',
                                                       [['entity', 'is', self.dialog.entity],
                                                        ['content', 'is', 'rigging']])
            self.dialog.task['name'] = 'rigging'
            self.dialog.version_name= self.getRiggingWorkVersion()
            self.dialog.version_dir = self.dialog.publish_root + '/' + self.dialog.version_name
            #self.dialog.tank_file = self.dialog.version_dir + '/' + self.dialog.version_name + '.ma'
            self.dialog.tank_file = self.dialog.version_dir + '/' + self.dialog.entity['name'] + '.ma'
            self.dialog.version_key = self.dialog.entity['name'] + '.' + self.dialog.step['name'] + '.' + self.dialog.task['name'].lower()
            #print '<create_dir_on_server>'
            #print 'version_name : '+self.dialog.version_name
            #print 'publish_root : '+self.dialog.publish_root
            print 'version_dir : '+self.dialog.version_dir
            #print '---------------------\n'

            #print '<maya_version_attr>'
            #print "master root tank_file : "+self.dialog.tank_file
            #dept  = self.dialog.step['name']
            #print "entity['name'] : "+self.dialog.entity['name']
            #print "dept=step['name'] : "+self.dialog.step['name']
            #print 'dept+Version : '+dept+'Version'
            #print 'dept+Path : '+dept + 'Path'
            #print '---------------------\n'

            #print '<model_mesh_xml>'
            #print self.dialog.d_assets_info
            for asset_name in self.dialog.d_assets_info.keys():
                #set dictionary
                self.dialog.d_assets_info[asset_name]['version_name']=self.dialog.version_name
                self.dialog.d_assets_info[asset_name]['version_dir']=self.dialog.version_dir
                self.dialog.d_assets_info[asset_name]['tank_file']=self.dialog.tank_file

                #print 
                version_name=self.dialog.d_assets_info[asset_name]['version_name']
                version_dir = self.dialog.d_assets_info[asset_name]['version_dir']
                tank_file=self.dialog.d_assets_info[asset_name]['tank_file']
                #print 'd_assets_info version_name : '+version_name
                #print 'd_assets_info version_dir : '+version_dir
                #print 'd_assets_info tank_file : '+tank_file

                #root = self.dialog.d_assets_info[asset_name]['node']
                #node_name = self.dialog.d_assets_info[asset_name]['node_name']
                #self.dialog.d_assets_info[asset_name]['parent']
                #print 'root : '+root
                #print 'node name : '+node_name
                #print "d_assets_info[asset_name]['parent'] : "+str(self.dialog.d_assets_info[asset_name]['parent'])

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
