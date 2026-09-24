# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Zhang Shirui
#
# Date: 2015.08
#
# Description: Shaders must be assigned to objects not faces
#
########################################################################################

import traceback
import pymel.core as pm
from proc.function_running_time import record_time

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"每个物体只赋一个材质。"
        self.description = u"对于粗模: 每个物体只赋一个材质，不允许按面赋材质。"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return


    @record_time(__file__)
    def run_check(self):
        try:
            multi_list = []
            empty_list = []
            if self.dialog.version_tag == u'粗模':
                for asset_name in self.dialog.d_assets_info.keys():
                    root = self.dialog.d_assets_info[asset_name]['node']
                    root_name = root.fullPath()

                    if not pm.objExists(root):
                        return u"资产" + asset_name + u"没有找到最高层的 " + root_name + u" 组。"

                    if not pm.objExists(root_name + "|poly"):
                        return u"资产" + asset_name + u"没有找到次高层的 " + root_name + u"|poly 组。"

                    if not pm.objExists(root_name + "|poly|hi"):
                        return u"资产" + asset_name + u"没有找到高模存放的 " + root_name + u"|poly|hi 组"

                    asset_type = self.dialog.d_assets_info[asset_name]['type']

                    if asset_type == 'prp' or asset_type == 'env':
                        sels = pm.ls(root_name + "|poly|hi", dag=True, type='mesh')

                        objs = []
                        for sel in sels:
                            objs += pm.listRelatives(sel, p=True)

                        objs = list(set(objs))

                        for o in objs:
                            shape = pm.listRelatives(o, s=True)[0]
                            shader_list = set(pm.listConnections(shape, type='shadingEngine'))
                            if not shader_list:
                                empty_list.append(o.longName())
                            elif len(shader_list) > 1:
                                multi_list.append(o.longName())
                
                if multi_list or empty_list:
                    return_string = ''
                    if multi_list:
                        return_string += u'以下物体存在分面赋予的材质：\n' + '\n'.join(multi_list) + '\n'
                    if empty_list:
                        return_string += u'以下物体无材质:\n' + '\n'.join(empty_list)
                    return return_string
                else:
                    return ''
            else:
                return ''
        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''

        try:
            import sys
            import os
            # sys.path.append("U:/toolset/tools/mod")
            # sys.path.append("/mnt/utility/toolset/tools/mod")
            toolset = os.getenv('LC_TOOLSET')
            sys.path.append(os.path.join(toolset, 'tools'))
            from mod.split_mod_by_shaders import split_mod_by_shaders
            reload(split_mod_by_shaders)
            split_mod_by_shaders.main()
            return ''
        except:
            return traceback.format_exc()


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


