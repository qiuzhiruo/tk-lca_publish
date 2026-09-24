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

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"Publish 子资产文件"
        self.description = u"Publish 子资产文件"
        return


    def proceed(self):
        try:
            py_script = os.path.dirname(__file__) + '/hyperloop_export.py'

            for asset in sorted(self.dialog.hyperloop.keys()):
                xml = self.dialog.hyperloop[asset]['xml']
                abc = self.dialog.hyperloop[asset]['abc']
                v_name = self.dialog.hyperloop[asset]['v_name']
                v_dir = self.dialog.hyperloop[asset]['v_dir']
                color_id = self.dialog.hyperloop[asset]['sg_color_id']
                if self.dialog.hyperloop[asset]['group'] != "shotgun":

                    self.dialog.print_log('  processing: ' + abc)
                    self.dialog.print_log('  to version: ' + v_dir)
                    os.makedirs(v_dir)
                    lca_rez_path = os.getenv('LCA_REZ')
                    cmd_str = ' '.join(['{}/launchers/nza/linux/mayapy'.format(lca_rez_path), py_script, abc, xml, v_dir, v_name, asset, color_id])
                    p = subprocess.Popen(cmd_str, shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE )
                    out, err = p.communicate()
                    self.dialog.print_log(cmd_str)

                    if 'Traceback' in err:
                        return u"错误信息：\n" + err

                    if not os.path.isfile(v_dir + 'assembly_definition/' + asset + '.ma'):
                        return u"没有创建子资产版本 %s 的 assembly 文件" % v_name



                    # self.dialog.hyperloop[asset]['ma'] = v_dir.split(".")[:-1] + 'assembly_definition/' + asset + '.ma'

                self.dialog.hyperloop[asset]['ma'] = v_dir + 'assembly_definition/' + asset + '.ma'

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

