# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: huangxin
#
# Date: 2019.4
#
# Description: As the description shows below
#
#export xgen guides
#
############################################

import os, shutil,sys
import traceback
import pymel.core as pm
import maya.cmds as cmds

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出xgen导线"
        self.description = u"将master下所有description的导线全部导出成一个abc文件，添加xgenDescription属性记录所属description."
        return


    def proceed(self):
        try:
            if 'cloth' in self.dialog.task['name']:
                return ''
            if not pm.ls(type='xgmDescription'):
                return ''
            des_info={}
            for des_node in pm.listRelatives('|master', ad=True, type='xgmDescription'):
                description = str(des_node)
                des_trans = str(des_node.getParent())
                des_name = des_trans.split(':')[-1]
                
                curves =[]
                for c in pm.listRelatives(des_trans, c=1, ad=1, typ='nurbsCurve'):
                    if not pm.attributeQuery('xgenDescription',node=c,ex =1):
                        pm.addAttr(c,longName='xgenDescription', dataType ='string')
                    c.attr('xgenDescription').set(des_name)
                    curves.append(c)

                if len(curves) > 0:
                    curveGroup = curves[0].getParent().getParent().longName()
                else:
                    curveGroup = None
                
                des_info[des_name] = {'des_name': des_name,
                    'curves': curves,
                    'curveGroup': curveGroup
                }
                
            pm.select(cl=1)
            for des_name, value in des_info.items():
                if value["curveGroup"]:
                    pm.select(value["curveGroup"], add=1)

            if cmds.ls(sl=1):
                filepath = self.dialog.version_dir + '/xgen/guides/guides.abc'
                dir = os.path.dirname(filepath)
                if not os.path.isdir(dir):
                    os.makedirs(dir)
                abcOptions = ' -stripNamespaces -worldSpace -dataFormat ogawa -attrPrefix xgen -uvWrite'
                abcCommandString = abcOptions + ' -root ' + ' -root '.join(cmds.ls(sl=1)) + ' -file ' + filepath
                frame = cmds.currentTime( query=True )
                abcCommandString = '-frameRange ' + str(frame) + ' ' + str(frame) + ' ' + abcCommandString

                print "Export guides abc Command string: %s" % abcCommandString
                cmds.AbcExport(j=abcCommandString)
            
            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
