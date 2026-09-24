# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
# Description: Copy publish files
#
############################################

import os
import traceback
import shutil
import subprocess
import sys

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"提交yzc的客户模板图"
        self.description = u"提交yzc的客户模板图"
        return

    def upload_image(self):
        image_list = [self.dialog.w_publish_file.listWidget_upload_img.item(i).text() for i in xrange(self.dialog.w_publish_file.listWidget_upload_img.count())]
        print image_list

        asset_info = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_asset_type','sg_client_name','code'])

        if asset_info['sg_client_name']:
            name_text = asset_info['sg_client_name']
        else:
            name_text = asset_info['code']


        i=0
        for image in image_list:
            preview_dir = self.dialog.version_dir + '/preview/'
            if i :
                index=str(i)
            else:
                index=''

            file_name = os.path.join(preview_dir,name_text+index+'.jpg')
            shutil.copy(image, file_name)

            i+=1

        return ''

    def proceed(self):
        try:
            self.upload_image()
            return ''
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


