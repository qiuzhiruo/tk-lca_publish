# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Check asset geometry hierarchy
#
############################################

import traceback
import maya.cmds as cmds
import os
import re
import production.pipeline.lcProdProj as clpp


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查surfacing prameters!"
        self.description = u"检查rigging中添加的prameter是否match在surfacing环节添加的userData"
        self.auto_fix = False
        self.duty = u"艺术家本人 or Surfacing or TD"
        return


    def check_userDataAttribute(self,chrname):
        #chrname='xiaolai'
        cp = clpp.lcProdProj()
        cp.setProj(self.dialog.ctx.project['name'].lower())
        xml=cp.get_srf_mat_info(chrname)
        allexattrs=self.getAllSurfacingPrametersOnMesh()
        #neededattrs=[]
        dataattrs=[]
        msg=u''
        if xml:
            data=cp.get_low_tex_xml_user_data(xml[1])
            #len(data)
            for d in data:
                #d=data[0]
                #print d
                for obj in ["master/hair"]:
                    if obj not in d['path']:
                        objname=d['path'].split('/')[-1]
                        if cmds.objExists(objname):
                            for p in d['parm']:
                                #p=d['parm'][0]
                                attrname=p['name']
                                attrtype=p['type']
                                if not cmds.objExists(objname+'.'+attrname):
                                    msg=msg+u'surfacing 添加的'+objname+'.'+attrname+u'在rigging中不存在\n'
                                dataattrs.append(objname+'.'+attrname)
                        else:
                            msg=msg+u"surfacing 添加了user data 的"+objname+u"在rigging文件中不存在\n"
            for attr in allexattrs:
                if not attr in dataattrs:
                    msg=msg+attr+u"不存在于surfacing的userData中，需要删除此parameter\n"
            #print msg
            return msg

    def getAllSurfacingPrametersOnMesh(self):
        meshes=cmds.ls(type='mesh')
        attrs=[]
        for m in meshes:
            #m=meshes[0]
            #m='L_wpm_eyeoutframe_2Shape'
            ats=cmds.listAttr(m)
            for at in ats:
                if 'lca_' in at:
                    attrname=m+'.'+at
                    #print 'delete attribute : ' + attrname
                    attrs.append(attrname)
        return attrs


    def check_disconnectedSurfacingPrameters(self):
        allattrs=self.getAllSurfacingPrametersOnMesh()
        msg=u""
        for attr in allattrs:
            if not cmds.listConnections(attr,s=1,d=0):
                msg=msg+attr+u"没有被任何属性连接\n"
        return msg


    def run_check(self):
        msg=u''
        try:
            #print 'entity name : '
            #print self.dialog.entity['name']
            checkstat=self.check_userDataAttribute(self.dialog.entity['name'])
            if not checkstat==None:
                msg=msg+checkstat
            msg=msg+self.check_disconnectedSurfacingPrameters()
            return msg
        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        return


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


