# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Guan ZeJie
#
# Date: 2022.0826
#
# Description: Check shtogun data
#
############################################

import traceback
import os
import re
from PIL import Image
import NodegraphAPI as ngapi

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查提交的Katana文件中自定义贴图是否合格。"
        self.description = u"检查提交的Katana文件中自定义贴图是否合格。"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def find_path(self,tx_path):
        udim_list = []
        try:
            path_list = os.listdir(os.path.dirname(tx_path))
            name_split = tx_path.split(".<udim>.")
            re_scr = name_split[0] + "\.\d{4}\." + name_split[1]

            for path in path_list:
                path_tx_file = re.match(re_scr, os.path.dirname(tx_path) + "/" + path)
                if path_tx_file:
                    name = path_tx_file.group()
                    udim_list.append(name)
            return udim_list
        except:
            return udim_list

    # 递归找到所有的材质组
    def do_get_group(self,mtl_group):
        connectedPort = mtl_group.getInputPorts()
        if len(connectedPort):
            for out_port in connectedPort:
                connectedPort = out_port.getConnectedPort(0)
                if not connectedPort:
                    mtl_group.removeInputPort(out_port.getName())
                    continue
                n_group = connectedPort.getNode()

                if n_group in self.retun_list:
                    continue

                if n_group.getType() == "Group":
                    self.retun_list.append(n_group)

                if n_group.getType() == "Merge":
                    self.do_get_group(n_group)

                if n_group.getInputPorts():
                    self.do_get_group(n_group)

        return


    def run_check(self):
        try:
            self.retun_list = []
            color_file_warn = []
            texture_file_warn = []
            texture_file_error = []
            all_merge_note = []
            mtl_Merge = ngapi.GetNode('srf_mtl_Merge')
            if mtl_Merge:
                mtl_group_list = mtl_Merge.getInputPorts()
                for out_port in mtl_group_list:
                    connectedPort = out_port.getConnectedPort(0)
                    if not connectedPort:
                        mtl_Merge.removeInputPort(out_port.getName())
                        continue
                    mtl_group = connectedPort.getNode()

                    if mtl_group.getType() == "Group":
                        all_merge_note.append(mtl_group)

                    if mtl_group.getType() == "Merge":
                        # print mtl_group.getInputPorts()
                        self.do_get_group(mtl_group)
                    if mtl_group.getInputPorts():
                        self.do_get_group(mtl_group)

                all_merge_note.extend(list(set(self.retun_list)))

                for mtl_M in all_merge_note:
                    print mtl_M

                if all_merge_note:
                    for merge_n in list(set(all_merge_note)):
                        customShader_note = merge_n.getParameter('user.customShader')
                        customPass_note = merge_n.getParameter('user.customPass')
                        if customShader_note:
                            customShader = customShader_note.getValue(0)
                            if customShader == "Texture":
                                customTexture = merge_n.getParameter('user.customTexture').getValue(0)
                                tex_path_re = re.compile('\S/work/projects/([a-z]{3})/asset/\w+/(\w+)/srf/task/images')
                                tx_analyze = re.findall(tex_path_re, customTexture)
                                if not tx_analyze:
                                    return merge_n.getName() + u" --> NodeName = " + customTexture + u"！！！自定义贴图存放位置错误，请放在image文件夹"

                                if "udim" in customTexture:

                                    file_list_path = self.find_path(customTexture)

                                    if customTexture:
                                        if file_list_path:
                                            texture_file_warn.append(merge_n.getName() + u" --> customShader设置为Texture")
                                        else:
                                            texture_file_error.append(
                                                merge_n.getName() + u" --> NodeName = " + customTexture + u"！！！自定义贴图丢失或已经损坏")
                                    else:
                                        texture_file_error.append(merge_n.getName() + u" --> customShader设置为Texture却没有赋予贴图")
                                else:
                                    if not os.path.isfile(customTexture):
                                        texture_file_error.append(
                                            merge_n.getName() + u" --> NodeName = " + customTexture + u"！！！自定义贴图丢失或已经损坏")

                            if customShader == "Color":
                                color_file_warn.append(merge_n.getName() + u" --> customShader设置为Color")

                        if customPass_note:
                            customPass_op = customPass_note.getValue(0)
                            if customPass_op == "Stripe":
                                stripeTexture = merge_n.getParameter('user.stripeTexture').getValue(0)
                                tex_path_re = re.compile('\S/work/projects/([a-z]{3})/asset/\w+/(\w+)/srf/task/images')
                                tx_analyze = re.findall(tex_path_re, stripeTexture)
                                if not tx_analyze:
                                    return merge_n.getName() + u" --> NodeName = " + stripeTexture + u"！！！条纹图存放位置错误，请放在image文件夹"

                                if stripeTexture:
                                    if "udim" in stripeTexture:
                                        file_list_path_stripe = self.find_path(stripeTexture)
                                        if not file_list_path_stripe:
                                            texture_file_error.append(
                                                merge_n.getName() + u" --> NodeName = " + stripeTexture + u"！！！条纹图丢失或已经损坏")
                                        else:
                                            if stripeTexture[-4:] == ".png" or stripeTexture[-4:] == ".PNG":
                                                pass
                                                # image = Image.open(file_list_path_stripe[0])
                                                # if image.mode != "RGBA":
                                                #     texture_file_error.append(merge_n.getName() + u" --> NodeName = " + stripeTexture + u"！！！条纹贴图不是RGBA模式")
                                            else:
                                                texture_file_error.append(
                                                    merge_n.getName() + u" --> NodeName = " + stripeTexture + u"！！！条纹贴图不是PNG格式")
                                    else:
                                        if not os.path.isfile(stripeTexture):
                                            texture_file_error.append(
                                                merge_n.getName() + u" --> NodeName = " + stripeTexture + u"！！！条纹图丢失或已经损坏")
                                        else:
                                            if stripeTexture[-4:] == ".png" or stripeTexture[-4:] == ".PNG":
                                                pass
                                                # image = Image.open(stripeTexture)
                                                # if image.mode != "RGBA":
                                                #     texture_file_error.append(merge_n.getName() + u" --> NodeName = " + stripeTexture + u"！！！条纹贴图不是RGBA模式")
                                            else:
                                                texture_file_error.append(
                                                    merge_n.getName() + u" --> NodeName = " + stripeTexture + u"！！！条纹贴图不是.PNG格式")

            else:
                texture_file_warn.append(u" 没找到 srf_mtl_Merge 节点")

            if color_file_warn:
                for cfw in color_file_warn:
                    print cfw
            if texture_file_warn:
                for tfw in texture_file_warn:
                    print tfw
            if texture_file_error:
                for tfe in texture_file_error:
                    return tfe
            else:
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
