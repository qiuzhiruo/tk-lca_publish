# -*- coding:utf-8 -*-

import os
import traceback
import sgtk
logger = sgtk.platform.get_logger(__name__)


def get_xgen_path(version_dir):
    xgenpaths = []
    file_path = os.listdir(version_dir)
    for file_name in file_path:
        if file_name.endswith('.xgen'):
            xgen_path = '{}/{}'.format(version_dir, file_name)
            if os.path.isfile(xgen_path):
                xgenpaths.append(xgen_path)
    return xgenpaths


def replace_textures_path(xgen_file, version_dir):
    old_data = []
    with open(xgen_file, 'r') as f:
        old_data.extend(f.readlines())

    with open(xgen_file, 'w') as f:
        for line in old_data:
            if '/3dPaintTextures/' in line:
                tmp_path = line.split('\t')[3].split('\n')[0]
                publish_version_folder = version_dir + '/tex/' + tmp_path.split('/')[-1]
                line = line.replace(tmp_path, publish_version_folder)
            f.write(line)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"替换publish目录下.xgen中3dPaintTextures的路径。"
        self.description = u"替换publish目录下.xgen中3dPaintTextures的路径。"

    def proceed(self):
        try:
            for xgenfile in get_xgen_path(self.dialog.version_dir):
                replace_textures_path(xgenfile, self.dialog.version_dir)
            logger.info('replace success')
        except:
            return traceback.format_exc()
        return ''

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
