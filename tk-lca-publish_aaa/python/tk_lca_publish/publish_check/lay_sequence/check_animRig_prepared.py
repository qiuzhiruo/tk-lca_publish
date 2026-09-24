# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.06
#
# Description: Check layout hierarchy
#
############################################
import traceback
import os
import pymel.core as pm

NO_ANIMRIG_GRPS = ['prp']           # artists can use model assets of these grps

# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查reference资产的rigging任务是否有版本'
        self.description = u'详见 <a href="http://shotgun.zhuiguang.com/detail/Ticket/2412">Ticket</a>'
        self.auto_fix = False
        self.duty = u'pc'
        return

    def run_check(self):
        try:
            import publish_check.lay.check_file_reference as check_file_reference;reload(check_file_reference)
            # e.g. assets_dict = {u'chr': [nt.Transform(u'lord:master'),nt.Transform(u'brother:master'),
            #                     u'scn': [nt.AssemblyReference(u'e90_hosptial_scn_AR')],
            #                     u'veh': [nt.Transform(u'car_lord:master'), ...}
            assets_dict = check_file_reference.get_top_assets()

            #chr/crd/prp/veh/rra,File Reference; flg/env/asb/scn, Assembly Reference
            illegal_assets_tuple = []
            for grp in check_file_reference.GRP_NAME:
                if not grp in assets_dict:
                    continue

                for asset in assets_dict[grp]:
                    name = os.path.splitext(os.path.basename(asset.referenceFile().path))[0]                # e.g. 'lord'
                    vers = self.dialog.sg.find('Version', [ ['project', 'is', self.dialog.project],
                                                            ['code', 'starts_with', name + '.rig.rigging.']],
                                                            ['code'])
                    if not vers and grp not in NO_ANIMRIG_GRPS:
                        illegal_assets_tuple.append((name, asset))
                    else:
                        try:
                            print vers[-1]
                        except:
                            print grp, name

            if illegal_assets_tuple:
                [illegal_assets_names, illegal_assets_masters] = zip(*illegal_assets_tuple)
                illegal_assets_names = list(set(illegal_assets_names))
                illegal_assets_masters = list(set(illegal_assets_masters))

                illegal_assets_shots_dict = {}
                for shot_info in self.dialog.shots_preview_data:
                    shot_name = shot_info['shot_info']['code']
                    shot_objSet = shot_name + '_assets'
                    shot_assets = pm.PyNode(shot_objSet).members()

                    for shot_asset in shot_assets:
                        if shot_asset in illegal_assets_masters:
                            index = illegal_assets_masters.index(shot_asset)
                            asset_name = illegal_assets_names[index]
                            if asset_name not in illegal_assets_shots_dict:
                                illegal_assets_shots_dict[asset_name] = []
                            illegal_assets_shots_dict[asset_name].append(shot_name)

                if illegal_assets_shots_dict:
                    msg = u'以下ref资产的rigging任务在shotgun上还没有版本，请联系pc与上游部门核对情况：\n'
                    for asset_name in illegal_assets_shots_dict:
                        msg += asset_name + ' (' + ' '.join(illegal_assets_shots_dict[asset_name]) + ')\n'

                    return msg

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

