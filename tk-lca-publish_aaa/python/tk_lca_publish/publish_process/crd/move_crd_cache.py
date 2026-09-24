# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: John Su
#
# Date: 2013.11
#
# Description: As the description shows below
#
############################################

import os
import traceback
import shutil
import glob
import sys
# sys.path.append('/mnt/utility/toolset/applications/houdini/H16/script/EfxVersionFactory')
import vf_utils

def findFiles(path, ext='.exr',onlyFileName=False):
    """
    Find all files in path
    """
    result=[]
    files=os.listdir(path)
    for parentf, folders, files in os.walk(path):
        files_ext = filter(lambda x: x.endswith(ext), files)
        if onlyFileName:
            result.extend(files_ext)
        else:
            fullPath = [os.path.join(parentf, f) for f in files_ext]
            result.extend(fullPath)
    return result

# All publish process will use StdProcess as the class name.
class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"复制Cache"
        self.description = u"复制所选cache目录到publish文件夹."

    def output(self, msg):
        self.dialog.print_log(str(msg))

    def findOwnerId(self, dir_path):
        from os import stat
        return stat(dir_path).st_uid

    def makeDir777AndChmodParent(self, dir_path, parent_dir_to_chmod='publish'):
        """
        make dir_path, and chmod a parent dir named parent_dir_to_chmod to 777
        """
        _p = '/%s/' % parent_dir_to_chmod
        if _p in dir_path:
            parent_dir = os.path.join(dir_path.split(_p)[0], parent_dir_to_chmod)
            if os.path.exists(parent_dir):
                if self.findOwnerId(parent_dir) == os.geteuid():
                    os.chmod(parent_dir, 0777)      # may cause exception
            else:
                os.makedirs(parent_dir)
                os.chmod(parent_dir, 0777)

        # may cause exception, use try outside of this method.
        os.makedirs(dir_path)
        os.chmod(dir_path, 0777)

    def _copy(self, src, dst):
        # # debug
        # self.output((src, dst))
        # return
        shutil.copy2(src, dst)
        #os.system('cp -r %s %s' % (src, dst))

    def proceed(self):
        try:
            publish_version_dir = self.dialog.version_dir

            abc_total = []
            for i in range(self.dialog.w_publish_file.listWidget_cache.count()):
                cache_path = self.dialog.w_publish_file.listWidget_cache.item(i).text().rstrip('/')
                abc_total.extend(findFiles(cache_path, '.abc'))
            if not abc_total:
                self.output(u'Warning: 没有在路径下发现abc.')

            for abc in abc_total:
                # .abc
                element_name = abc.rsplit('/abc/')[0].split('/')[-1]
                target_dir = os.path.join(publish_version_dir, element_name, 'abc')
                if not os.path.exists(target_dir):
                    os.makedirs(target_dir)
                self._copy(abc, target_dir)

                # .info
                info_path = os.path.join(os.path.dirname(abc), element_name+'.info')
                if os.path.exists(info_path):
                    self._copy(info_path, target_dir)
            return ""
        except:
            # self.output(u'publish错误，请检查路径是否符合标准.')
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


