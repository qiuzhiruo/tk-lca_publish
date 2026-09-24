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
        self.check_name = u"检查资产层级命名。"
        self.description = u"资产最上层组为master,其次为rig,poly, hi/lo组。lo组必须有。如果是layout rig任务，只有lo组"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def check_wrongname_pri_and_sec(self):
        wgrps=[]
        ws=self.check_wrongname_sec()
        wp=self.check_wrongname_pri()
        wgrps=ws+wp
        wms=""
        for g in wgrps:
            wms=wms+g+' : the name or hierarchy of this group is wrong.\n'
        print wms
        return wms

    def check_wrongname_sec(self):
        wgrps=[]
        secs=cmds.ls('*_sec_ctrl')
        for sec in secs:
            #sec = secs[0]
            #sec='null1_sec_ctrl'
            cs=cmds.listRelatives(sec,c=1,pa=1)
            #if none child
            if (not cs):
                wgrps.append(sec)
                continue
            else:
                c=cs[0]
                #if has child but wrong name
                if (not sec.replace('_sec_','_pri_')==c):
                    wgrps.append(sec)
                    continue
                else:
                    ccs=cmds.listRelatives(c,c=1,pa=1)
                    #if has no grand child
                    if (not ccs):
                        wgrps.append(sec)
                        continue
                    else:
                        cc=ccs[0]
                        #if has grand child nit wrong name
                        if not sec.replace('_sec_','_')==cc:
                            wgrps.append(sec)
                            continue
        return wgrps
        
    def check_wrongname_pri(self):
        wgrps=[]
        pris=cmds.ls('*_pri_ctrl')
        for pri in pris:
            #pri = pris[0]
            #pri='dsadsa_pri_ctrl'
            cs=cmds.listRelatives(pri,c=1,pa=1)
            #if none child
            if (not cs):
                wgrps.append(pri)
                continue
            else:
                c=cs[0]
                #if has child but wrong name
                if (not pri.replace('_pri_','_')==c):
                    wgrps.append(pri)
                    continue
                else:
                    ps=cmds.listRelatives(pri,p=1,pa=1)
                    #if has no parent
                    if (not ps):
                        wgrps.append(pri)
                        continue
                    else:
                        p=ps[0]
                        #if has grand child nit wrong name
                        if not pri.replace('_pri_','_sec_')==p:
                            wgrps.append(pri)
                            continue
        return wgrps


    def run_check(self):
        headctrl='head_M_ctrl'
        animmoduals='anim_modules_grp'
        globalgrp='root_ctrl'
        headgeo='body_geo'
        facialgeo='head_geo'
        anim_rig='anim_rig'
        rig='rig'
        anim_controls_grp='anim_controls_grp'


        try:
            import pymel.core as pm
            if not cmds.objExists("|master"):
                return u"没有找到最高层的 |master 组。"

            if not cmds.objExists("|master|poly"):
                return u"没有找到次高层的 |master|poly 组。"

            if not cmds.objExists("|master|rig"):
                return u"没有找到次高层的 |master|rig 组。"

            if self.dialog.task['name'].startswith('layout_rig'):
                if cmds.objExists("|master|poly|hi"):
                    return u"如果是layout rig任务,没有hi组,只有lo组"

            #check hirarchy under the master group
            cs=cmds.listRelatives('|master',c=1,pa=1)
            grps=['poly','shape','rig']
            for grp in grps:
                if grp in cs:
                    cs.remove(grp)
            if not (cs==None or cs==[]):
                return u"|master 层级下不能有多余的组,只能有['poly','shape','rig']"

            cs=cmds.listRelatives('|master|rig',c=1,pa=1)
            grps=['anim_rig','tech_rig']
            for grp in grps:
                if grp in cs:
                    cs.remove(grp)
            if not (cs==None or cs==[]):
                return u"|master|rig 层级下不能有多余的组,只能有['anim_rig','tech_rig']"  

            cs=cmds.listRelatives('|master|rig|anim_rig',c=1,pa=1)
            grps=['anim_controls_grp','anim_skeletons_grp','anim_modules_grp']
            for grp in grps:
                if grp in cs:
                    cs.remove(grp)
            if not (cs==None or cs==[]):
                return u"|master|rig|anim_rig 层级下不能有多余的组,只能有['anim_controls_grp','anim_skeletons_grp','anim_modules_grp']"

            if cmds.objExists('|master|rig|tech_rig'):
                cs=cmds.listRelatives('|master|rig|tech_rig',c=1,pa=1)
                grps=['tech_controls_grp','tech_skeletons_grp','tech_modules_grp']
                for grp in grps:
                    if grp in cs:
                        cs.remove(grp)
                if not (cs==None or cs==[]):
                    return u"|master|rig|tech_rig 层级下不能有多余的组,只能有['tech_controls_grp','tech_skeletons_grp','tech_modules_grp']"
                    

            if not cmds.objExists(headctrl):
                return u'找不到名为：'+headctrl+u' 的控制器【所有身体设置头部控制器必须命名为】'+headctrl
            if not cmds.objExists(animmoduals):
                return u'找不到名为：'+animmoduals+u' 的组【所有身体设置必须有名为】'+animmoduals+u'的组，用于放非控制器DAG节点'
            if not cmds.objExists(globalgrp):
                return u'找不到名为：'+globalgrp+u' 的控制器【所有身体设置的Root控制器必须命名为】'+globalgrp
            if not cmds.objExists(headgeo) and not cmds.objExists(facialgeo):
                return u'找不到名为：'+headgeo+u' 的模型  或者  '+facialgeo+u' 的模型【2者必存其1】'
            if not cmds.objExists(anim_rig):
                return u'找不到名为：'+anim_rig+u' 的组【所有身体设置必须有名为】'+anim_rig+u'的组，用于放anim_rig的DAG节点'
            if not cmds.objExists(rig):
                return u'找不到名为：'+rig+u' 的组【所有身体设置必须有名为】'+rig+u'的组，用于放所有rig添加的DAG节点'
            if not cmds.objExists(anim_controls_grp):
                return u'找不到名为：'+anim_controls_grp+u' 的组【所有身体设置必须有名为】'+anim_controls_grp+u'的组，用于放所有anim_rig的控制器节点'

            bodygeoln=cmds.ls(headgeo,l=1)
            isbodyinhi=True
            if bodygeoln:
                bg=bodygeoln[0]
                print bg
                if not '|hi|' in bg:
                    isbodyinhi=False

            headgeoln=cmds.ls(facialgeo,l=1)
            isheadinhi=True
            if headgeoln:
                hg=headgeoln[0]
                print hg
                if not '|hi|' in hg:
                    isheadinhi=False

            if (isbodyinhi==False and isheadinhi==False):
                return headgeo+u' , '+facialgeo+u' 有且只有一个应该放在poly|hi|层级下'

            if (isbodyinhi==True and isheadinhi==True) and bodygeoln and headgeoln:
                return headgeo+u' , '+facialgeo+u' 有且只有一个应该放在poly|hi|层级下'
                
            #if not cmds.objExists("|master|poly|lo"):
            #    return u"没有找到低模 |master|poly|lo 组。"

            n = cmds.ls('visibility_ctrl')
            if not n:
                return u"没有找到 visibility_ctrl 控制器。"

            visattrlist=['mesh_display_type','proxy_vis','facial_panel','char_name','tech_rig_vis','anim_rig_vis']
            for vattr in visattrlist:
                if not cmds.objExists('visibility_ctrl.'+vattr):
                    return u"visibility_ctrl 控制器不是系统生成的，请删除并用系统生成一个新的。"

            check_pri_sec_grp=self.check_wrongname_pri_and_sec()

            return check_pri_sec_grp
            
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


