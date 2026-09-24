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
import json
from production.shotgun_connection import Connection
sg = Connection('get_project_info').get_sg()


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查 rigPass"
        self.description = u"检查 rigPass"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            print('start check')
            returnInfo = ''
            returnInfo1 = self.check_rigPass_match()
            if returnInfo1:
                returnInfo = str(returnInfo1)

            # set pass key
            attr_list = ['headHair', 'faceHair', 'facePass', 'rigPass', 'lookPass', 'rigPass']
            ctrl_name = 'visibility_ctrl'
            for i in attr_list:
                attr_name = '{}.{}'.format(ctrl_name, i)
                if cmds.objExists(attr_name):
                    cmds.setAttr(attr_name, keyable=True)

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
    def normal_path(self, input_path):
        import os
        cur_path = os.path.normpath(input_path)
        cur_path = cur_path.replace("\\", "/")
        return cur_path
    def get_rig_pass(self, project, char):
        project = sg.find_one('Project', [['name', 'is', project]], [])
        entity = sg.find_one('Asset', [['project', 'is', project], ['code', 'is', char]])
        asset = sg.find_one('Asset', [['id', 'is', entity['id']]], ['sg_rig_passes'])
        return asset

    def read_json_from_file(self, filename):
        with open(filename, 'r') as f:
            return json.load(f)

    def get_publish_rigPass_info(self, rigPass_attr):
        if rigPass_attr == "":
            return
        file_rigPass = rigPass_attr.split('.')[-1]
        path = cmds.file(q=True, sn=True)
        chr_name = path.split("/rig")[0].split("/")[-1]
        proj = path.split("projects/")[-1].split("/asset")[0]
        sector = path.split("/rig")[0].split("/")[-2]
        publish_path = r'{0}/projects/{1}/asset/{2}/{3}/rig/publish'.format(
            os.environ['LC_PROJ'], proj, sector, chr_name)

        dir_array = os.listdir(publish_path)

        json_path_array = []
        for each_dir in dir_array:
            json_path = os.path.normpath(os.path.join(publish_path, each_dir, "rig_pass_info.json"))
            if os.path.isfile(json_path):
                ctime = os.path.getctime(json_path)
                json_path_array.append([json_path, ctime])

        json_rigPass_array = []
        json_path_array.sort(key=lambda x: x[1])  # rigPassInfo创建时间从早到晚排序
        for path, ctime in json_path_array:
            json_rigPass = self.read_json_from_file(path)["pass_info"]["rigPass_name"].split(".")[-1]
            json_rigPass_array.append(json_rigPass)

        if len(json_rigPass_array) == 0:
            if file_rigPass != "rigPass":
                return (
                    "publish for the first time, the rigpass name must be (rigPass). current:({})".format(file_rigPass))
        else:
            if json_rigPass_array[-1] == "":
                return
            if file_rigPass != json_rigPass_array[-1]:
                return (("RigPass attribute name is different from before, (must use 'rigPass')     ") +
                        ("current name: ({}), before name: ({})".format(file_rigPass, json_rigPass_array[-1])))
        return

    def check_rigPass_match(self):
        rigPassAttr = ""
        rigPassAttr1 = "visibility_ctrl.rigPass"
        rigPassAttr2 = "visibility_ctrl.RigPass"
        rigPassAttr3 = "visibility_ctrl.Rigpass"
        rigPassAttr4 = "visibility_ctrl.rigpass"
        rigPassAttr5 = "visibility_ctrl.rig_Pass"
        rigPassAttr6 = "visibility_ctrl.Rig_Pass"
        rigPassAttr7 = "visibility_ctrl.Rig_pass"
        rigPassAttr8 = "visibility_ctrl.rig_pass"
        rigPassAttr9 = "visibility_ctrl.pear_state"
        rigPassAttr10 = "visibility_ctrl.handle_bar_state"
        rigPassAttr11 = "visibility_ctrl.Book_open"
        if cmds.objExists(rigPassAttr1):
            rigPassAttr = rigPassAttr1
        elif cmds.objExists(rigPassAttr2):
            rigPassAttr = rigPassAttr2
        elif cmds.objExists(rigPassAttr3):
            rigPassAttr = rigPassAttr3
        elif cmds.objExists(rigPassAttr4):
            rigPassAttr = rigPassAttr4
        elif cmds.objExists(rigPassAttr5):
            rigPassAttr = rigPassAttr5
        elif cmds.objExists(rigPassAttr6):
            rigPassAttr = rigPassAttr6
        elif cmds.objExists(rigPassAttr7):
            rigPassAttr = rigPassAttr7
        elif cmds.objExists(rigPassAttr8):
            rigPassAttr = rigPassAttr8
        elif cmds.objExists(rigPassAttr9):
            rigPassAttr = rigPassAttr9
        elif cmds.objExists(rigPassAttr10):
            rigPassAttr = rigPassAttr10
        elif cmds.objExists(rigPassAttr11):
            rigPassAttr = rigPassAttr11

        listdirTemp = cmds.file(q=True, sn=True)

        # 检查 如果是第一次提交，rigPass 名称必须是 “rigPass”
        rigPass_info = self.get_publish_rigPass_info(rigPassAttr)
        if rigPass_info:
            return rigPass_info

        # charName = os.path.split(listdir)[1].split('.')[0]
        # project = re.findall('(?<=projects/)\w+', listdir)[0]
        # Find the name after 'chr/'
        listdir = self.normal_path(listdirTemp)
        if '/chr/' in listdir:
            chr_index = listdir.index('chr/') + len('chr/')
        elif '/prp/' in listdir:
            chr_index = listdir.index('prp/') + len('prp/')
        elif '/crd/' in listdir:
            chr_index = listdir.index('crd/') + len('crd/')
        else:
            return
        charName = listdir[chr_index:].split('/')[0]

        # Find the name after 'projects/'
        projects_index = listdir.index('projects/') + len('projects/')
        project = listdir[projects_index:].split('/')[0]
        shotgunrigPass = self.get_rig_pass(project, charName).get('sg_rig_passes')
        rigPassLenth = len(shotgunrigPass)

        if rigPassAttr or shotgunrigPass:
            if cmds.objExists(rigPassAttr):
                enum_names = cmds.attributeQuery(rigPassAttr.split(".")[1], node=rigPassAttr.split(".")[0],
                                                 listEnum=True)
                result_list = self.convertEnumToList(enum_names)
                print('rig pass info:' + "-"*100)
                print('shotgunrigPass: ', shotgunrigPass)
                print('rigPassLenth: ', rigPassLenth)
                print('enum_names: ', result_list)
                print('enum_names_lenth: ', len(result_list))

                # 检查文件中rig pass 的数量和 shotgun 上记录的数量是否一致
                if rigPassLenth + 1 != len(result_list):
                    return('  current rigPass not match shotgun, please update rigPass')

                # 上述检查数量一致时，按顺序检查名称是否一致
                sg_attribute_list = []
                for i in shotgunrigPass:
                    entity_type = i["type"]
                    entity_id = i["id"]
                    filters = [['id', 'is', entity_id]]
                    fields = ['sg_attribute']
                    sg_attribute = sg.find(entity_type, filters, fields)[0]["sg_attribute"]
                    sg_attribute_list.append(sg_attribute.split(".")[-1])

                print('current file rigPass:  ', result_list)
                print('shotgun rigPass:  ', sg_attribute_list)

                for i, item in enumerate(result_list):
                    if i == 0:
                        if not item == "default":
                            return ('  rigPass default name is error !!! ')
                    else:
                        if not item in sg_attribute_list:
                            return ('  rigPass name is error !!! ({})'.format(item))
                        sg_attribute_list.remove(item)

                if not len(sg_attribute_list) == 0:
                    return 'CHECK redundant rigPass !!!'

                # 检查rig pass 的值是否是 default
                return self.checkIfPassValueDefault(rigPassAttr)

            else:
                return 'please create rigPass attribute'
        else:
            return





