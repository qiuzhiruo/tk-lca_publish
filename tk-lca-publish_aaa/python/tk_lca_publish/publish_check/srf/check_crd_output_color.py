# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Guan ZeJie
#
# Date: 2023.01
#
# Description: Check shtogun data
#
############################################

import traceback
import NodegraphAPI as ngapi
from production.shotgun_connection import Connection
sg = Connection('get_project_info').get_sg()


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查带crd_face_pass的crd资产颜色吸取节点。"
        self.description = u"检查带crd_face_pass的crd资产颜色吸取节点。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            proj =self.dialog.project['name']
            asset_name = self.dialog.entity['name']
            flt = [['project', 'name_is', proj.upper()], ['code', 'is', asset_name]]
            asset_info = self.dialog.sg.find_one('Asset', flt, ['code', 'tag_list'])
            if 'crd_face_pass' not in asset_info['tag_list']:
                return ''

            look_file_color_nodes = ngapi.GetAllNodesByType('Group')
            look_color = ngapi.GetNode('LookPass_Color_Export')
            if not look_color and look_file_color_nodes:
                for child in look_file_color_nodes:
                    if "LookPass_Color_Export" in child.getName():
                        look_color = child
                        break
                    if 'LookPass_Color_SRF' in child.getName():
                        look_color = child
                        break
            look_file_bake_nodes = ngapi.GetAllNodesByType('LookFileBake')
            look_file = ngapi.GetNode('LookFileBake')
            if not look_file and look_file_bake_nodes:
                for child in look_file_bake_nodes:
                    if "LookFileBake" in child.getName():
                        look_file = child
                        break
            if not look_file:
                return u'没找到LookFileBake节点'
            if not look_color:
                return u'没找到LookPass_Color_Export节点'

            port_list = []
            for port in look_file.getInputPorts():
                prot_name = port.getName()
                if 'orig' in prot_name:
                    continue
                port_list.append(prot_name)

            color_grp = look_color.getParameter('user.color_grp')
            if not color_grp:
                return u'LookPass_Color_Export节点错误，请换一个新节点'
            if not color_grp.getChildren():
                return u'LookPass_Color_Export节点，没有点击设置颜色'

            color_list = []
            color_dict = {}
            for chi in color_grp.getChildren():
                color_list.append(chi.getName())
                color = []
                for v in chi.getChildren():
                    color.append(v.getValue(0))
                color_dict[chi.getName()] = color

            if len(port_list) != len(color_list):
                return u'LookPass_Color_Export节点LookPass数量不对'
            else:
                for i in port_list:
                    if i not in color_list:
                        return u'LookPass_Color_Export节点LookPass名字错误'

            for key, value in color_dict.items():
                if not sum(value):
                    return u'LookPass_Color_Export节点，没有设置颜色'

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
