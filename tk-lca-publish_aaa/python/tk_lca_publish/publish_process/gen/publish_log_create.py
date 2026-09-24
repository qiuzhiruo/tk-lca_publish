# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'

import os
import traceback
import pymel.core as pm

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"create publish log file on work path"
        self.description = u"create publish log file on work path, in order to debug publish process"
        return

    def proceed(self):
        try:
            try:
                current_file = pm.sceneName().replace('\\','/')
                log_file = os.path.dirname(current_file) + '/publish_log/' + os.path.basename(current_file)[:-3]+'.log.txt'
                log_file = log_file.replace('//', '/')

                if not '/work/' in log_file and not 'W:/' in log_file:
                    return ""

                if not os.path.isdir(os.path.dirname(log_file)):
                    os.makedirs(os.path.dirname(log_file))

                if os.path.isfile(log_file):
                    os.remove(log_file)

                file_id = open(log_file, 'w')
                file_id.write('Start to log publish process...\n')
                file_id.close()
            except:
                pass

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
