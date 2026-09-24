# -*- coding: UTF-8 -*-
# @Time:2024/2/27 上午9:56
import traceback


# 已被废弃，该检查项已合并到了 check_crd_assets.py

class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查crd shot prp"
        self.description = u"检查crd镜头的道具资产是否有使用对应'_low'版本"
        self.auto_fix = False
        self.duty = u"艺术家本人"

    def run_check(self):
        try:
            error_prp = []
            import maya.cmds as cmds
            if cmds.ls('|assets|crd'):
                if cmds.listRelatives('|assets|crd',c=1):
                    if not cmds.ls('|assets|prp'):
                        return ''
                    prp_grp = cmds.listRelatives('|assets|prp',c=1)
                    if not prp_grp:
                        return ''
                    for i in prp_grp:
                        prp_name = i.split(':')[0]
                        if prp_name.endswith('_low'):
                            continue
                        low_prp_name = prp_name+'_low'
                        asset_find = self.dialog.sg.find_one("Asset",[['project', 'is', self.dialog.project],
                                                                        ['code', 'is', low_prp_name]],[])
                        if asset_find:error_prp.append(i)

            if error_prp:
                return   '以下prp资产应该使用对应的low版本(请自行替换):\n' +' '.join(error_prp)
            else:return ''

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







