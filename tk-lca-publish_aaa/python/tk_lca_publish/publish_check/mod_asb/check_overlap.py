# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Guan ZeJie
#
# Date: 2022.06
#
# Description:
#
############################################
import traceback

import pymel.core as pm

class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查 Assembly Reference 是否有重叠，检查是否有隐藏的物体。'
        self.description = u'检查 Assembly Reference 是否有重叠，检查是否有隐藏的物体。skip tag: overlap_asset'
        self.auto_fix = False
        self.duty = u'艺术家本人。'
        return

    def get_asset_shotgun_info(self, asset_name):
        flt = [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'is', asset_name]]
        asset_info = self.dialog.sg.find_one('Asset', flt, ['code', 'tag_list'])
        return asset_info


    def run_check(self):

        try:
            # 设置跳过该检查项的条件{
            ast_info = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_asset_type', 'code'])
            print ast_info
            asset_n = ast_info['code']
            # add skip tag check

            sg_info = self.get_asset_shotgun_info(asset_n)

            if 'overlap_asset' in sg_info['tag_list']:
                return ""
            #}
            # 开始干活
            asset_name_list = []
            overlap = []
            hide_geo = []
            overlap_info = {}
            # 检查是否有隐藏的物体{
            trans_list = pm.ls(type = "transform")
            for trans in trans_list:
                if pm.getAttr(trans + ".visibility") == False and trans.getShape() == None:
                    hide_geo.append(trans)

            if hide_geo:
                pm.select(hide_geo)
                return u"发现文件中有隐藏组,组文件已经选择，有问题找TD，跳过tags:overlap_asset"
            # }
            # 查找是否有重复的物体,把所有不同名的文件放到一个列表里
            reference_list = pm.ls(type='assemblyReference')
            for ar in reference_list:
                ref_path = str(ar.getAttr("definition")).replace('\\', '/')

                asset_name = ref_path.split("/")[-1][:-3]

                if asset_name not in asset_name_list:

                    asset_name_list.append(asset_name)

                if pm.getAttr(ar+".visibility") == False:
                    hide_geo.append(ar)

            if hide_geo:
                pm.select(hide_geo)
                return u"发现文件中有隐藏物体,文件已经选择，有问题找TD，跳过tags:overlap_asset"
            # 遍历所有文件，并列出相同的文件
            for name_asset in asset_name_list:

                list_date = []

                for name_ref in reference_list:
                    ref_path = str(name_ref.getAttr("definition")).replace('\\', '/')
                    asset_name = ref_path.split("/")[-1][:-3]

                    if str(name_asset) == asset_name:
                        ma_data = [float('{:.6f}'.format(c)) for c in pm.xform(name_ref, query=True, ws=True, m=True)]
                        list_date.append([str(name_ref), ma_data])

                for i in list_date:
                    temp_list = []
                    for j in list_date:
                        if i[1] == j[1]:
                            temp_list.append(i[0])
                    if len(temp_list) >= 2:
                        overlap.append(i[0])
                        if str(i[1]) not in overlap_info:
                            overlap_info.update({str(i[1]): [i[0]]})
                        else:
                            overlap_info[str(i[1])].append(i[0])

            if overlap_info:
                error_assets = [str(i) for i in overlap_info.values()]
                pm.select(overlap, add=True)
                error_msg = u'发现重叠文件\n{}\n文件已经选择，有问题找TD，' \
                            u'跳过tags:overlap_asset'.format('\n'.join(error_assets))

                return error_msg

            if not overlap_info:
                return ""

        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
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

