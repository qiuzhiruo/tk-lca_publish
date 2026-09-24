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
import sys
import time
import traceback
import shutil
import subprocess
import getpass
import tempfile
import re

os.environ['RV_ENABLE_MIO_FFMPEG'] = '1'

# ACES
ocio_path = os.path.join('/mnt/work/software/color_management/OpenColorIO-Configs', 'aces_1.2', 'config.ocio')
exr2movjpg_single_rv = '/mnt/work/software/color_management/OpenColorIO-Configs/rv_template/aces_1.2/exr2movjpg_single.rv'
exr2movjpg_double_rv = '/mnt/work/software/color_management/OpenColorIO-Configs/rv_template/aces_1.2/exr2movjpg_double.rv'

# TODO: Check for different O.S.
# All publish process will use StdProcess as the class name.


def path_change_chmod(path):
    cmd = 'su -'
    root_cmd = '''chmod 777 -R %s''' % path
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


def get_subprocess_info(p):
    import select

    msg = []
    while True:
        reads = [p.stdout.fileno(), p.stderr.fileno()]
        ret = select.select(reads, [], [])

        for fd in ret[0]:
            if fd == p.stdout.fileno():
                read = p.stdout.readline()
                sys.stdout.write('stdout: ' + read)
                msg.append(read)
            if fd == p.stderr.fileno():
                read = p.stderr.readline()
                sys.stderr.write('stderr: ' + read)
                msg.append(read)

        if p.poll() != None:
            break
    return msg


