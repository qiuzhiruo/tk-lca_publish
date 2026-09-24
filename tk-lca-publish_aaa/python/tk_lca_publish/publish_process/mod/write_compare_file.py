# -*- coding:utf-8 -*-

import os
import traceback
from proc.function_running_time import record_time


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"将模型修改信息写出文件。"
        self.description = u"将模型修改的完整信息写出文件。"
        return

    @record_time(__file__)
    def proceed(self):
        try:
            compare_file=self.dialog.version_dir + '/' + 'compare_file.txt'
            all_text=self.dialog.md_msg
            f = open(compare_file, 'w')
            f.write(all_text.encode('utf8'))
            f.close()
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description



