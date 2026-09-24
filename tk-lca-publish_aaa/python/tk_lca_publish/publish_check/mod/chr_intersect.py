# -*- coding:utf-8 -*-


# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Check asset model group hierarchy
#
############################################

import traceback

import pymel.core as pm
from proc.function_running_time import record_time


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查资产角色模型自穿插。"
        self.description = u"为绑定检查角色模型的自穿插,穿插位置显示红圈"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return


    @record_time(__file__)
    def run_check(self):

        try:
            res = ''

            for asset_name in self.dialog.d_assets_info.keys():
                if self.dialog.d_assets_info[asset_name]['type'] != 'chr':
                    return res
                else:
                    pm.loadPlugin('SOuP.so', quiet=True)
                    main_module = __import__("__main__", globals(), locals(), [], 0)
                    self.dialog.print_log("asset name "+asset_name)
                    self.dialog.print_log("pm.pluginInfo('SOuP.so',query = True, loaded = True): " + str(pm.pluginInfo('SOuP.so',query = True, loaded = True)))

                    new_name_list = []
                    root_node = pm.PyNode("|master|poly")
                    for i in pm.listRelatives(root_node, ad=True, type="mesh"):
                        transform_node = i.listRelatives(p=1)[0]
                        level_list = transform_node.fullPath().split("|")


                        flag = False
                        for index in range(len(level_list)):
                            level = "|".join(level_list[:index + 1])

                            level_exist = pm.objExists(level)
                            if level_exist:
                                visi = pm.PyNode(level).getAttr("visibility")
                                if visi == 0:
                                    flag = True
                                    continue
                        if not flag:
                            new_name_list.append(transform_node.name())



                    inter_str = main_module.intersections_SOuP().create(selfIntersect=False,
                                                            color=[1, 0, 0], width=0.01, drawAsMesh=True)

                    inter_node = pm.PyNode(inter_str)
                    inter_node.rename(inter_str + "_del")

                    main_module.intersections_SOuP().add(nodes=new_name_list)
                    default_value_dict = {"borderLines": 0, "lineWidth": 0.01, "selfIntersect": 0}

                    inter_node_shape = pm.listRelatives(inter_node, s=1)[0]

                    self_inter_list = []

                    for new_name in new_name_list:
                        self_inter_str = main_module.intersections_SOuP().create(selfIntersect=True,
                                                                            color=[0, 0.7, 1], width=0.01,
                                                                            drawAsMesh=True)

                        self_inter_node = pm.PyNode(self_inter_str)
                        self_inter_node.rename(self_inter_str + "_"+new_name+ "_self_del")

                        main_module.intersections_SOuP().add(nodes=[new_name])
                        self_default_value_dict = {"borderLines": 0, "lineWidth": 0.01}

                        self_inter_node_shape = pm.listRelatives(self_inter_node, s=1)[0]
                        if self_inter_node_shape.getAttr("outMainCurveCount") > 0:

                            for attr_name, default_value in self_default_value_dict.items():
                                self_inter_node_shape.setAttr(attr_name, default_value)
                            self_inter_list.append(self_inter_node)
                            res = u"角色模型自穿插"
                        else:
                            res = ""
                            pm.delete(self_inter_node)

                    if inter_node_shape.getAttr("outMainCurveCount") > 0:
                        for attr_name, default_value in default_value_dict.items():
                            inter_node_shape.setAttr(attr_name, default_value)
                        res += u" |角色模型相互穿插"
                    else:
                        res += ""
                        pm.delete(inter_node)

                    if self_inter_list:
                        self_grp = pm.group(self_inter_list)
                        self_grp.rename("displayIntersections_self_del_"+self_grp.name())


            return res
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


