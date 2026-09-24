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
import os
import re
import pymel.core as pm

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"flg 提前检查资产模型层级命名。"
        self.description = u"模型最上层组为master,其次为poly,再次为hi, md, lo 等表示精细度的组。\nhi组必须有且不能是空的。lo/md 组现在不是必须的，但如果有了这样的组，组内不能为空。\n如果有多个组(hi,md,lo),需要按照 hi, md, lo 这样的次序上下排列"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):

        try:
            d_assets_info = {}

            if not pm.objExists("|master"):
                return u"没有找到最高层的 |master 组。"

            # to mark which group needs standard model checks
            asset = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_asset_type', 'sg_manual_lod'] )
            d_assets_info[self.dialog.entity['name']] = {'node':pm.PyNode('|master'),'type':asset['sg_asset_type'],'lod':asset['sg_manual_lod']}

            for asset_name in d_assets_info.keys():
                root = d_assets_info[asset_name]['node']
                root_name = root.fullPath()
                asset_type = d_assets_info[asset_name]['type']
                lod = d_assets_info[asset_name]['lod']
                if asset_type == 'flg' :
                    if not pm.objExists(root):
                        return u"资产" + asset_name + u"没有找到最高层的 " + root_name + u" 组。"

                    if not pm.objExists(root_name + "|poly"):
                        return u"资产" + asset_name + u"没有找到次高层的 " + root_name + u"|poly 组。"

                    for grp in pm.listRelatives(root_name, c=True):
                        if not grp.nodeName() in ['poly', 'shape', 'misc']:
                            return u"资产" + asset_name + u"的第二层只能有 poly shape 和 misc 组。现在发现了" + grp.nodeName()

                    l_res = pm.listRelatives(root_name + '|poly', c=True)
                    if not 'hi' in [res.nodeName() for res in l_res]:
                        return u"资产" + asset_name + u"没有找到高模存放的 " + root_name + u"|poly|hi 组"

                    error_name_meshes=[]
                    for res in l_res:
                        if not res.nodeName() in ['hi', 'md', 'lo', 'proxy']:
                            return u"资产" + asset_name + u"下的精度组，只能有 hi, md, lo, proxy，现在发现了" + res.name()

                        l_meshes = pm.listRelatives(res, ad=True, type='mesh')
                        if len(l_meshes) == 0:
                            return u"资产" + asset_name + u"下" + res.name() + u"组不能为空。请在这个组下建模或者把空组删了。"

                        if asset_type == 'flg':
                            if 'md' in res.nodeName() or 'lo' in res.nodeName():
                                l_meshes = pm.listRelatives(res, noIntermediate=True,ad=True, type='mesh')
                                error_meshes=[m for m in l_meshes if ('_'+res) not in  m.nodeName()]
                                error_name_meshes.extend(error_meshes)

                    if len(error_name_meshes)>0:
                        pm.select(error_name_meshes)
                        return u"flg 资产md/lo模型的mesh需要加 (md/lo) 的后缀:"+u" ,".join([n.nodeName() for n in error_name_meshes])


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


