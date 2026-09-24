# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.11
#
# Description: As the description shows below
#
#export xgen file need to change 1 the "xgFileName" 2 the datapath 3 export the ma file 4 restore the oreint state
#
#
#
#
#
#
############################################
#
# import logging
#
# logxgenEx = logging.getLogger('xgenExpoter')
# hdlr = logging.FileHandler('/home/zhixiang/Desktop/xgenex.log')
# formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
# hdlr.setFormatter(formatter)
# logxgenEx.addHandler(hdlr)
# logxgenEx.setLevel(logging.DEBUG)
#




import os, shutil,sys
import traceback
import plt.xgen_file_manager.file_utils as pxfu

import production.python_job as ppj
convert_usd_cache = '{}/linked_tools/usd/lcx2u/scripts/build_shot.py'.format(os.getenv('LC_UTILITY'))
lc_py = '{}/launchers/gen/linux/lca_python'.format(os.getenv('LCA_REZ'))

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出植被分布"
        self.description = u""
        return

    def proceed(self):
        # This function has been moved to the "ple_tools" library, so we have commented out the current code.
        return ''
        try:
            pxfu.publish_xgen_shot_cache_to(self.dialog.version_dir+'/cache')

            # 往农场发一个转换byshot usd的任务
            proj_name = self.dialog.project.get("name").lower()
            shot_name = self.dialog.entity_name
            me = self.dialog.user['name']
            arg = ' plt --proj {} --shots {} --time_elapsed=0.0'.format(proj_name, shot_name)
            jb_name = 'Export USD PLT SHOT {} {} by {}'.format(proj_name, shot_name, me)
            usd_shot_id = ppj.send_job(convert_usd_cache,
                                              args=arg,
                                              proj=proj_name,
                                              job_name_prefix=jb_name,
                                              step='PLT',
                                              pools='centos7',
                                              user=me,
                                              python_exe=lc_py,
                                              submitdl=True
                                              )
            print ('Export USD PLT SHOT: ', usd_shot_id)
            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description