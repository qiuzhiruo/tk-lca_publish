# -*- coding:utf-8 -*-

import os
import traceback
import shutil
import pymel.core as pm

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"建立 Assembly Definition 文件。"
        self.description = u"建立 Assembly Definition 文件。"
        return


    def build_asb_def(self):
        maya_file = self.dialog.version_dir + '/' + self.dialog.entity['name'] + '.ma'
        assembly_file = self.dialog.version_dir + '/assembly_definition/' + self.dialog.entity['name'] + '.ma'

        shutil.copyfile(os.path.dirname(__file__)+'/assembly_definition.ma', assembly_file)
        f = open(assembly_file, 'r')
        l_lines = f.readlines()
        f.close()
        f = open(assembly_file, 'w')
        for line in l_lines:
            new_line = line.replace('{ASSET}', self.dialog.entity['name'])
            new_line = new_line.replace('{MAYA_FILE}', maya_file)
            f.write(new_line)
        f.close()

        self.dialog.assembly_definition = assembly_file
        return


    def proceed(self):
        try:
            # Create Folders
            if not os.path.isdir(self.dialog.version_dir + '/assembly_definition/'):
                os.makedirs(self.dialog.version_dir + '/assembly_definition/')

            self.build_asb_def()
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


