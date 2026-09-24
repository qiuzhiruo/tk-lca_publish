# -*- coding:utf-8 -*-

import os
import traceback
import shutil

import pymel.core as pm


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"自动升级一个版本， 将旧的版本指向带版本号的asb"
        self.description = u"自动升级一个版本， 将旧的版本指向带版本号的asb"
        return


    def proceed(self):
        try:
            # get version path
            asb_version_path = ''
            try:
                path = os.path.dirname( pm.sceneName() ).replace('\\', '/')
                f = open( os.path.join(path, os.path.basename(pm.sceneName())[:-3]+'.asb_version.txt'), 'r' )
                asb_version_path = f.read()
                f.close()
                asb_version_path = asb_version_path.strip()
                os.remove( os.path.join(path, os.path.basename(pm.sceneName())[:-3]+'.asb_version.txt') )
            except:
                pass

            ma_file = pm.sceneName()
            version_up = ma_file[:-7] + 'v' + format( int(self.dialog.version_num)+1, '#03' ) + '.ma'

            # close current scene before editing the ma file
            import maya.cmds as cmds
            try:
                cmds.file(new=True, force=True)
            except:
                print traceback.format_exc()

            # version up
            try:
                shutil.copyfile( ma_file, version_up )
            except:
                return u"升级版本失败: "+version_up

            # edit old .ma file
            if not os.path.isfile( asb_version_path ):
                return ""

            contents = []
            with open(ma_file, 'r') as f:
                for line in f:
                    contents.append(line)
            # there is no need to close f with this syntax

            asb_name = os.path.basename(asb_version_path)
            for i in range(len(contents)):
                if contents[i].startswith('file ') and asb_name in contents[i]:
                    buffer = contents[i].replace('\\', '/').split('/')
                    for b in range(len(buffer)):
                        if asb_name in buffer[b]:
                            buffer[b-1] = asb_version_path.replace('\\', '/').split('/')[-2]
                    contents[i] = '/'.join( buffer )

            file_handle = open(ma_file, 'w')
            file_handle.writelines(contents)
            file_handle.close()

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