def get_shot_client_name(dialog):
    projFilter = [['name', 'is', str(dialog.project['name'])]]
    shotgunProjInfo = dialog.sg.find_one('Project', projFilter)

    shotFilter = [
        ['code', 'is', dialog.entity['name']],
        ['project', 'is', {'type': 'Project', 'id': shotgunProjInfo['id']}]
    ]
    info = dialog.sg.find_one('Shot', shotFilter, ['sg_client_name'])
    if info:
        client_name = info['sg_client_name']
        return client_name


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"上传缩略图"
        self.description = u"为shotgun提交版本直接上传或者将图片序列转换一个视频文件(*.mov)作为版本预览，会帮助其他艺术家快速了解这个版本。"
        return

    def check_img_size(self, src):
        p = subprocess.Popen('"' + self.dialog.rvls_path + '" -l ' + src, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)
        p_communicate = p.communicate()
        tokens = [0, 'x', 0]
        size_ptn = re.compile(r'\b\d+\b\sx\s\b\d+\b')
        try:
            # tokens = p_communicate[0].split('\n')[1].split()
            for i in p_communicate[0].split('\n'):
                if not size_ptn.search(i):
                    continue
                tokens = i.split()
        except:
            self.dialog.print_log(traceback.format_exc())
            return 0, 0

        img_w = int(tokens[0])
        img_h = int(tokens[2])
        return img_w, img_h

    def get_mov_length(self, src):
        p = subprocess.Popen('"' + self.dialog.rvls_path + '" -l ' + src, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)
        p_communicate = p.communicate()
        tokens_a = p_communicate[0].split('\n')
        if len(tokens_a) >= 2:
            tokens_b = [i for i in tokens_a[1].split(' ') if i != '']
            if len(tokens_b) >= 8 and tokens_b[6].isdigit():
                return int(tokens_b[6])

        return None

    # standard sequnced images are named as <entity>.<step>.<task>.<version>.<frame>.<ext>
    def get_src_sequence(self, l_files):
        l_files.sort()
        std_path = l_files[0]
        std_tokens = l_files[0].split('.')
        if not (std_tokens[-2].isdigit() and len(std_tokens[-2]) == 4):
            return '', -1

        for path in l_files:
            tokens = path.split('.')
            if len(tokens) != len(std_tokens):
                return '', -1
            if not (tokens[-2].isdigit() and len(tokens[-2]) == len(std_tokens[-2])):
                return '', -1
            tokens[-2] = std_tokens[-2]
            if '.'.join(tokens) != std_path:
                return '', -1

        # if l_files are not all frame files in current folder
        self.dialog.print_log('l_files length: {}'.format(len(os.listdir(os.path.dirname(l_files[0])))))
        current_folder_file_list = []
        for i in os.listdir(os.path.dirname(l_files[0])):
            if '.tmp' not in i:
                current_folder_file_list.append(i)
        self.dialog.print_log('local files length (not contain .tmp file): {}'.format(len(current_folder_file_list)))
        if len(current_folder_file_list) != len(l_files):
            return '', -1

        # preview_dir + self.dialog.version_name + '.%04d.jpg'
        tokens[-2] = '%0' + str(len(std_tokens[-2])) + 'd'
        return '.'.join(tokens), int(std_tokens[-2])

    def copy_file(self, src, dst, img_size=None):
        if not img_size:
            img_w, img_h = self.check_img_size(src)
        else:
            (img_w, img_h) = img_size

        if img_w == 0 or img_h == 0:
            return

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

    def create_version_preview(self, is_aces=False):
        print 'version dir: ' + self.dialog.version_dir

        # create preview folder
        preview_dir = self.dialog.version_dir + '/preview/'
        if not os.path.isdir(preview_dir):
            os.makedirs(preview_dir)

        # Convert string, in case if it's a problem 
        self.dialog.l_preview_files = [str(f_path) for f_path in self.dialog.l_preview_files]

        if '.mov' in [n[-4:] for n in self.dialog.l_preview_files]:
            # Case 1: one mov - copy
            if len(self.dialog.l_preview_files) == 1:
                src = self.dialog.l_preview_files[0]
                if src.endswith('stereo.mov'):
                    self.dialog.v_preview = preview_dir + self.dialog.version_name + '.stereo.mov'
                else:
                    self.dialog.v_preview = preview_dir + self.dialog.version_name + '.mov'
                shutil.copyfile(src, self.dialog.v_preview)

            # Case 2: multi mov files - combine them
            else:
                self.dialog.v_preview = preview_dir + self.dialog.version_name + '.mov'
                mov_files = ' '.join(self.dialog.l_preview_files)

                cmd = '"' + self.dialog.rvio_path + '" ' + mov_files + ' -o ' + self.dialog.v_preview
                if sys.platform.startswith('linux'):
                    cmd += ' -outparams comment="author ' + getpass.getuser() + '"'

                self.dialog.print_log('Merge mov files. ' + cmd)
                p = subprocess.Popen(cmd, shell=True)
                p.communicate()
        else:
            # Case 3: images > copy (convert to jpegs) and convert
            self.dialog.v_preview = preview_dir + self.dialog.version_name + '.mov'
            l_copied_files = []
            self.dialog.l_preview_files.sort()
            first_frame = -1

            # self.dialog.print_log('self.dialog.l_preview_files: ' + str(self.dialog.l_preview_files))
            # if this is a standard image sequence, use it, no need to copy. To save some time for lighter...
            src_seq, first_frame = self.get_src_sequence(self.dialog.l_preview_files)
            if src_seq == '':
                self.dialog.print_log(u'将图片序列拷贝到publish preview下转换.')
                for i in range(len(self.dialog.l_preview_files)):
                    src = self.dialog.l_preview_files[i]
                    dst = preview_dir + '/tmp_jpg/' + (self.dialog.version_name + ('.%04d.' % i) + 'jpg')
                    if not os.path.isdir(os.path.dirname(dst)):
                        os.makedirs(os.path.dirname(dst))
                    self.copy_file(src, dst, img_size=None)
                    if os.path.isfile(dst):
                        l_copied_files.append(dst)
                        self.dialog.print_log(u'Copy l_preview_file to :' + dst)
                        tokens = src.split('.')
                        if len(tokens) > 1 and tokens[-2].isdigit() and (
                                first_frame == -1 or int(tokens[-2]) < first_frame):
                            first_frame = int(tokens[-2])

                if first_frame == -1:
                    first_frame = 1

                src_seq = preview_dir + '/tmp_jpg/' + self.dialog.version_name + '.%04d.jpg'

            self.dialog.print_log('src_seq: ' + src_seq)
            if src_seq.endswith('.jpg') and is_aces:
                raise "ACES can't use jpg comp mov, please call TD!"

            temp_mov = tempfile.mktemp() + os.path.basename(self.dialog.version_dir) + '.mov'
            self.dialog.print_log('rvio convert mov file : ' + temp_mov)

            if hasattr(self.dialog, 'shot_audio_file') and len(os.listdir(os.path.dirname(src_seq))) > 1:
                cmd = '"' + self.dialog.rvio_path + '" [ ' + src_seq + ' ' + self.dialog.shot_audio_file + ' -pa 1.0 ] -o ' + temp_mov
                if is_aces:
                    cmd = ['OCIO={}'.format(ocio_path), 'RV_PATHSWAP_SOURCE_A={}'.format(src_seq),
                           'RV_PATHSWAP_SOURCE_B={}'.format(self.dialog.shot_audio_file), self.dialog.rvio_path,
                           exr2movjpg_double_rv, '-pa', str(1.0), '-o', temp_mov]

                    cmd = ' '.join(cmd)
            else:
                cmd = '"' + self.dialog.rvio_path + '" [ ' + src_seq + ' -pa 1.0 ] -o ' + temp_mov
                if is_aces:
                    cmd = ['OCIO={}'.format(ocio_path), 'RV_PATHSWAP_SOURCE_A={}'.format(src_seq),
                           self.dialog.rvio_path, exr2movjpg_single_rv, '-pa', str(1.0), '-o', temp_mov]
                    cmd = ' '.join(cmd)

            if src_seq.endswith('.exr'):
                if not is_aces:
                    cmd += ' -outsrgb'

            cmd += ' -outparams comment="author ' + getpass.getuser() + '" timecode=' + str(first_frame)

            # add "client name | shot name" on preview mov 
            # client_name = get_shot_client_name(self.dialog)
            # water_mark = ''
            # if client_name:
            #     water_mark = ' -overlay textburn " " " " "{0} | {1}" " " " " " " 0.33 20.0'.format(
            #         self.dialog.entity['name'], client_name)
            # cmd += water_mark

            self.dialog.print_log(cmd)

            p = subprocess.Popen(cmd, shell=True)
            p.communicate()
            # self.dialog.print_log('\n--'.join(get_subprocess_info(p)))

            if os.path.isfile(temp_mov):
                self.dialog.print_log('Move temp mov file ' + temp_mov + ' to ' + self.dialog.v_preview)
                self.dialog.print_log('Mov file size : ' + str(os.path.getsize(temp_mov)))
                os.system("chmod 777 %s" % os.path.dirname(self.dialog.v_preview))

                # for win
                if sys.platform.startswith('win'):
                    shutil.move(temp_mov, self.dialog.v_preview)

                # for linux copy
                if sys.platform.startswith('linux'):
                    copy_in_ternimal(temp_mov, self.dialog.v_preview)

            self.dialog.print_log(u'self.dialog.version_tag: {}'.format(self.dialog.version_tag))

            if self.dialog.step['name'] in ['lgt', 'pfx']:
                edit_slate_output_result = 'R3' not in self.dialog.version_tag
                self.dialog.print_log('Edit slate output for master : {}'.format(edit_slate_output_result))
                if edit_slate_output_result:
                    toolset = os.getenv('LC_TOOLSET')
                    edit_slate_cmd = 'python ' + toolset + '/tools/gene/diTools/send_master.py ' + src_seq + ' ' + self.dialog.v_preview + ' ' + getpass.getuser() + ' ' + self.dialog.version_name
                    edit_slate_p = subprocess.Popen(edit_slate_cmd, shell=True)
                    edit_slate_p.communicate()

                    self.dialog.print_log(edit_slate_cmd)

            # clean jpg files
            # remove clean jpg files, move jpg to tmp_jpg, and fix the bug of edit_slate_cmd can't found jpg file
            # for file_path in l_copied_files:
            #     os.remove(file_path)
            if l_copied_files:
                tmp_jpg_path = os.path.dirname(l_copied_files[0])
                if os.path.isdir(tmp_jpg_path):
                    shutil.rmtree(tmp_jpg_path)

        print 'preview file: ' + self.dialog.v_preview

        return

    def rig_preview(self):
        """
        只对rig环节提交有效果
        """
        if "rig.rigging" not in str(self.dialog.v_preview):
            return

        import maya.cmds as mc
        if mc.objExists("poly"):
            mc.select("poly")
            mc.viewFit()
            mc.select(d=True)
            mc.refresh()
        image_path = self.dialog.v_preview.split("preview/")[0] + "preview/thumbnail.jpg"
        mc.refresh(cv=True, fe="jpg", fn=image_path)

    def proceed(self):
        try:
            color_space_info = self.dialog.sg.find_one('Project',
                                                       [['name', 'is', self.dialog.project['name']]],
                                                       ['sg_color_space'])
            if color_space_info['sg_color_space'] == "ACES" and self.dialog.step['name'] in ['lgt', 'pfx', 'dmt']:
                is_aces = True
            else:
                is_aces = False

            self.dialog.print_log(u"Current proj {0}'s color space info is: {1}. \nIs ACES: {2}".format(
                str(self.dialog.project['name']), str(color_space_info), str(is_aces)))

            self.create_version_preview(is_aces=is_aces)

            self.rig_preview()

            self.dialog.sg.update('Version', self.dialog.v_info['id'],
                                  {'sg_path_to_movie': self.dialog.v_preview.replace('Z:/', '${RV_PATHSWAP_ROOT}/').
                                  replace('/mnt/proj/', '${RV_PATHSWAP_ROOT}/').
                                  replace('/Volumes/lcadata/', '${RV_PATHSWAP_ROOT}/').replace('\\', '/')})

            # Upload
            try:
                self.dialog.sg.upload('Version', self.dialog.v_info['id'], self.dialog.v_preview, "sg_uploaded_movie")
            except:
                print 'Failed to upload the mov file. Will be upload later.'
                # from PySide import QtGui
                import sgtk
                from sgtk.platform.qt import QtGui
                self.dialog.print_log('Failed to upload the mov file. Will be upload later.',
                                      txt_color=QtGui.QColor(255, 150, 30))

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
