# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'

import os
import traceback
import shutil
import pymel.core as pm
import xml.etree.ElementTree as ET
import sys

import gene.stereoDataExport.stereoData as stereoData
reload(stereoData)

import lay.lca_camera_lock.functions as functions_cl
reload(functions_cl)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出立体安全平面和其他相关信息。"
        self.description = u"将立体相机的安全平面,浮动窗口信息输出到stereo_data文件夹下。"
        return

    def write_log(self, content):
        try:
            import proc.log_publish_process as lpp
            reload(lpp)
            current_file = pm.sceneName().replace('\\','/')
            log_file = os.path.dirname(current_file) + '/publish_log/' + os.path.basename(current_file)[:-3]+'.log.txt'
            log_file = log_file.replace('//', '/')
            lpp.log(log_file, content)
        except:
            pass

    def proceed(self):
        try:
            log = 'export_stereo_data.py\n'
            task = self.dialog.task['name'].lower()
            if task !='stereo' and functions_cl.is_camera_locked():
                # ignored exporting stere data if the status is locked
                log += 'camera is locked, no need to export stereo data\n'
                self.write_log(log)
                return ''

            if self.dialog.project['name'].lower() == 'god':
                root_path = self.dialog.version_dir + '/stereo_data'
            else:
                root_path = self.dialog.version_dir + '/camera/stereo_data'
                log += 'stereo data path: '+self.dialog.version_dir+'/camera/stereo_data\n'

            if not os.path.isdir(root_path):
                os.makedirs(root_path)

            xml_name = self.dialog.entity['name'] + '_stereo_data.xml'
            abc_name = self.dialog.entity['name'] + '_safePlane.abc'

            s3d = stereoData.StereoData()
            if not s3d.stereoPluginTest():
                print 'Failed to load stereo plugins, aborted exporting of stereo data.'
                log += 'failed to load stereo plugins, aborted exporting of stereo data\n'
                self.write_log(log)
                return ''

            s3d.main( root_path+'/'+xml_name, root_path+'/'+abc_name )
            log += 'export stereo data successfully\n'
            self.write_log(log)

            return ''

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


