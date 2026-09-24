# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.07
#
# Description:
#
############################################
import traceback
import os
import pymel.core as pm
import production.mayautils.assembly as assutils

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查 Assembly Reference 的放缩。'
        self.description = u'如果 Assembly Reference 资产的三个轴的放缩值不能为0 (包括接近0的极小值)。如果调用的是的绑定，放缩必须一致。'
        self.auto_fix = False
        self.duty = u'艺术家本人。'
        return

    def get_asset_shotgun_info(self, asset):
        flt = [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'is', asset]]
        asset_info = self.dialog.sg.find_one('Asset', flt, ['code', 'tag_list', 'sg_remark', 'sg_chinese'])
        return asset_info

    def run_check(self):
        try:
            print self.dialog.entity['name']
            d_ar_info = {'not_unify':[], 'zero':[]}
            for ar in pm.ls(type='assemblyReference'):
                # Skip sub assets
                if ':' in ar.name():
                    continue
                
                ref_path = str(ar.getAttr("definition")).replace('\\', '/')
                scale_x = ar.getAttr('scaleX')
                scale_y = ar.getAttr('scaleY')
                scale_z = ar.getAttr('scaleZ')

                if '%.4f'%scale_x != '%.4f'%scale_y or '%.4f'%scale_y != '%.4f'%scale_z :
                    d_ar_info['not_unify'].append( ar.name() + u": " + str(scale_x) + u" " + str(scale_y) + u" " + str(scale_z))

                if scale_x < 0.00000001 or scale_y < 0.00000001 or scale_z < 0.00000001 :
                    d_ar_info['zero'].append( ar.name() + u": " + str(scale_x) + u" " + str(scale_y) + u" " + str(scale_z))

            if len(d_ar_info['zero']) > 0:
                return u"发现缩放为0 (或接近0的极小值或为负值):\n\t" + u"\n\t".join(d_ar_info['zero'])
            print self.get_asset_shotgun_info(self.dialog.entity['name'])
            if 'skip_asb_scale' in self.get_asset_shotgun_info(self.dialog.entity['name'])['tag_list']:
                print u'跳过轴向缩放不一致 ! ! !'
                return ""

            if len(d_ar_info['not_unify']) > 0:
                return u"发现三个轴缩放不一致:\n\t" + u"\n\t".join(d_ar_info['not_unify'])


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

