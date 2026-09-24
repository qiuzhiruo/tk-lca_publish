# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Guan ZeJie
#
# Date: 2023.03
#
# Description: Check texture name and path
#
############################################

import traceback
import NodegraphAPI
import os
import re


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查贴图文件名名规范。"
        self.description = u"检查贴图文件名名规范。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    def run_check(self):
        try:
            l_maps = []
            l_nameError = []
            l_pathError = []
            pattern = re.compile(
                r"^/mnt/work/projects/[a-z]+/asset/[a-z]+/[a-z,0-9,_]+/srf/task/images/tex/[a-z,0-9,_]+\.[a-z,0-9,_]+(?:\.####|\.<udim>|\.\d{4})*?\.tx$")

            # get SRF images nodes
            for node in NodegraphAPI.GetAllNodesByType('ArnoldShadingNode'):
                if node.getParameter('nodeType').getValue(0) in ['image', 'MayaFile', 'alTriplanar',
                                                                 'TextureRepetition', 'alTriplanarPlus',
                                                                 'Interior']:
                    if not 'SRF_PBR_RIG' in node.getParent().getName() and not "Custom_color_shader_Group" in node.getParent().getName():
                        if node.getParameter('nodeType').getValue(0) == 'image' and \
                                not node.getParameter('parameters.filename.value').getValue(0).startswith(
                                    '$LC_PROJ_PATH/render_lib/shader'):
                            l_maps.append(node)
            # check image path/node name
            for map_node in l_maps:
                nodeName = map_node.getName()
                try:
                    if map_node.getParameter('nodeType').getValue(0) in ['image', 'MayaFile']:
                        path = map_node.getParameter('parameters.filename.value').getValue(0)
                        if pattern.findall(path) == []:
                            l_pathError.append(nodeName)
                    elif map_node.getParameter('nodeType').getValue(0) == 'Interior':
                        interior_parameters = map_node.getParameter('parameters').getChildren()
                        parameters_name_list = ['left', 'Right', 'Back', 'Ceil', 'Floor', 'Front', 'interior']
                        for interior_attr in interior_parameters:

                            if interior_attr.getName() in parameters_name_list:
                                tex = interior_attr.getChild('value').getValue(0)

                                if len(tex) > 0 and '.<SLICE>.' not in tex:
                                    if pattern.findall(tex) == [] or not os.path.isfile(tex):
                                        l_pathError.append(nodeName)

                    else:
                        path = map_node.getParameter('parameters.texture.value').getValue(0)
                        if pattern.findall(path) == [] or not os.path.isfile(path):
                            l_pathError.append(nodeName)
                except:
                    print 'not find parameters : ', nodeName

            if l_nameError:
                return u"节点的贴图名字不符合规范"+u"  ".join(l_nameError) + u"请使用srfFinalize工具重新检查文件"

            if l_pathError:
                return u"节点的贴图路径不符合规范"+u"  ".join(l_pathError) + u"请使用srfFinalize工具重新检查文件"

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