#-*- coding:utf-8 -*-
__author__ = 'yingjie'


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
import sgtk
from sgtk.platform.qt import QtCore, QtGui
import NodegraphAPI as ngapi
import common.katanaUtils as cku
import traceback
import shutil


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查贴图路径是否规范"
        self.description = u"检查贴图路径是否规范，符合/mnt/work/projects/ <proj> /asset/ <type> / <asset> /srf/task/images"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def get_invalid_textures(self):
        ard_shd_nodes = ngapi.GetAllNodesByType('ArnoldShadingNode')
        invalid_image_node={'invalid_path':[]}
        tex_path_re=re.compile('\S/work/projects/([a-z]{3})/asset/\w+/(\w+)/srf/task/images')

        for asn in ard_shd_nodes:
            if asn.isBypassed() or 'SRF_PBR_RIG' in cku.get_node_full_path(asn):
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
                if not tex or tex.startswith('$LC_PROJ_PATH/render_lib/shader'):
                    continue

                if tex.endswith('.tx'):
                    tx_analyze=re.findall(tex_path_re,tex)
                    if not tx_analyze:
                        invalid_image_node['invalid_path'].append((shader_node_name,tex))
                        continue

        return invalid_image_node

    def run_check(self):
        try:
            if int(self.dialog.w_publish_file.checkBox.isChecked()):
                return ''
                
            invalid_tex=self.get_invalid_textures()

            error_info=''
            for p in invalid_tex.get('invalid_path',[]):
                error_info+=(u'发现这些节点：\n [%s], 使用非法贴图路径: %s' % \
                    (p[0],\
                     p[1],\
                    ))
            
            if error_info:
                error_info+= u'\nTx 路径必须满足格式 : /mnt/work/projects/ <proj> /asset/ <type> / <asset> /srf/task/images'

            return error_info
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


