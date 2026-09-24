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
import getpass

log_root_path='/mnt/proj/trash/srf_sg_publish_log'
tool_srf_path='{}/python/tk_lca_publish/publish_process/srf_sg'.format(os.getenv('LCA_PUBLISH_APP'))
# tool_srf_path='/mnt/work/home/yingjie/git_repo/tk-lca-publish/python/tk_lca_publish/publish_process/srf_sg'

# cur_dir,cur_name = os.path.split(__file__)

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"将katana文件的所有srf数据出cache"
        self.description = u"调用scan_publish.py导出数据。"
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
            self.dialog.print_log('Log : Start publish srf files...')
        
            if int(self.dialog.w_publish_file.checkBox.isChecked()):
                self.dialog.print_log('Log : Only publish scene_graph_xml file.')
                return self.publish_uv()

            if not self.dialog.katana_file or not os.path.isfile(self.dialog.katana_file):
                return (u'文件错误 : '+self.dialog.katana_file)

            #defined in ./tk-lca-publish/python/tk_lca_publish/depts/srf_sg/app_dialog.py
            lca_rez_path = os.getenv('LCA_REZ')
            katanaApp=lca_rez_path + '/launchers/'+self.dialog.project['name'].lower()+'/linux/katana'
            
            # self.dialog.katanaApp='/mnt/work/home/yingjie/Desktop/kl2.1v1'

            asset_info = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_asset_type'])
            asset_type=asset_info['sg_asset_type']
            export_xgen=int(self.dialog.w_publish_file.checkBox_xgenarc.isChecked())

            self.dialog.print_log('Log : Build publish cmd...')

            self.out_info_file=log_root_path+'/'+getpass.getuser()+'.srf_publish_log.txt'
            out = open(self.out_info_file,'w')
            err = open(log_root_path+'/'+getpass.getuser()+'.srf_publish_error.txt','w')

            try:
                # export_xgen=0
                cmd = katanaApp+' '+ '--script='+tool_srf_path+'/do_publish_srf_katana.py'
                cmd += ' '+self.dialog.version_dir
                cmd += ' '+self.dialog.katana_file
                cmd += ' '+str(export_xgen)
                cmd += ' '+self.dialog.l_preview_files[0]
                self.dialog.print_log('Log : Publish cmd is '+cmd)
    
                pp = subprocess.Popen(cmd, shell=True, stdout=out,stderr=err)
                
                line=u'Katana 进程启动，正在检测 & Publish，请耐心等待...\n\n'
                # while line!='':
                #     self.dialog.print_log(line)
                #     line=pp.stdout.readline()
                self.dialog.print_log(line)
                pp.wait()
            except:
                self.after_error()
                return traceback.format_exc()

            check_katana_file=self.check_katana_file()
            if check_katana_file: return check_katana_file

            check_klf_file=self.check_klf()
            if check_klf_file: return check_klf_file

            check_scene_graph=self.check_scene_graph()
            if check_scene_graph: return check_scene_graph

            return ''
        except:
            return traceback.format_exc()

    def check_scene_graph(self):
        if not os.path.isdir(os.path.join(self.dialog.version_dir,'scene_graph_xml')):
            self.after_error()
            return (u'scene_graph_xml '+os.path.join(self.dialog.version_dir,'scene_graph_xml')+u' 文件夹没有publish.')
        return ''    

    def check_katana_file(self):
        asset_name=os.path.basename(self.dialog.katana_file)
        asset_name=asset_name.split('.')[0]
        if not os.path.isfile(os.path.join(self.dialog.version_dir,asset_name+'.katana')) :
            self.after_error()
            return u'Katana 文件没有publish成功 '+os.path.join(self.dialog.version_dir,asset_name+'.katana')
        return ''        

    def check_klf(self):
        file_s=os.listdir(self.dialog.version_dir)
        has_klf=False
        for f in file_s:
            if f.endswith('.klf'):
                has_klf=True
                break
        if not has_klf :
            self.after_error()
            return (u'Klf 文件没有publish成功 '+os.path.join(self.dialog.version_dir,asset_name+'.klf'))
        
        return ''

    def after_error(self):
        try:
            subprocess.Popen('gedit '+self.out_info_file,shell=True)
            if self.dialog.version_dir and os.path.isdir(self.dialog.version_dir):
                print 'Try to delete dir ',self.dialog.version_dir
                shutil.rmtree(self.dialog.version_dir)
        except:
            pass

    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


