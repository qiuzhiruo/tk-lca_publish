# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: John Su
#
# Date: 2014.1
#
# Description: As the description shows below
#
############################################

import os
import traceback
import re
import glob
import sys
# sys.path.insert(0, '/mnt/work/home/yingjie/git_repo/lcatools/tools/plt/xgen_file_manager')
import plt.xgen_file_manager.file_utils as pxgfu
# import file_utils as pxgfu

# All system check classes will use StdCheck as the class name.





class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查所选output cache中xgen，xml文件中的output路径的合法性"
        self.description = u"xgen，ass中的路径必须为当前output 版本的路径"
        self.auto_fix = True
        self.duty = u"艺术家本人"
        return

    @staticmethod
    def get_xgen_xml(output_folder):
        xg_f=[]
        xg_f.extend(glob.glob(output_folder+'/cache/*/xgen/collections/*/*.xgen'))
        xg_f.extend(glob.glob(output_folder+'/cache/*/xgen/collections/*/*/xml/*.xml'))
        return xg_f

    @staticmethod
    def check_file_content(all_files):
        re_str="/output/projects/[a-z]{3}/shot/[a-z]\d{2}/[a-z]\d{5}/plt/output/\S+\.plt\.\S+\.v\d{3}/cache"

        error_files=[]
        output_str=[]
        for af in all_files:
            publish_folder=af.split('/cache/')[0]+'/cache'
            publish_folder=publish_folder.replace('/mnt/output/projects/', '/output/projects/')

            with open(af) as f:
                text=f.read()
                
                output_str=re.findall(re_str, text)
                if output_str:
                    if any([s!=publish_folder for s in output_str]):
                        error_files.append(af)
        if error_files:
            return error_files
        else:
            return ''

    def run_check(self):
        try:
            if self.dialog.ui.comboBox_publish_mode.currentIndex()==0:
                return ''

            output_cache=str(self.dialog.w_publish_file.lineEdit_cache.text())
            ctx=self.dialog.ctx
            me_entity=self.dialog.sg.find_one(ctx.entity['type'], [['id', 'is', ctx.entity['id']]], ['type', 'sg_asset_type', 'code'])

            if me_entity['type'] == 'Shot':
                if output_cache and os.path.isdir(output_cache+'/cache'):
                    all_files=StdCheck.get_xgen_xml(output_cache)
                    error_files=StdCheck.check_file_content(all_files)
                    if error_files:
                        return u'以下文件包含 [非当前output版本路径] 的路径:\n'+'\n'.join(error_files)
                    else:
                        return ''
                else:
                    return u"文件夹为空，或者没有/cache文件夹"
            elif output_cache:
                if not os.path.isdir(output_cache+'/xgen'):
                    return u"不是资产下的output版本"

            return ''

        except:
            return traceback.format_exc()
    

    def run_fix(self):
        '''Auto Fix'''
        try:
            output_cache=str(self.dialog.w_publish_file.lineEdit_cache.text())
            all_files=StdCheck.get_xgen_xml(output_cache)
            for af in all_files:
                pxgfu.replace_output_path(af)
        except:
            return traceback.format_exc()

        return ''


    def get_check_name(self):
        return self.check_name


    def get_description(self):
        return self.description


    def get_auto_fix(self):
        return self.auto_fix


    def get_duty(self):
        return self.duty


