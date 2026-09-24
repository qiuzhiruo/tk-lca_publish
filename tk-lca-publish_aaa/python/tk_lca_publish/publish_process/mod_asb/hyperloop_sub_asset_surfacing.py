# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2019 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2019.06
#
############################################

import os
import sys
import traceback
import shutil
import subprocess

sys.path.append('{}/linked_tools/srf_tools'.format(os.getenv('LC_UTILITY')))
# sys.path.append('/mnt/public/Share/qinlingbo/git/srf_tools')
from hypeloop_auto_publish import hypeloop_send_publish as hsp
reload(hsp)

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"自动提交单体材质版本"
        self.description = u"自动提交单体材质版本"
        return

    def proceed(self):
        try:
            for asset in sorted(self.dialog.hyperloop.keys()):
                if self.dialog.hyperloop[asset]['group'] != "shotgun":
                    print asset
                    srf_info = self.dialog.sg.find("Version",
                                       [['project', 'is', self.dialog.project],['sg_task.Task.step', 'name_is', 'srf'],['entity', 'name_is', asset]],
                                                   ['description', 'code', 'entity.Asset.sg_asset_type'])

                    asset_info = self.dialog.sg.find_one('Asset',[['project', 'is', self.dialog.project],['code','is',asset]],
                                                         ['sg_asset_type'])

                    if srf_info and srf_info[-1]['description'] != 'gas_asset_auto_publish' or asset_info['sg_asset_type'] in ['asb']:
                        print '%s need not update surfacing verison!' % asset
                    else:
                        hsp.hypeloop_srf_publish(self.dialog.project['name'].lower(), asset)

                return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

