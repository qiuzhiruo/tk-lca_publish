#! -*- coding:utf-8 -*-
import glob
import os
import traceback
import shutil
import subprocess
import getpass


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"修改preview从1001帧开始播放"
        self.description = u"修改preview从1001帧开始播放。"
        return

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

        tokens[-2] = '%0' + str(len(std_tokens[-2])) + 'd'
        return '.'.join(tokens), int(std_tokens[-2])

    def modify_preview(self):
        preview_dir = self.dialog.version_dir + '/preview/'

        entries = os.listdir(self.dialog.version_dir)
        tmp_dir = os.path.join(self.dialog.version_dir, 'tmp')
        if not os.path.isdir(tmp_dir):
            os.makedirs(tmp_dir)

        if os.path.exists(preview_dir):
            file_list = os.listdir(preview_dir)
            for file in file_list:
                file_path = os.path.join(preview_dir, file)
                os.remove(file_path)

        for entry in entries:
            file_path = os.path.join(self.dialog.version_dir, entry)
            if os.path.isfile(file_path):
                if file_path.endswith('.jpg'):
                    file_name = os.path.basename(file_path)
                    tmp_file_path = os.path.join(tmp_dir, file_name)
                    shutil.copyfile(file_path, tmp_file_path)

                    name, ext = os.path.splitext(os.path.basename(tmp_file_path))
                    _file_name = '{}.{}{}'.format(name, 1001, ext)
                    new_tmp_file = os.path.join(tmp_dir, _file_name)
                    os.rename(tmp_file_path, new_tmp_file)

                    tmp_file_list = glob.glob(tmp_dir + '/*')
                    src_seq, first_frame = self.get_src_sequence(tmp_file_list)
                    preview_file = self.dialog.version_dir.split('/')[-1] + '.mov'
                    preview_mov = os.path.join(preview_dir, preview_file)
                    cmd = '"' + self.dialog.rvio_path + '" [ ' + new_tmp_file + ' -pa 1.0 ] -o ' + preview_mov
                    cmd += ' -outparams comment="author ' + getpass.getuser() + '" timecode=' + str(first_frame)
                    self.dialog.print_log(cmd)
                    p = subprocess.Popen(cmd, shell=True)
                    p.communicate()
        if os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)
            self.dialog.print_log('remove tmp dir.')

    def proceed(self):
        try:
            self.modify_preview()
            self.dialog.sg.update('Version', self.dialog.v_info['id'], {
                'sg_path_to_movie': self.dialog.v_preview.replace('Z:/', '${RV_PATHSWAP_ROOT}/').replace('/mnt/proj/',
                                                                                                         '${RV_PATHSWAP_ROOT}/').replace(
                    '/Volumes/lcadata/', '${RV_PATHSWAP_ROOT}/').replace('\\', '/')})
            self.dialog.print_log('update version preview.')
            # Upload
            try:
                self.dialog.sg.upload('Version', self.dialog.v_info['id'], self.dialog.v_preview, "sg_uploaded_movie")
                self.dialog.print_log('upload version preview.')
            except:
                print('Failed to upload the mov file. Will be upload later.')
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
