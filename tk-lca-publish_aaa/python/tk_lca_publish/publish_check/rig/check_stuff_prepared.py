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



# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查其他模块的rigging rask是否都已经上传[rigging_body 或者 rigging_facial]"
        self.description = u"检查其他模块的rigging rask是否都已经上传[rigging_body 或者 rigging_facial],如果检查不通过，请在publish第一页选择上传模块，等所有task都上传时在合并final rigging上传"
        self.auto_fix = False
        self.duty = u"Rig TD。"
        return

    def edo_getLastVersionStr(self,root,task):
        #root=root
        #task=bodyrigtask
        alldirs=os.listdir(root)
        version=-1
        maxversion=''
        for dir in alldirs:
            #dir=alldirs[11]
            #print dir
            if task in dir:
                #print dir
                vstr = dir.split(task)[-1]
                #vstr=dir.replace(task,'')
                vid=int(vstr.replace('v',''))
                #print vid
                if vid>version:
                    version=vid
                    maxversion=vstr
        print maxversion
        return maxversion

    def run_check(self):
        try:
            tag=self.dialog.version_tag
            print tag
            if tag==u"成品":
                task=self.dialog.task['name'].lower()
                print "current task name is : "+task
                neededStuff=self.dialog.publish_root+'/'+self.dialog.version_name
                version=neededStuff.split('.')[-1]
                neededStuff=neededStuff.replace('.'+version,'')
                finalRigging=neededStuff.replace(task,'rigging')
                root = self.dialog.publish_root+'/'
                print 'root path is : ' + root
                print finalRigging
                if not os.path.exists(finalRigging):
                    return u"第一次表情身体设置合并不支持自动合并上传，请选择上传<模块>模式重新上传，再在rigging task中合并final rig上传"
                #help(self.dialog)
                if task=='rigging_body':
                    #neededStuff=neededStuff
                    neededStuff=neededStuff.replace(task,'rigging_facial.')
                    facialvstr=self.edo_getLastVersionStr(root,'.rig.rigging_facial.')
                    print "facialvstr : "+facialvstr
                    neededStuff=neededStuff+facialvstr
                    print "neededStuff : "+neededStuff
                    if not os.path.exists(neededStuff):
                        return u"表情设置还未被上传"
                if task=='rigging_facial':
                    neededStuff=neededStuff.replace(task,'rigging_body.')
                    bodyvstr=self.edo_getLastVersionStr(root,'.rig.rigging_body.')
                    print "bodyvstr : "+bodyvstr
                    neededStuff=neededStuff+bodyvstr
                    print "neededStuff : "+neededStuff
                    if not os.path.exists(neededStuff):
                        return u"身体设置还未被上传"
            return ""

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


