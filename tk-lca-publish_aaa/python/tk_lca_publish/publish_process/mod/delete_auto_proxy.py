# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2014 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.06
#
# Description: 
#
############################################

import os
import traceback
import math
import pymel.core as pm
from proc.function_running_time import record_time

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"删除自动输出的proxy代理模。"
        self.description = u"删除自动输出的proxy代理模。"
        return

    @record_time(__file__)
    def proceed(self):
        try:

            for asset_name in self.dialog.d_assets_info.keys():
                version_dir = self.dialog.d_assets_info[asset_name]['version_dir']
                root = self.dialog.d_assets_info[asset_name]['node']
                node_name = self.dialog.d_assets_info[asset_name]['node_name']
                asset_type = self.dialog.d_assets_info[asset_name]['type']

                if asset_type == 'chr' and self.dialog.step['name'] == 'rig':
                    continue

                # make a master if necessary
                if self.dialog.d_assets_info[asset_name]['parent']:
                    pm.parent(root, world=True)

                if node_name != 'master':
                    root.rename('master')

                # Create proxy res
                if pm.objExists('|master|poly|proxy'):
                    n = pm.PyNode('|master|poly|proxy')
                    if n.hasAttr('auto_proxy'):
                        pm.delete(n)
                        print 'delete auto proxy success'
                    else:
                        print 'delete auto proxy fail',n

                else:
                    print 'not find proxy ....'

                # recovery root node
                if self.dialog.d_assets_info[asset_name]['parent']:
                    pm.parent(root, self.dialog.d_assets_info[asset_name]['parent'])

                if node_name != 'master':
                    root.rename(node_name)

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


