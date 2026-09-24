# -*- coding:utf-8 -*-
import os
import platform
import traceback
import maya.cmds as cmds


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"Write Publish Cache Log To Trash"
        self.description = u"记录publish文件路径到'/mnt/proj/trash/ani_cache_log', 作为event补救"
        return

    def proceed(self):
        try:
            proj = self.dialog.project['name'].lower()
            dept = self.dialog.step['name']
            version_name = cmds.file(q=True, sceneName=True, shortName=True).rsplit('.', 1)[0]
            if not proj:
                self.dialog.print_log("'No project linked to publish")
                return traceback.format_exc()
            if not dept:
                self.dialog.print_log("'No dept")
                return traceback.format_exc()
            version_entity = self.dialog.sg.find_one('Version',
                                                     [['project', 'name_is', proj], ['code', 'is', version_name]],
                                                     ['sg_version_folder'])
            version_dir = version_entity['sg_version_folder']['local_path_linux'].rsplit('/', 1)[0]
            # write log
            if platform.system() == 'Linux':
                publish_log = "/mnt/proj/trash/ani_cache_log/{proj}_publish_cache_log.txt".format(proj=proj.lower())
            else:
                publish_log = "Z:/trash/ani_cache_log/{proj}_publish_cache_log.txt".format(proj=proj.lower())
            if os.path.exists(publish_log):
                with open(publish_log, "r") as wf:
                    lines = wf.readlines()
                    if lines:
                        for line in lines:
                            line = line.rstrip("\n")
                            if version_dir in line:
                                print 'This task already exists'
                                return ""
            with open(publish_log, 'a') as wf:
                wf.write(dept + ' ' + version_dir + '\n')
            print "publish_log:", publish_log

            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description

# if __name__ == '__main__':
#     print sg.find('Version',[['entity','is',{'type': 'Shot', 'id': 32549}]],['code'])
