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
from production.shotgun_connection import Connection
reload(clpp)

def normal_path(input_path):
    cur_path = os.path.normpath(input_path)
    cur_path = cur_path.replace("\\", "/")
    return cur_path

def add_lca_look_pass(project,chr_name):
    if 1:
        sg = Connection('get_project_info').get_sg()
        proj = sg.find_one('Project', [['name', 'is', project]], [])
        crd_color = sg.find_one('Asset', [['project', 'is', proj], ['code', 'is', chr_name]], ['sg_look_passes_1','parents','sg_asset_type'])
        look_pass_list = crd_color.get('sg_look_passes_1')

        find_pass_list = []
        for _pass in look_pass_list:
            look_pass = sg.find_one("CustomEntity03",[['id', 'is', _pass.get("id")]], ['created_at', 'code'])
            find_pass_list.append(look_pass)

        name_date = {}
        for item in find_pass_list:
            date_i = item['created_at']
            name = item['code']
            name_date[name] = str(date_i)
        add_att_list = [key for key, value in sorted(name_date.items(), key=lambda item: item[1])]


        Attr = "visibility_ctrl.lookPass"
        list_old = []
        if cmds.objExists(Attr):
            list_old = cmds.attributeQuery('lookPass', node='global_ctrl', listEnum=True)[0].split(":")
        if add_att_list:
            for i in add_att_list:
                if i not in list_old:
                    list_old.append(i)

        for a in ['global_ctrl.lookShaderList', 'global_ctrl.lookXmlFile']:
            if cmds.objExists(a):
                cmds.deleteAttr(a)


        if list_old:
            enum = list_old[:]
            if "default" not in enum:
                enum.insert(0,"default")
            enums = ":".join(enum)
            if cmds.objExists('global_ctrl.lookPass'):
                cmds.addAttr('global_ctrl.lookPass', e=1, enumName=enums)
            else:
                cmds.addAttr("global_ctrl",ln="lookPass",at="enum",en =enums )
            drv_Attr = "%s.%s"%("global_ctrl","lookPass")

        pass_color = cmds.addAttr("global_ctrl.lookPass", q=1, enumName=1)
        if cmds.objExists(Attr):
            cmds.addAttr(Attr, e=1, enumName=pass_color)
        else:
            cmds.addAttr(Attr.split(".")[0],ln="lookPass" ,at="enum" ,en = pass_color,k=1)
            cmds.connectAttr(Attr, "global_ctrl.lookPass", f=1)




