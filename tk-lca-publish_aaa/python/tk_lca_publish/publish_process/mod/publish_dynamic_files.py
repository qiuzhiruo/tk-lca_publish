# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2015.10
#
# Description: Copy alembic files
#
############################################

import os
import traceback
import shutil
from proc.function_running_time import record_time

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝动态版本的abc文件到服务器上版本文件夹"
        self.description = u"将艺术家提交动态版本的abc文件拷贝到版本文件夹。"
        return

    @record_time(__file__)
    def proceed(self):
        try:
            work_dynamic_file_list = [self.dialog.w_publish_file.listWidget_dy.item(i).text() for i in xrange(self.dialog.w_publish_file.listWidget_dy.count())]
            if len(work_dynamic_file_list)!=0:
                dynamic_path=self.dialog.version_dir + '/dynamic'
                if not os.path.isdir(dynamic_path ):
                        os.makedirs(dynamic_path )
                        os.chmod(dynamic_path, 0777)

                for work_dynamic_file in work_dynamic_file_list:
                    publish_dynamic_file=os.path.join(dynamic_path,os.path.basename(work_dynamic_file))
                    shutil.copyfile(work_dynamic_file,publish_dynamic_file)

                    if os.path.isfile(work_dynamic_file) and '.hi.' in work_dynamic_file:

                        proxy_path = self.dialog.version_dir + '/scene_graph_xml/proxy.abc'
                        xmlFilePath = self.dialog.version_dir + '/scene_graph_xml/' + self.dialog.entity['name'] + '.xml'
                        dynamic_xml_path=os.path.join(dynamic_path,os.path.basename(xmlFilePath))
                        proxy_xml_path=os.path.join(dynamic_path,os.path.basename(proxy_path))

                        os.chmod(self.dialog.version_dir, 0777)

                        shutil.copyfile(xmlFilePath,dynamic_xml_path)
                        shutil.copyfile(proxy_path,proxy_xml_path)

                            # os.chdir(dynamic_path)
                            # os.symlink('./'+os.path.basename(work_dynamic_file),'./hi.abc')


            else:
                print 'not dynamic output.'


            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


