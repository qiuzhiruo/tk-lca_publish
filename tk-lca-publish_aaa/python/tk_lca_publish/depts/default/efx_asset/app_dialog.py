# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: John Su
#
# Date: 2014.1.2
#
# Description: EFX publish tool.
#
########################################################################################

import os
import traceback
from efx_utils import *

try:
    import sgtk
    from sgtk.platform.qt import QtCore, QtGui

    # TODO
    import publish_dialog
    reload(publish_dialog)
    from publish_dialog import PublishDialog

    from ....ui.dialog import Ui_Dialog
    from ....ui.widget_sys import Ui_Form as widget_sys
    from ....ui.widget_version import Ui_Form as widget_version
    from ....ui.widget_file import Ui_Form as widget_file
    from ....ui.widget_check import Ui_Form as widget_check
    from ....ui.widget_publish import Ui_Form as widget_publish

    from ....ui.widget_file_efx import Ui_Form as widget_publish_file

except:
    print traceback.format_exc()


class AppDialog(PublishDialog):
    
    def __init__(self, app):

        try:
            PublishDialog.__init__(self, app)

            # Get environment info & production info from sgtk
            self.set_vars()
            self.set_dept_vars( __file__ )

            # set up the UI, which includes the dialog and all process widgets            
            self.setup_gui(Ui_Dialog, widget_sys, widget_version, widget_file, widget_check, widget_publish, widget_publish_file)

            # setup widget functions
            self.do_bind()
            self.do_dept_bind()

            self.show_app_info()

            self.w_publish_file.pushButton_pick_cache.setText('选取文件')
            self.w_file.label_description.setText('请选择需要Publish的文件，而不是父文件夹。所选文件会直接移动到Shotgun版本目录中.')

        except sgtk.TankError, e:
            self._app.log_error(str(e))

        except Exception:
            print traceback.format_exc()
            self._app.log_error(traceback.format_exc())

        return


    def do_dept_bind(self):
        self.w_publish_file.pushButton_pick_cache.clicked.connect(self.on_pick_cache)
        self.w_publish_file.listWidget_cache.itemClicked.connect(self.remove_cache)
        self.w_publish_file.pushButton_clear_cache.clicked.connect(self.remove_all_cache)

        return


    def on_pick_cache(self):
        pick_dialog = QtGui.QFileDialog(self)

        pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
        pick_dialog.setFileMode(QtGui.QFileDialog.Directory)
        pick_dialog.setOption(QtGui.QFileDialog.ShowDirsOnly, on=True)
        new_root=self.work_root.replace('/task/maya', '')
        new_root=new_root.replace('/mnt/work','/efxcache')
        pick_dialog.setDirectory(new_root)

        res = pick_dialog.exec_()
        if res != QtGui.QDialog.Accepted:
            return
        cache_dir = pick_dialog.selectedFiles()

        result_files=[]

        try:
            for d in cache_dir:
                result_files.extend(get_efx_data_from_folder(d))

            items = []
            for index in xrange(self.w_publish_file.listWidget_cache.count()):
                 items.append(str(self.w_publish_file.listWidget_cache.item(index).text()))

            current_comp=[]
            comp_index=[]
            for i in result_files:
                if i in items:
                    continue

                #find existing component name and store them
                for index in xrange(self.w_publish_file.listWidget_cache.count()):
                    current_item=str(self.w_publish_file.listWidget_cache.item(index).text())
                    if 'CompName:' in current_item:
                        current_comp.append(current_item)
                        comp_index.append(index)

                abs_path = os.path.abspath(i)
                extension= abs_path.split('.')[-1]

                #get the component name of the selected file
                comp_name=get_component_name(abs_path)
                component = 'CompName: '+comp_name+'---'+extension
                if 'Error' in component:
                    self.print_log('Cannot get component name for '+abs_path,txt_color=publish_dialog.TXT_RED)
                    continue

                if extension=='vdb':
                    if not any(['smoke' in comp_name, 'dust' in comp_name,'fire' in comp_name]):
                        self.print_log('Can not find smoke,dust,fire.',publish_dialog.TXT_RED)

                    look_file=os.path.join(os.path.dirname(abs_path),comp_name+'.klf')
                    if not look_file or not os.path.isfile(look_file):
                        self.print_log('Can not find look file for vdb '+comp_name,publish_dialog.TXT_ORANGE)

                #for exr we need display L or R
                if extension=='exr':
                    component+=' '+abs_path.split('/')[-2]

                #if the component name already exists, we won't add them to the list if it's vdb or exr
                if component in current_comp:
                    self.print_log(extension+' '+component)
                    if extension in ['vdb','exr']:
                        self.print_log('Component name "'+comp_name+'" already exists.',txt_color=publish_dialog.TXT_RED)
                        continue

                    self.w_publish_file.listWidget_cache.insertItem(comp_index[current_comp.index(component)]+1, abs_path)

                else:
                    self.w_publish_file.listWidget_cache.insertItem(0, abs_path)
                    self.w_publish_file.listWidget_cache.insertItem(0, component)

        except Exception:
            self.print_log(traceback.format_exc())

        return

    def remove_all_cache(self):
        self.w_publish_file.listWidget_cache.clear()
        
    def remove_cache(self):
        l_items = self.w_publish_file.listWidget_cache.selectedItems()

        if True: #self.w_publish_file.listWidget_cache._mouse_button.name == 'RightButton':
            for item in l_items:
                i = self.w_publish_file.listWidget_cache.indexFromItem(item).row()
                self.w_publish_file.listWidget_cache.takeItem(i)
        return


