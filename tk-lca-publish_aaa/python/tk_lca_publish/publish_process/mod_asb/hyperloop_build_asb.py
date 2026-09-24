# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2019 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2019.06
#
############################################

import os
import sys
import re
import pickle
import traceback
import subprocess
import shutil

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"构建 asb"
        self.description = u"构建 asb"
        return

    def build_asb_def(self):

        maya_file = self.dialog.version_dir + '/assembly_reference/' + self.dialog.entity['name'] + '.ma'
        assembly_file = self.dialog.version_dir + '/assembly_definition/' + self.dialog.entity['name'] + '.ma'
        gpu_cache_file = self.dialog.version_dir + '/gpu/proxy.abc'
        proj_tags = self.dialog.sg.find_one('Project', [['name', 'is', self.dialog.project['name'].upper()]], ['tag_list'])['tag_list']
        if not 'No USD' in proj_tags:
            shutil.copyfile(os.path.dirname(__file__)+'/assembly_definition_usd.ma', assembly_file)
        else:
            shutil.copyfile(os.path.dirname(__file__)+'/assembly_definition.ma', assembly_file)
        f = open(assembly_file, 'r')
        l_lines = f.readlines()
        f.close()
        f = open(assembly_file, 'w')
        for line in l_lines:
            new_line = line.replace('{ASSET}', self.dialog.entity['name'])
            new_line = new_line.replace('{MAYA_FILE}', maya_file)
            new_line = new_line.replace('{GPU_CACHE_PROXY}', gpu_cache_file)

            f.write(new_line)
        f.close()

        self.dialog.assembly_definition = assembly_file
        return

    def replace_version(self):
        default_file = self.dialog.version_dir + "/" + self.dialog.entity['name'] + '.ma'
        maya_file = self.dialog.version_dir + '/assembly_reference/' + self.dialog.entity['name'] + '.ma'
        assembly_file = self.dialog.version_dir + '/assembly_definition/' + self.dialog.entity['name'] + '.ma'
        file_list = [default_file, maya_file, assembly_file]
        for single_file in file_list:
            f = open(single_file, 'r')
            l_lines = f.readlines()
            f.close()
            f = open(single_file, 'w')
            for line in l_lines:
                asset_re = re.compile('	setAttr \".def" -type "string" "(\S*)";')
                asset_match = asset_re.match(line)
                if asset_match:
                    asset_path = asset_match.groups()[0]

                    compents = asset_path.split("/")

                    version = compents[10]
                    no_version_list = version.split(".")[:-1]
                    no_version = ".".join(no_version_list)

                    compents[10] = no_version

                    new_file_no_version = "/".join(compents)
                    new_line = '	setAttr ".def" -type "string" "{0}";\n'.format(new_file_no_version)
                    new_line = new_line.replace("/mnt/proj/", "Z:/")
                else:
                    new_line = line


                f.write(new_line)
            f.close()


    def proceed(self):
        try:
            py_script = os.path.dirname(__file__) + '/hyperloop_build.py'
            pkl_file = self.dialog.version_dir + '/assets.pkl'
            xml_file = self.dialog.w_publish_file.lineEdit_xml.text()
            maya_file = self.dialog.version_dir + '/' + self.dialog.entity['name'] + '.ma'
            gpu_cache_file = self.dialog.version_dir + '/gpu/proxy.abc'

            for dir_name in ['assembly_reference', 'assembly_definition', 'gpu', 'scene_graph_xml']:
                if not os.path.isdir(self.dialog.version_dir + '/' + dir_name):
                    os.makedirs(self.dialog.version_dir + '/' + dir_name)

            f = open(pkl_file, 'w')
            pickle.dump(self.dialog.hyperloop, f)
            f.close()
            lca_rez_path = os.getenv('LCA_REZ')
            cmd_str = ' '.join(['{}/launchers/nza/linux/mayapy'.format(lca_rez_path), py_script, pkl_file, xml_file, maya_file, self.dialog.version_name, self.dialog.entity['name']])
            p = subprocess.Popen(cmd_str, shell=True, stdin=subprocess.PIPE, stderr=subprocess.PIPE )
            out, err = p.communicate()
            self.dialog.print_log(cmd_str)

            if 'Traceback' in err:
                return u"错误信息：\n" + err

            if not os.path.isfile(maya_file):
                return u"没有创建 asb 的 assembly: " + maya_file

            if not os.path.isfile(gpu_cache_file):
                return u"没有创建 gpu cache: " + gpu_cache_file

            shutil.copyfile(maya_file, self.dialog.version_dir + '/assembly_reference/' + self.dialog.entity['name'] + '.ma')

            self.build_asb_def()

            #replace version path
            self.replace_version()

            if len(self.dialog.l_preview_files) == 1 and os.path.basename(self.dialog.l_preview_files[0]) == 'hyperloop_logo.jpg':
                if os.path.isfile(self.dialog.version_dir + '/preview/' + self.dialog.version_name + '.jpg'):
                    self.dialog.l_preview_files = [self.dialog.version_dir + '/preview/' + self.dialog.version_name + '.jpg']

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

