# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Upload the thumbnail for shotgun
#
############################################

import os
import traceback
import shutil
import subprocess
import datetime


# from PySide import QtGui
import sgtk
from sgtk.platform.qt import QtCore, QtGui


# TODO: Check for different O.S.
# All publish process will use StdProcess as the class name.
class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"更新综合版本mov。"
        self.description = u"为shotgun的v000版本上传或者将图片序列转换一个视频文件(*.mov)或pdf文件作为预览，该文件会帮助其他艺术家快速了解这个版本。"
        return

    def copy_file(self, src, dst):
        self.dialog.print_log('copy file :'+src+'  '+dst)
        p = subprocess.Popen('"' + self.dialog.rvls_path + '" -l ' + src, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)
        tokens = p.communicate()[0].split('\n')[1].split(' ')
        tokens = [i for i in tokens if i != '']

        img_w = int(tokens[0])
        img_h = int(tokens[2])
        ext_src = src.lower().split('.')[-1]

        if max(img_w, img_h) > 2048:
            ratio = str(2048.0 / float(max(img_w, img_h)))
            cmd = '"' + self.dialog.rvio_path + '" ' + src + ' -scale ' + ratio + ' -o ' + dst
            if ext_src == 'exr':
                cmd += ' -outsrgb'
            os.system(cmd)
        elif ext_src != 'jpg':
            cmd = '"' + self.dialog.rvio_path + '" ' + src + ' -o ' + dst
            if ext_src == 'exr':
                cmd += ' -outsrgb'
            os.system(cmd)
        else:
            shutil.copyfile(src, dst)

        return

    def create_version_preview(self):
        # create preview folder
        v000_dir = self.dialog.version_dir[:-4] + 'v000'
        version_name = self.dialog.version_name[:-4] + 'v000'
        preview_dir = os.path.join(v000_dir, 'preview')
        if not os.path.isdir(preview_dir):
            os.makedirs(preview_dir, 0777)
            os.system('chmod 777 '+ preview_dir)

        if not os.access(preview_dir,os.W_OK):
            return

        l_preview_files = []
        for f in os.listdir(v000_dir):
            preview_file=os.path.join(v000_dir, f)
            
            if not os.path.isfile(preview_file):
                continue
                
            if  f.split('.')[-1].lower() in ['jpg','jpeg','tif','tiff','png','tga']:
                l_preview_files.append(preview_file)
                
        if len(l_preview_files)==0:
            l_preview_files=[__file__.split('publish_process')[0]+'depts/default/art/delete_image.jpg']

        l_copied_files = []
        l_preview_files.sort()
        
        
        for i in range(len(l_preview_files)):
            dst = os.path.join(preview_dir, version_name + ('.%04d.' % i) + 'jpg')
            self.copy_file(l_preview_files[i], dst)
            l_copied_files.append(dst)
            
        

        v_preview = os.path.join(preview_dir, version_name + '.'+datetime.datetime.now().strftime("%Y%m%d%H%M%S")+'.mov')
        # if os.path.isfile(v_preview):
        #     os.chmod(v_preview, 0777)
        #     os.remove(v_preview)

        cmdStr = '"' + self.dialog.rvio_path + '" [ ' + os.path.join(preview_dir, version_name) + '.%04d.jpg -pa 1.0 ] -o ' + v_preview
        self.dialog.print_log(cmdStr)
        os.system(cmdStr)


        #clean jpg files
        for file_path in l_copied_files:
            if os.path.isfile(file_path):
                os.chmod(file_path, 0777)
                os.remove(file_path)

        return v_preview

    def write_log(self,log):
        import tempfile,datetime
        tmpdir = tempfile.gettempdir()
        name = os.path.basename( __file__ )
        logf = os.path.join(tmpdir, name)
        logtime =str(datetime.datetime.now())
        with open('%s.txt'%logf,'a') as f:
            f.write( '\r\n debug:'+log+'\t @'+logtime)
    def proceed(self):
        try:
            try:
                v_preview = self.create_version_preview()
            except:
                return ""
            if not os.path.isfile(v_preview):
                return ""

            # Upload
            old_version = self.dialog.sg.find_one('Version', [['id', 'is', self.dialog.v_info['id']]],
                                                  ['entity', 'project', 'user', 'description',
                                                   'entity.Asset.sg_asset_type', 'code', 'id', 'sg_version_folder',
                                                   'sg_uploaded_movie', 'sg_path_to_movie', 'sg_task',
                                                   'sg_version_type', 'created_by'])

            v000_name = old_version['code'][:-4] + 'v000'
            v000 = self.dialog.sg.find_one('Version',
                                           [['code', 'is', v000_name],
                                            ['sg_task', 'is', old_version['sg_task']]],
                                           ['id', 'project'])

            if v000 is None:
                # Sync art version preview to v000

                local_path = old_version['sg_version_folder']['local_path'][:-5] + 'v000/'
                self.write_log('local_path:' + str(local_path))
                if not os.path.isdir(local_path):
                    os.makedirs(local_path, 0777)

                d_version = {'project': old_version['project'], 'entity': old_version['entity'],
                             'sg_task': old_version['sg_task'], 'code': v000_name,
                             'user': old_version['user'],
                             'description': 'v000 auto publish',
                             'sg_version_folder': {'local_path': local_path, 'name': v000_name,
                                                   'content_type': None, 'link_type': 'local'},
                             'sg_version_type': old_version['sg_version_type'],
                             'created_by': old_version['created_by']}

                v000 = self.dialog.sg.create('Version', d_version)
                self.write_log('create v000 version')
                #self.write_log(str(v_preview))
                self.dialog.sg.update('Version', v000['id'], {'sg_path_to_movie': v_preview.replace('Z:/', '${RV_PATHSWAP_ROOT}/').replace('/mnt/proj/', '${RV_PATHSWAP_ROOT}/').replace('/Volumes/lcadata/', '${RV_PATHSWAP_ROOT}/') })
                self.dialog.sg.upload('Version', v000['id'],
                                      v_preview,
                                      "sg_uploaded_movie")

                return ""

            try:

                self.dialog.sg.upload('Version', v000['id'], v_preview, "sg_uploaded_movie")
                self.dialog.sg.update('Version', v000['id'], {'sg_path_to_movie': v_preview.replace('Z:/', '${RV_PATHSWAP_ROOT}/').replace('/mnt/proj/', '${RV_PATHSWAP_ROOT}/').replace('/Volumes/lcadata/', '${RV_PATHSWAP_ROOT}/') })

            except:
                self.dialog.print_log('Failed to upload the mov file. Will be upload later.',
                                      txt_color=QtGui.QColor(255, 150, 30))

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
