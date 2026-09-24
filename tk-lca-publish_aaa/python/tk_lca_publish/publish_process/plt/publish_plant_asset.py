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

import os, shutil,sys
import traceback
import glob
import plt.xgen_file_manager.file_utils as pxfu
reload(pxfu)
from pymel.core import *

def add_plant_to_cache(proj,asset):
    file_path='/mnt/proj/trash/plant/%s/plant_asset'%proj.lower()
    folder_name=os.path.dirname(file_path)
    try:
        if not os.path.isdir(folder_name):
            os.makedirs(folder_name)
            os.system('chmod 777 '+folder_name)
    except:
        pass
    if not os.path.isfile(file_path):
        os.system('touch '+file_path)
        os.system('chmod 777 '+file_path)
    plant_assets=[]
    with open(file_path) as f:
        plant_assets=[n.strip().split(';')[0] for n in f.readlines()]
    if asset not in plant_assets:
        with open(file_path,'a') as f:
            f.write(asset+';\n')

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出植被分布 ma文件。"
        self.description = u"将文件另存为一个ma文件，合并reference。"
        return


    def proceed(self):
        try:
            palettes = ls(et='xgmPalette')
            if len(palettes)>0:
                add_plant_to_cache(self.dialog.project['name'],self.dialog.entity['name'])

            pxfu.publish_xgen_asset_cache_to(self.dialog.version_dir)
            if self.dialog.project['name'] == 'LRS':
                xgen_files = glob.glob(self.dialog.version_dir+'/*.xgen')
                for xg_file in xgen_files:
                    self.write_fur_ass(xg_file)

            self.dialog.tank_file = self.dialog.version_dir +'/'+ self.dialog.entity['name'] + '.ma'
            
            return ""
        except:
            return traceback.format_exc()

    def write_fur_ass(self,xg_f):
        replace_dict = {'/hi/': '/hi_hair/', '/md/': '/md_hair/', '/lo/': '/lo_hair/'}

        info, line = pxfu.get_xgen_archive(xg_f)
        for des_name, archive_info in info.items():
            new_archive = archive_info['file']
            for k, v in replace_dict.items():
                new_archive = new_archive.replace(k, v)
            if os.path.exists(os.path.expandvars(new_archive)):
                line[archive_info['line']] = new_archive

        with open(xg_f, 'w') as fn:
            fn.writelines(line)

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description