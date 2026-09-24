# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
# Description: Copy publish files
#
############################################

import os
import traceback
import shutil
import subprocess
import sys


if 'REZ_SRF_TOOLS_ROOT' in os.environ.keys():

    import srf_publish_tools.scan_publish as ssk
    reload(ssk)
    import srf_publish_tools.checkFinalize as sstcf
    reload(sstcf)

else:
    lctools_env = os.environ.get('LCTOOLSET')
    sys.path.append(lctools_env+'/tools/srf/srf_publish_tools')
    try:
        import srf.srf_publish_tools.scan_publish as ssk
        reload(ssk)
        import srf.srf_publish_tools.check_finalize as sstcf
        reload(sstcf)
    except:
        import scan_publish as ssk
        reload(ssk)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"将katana文件的所有srf数据出cache"
        self.description = u"调用scan_publish.py导出数据。"
        self.dialog.w_publish.plainTextEdit_auto_description.setPlainText(sstcf.auto_description())
        return

    def publish_uv(self):

        task_scene_graph_xml=self.dialog.ctx.filesystem_locations[0]+'/srf/task/katana/scene_graph_xml'
        if not os.path.isdir(task_scene_graph_xml):
            return (u'文件夹'+task_scene_graph_xml+'不存在')
            
        out_files = os.listdir(task_scene_graph_xml)

        sg_xml_folder = self.dialog.version_dir+'/scene_graph_xml'
        if not os.path.isdir(sg_xml_folder):
            os.mkdir(sg_xml_folder)
            os.chmod(sg_xml_folder,0777)

        for f in out_files:
            f_path = os.path.join(task_scene_graph_xml, f)
            if os.path.isdir(f_path):
                shutil.copytree(f_path, sg_xml_folder)
            else:
                shutil.copy(f_path, sg_xml_folder)
        return ''

    def proceed(self):
        try:
            if int(self.dialog.w_publish_file.checkBox.isChecked()):
                print 'Only publish scene_graph_xml file.'
                return self.publish_uv()

            asset_info = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_asset_type'])
            asset_type=asset_info['sg_asset_type']
            export_xgen = int(asset_type=='flg' or self.dialog.w_publish_file.checkBox_xgenarc.isChecked())
            push_shader = int(self.dialog.w_publish_file.checkBox_shader.isChecked())
            publish_exp = int(self.dialog.w_publish_file.checkBox_exp.isChecked())
            
            try:
                sk = ssk.SrfKatana(dialog=self.dialog,
                                   xgen_archive=export_xgen,
                                   preview_file=self.dialog.l_preview_files[0],
                                   push_shader=push_shader,
                                   publish_exp=publish_exp)
                
                sk.do_publish()
            except:
                self.after_error()
                raise Exception(traceback.format_exc())

            asset_name=os.path.basename(self.dialog.katana_file)
            asset_name=asset_name.split('.')[0]
            if not os.path.isfile(os.path.join(self.dialog.version_dir,asset_name+'.katana')):
                self.after_error()
                return u'Katana 文件没有publish成功'

            file_s=os.listdir(self.dialog.version_dir)
            has_klf=False
            for f in file_s:
                if f.endswith('.klf'):
                    has_klf=True
                    break
            if not has_klf:
                self.after_error()
                return u'Klf 文件没有publish成功'
            return ''

        except:
            return traceback.format_exc()

    def after_error(self):
        try:
            if self.dialog.version_dir and os.path.isdir(self.dialog.version_dir):
                print 'Try to delete dir ',self.dialog.version_dir
                shutil.rmtree(self.dialog.version_dir)
        except:
            pass

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


