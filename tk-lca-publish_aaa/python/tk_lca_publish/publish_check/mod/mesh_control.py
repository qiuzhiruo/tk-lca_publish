# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.08
#
# Description: 
#
############################################

import traceback
import pymel.core as pm
import re
import maya.cmds as mc
from proc.function_running_time import record_time


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"资产面数控制。"
        self.description = u"hi模不能是空的。\n针对我们面数控制规范的检查:\n三级角色不能超过十万面。skip tag: face_cnt"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def get_mesh_count(self, root_node):
        cnt = 0
        if pm.objExists(root_node):
            # mark all the hidden obj(transform and meshes):
            all_objs = pm.listRelatives(root_node, ad=True)
            hidden_lst = []
            for obj in all_objs:
                if pm.getAttr(obj+".visibility") == False:
                    hidden_lst.append(obj)
            l_meshes = pm.listRelatives(root_node, ad=True, type='mesh')
            if len(l_meshes) == 0:
                return cnt

            pm.select(l_meshes, r=True)
            pm.showHidden(above=True)
            cnt = pm.polyEvaluate(f=True)

            # re-hide the hidden objects
            if len(hidden_lst)>0:
                pm.select(hidden_lst, r=True)
                pm.hide()

        pm.select(cl=True)
        return cnt

    @record_time(__file__)
    def run_check(self):

        try:


            for asset_name in self.dialog.d_assets_info.keys():

                mod_asset = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]],
                                                    ['tags', 'tag_list', 'code', 'sg_asset_type', 'sg_diffculty2', 'sg_remark'])
                if mod_asset['sg_asset_type'] in ['flg'] and 'face_cnt' in mod_asset['tag_list']:
                    print 'flg skip check...'
                    return ''

                root = self.dialog.d_assets_info[asset_name]['node']
                if root.fullPath() == '|master':
                    hi_cnt = self.get_mesh_count('|master|poly|hi')
                    lo_cnt = self.get_mesh_count('|master|poly|lo')
                else:
                    hi_cnt = self.get_mesh_count(root.fullPath())
                    lo_cnt = 0

                if hi_cnt == 0:
                    return u"资产:" + asset_name + u"高低模面数都是0。新的规范中，可以没有lo模，但是必须有hi模。"

                if hi_cnt < lo_cnt and hi_cnt != 0:
                    return u"资产:" + asset_name + u"低模面数 "+ str(lo_cnt)  +u" 比高模面数 "+str(hi_cnt) +u" 多。"

                if hi_cnt <= lo_cnt and hi_cnt > 1000:
                    return u"资产:" + asset_name + u"高低模面数都是" + str(lo_cnt) + u",请精简底模再publish."

                if lo_cnt > 100000:
                    return u"资产:" + asset_name + u"资产低模不能超过十万面。"

                if mod_asset['sg_asset_type'] in ['chr']:
                    print  'mod_asset : ',mod_asset
                    if pm.objExists('td_name_check'):
                        n = pm.PyNode('td_name_check')
                        if n.hasAttr('asset') and n.getAttr('asset') == self.dialog.entity['name']:
                            return ""

                    if 'face_cnt' in mod_asset['tag_list']:
                        print "mesh_control skip for 3 level chr"
                        return ''

                    hair_list = pm.ls('*hair*',type='mesh')
                    if hair_list:
                        for hair in hair_list:
                            if '|hi|' in mc.ls(hair.name(),l=True):
                                continue
                            if '|proxy|' in mc.ls(hair.name(),l=True):
                                continue
                            else:
                                pm.select(hair)
                                hi_cnt += pm.polyEvaluate(f=True)
                                pm.select(cl=True)
                    if mod_asset['sg_diffculty2'] == '3' and hi_cnt>100000:
                        return u"资产:" + asset_name + u"高模面数是" + str(hi_cnt) + u"\n三级角色请精简到10万面以下或组长检测通过再publish\n组长检查完名后使用 LCA MOD > Check > Lead Check 给当前文件打上通过的记号。\n模型师重开文件后可以 Publish。"
                    # add chr face cnt limit
                    remark_str = mod_asset['sg_remark']
                    if not remark_str:
                        return ''
                    results = re.search(r"((face_cnt:)(\d+))", remark_str)
                    if not results:
                        # print "mesh_control skip "
                        return ''
                    face_cnt_limit_value = int(results.group(3))
                    # print  face_cnt_limit_value
                    if hi_cnt > face_cnt_limit_value*10000:
                        return u"资产:" + asset_name + u"高模面数是" + str(hi_cnt) + u"\n请精简到{}万面以下或组长检测通过后由组长修改shotgun的remark,再publish".format(str(face_cnt_limit_value))

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




