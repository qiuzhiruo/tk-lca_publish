# -*- coding: utf-8 -*-
# @Time    : 18-5-9 上午11:23
# @Author  : zhangzheng
__author__ = 'zhangzheng'
__maintainer__ = 'zhangzheng'


import os
import traceback
import shutil

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝文件到服务器上版本文件夹"
        self.description = u"将艺术家提交的文件及actions文件拷贝到版本文件夹内。"
        return


    def proceed(self):
        try:
            import pymel.core as pm
            # Copy ma file
            ma_file = str(pm.saveFile())
            self.dialog.tank_file = self.dialog.version_dir + '/' + self.dialog.entity['name'] + '.ma'
            publish_file = os.path.basename(ma_file).split('.')[0] + '.ma'
            publish_path = self.dialog.version_dir + '/' + publish_file
            print 'publish path is \n\t', publish_path
            actions_dir = os.path.dirname(ma_file)+'/actions'
            publish_actions_dir = self.dialog.version_dir + '/actions'
            try:
                if os.path.isfile(ma_file):
                    shutil.copyfile(ma_file, publish_path)
                    print 'copy file to publish done !!!'
            except:
                return 'con not copy file to publish !!!'
            try:
                if os.path.isdir(actions_dir):
                    if os.path.isdir(publish_actions_dir):
                        print 'publish_actions_dir is \n\t',publish_actions_dir
                        shutil.rmtree(publish_actions_dir)
                        print 'delete publish_actions_dir done !!!'
                    shutil.copytree(actions_dir,publish_actions_dir)
                    print 'copy actions to publish done !!!'
                else:
                    traceback.print_exc()
                    print 'not find actions dir !!!'
            except:
                traceback.print_exc()
                return 'con not copy actions to publish !!!'
            
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description