class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查 lookPass"
        self.description = u"检查 lookPass"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            if cmds.objExists('master'):
                #listdirTemp = cmds.getAttr("master.modPath")
                #listdir = normal_path(listdirTemp)
                #charName = os.path.split(listdir)[1].split('.')[0]
                #project = re.findall('(?<=projects/)\w+', listdir)[0]
                #add_lca_look_pass(project, charName)
                import srf.push_shader.push_rig_shader as sp
                reload(sp)
                sp.push_rig_shader()
        except:
            print('fail to get pass')
        try:
            print('start check')
            returnInfo = ''
            returnInfo1 = self.check_lookPass_match()
            if returnInfo1:
                returnInfo = str(returnInfo1)
                print(returnInfo)
            return returnInfo
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

    def normal_path(self,input_path):
        cur_path = os.path.normpath(input_path)
        cur_path = cur_path.replace("\\", "/")
        return cur_path

    def convertEnumToList(self,enum_names):
        input_str = str(enum_names)
        if input_str.startswith(u"[u'") and input_str.endswith(u"']"):
            cleaned_str = input_str[3:-2]
            result_list = cleaned_str.split(':')
            return result_list
        else:
            print("Input string format doesn't match expected pattern.")

    def checkIfPassValueDefault(self,lookPassAttr):
        if cmds.objExists(lookPassAttr):
            if cmds.getAttr(lookPassAttr) != 0:
                return('please change pass value to default')
            else:
                return
    def check_lookPass_match(self): # check if lookPass is match for shotgun
        # get shotgun lookPass info
        import re
        from production.shotgun_connection import Connection
        listdirTemp = cmds.file(q= True, sn= True)
        listdir = self.normal_path(listdirTemp)
        # Find the name after 'chr/'
        if '/chr/' in listdir:
            chr_index = listdir.index('chr/') + len('chr/')
        elif '/prp/' in listdir:
            chr_index = listdir.index('prp/') + len('prp/')
        elif '/crd/' in listdir:
            chr_index = listdir.index('crd/') + len('crd/')
        else:
            return
        chr_name = listdir[chr_index:].split('/')[0]

        # Find the name after 'projects/'
        projects_index = listdir.index('projects/') + len('projects/')
        projects_name = listdir[projects_index:].split('/')[0]

        sg = Connection('get_project_info').get_sg()
        proj = sg.find_one('Project', [['name', 'is', projects_name]], [])
        crd_color = sg.find_one('Asset', [['project', 'is', proj], ['code', 'is', chr_name]],
                                ['sg_look_passes_1', 'parents', 'sg_asset_type'])
        lookPassLen = len(crd_color.get('sg_look_passes_1'))
        result_list = []

        lookPassNameList = crd_color.get('sg_look_passes_1')
        names_list = [entity['name'] for entity in lookPassNameList]
        names_list.append('default')
        #names_list.insert(0, 'default')

        # get current file lookPass info
        lookPassAttr = ""
        lookPassAttr1 = "visibility_ctrl.lookPass"
        lookPassAttr2 = "visibility_ctrl.LookPass"
        lookPassAttr3 = "visibility_ctrl.Lookpass"
        lookPassAttr4 = "visibility_ctrl.lookpass"
        lookPassAttr5 = "visibility_ctrl.look_Pass"
        lookPassAttr6 = "visibility_ctrl.Look_Pass"
        lookPassAttr7 = "visibility_ctrl.Look_pass"
        lookPassAttr8 = "visibility_ctrl.look_pass"

        if cmds.objExists(lookPassAttr1):
            lookPassAttr = lookPassAttr1
        elif cmds.objExists(lookPassAttr2):
            lookPassAttr = lookPassAttr2
        elif cmds.objExists(lookPassAttr3):
            lookPassAttr = lookPassAttr3
        elif cmds.objExists(lookPassAttr4):
            lookPassAttr = lookPassAttr4
        elif cmds.objExists(lookPassAttr5):
            lookPassAttr = lookPassAttr5
        elif cmds.objExists(lookPassAttr6):
            lookPassAttr = lookPassAttr6
        elif cmds.objExists(lookPassAttr7):
            lookPassAttr = lookPassAttr7
        elif cmds.objExists(lookPassAttr8):
            lookPassAttr = lookPassAttr8

        if lookPassAttr or crd_color.get('sg_look_passes_1'):
            if cmds.objExists(lookPassAttr):
                cmds.connectAttr(lookPassAttr, "global_ctrl.lookPass", f=1)
                if cmds.attributeQuery(lookPassAttr.split(".")[1], node=lookPassAttr.split(".")[0], exists=True):
                    enum_names = cmds.attributeQuery(lookPassAttr.split(".")[1], node=lookPassAttr.split(".")[0],
                                                     listEnum=True)

                    result_list = self.convertEnumToList(enum_names)
                    print('shotgunlookPass: ', crd_color.get('sg_look_passes_1'))
                    print('lookPassLenth: ', lookPassLen)
                    print('enum_names: ', result_list)
                    print('enum_names_lenth: ', len(result_list))
                    print('shotgun_names', names_list)
                    if set(names_list) == set(result_list):
                        if cmds.objExists('global_ctrl.lookPass'):
                            cmds.deleteAttr('global_ctrl.lookPass')
                        enum_options = ":".join(result_list)
                        cmds.addAttr('global_ctrl', longName='lookPass', attributeType='enum', enumName=enum_options)
                        cmds.setAttr('global_ctrl.lookPass', edit=True, cb=False)
                        cmds.connectAttr(lookPassAttr, 'global_ctrl.lookPass', f=1)
                        return self.checkIfPassValueDefault(lookPassAttr)
                    else:
                        return 'lookPass not match shotgun info, might by reused character, please recreate attribute'
            else:
                return 'please create lookPass attribute'
        else:
            return

