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
import fnmatch
import sys
import traceback
import shutil
import subprocess
# from PySide import QtGui
import sgtk
import getpass
from sgtk.platform.qt import QtCore, QtGui

logger = sgtk.platform.get_logger(__name__)

ocio_path = os.path.join('/mnt/work/software/color_management/OpenColorIO-Configs', 'aces_1.2', 'config.ocio')
exr2movjpg_single_rv = '/mnt/work/software/color_management/OpenColorIO-Configs/rv_template/aces_1.2/exr2movjpg_single.rv'
exr2movjpg_double_rv = '/mnt/work/software/color_management/OpenColorIO-Configs/rv_template/aces_1.2/exr2movjpg_double.rv'


# TODO: Check for different O.S.
# All publish process will use StdProcess as the class name.
def copy_in_ternimal(source_path, target_path):
    cmd = 'su -'
    root_cmd = 'mv {source_path}  {target_path}'.format(source_path=source_path, target_path=target_path)

    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.stdin.write('20150312')
    p.stdin.write('\n')
    out, err = p.communicate(root_cmd)
    if err is None:
        # print('change chmod ok')
        return True
    else:
        # print ('change chmod error')
        return False


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"上传缩略图"
        self.description = u"为shotgun提交版本直接上传或者将图片序列转换一个视频文件(*.mov)作为版本预览，会帮助其他艺术家快速了解这个版本。"
        return

    def create_version_preview(self, is_aces=False):
        print 'version dir: ' + self.dialog.version_dir
        logger.info("my_upload_view")
        # create preview folder
        preview_dir = self.dialog.version_dir + '/preview/'
        if not os.path.isdir(preview_dir):
            os.makedirs(preview_dir)
        jpg_dir = self.dialog.version_dir + '/jpg/'
        if is_aces:
            jpg_dir = self.dialog.version_dir + '/exr/'
        if not os.path.isdir(jpg_dir):
            os.makedirs(jpg_dir)

        # Jpg - copy and convert
        # mov - copy

        if len(self.dialog.l_preview_files) == 1 and self.dialog.l_preview_files[0].endswith('.mov'):
            version_2d = ''
            version_3d = ''
            if self.dialog.l_preview_files[0].endswith('stereo.mov'):
                version_3d = self.dialog.l_preview_files[0]
                version_2d = os.path.dirname(self.dialog.l_preview_files[0]) + '/' + self.dialog.version_name + '.mov'
                if not os.path.isfile(version_2d):
                    version_2d = ''
                self.dialog.v_preview = preview_dir + self.dialog.version_name + '.stereo.mov'
                # cmdStr = ' '.join(['Copy', self.dialog.l_preview_files[0], self.dialog.v_preview])
                shutil.copyfile(version_3d, self.dialog.v_preview)
                if version_2d != '':
                    shutil.copyfile(version_2d, preview_dir + self.dialog.version_name + '.mov')
            else:
                version_2d = self.dialog.l_preview_files[0]
                version_3d = os.path.dirname(
                    self.dialog.l_preview_files[0]) + '/' + self.dialog.version_name + '.stereo.mov'
                if not os.path.isfile(version_3d):
                    version_3d = ''
                self.dialog.v_preview = preview_dir + self.dialog.version_name + '.mov'
                # cmdStr = ' '.join(['Copy', self.dialog.l_preview_files[0], self.dialog.v_preview])
                shutil.copyfile(version_2d, self.dialog.v_preview)
                if version_3d != '':
                    shutil.copyfile(version_3d, preview_dir + self.dialog.version_name + '.stereo.mov')

        else:
            src_files = []
            exists_pattern = []
            # self.dialog.l_preview_files.sort()
            for f in self.dialog.l_preview_files:
                # expand automatically any file collections in the format of name.pad.ext
                if f.split('.')[-2].isdigit() and self.dialog.select_sequences:
                    dirpath = os.path.dirname(f).replace('\\', '/')
                    basename = os.path.basename(f)
                    pattern = basename.replace(basename.split('.')[-2], '*')
                    if pattern in exists_pattern:
                        continue
                    else:
                        exists_pattern.append(pattern)
                    for file in sorted(os.listdir(dirpath)):
                        if fnmatch.fnmatch(file, pattern):
                            src_files.append(dirpath + '/' + file)
                else:
                    src_files.append(f.replace('\\', '/'))

            if not os.path.isdir(jpg_dir + 'L/'):
                os.makedirs(jpg_dir + 'L/')

            src_num_list = []
            for f in src_files:
                tmp = '.'.join(self.dialog.version_name.split('.')[:-1]) + '.' + os.path.basename(f).split('.')[
                    -2] + '.jpg'
                if is_aces:
                    tmp = '.'.join(self.dialog.version_name.split('.')[:-1]) + '.' + os.path.basename(f).split('.')[
                        -2] + '.exr'
                shutil.copyfile(f, jpg_dir + 'L/' + tmp)
                src_num_list.append(os.path.basename(f).split('.')[-2])
                # if sys.platform.startswith('linux'):
                #     copy_in_ternimal(f,jpg_dir +'L/'+ tmp)

            self.dialog.v_preview = preview_dir + self.dialog.version_name + '.mov'
            # cmdStr = '"'+ self.dialog.rvio_path +'" [ ' + jpg_dir+'L/' + '.'.join(self.dialog.version_name.split('.')[:-1]) + '.%04d.jpg -pa 1.0 ] -o ' + self.dialog.v_preview
            # 纠正合成dmt mov的色彩空间为rgb
            cmdStr = '"' + self.dialog.rvio_path + '" [ ' + jpg_dir + 'L/' + '.'.join(
                self.dialog.version_name.split('.')[
                :-1]) + '.%04d.jpg -pa 1.0  ] -quality 1 -outrgb -o ' + self.dialog.v_preview

            if is_aces:
                cmd = ['OCIO={}'.format(ocio_path), 'RV_PATHSWAP_SOURCE_A={}'.format(
                    jpg_dir + 'L/' + '.'.join(self.dialog.version_name.split('.')[:-1]) + '.%04d.exr'),
                       self.dialog.rvio_path, exr2movjpg_single_rv, '-pa', str(1.0), '-o', self.dialog.v_preview]
                cmdStr = ' '.join(cmd)

            first_frame = sorted(src_num_list)[0]
            cmdStr += ' -outparams comment="author ' + getpass.getuser() + '" timecode=' + str(first_frame)

            # cmdStr = '"' + self.dialog.rvio_path + '" [ ' + jpg_dir + 'L/' + '.'.join(self.dialog.version_name.split('.')[:-1]) + '.%04d.jpg -pa 1.0  ] -quality 1 -outsrgb -o ' + self.dialog.v_preview
            logger.info("cmd:" + cmdStr)
            # os.system(cmdStr)
            cmd = 'su -'
            # root_cmd = " /usr/local/rv/rv-linux/bin/rvio_hw [ /mnt/proj/projects/lrs/shot/c90/c90050/dmt/publish/c90050.dmt.matte_painting.v0005/jpg/L/c90050.dmt.matte_painting.%04d.jpg -pa 1.0  ] -quality 1 -outrgb -o /mnt/proj/projects/lrs/shot/c90/c90050/dmt/publish/c90050.dmt.matte_painting.v002/preview/c90050.dmt.matte_painting.v002.mov "

            p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT)
            p.stdin.write('20150312')
            p.stdin.write('\n')
            out, err = p.communicate(cmdStr)
            print out
            logger.info('rv out: ' + out)

        print 'preview file: ' + self.dialog.v_preview
        logger.info('preview file: ' + self.dialog.v_preview)

        return

    def proceed(self):
        try:
            color_space_info = self.dialog.sg.find_one('Project',
                                                       [['name', 'is', self.dialog.project['name']]],
                                                       ['sg_color_space'])
            if color_space_info['sg_color_space'] == "ACES":
                is_aces = True
            else:
                is_aces = False
            self.create_version_preview(is_aces=is_aces)
            self.dialog.sg.update('Version', self.dialog.v_info['id'], {
                'sg_path_to_movie': self.dialog.v_preview.replace('Z:/', '${RV_PATHSWAP_ROOT}/')
                                  .replace('/mnt/proj/', '${RV_PATHSWAP_ROOT}/')
                                  .replace('/Volumes/lcadata/', '${RV_PATHSWAP_ROOT}/')})

            # Upload
            try:
                self.dialog.sg.upload('Version', self.dialog.v_info['id'], self.dialog.v_preview, "sg_uploaded_movie")
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
