# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.01
#
# Description: 
#
############################################

import os
import sys
import traceback
import shutil

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"转化 EDL 文件"
        self.description = u" Final Cut 的 EDL 文件转为 RV 可以使用的 EDL 文。 拷贝wav文件"
        return


    def get_frame(self, time_str):
        l_tokens = time_str.split(':')
        if len(l_tokens) != 4:
            return None

        if not (l_tokens[0].isdigit() and l_tokens[1].isdigit() and l_tokens[2].isdigit() and l_tokens[3].isdigit()):
            return None

        f = int(l_tokens[3])
        f += int(l_tokens[2]) * 24
        f += int(l_tokens[1]) * 1440
        f += int(l_tokens[0]) * 86400
        return f


    def get_file(self, file_name):
        file_name = file_name.lower()
        if len(file_name) <10:
            return None

        seq = file_name[:3]
        shot = file_name[:6]
        dept = file_name[7:10]
        #version = file_name[:-4]
        version_key = file_name[:-9]

        publish_root = self.root + '/projects/' + self.show_name + '/shot/' + seq + '/' + shot + '/' + dept + '/publish/'
        if not os.path.isdir(publish_root):
            return None

        l_versions = os.listdir(publish_root)
        l_task_versions = []
        for version in l_versions:
            if version.startswith(version_key) and version[-3:].isdigit():
                l_task_versions.append(version)

        if len(l_task_versions) == 0:
            return None

        l_task_versions.sort()
        version = l_task_versions[-1]

        file_path = self.root + '/projects/' + self.show_name + '/shot/' + seq + '/' + shot + '/' + dept + '/publish/' + version + '/preview/' + version + '.mov'

        if not os.path.isfile(file_path):
            return None

        if version+'.mov' < file_name:
            print file_name, '>', version+'.mov'

        return file_path


    def proceed(self):
        try:
            # Copy ma file
            if sys.platform.startswith('win'):
                self.root = 'Z:'
            elif sys.platform.startswith('linux'):
                self.root = '/mnt/proj'
            elif sys.platform.startswith('darwin'):
                self.root = '/Volumes/lcadata'

            self.show_name = self.dialog.project['name'].lower()
            self.dialog.l_valid_chunks = []

            fc_edl = str(self.dialog.w_publish_file.lineEdit_edl.text())
            if not os.path.isfile(fc_edl):
                return ""

            f = open(fc_edl, 'r')
            contents = f.readlines()
            f.close()

            l_chunks = []
            chunk = []

            for line in contents:
                if line == '\n':
                    l_chunks.append(chunk)
                    chunk = []
                else:
                    chunk.append(line[:-1])

            for chunk in l_chunks:
                f_start = f_end = file_path = v_start = v_end = None
                for line in chunk:
                    l_tokens = line.split(' ')
                    if ' AX V ' in line:
                        #print line
                        while '' in l_tokens:
                            l_tokens.remove('')

                        if f_start == None:
                            f_start = self.get_frame(l_tokens[-4])
                            f_end = self.get_frame(l_tokens[-3]) - 1
                            v_start = self.get_frame(l_tokens[-2])
                            v_end = self.get_frame(l_tokens[-1]) -1

                    if '.MOV' in line:
                        #print line
                        while '' in l_tokens:
                            l_tokens.remove('')
                        l_tokens = line.split(' ')
                        file_path = self.get_file( l_tokens[-1])

                if f_start != None and f_end != None and file_path:
                    if len(self.dialog.l_valid_chunks) > 0 and self.dialog.l_valid_chunks[-1][0] == file_path and f_start == self.dialog.l_valid_chunks[-1][2] + 1 and v_start == self.dialog.l_valid_chunks[-1][4] + 1:
                        self.dialog.l_valid_chunks[-1][2] = f_end
                        self.dialog.l_valid_chunks[-1][4] = v_end
                    else:
                        self.dialog.l_valid_chunks.append([file_path, f_start, f_end, v_start, v_end])

            f = open( self.dialog.version_dir + "/" + self.dialog.entity['name'] + ".rvedl", 'w')
            if len(self.dialog.l_valid_chunks) > 0:
                chunk = self.dialog.l_valid_chunks[0]
                f.write('"'+chunk[0].replace(self.root, "${RV_PATHSWAP_ROOT}")+'" '+ str(chunk[1]) + ' '+ str(chunk[2]) + '\n')
                for i in range(len(self.dialog.l_valid_chunks) - 1):
                    previous_chunk = self.dialog.l_valid_chunks[i]
                    chunk = self.dialog.l_valid_chunks[1+i]
                    gap = chunk[3] - previous_chunk[4]
                    if gap == 1:
                        f.write('"'+chunk[0].replace(self.root, "${RV_PATHSWAP_ROOT}")+'" '+ str(chunk[1]) + ' '+ str(chunk[2]) + '\n')
                    elif gap > 1:
                        shutil.copyfile(os.path.split( __file__ )[0] + '/black_frame.tif', self.dialog.version_dir + "/black_frame.tif" )
                        f.write('"' + self.dialog.version_dir.replace(self.root, "${RV_PATHSWAP_ROOT}") + '/black_frame.tif" 0 '+ str(gap -1) + '\n')
                        f.write('"'+chunk[0].replace(self.root, "${RV_PATHSWAP_ROOT}")+'" '+ str(chunk[1]) + ' '+ str(chunk[2]) + '\n')
                        #shutil.copy

            f.close()


            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


