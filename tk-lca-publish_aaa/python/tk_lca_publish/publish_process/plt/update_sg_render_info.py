# -*- coding:utf-8 -*-

import os,sys,re,traceback
import plt.xgen_file_manager.file_utils as pxfu
reload(pxfu)

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"写出植被渲染内存和耗时"
        self.description = u"写出植被渲染内存和耗时"
        return

    def proceed(self):
        try:
            proj = self.dialog.project['name']
            entity = self.dialog.entity['name']
            if not re.match('[a-z]\d{5}', entity):
                return ''
            mov_file = [str(f_path) for f_path in self.dialog.l_preview_files][0]
            output_cache=str(self.dialog.w_publish_file.lineEdit_cache.text())
            mem_data, setup_time, render_time = pxfu.get_plt_render_info(proj, entity, mov_file, output_cache)
            self.dialog.sg.update('Version', self.dialog.v_info['id'], \
                {'sg_memory': float('%.2f'%mem_data), 'sg_remark':'%.2fmin'%render_time})
            return ""
        except:
            return entity+' '+mov_file+'\n'+traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
