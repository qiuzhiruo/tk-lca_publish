# -*- coding: utf-8 -*-
import traceback

import maya.cmds as cmds


class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查除了z1开头的镜头是否有使用crd资产"
        self.description = u"除了z1开头的镜头外，不能使用crd类型的资产"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        # 获取文件路径
        target_group = "|assets|crd"
        full_path = cmds.file(query=True, sceneName=True)
        path_part = full_path.split('/')
        # 通过切割，判断shot后的字段为镜头号
        seq_name = ""
        if 'shot' in path_part:
            shot_index = path_part.index('shot')
            seq_name = path_part[shot_index + 1]

            print seq_name

        # 找crd组下是否有资产
        found_ref_assets = []
        if cmds.objExists(target_group):
            children = cmds.listRelatives(target_group, children=True, fullPath=True) or []
            if children:
                for crd_asset in children:
                    # begin
                    # 跳过 - 摆cache镜头时可以有crd的
                    if "cycle_" in str(crd_asset) and "_srf" in str(crd_asset):
                        continue
                    # end
                    if cmds.referenceQuery(crd_asset, isNodeReferenced=True):
                        found_ref_assets.append(crd_asset)
                    print crd_asset
            else:
                print "0000000"
        else:
            return ''
        if seq_name.startswith('z1'):
            return ''

        if not found_ref_assets:
            return ''
        else:
            return u"该场次镜头不能使用crd资产，请remove下列资产或着替换成非crd资产：{}".format(str(found_ref_assets))

    def run_fix(self):
        return self.run_fix

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
