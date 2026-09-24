# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2014 Light Chaser Animation
#
# Author: guanzejie
#
# Date: 2022.05
#
# Description:
#
############################################

import os
import sys
import traceback
import pymel.core as pm
import maya.cmds as cmds
from proc.function_running_time import record_time

class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"根据房子高模自动输出一个的低模,并且自动提交。"
        self.description = u"根据房子高模自动输出一个的低模,并且自动提交。"
        return


    def do_reduce(self,proj,asset_type,asset_name,auto_pu):
        # do reduce

        cmds.select("|master")

        linux_export_path = '/mnt/work/projects/{0}/asset/{1}/{2}/mod/task/maya/low_model/'.format(
            proj.lower(), asset_type, asset_name + "_low")

        windows_export_path = 'W:/projects/{0}/asset/{1}/{2}/mod/task/maya/low_model/'.format(
            proj.lower(), asset_type, asset_name + "_low")

        if sys.platform.startswith("win"):

            wa_path = windows_export_path + "wapian_abc/"
            if not os.path.exists(windows_export_path):
                os.makedirs(windows_export_path)
            if not os.path.exists(wa_path):
                os.makedirs(wa_path)
            export_name = windows_export_path + asset_name + "_low" + '.mod.model.v000.ma'

        else:
            wa_path = linux_export_path + "wapian_abc/"
            if not os.path.exists(linux_export_path):
                os.makedirs(linux_export_path)
            if not os.path.exists(wa_path):
                os.makedirs(wa_path)
            export_name = linux_export_path + asset_name + "_low" + '.mod.model.v000.ma'

        if os.path.exists(export_name):
            os.remove(export_name)

        cmds.file(export_name, force=True, options="v=0;", typ="mayaAscii", pr=True, es=True)

        cmds.select(cl=True)

        mod_path = os.path.dirname(__file__) + "/create_low_mod"

        sys.path.append(mod_path)

        import create_low_mod.setupUi_low as setupUi

        print(mod_path)

        export_name_l = linux_export_path + asset_name + "_low" + '.mod.model.v000.ma'

        wa_path_l = linux_export_path + "wapian_abc/"

        setupUi.setupUi(export_name_l, wa_path_l, auto_pu)

    @record_time(__file__)
    def proceed(self):
        try:

            asset_name = self.dialog.entity['name'].lower()

            proj = self.dialog.project['name']

            asset_type = self.dialog.d_assets_info[asset_name]['type']

            filters_asset = [['project', 'name_is', proj], ['code', 'is', asset_name+"_low"]]

            filters = [['project.Project.name', 'is', proj], ['entity', 'name_is', asset_name], ["content", "is", "model"]]

            sg_version = self.dialog.sg.find_one('Task', filters, ['sg_last_version'])

            sg_asset = self.dialog.sg.find_one('Asset', filters_asset, ['tank_file'])

            print(r"__________________________test_____________________________")
            print(sg_version, sg_asset, asset_name, proj, asset_type)
            print(r"__________________________test_____________________________")

            make_low = self.dialog.w_publish_file.comboBox_make_low.currentText()

            if make_low == "Make Low(Yes)":

                if sg_asset:
                    print("YES")
                    if asset_type not in ["env", "prp"]:
                        return ""

                    auto_pu = "0"
                    self.do_reduce(proj, asset_type, asset_name,auto_pu)

                    return""

                else:
                    return""

            if make_low == "Make Low(No)":
                print("NO")

                if not sg_asset:
                    print(r"——————————————————————********shotgun has not low asset********——————————————————————————")
                    print(r"——————————————————————********shotgun has not low asset********——————————————————————————")
                    print(r"——————————————————————********shotgun has not low asset********——————————————————————————")
                    print(r"——————————————————————********shotgun has not low asset********——————————————————————————")
                    print(r"——————————————————————********shotgun has not low asset********——————————————————————————")
                    return ""

                if sg_version['sg_last_version']:
                    print(r"——————————————————————********has version********——————————————————————————")
                    print(r"——————————————————————********has version********——————————————————————————")
                    print(r"——————————————————————********has version********——————————————————————————")
                    print(r"——————————————————————********has version********——————————————————————————")
                    print(r"——————————————————————********has version********——————————————————————————")
                    return ""

                if asset_type not in ["env", "prp"]:
                    return ""

                auto_pu = "1"
                
                print(proj, asset_type, asset_name, auto_pu)

                self.do_reduce(proj, asset_type, asset_name, auto_pu)

                return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


