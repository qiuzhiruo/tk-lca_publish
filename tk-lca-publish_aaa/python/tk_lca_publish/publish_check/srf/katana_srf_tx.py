# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Check shtogun data
#
############################################

import traceback

import os
import re
from Katana import FarmAPI
import sgtk
from sgtk.platform.qt import QtCore, QtGui
import NodegraphAPI as ngapi

def get_invalid_textures():
    ard_shd_nodes = ngapi.GetAllNodesByType('ArnoldShadingNode')
    invalid_image_node={'not_tex':[],'no_tex':[],'name':[]}
    filename_re= re.compile("[\w\.<>#%]*$")
    for asn in ard_shd_nodes:
        if asn.isBypassed():
            continue

        asn.checkDynamicParameters()
        nt_param = asn.getParameter('nodeType')
        if not nt_param:
            continue
        node_type = nt_param.getValue(0)
        shader_node_name = asn.getName()
        if node_type == 'MayaFile' or node_type=='image':

            param = asn.getParameter('parameters.filename.value')
            tex = param.getValue(0)
            if not tex:
                continue

            if not tex.endswith('.hdr') and not tex.endswith('.tx'):
                if os.path.basename(tex) != "check_chr_sss.exr":
                    invalid_image_node['not_tex'].append(shader_node_name+' : '+tex)

            if not filename_re.match(os.path.basename(tex)):
                invalid_image_node['name'].append(shader_node_name+' : '+tex)

    return invalid_image_node

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查提交的Katana文件中tx文件是否合格，场景内只能有hdr,tx。"
        self.description = u"检查提交的Katana文件中tx文件是否合格，场景内只能有hdr,tx。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def check_path(self, path, key):
        p = re.compile("[\w\.]*$")
        tokens = path.replace(":", "\\").replace("/", "\\").split("\\")
        for token in tokens:
            if not p.match(token):
                return key + u" 各级文件夹需要由a-z的字母，0-9数字，下划线\"_\"和点\".\"组成:\n  " + path

        return ''

    def run_check(self):

        try:
            if int(self.dialog.w_publish_file.checkBox.isChecked()):
                return ''
            invalid_tex = get_invalid_textures()
            if invalid_tex.get('no_tex',[]):
                no_tx = '\n'.join(invalid_tex.get('no_tex',[]))
                return u'不存在的tx文件\n'+no_tx

            if invalid_tex.get('not_tex',[]):
                not_tx = '\n'.join(invalid_tex.get('not_tex',[]))
                return u'非tx文件\n'+not_tx

            if invalid_tex.get('name',[]):
                not_tx = '\n'.join(invalid_tex.get('name',[]))
                return u'tx文件名称不合格，只能用数字,字母,_,<,>组成\n'+not_tx

            return''
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


