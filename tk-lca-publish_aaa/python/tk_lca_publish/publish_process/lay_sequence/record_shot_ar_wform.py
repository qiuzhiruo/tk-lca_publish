# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import traceback
import sys
import os

import pymel.core as pm

import lay.utilities.assembly_operations as aos;reload(aos)
import json


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"记录asb资产的wform"
        self.description = u"在split_into_shots之前记录asb资产的wform到asb_wmatrix.json中, "
        return

    def proceed(self):
        try:
            for data in self.dialog.shots_preview_data:
                shot_name = data['shot_info']['code'] + '_shot'
                pm.currentTime(pm.getAttr(str(shot_name) + '.startFrame'))
                
                result_dict = aos.get_asb_wform()
                ar_info_file = os.path.join(data['version_dir'], 'asb_wmatrix.json').replace('\\', '/')
                with open(ar_info_file, 'w') as op:
                    content = json.dumps(result_dict, indent = 4, sort_keys = True, separators = (',', ':'), ensure_ascii = False)
                    op.write(content)
            
            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description



