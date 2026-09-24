# -*- coding:utf-8 -*-

import os
import traceback
import shutil

import sys
sys.path.append( '/'.join(os.path.dirname(__file__).replace('\\','/').split('/')[:-1]) + '/gen' )
import convertHi2Lo as hi2lo
# sys.path.append('U:/toolset/lib/production')
# sys.path.append('/mnt/utility/toolset/lib/production')
# sys.path.append('/Volumes/utility/toolset/lib/production')


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"将asb资产的reference路径替换成low版本。"
        self.description = u"将asb资产的reference路径替换成low版本，该操作在上一步骤生成的.ma文件上修改。仅对带版本号的.ma文件做此操作。"
        return

    def proceed(self):
        try:
            try:
                if not os.access(self.dialog.version_dir, os.W_OK):
                    return u"Writing permission denied by system when rewrite low resolution asb file!"
                if not os.path.isfile(self.dialog.version_dir+'/'+self.dialog.entity['name'] + '.ma'):
                    return u"Failed to find asb file: " + self.dialog.version_dir+'/'+self.dialog.entity['name'] + '.ma'
                try:
                    try:
                        # backup before overwrite
                        os.mkdir(self.dialog.version_dir+'/backup/')
                        shutil.copyfile(self.dialog.version_dir+'/'+self.dialog.entity['name']+'.ma', self.dialog.version_dir+'/backup/'+self.dialog.entity['name']+'.ma')
                    except:
                        print 'Failed to backup scene, keep going...'
                    hi2lo.ConvertHi2Lo(self.dialog.version_dir+'/'+self.dialog.entity['name'] + '.ma', overwrite=True).convert()
                except:
                    return u"Failed to convert asb to low resolution file!"
            except:
                return u"Failed to rewrite low resolution asb file!"

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


