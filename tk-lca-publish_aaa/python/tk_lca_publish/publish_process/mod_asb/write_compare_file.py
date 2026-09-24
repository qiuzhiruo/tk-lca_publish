# -*- coding:utf-8 -*-

import os
import json
import traceback


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"将asb修改信息写出文件。"
        self.description = u"将asb修改的完整信息写出文件。"
        return

    def proceed(self):
        try:
            # 暂时保留txt文件
            if not hasattr(self.dialog, 'ar_info') or not self.dialog.ar_info:
                self.dialog.ar_info = {'add_ar': [],
                        'remove_ar':[],
                        'hierarchy_change': [],
                        'xform_change': []}
            compare_file=self.dialog.version_dir + '/' + 'compare_file.txt'

            all_text=self.dialog.ar_msg
            ar_info_file = self.dialog.version_dir + '/' + 'compare_ar_file.json'
            
            with open(ar_info_file, 'w') as j:
                j.write(json.dumps(self.dialog.ar_info, indent=4, encoding='utf-8'))
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
