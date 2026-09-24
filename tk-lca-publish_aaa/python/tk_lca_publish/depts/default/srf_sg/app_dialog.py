# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Art publish tool. Create version on server and shtogun
#              This is the first publish tool in the LCA. All publish tools of
#              different departments will share:
#              Gui widgets; system check module; version check module
#
########################################################################################

import os
import sys
import pprint
import shutil
import traceback
import time
import getpass
import glob

lca_utility = os.getenv('LC_UTILITY')

tool_srf_path='%s/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/depts/default/srf_sg' % lca_utility
# tool_srf_path='/home/yingjie/git_repo/tk-lca-publish/python/tk_lca_publish/depts/srf_sg'
app_path = os.environ.get('LC_APP_PATH')

print("app_path:", app_path)

try:
    import sgtk
    from sgtk.platform.qt import QtCore, QtGui

    import publish_dialog
    reload(publish_dialog)
    from publish_dialog import PublishDialog

    from ....ui.dialog import Ui_Dialog
    from ....ui.widget_sys import Ui_Form as widget_sys
    from ....ui.widget_version import Ui_Form as widget_version
    from ....ui.widget_file import Ui_Form as widget_file
    from ....ui.widget_check import Ui_Form as widget_check
    from ....ui.widget_publish import Ui_Form as widget_publish

    from ....ui.widget_file_srf_sg import Ui_Form as widget_publish_file

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

            # TODO Can't use the thumbnail widget outside Maya
            self.w_file.thumbnail_widget.setEnabled(False)

            self.w_publish_file.pushButton_upload_img.clicked.connect(self.on_pick_upload)
            # setup widget functions
            self.do_bind()
            self.do_dept_bind()

            self.show_app_info()
            self.init_add_image()
            self.katanaApp='katana'

            sys.path.append(app_path+'/katana_v2/Scripts')
            self.katanaApp=None
            try:
                import common.katana_config as ckc
                self.katanaApp = ckc.katanaApp
            except:
                traceback.print_exc()
            self.print_log('Use katana '+self.katanaApp)

        except sgtk.TankError, e:
            self._app.log_error(str(e))

        except Exception:
            self._app.log_error(traceback.format_exc())
        self.xml_folder=None

        return

    def pick_preview(self):

        modifiers = QtGui.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            self.pick_preview_folder()
        else:
            # overwrite method of base class, to prompt path picker pointing to nuke task folder, and add checkbox for sequence expanding
            pick_dialog = QtGui.QFileDialog(self)
            pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
            pick_dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)

            #########################################
            task_folder = self.work_root.replace('\\', '/').replace('/maya', '/katana') + '/render'
            if os.path.isdir( task_folder ):
                pick_dialog.setDirectory( task_folder )
            else:
                pick_dialog.setDirectory( self.work_root.replace('\\', '/').replace('/maya', '/katana') )

            pick_dialog.setNameFilters(["Images or Video (*.jpg *.jpeg *.tif *.tiff *.mov *.exr)"])
            pick_dialog.exec_()
            l_files = pick_dialog.selectedFiles()

            for file_path in l_files:
                self.w_file.listWidget_preview.addItem(file_path.replace('\\', '/'))

            if self.page_permit < 2:
                self.page_permit = 2
                if self.w_ver.lineEdit_version_name.text() != '.v':
                    self.page_permit = 3
        return


    def do_dept_bind(self):
        # self.w_publish_file.pushButton_pick_ma.clicked.connect(self.on_pick_info)
        self.w_publish_file.pushButton_pick_katana.clicked.connect(self.on_pick_katana)
        # self.w_publish_file.pushButton_pick_xml.clicked.connect(self.on_pick_xml)
        self.w_publish_file.checkBox.stateChanged.connect(self.enable_xml_publish)
        return

    def enable_xml_publish(self):
        if int(self.w_publish_file.checkBox.isChecked()):
            # self.w_publish_file.pushButton_pick_xml.setEnabled(True)
            # self.w_publish_file.lineEdit_xml.setEnabled(True)

            self.w_publish_file.pushButton_pick_katana.setEnabled(False)
            self.w_publish_file.lineEdit_katana.setEnabled(False)
            self.w_publish_file.checkBox_xgenarc.setEnabled(False)
      
            self.w_file.listWidget_preview.addItem(tool_srf_path+'/default_xml_preview.jpg')
            if self.page_permit < 2:
                self.page_permit = 2
                if self.w_ver.lineEdit_version_name.text() != '.v':
                    self.page_permit = 3
    
        else:
            # self.w_publish_file.pushButton_pick_xml.setEnabled(False)
            # self.w_publish_file.lineEdit_xml.setEnabled(False)
            self.w_file.listWidget_preview.clear()
            self.page_permit = 1

            self.w_publish_file.pushButton_pick_katana.setEnabled(True)
            self.w_publish_file.lineEdit_katana.setEnabled(True)
            self.w_publish_file.checkBox_xgenarc.setEnabled(True)

    def xgenarc_enable(self):
        asset_type=self.work_root.replace('\\', '/').split('/')[6]
        if asset_type=='flg':
            self.w_publish_file.checkBox_xgenarc.setChecked(True)


    # def run_auto_make_katana(self):
    #     xml_file=glob.glob(self.xml_folder+'/*.xml')
    #     if xml_file:
    #         cmd = self.katanaApp+' '+ '--script='+tool_srf_path+'/do_make_katana.py'
    #         cmd += ' '+self.xml_folder
    #         cmd += ' '+tool_srf_path+'/auto_bake_template.katana'

    #         asset_name=os.path.basename(xml_file[0]).split('.')[0]
    #         katana_file=os.path.dirname(self.xml_folder)+'/'+asset_name+'.srf.v000.katana'

    #         os.system(cmd)

    #         return katana_file

    # def on_pick_xml(self):
    #     pick_dialog = QtGui.QFileDialog(self)
    #     pick_dialog.setDirectory(self.work_root.replace('/maya', '/katana'))
    #     self.xml_folder = str(pick_dialog.getExistingDirectory(self,options=QtGui.QFileDialog.ShowDirsOnly))
    #     self.w_publish_file.lineEdit_xml.setText(self.xml_folder)

    #     if self.xml_folder and self.xml_folder!='None':
    #         katana_file=self.run_auto_make_katana()
    #         self.w_publish_file.lineEdit_katana.setText(katana_file)
    #         if katana_file:
    #             self.w_file.listWidget_preview.clear()
    #             self.w_file.listWidget_preview.addItem(tool_srf_path+'/default_xml_preview.jpg')
    #     else:
    #         self.xml_folder=None

    #     if self.page_permit < 2:
    #         self.page_permit = 2
    #         if self.w_ver.lineEdit_version_name.text() != '.v':
    #             self.page_permit = 3


    def on_pick_katana(self):

        pick_dialog = QtGui.QFileDialog(self)
        pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
        pick_dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
        pick_dialog.setDirectory(self.work_root.replace('/maya', '/katana'))
        pick_dialog.setNameFilters(["Katana File (*.katana)"])
        pick_dialog.exec_()
        l_files = pick_dialog.selectedFiles()

        for file_path in l_files:
            self.w_publish_file.lineEdit_katana.setText(file_path.replace('\\', '/'))

        return

    # def on_pick_info(self):

    #     pick_dialog = QtGui.QFileDialog(self)
    #     pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
    #     pick_dialog.setFileMode(QtGui.QFileDialog.ExistingFile)
    #     pick_dialog.setDirectory(self.work_root)
    #     pick_dialog.setNameFilters(["ToMod (*.info)"])
    #     pick_dialog.exec_()
    #     l_files = pick_dialog.selectedFiles()

    #     for file_path in l_files:
    #         self.w_publish_file.lineEdit_ma_file.setText(file_path.replace('\\', '/'))
    #     return



    def init_add_image(self):
        proj = self.project['name'].lower()
        asset = self.entity['name']
        asset_info = self.sg.find_one('Asset', [['id', 'is', self.entity['id']]], ['sg_asset_type'])
        typee = asset_info['sg_asset_type']
        jpg_folder = '/mnt/output/projects/%s/asset/%s/%s/srf/output/render'%(proj,typee,asset)
        print jpg_folder
        if not os.path.exists(jpg_folder):
            self.print_log('jpg_folder not exists : '+jpg_folder)
            return
        
        vers = sorted([ver for ver in os.listdir(jpg_folder) if 'srf.render' in ver])
        print vers
        if vers:
            latest_ver = vers[-1]
            img_list = glob.glob(jpg_folder + latest_ver + '/*/*/*_yzc.jpg')
            print img_list
            for i in img_list:
                self.w_publish_file.listWidget_upload_img.addItem(i)

    def on_pick_upload(self):
        spm_file_list = QtGui.QFileDialog.getOpenFileNames(self, "Select a image to upload", self.work_root, "image (*.jpg)")
        for spm_file in spm_file_list:
            if os.path.isfile(spm_file):
                self.w_publish_file.listWidget_upload_img.addItem(spm_file)
        return


    def pick_preview_folder(self):
        pick_dialog = QtGui.QFileDialog(self)
        pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
        pick_dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)

        #########################################
        task_folder = self.work_root.replace('\\', '/').replace('/mnt/work/', '/mnt/output/').replace('/task/maya',
                                                                                                      '/output')
        output_folder = task_folder

        c_time = 0
        mov_list = glob.glob(task_folder + '/*/*/*/*/*.mov')
        if mov_list:
            for mov in mov_list:
                if os.stat(mov).st_ctime > c_time or c_time == 0:
                    c_time = os.stat(mov).st_ctime
                    new_mov = mov

            output_folder = os.path.dirname(new_mov)

        pick_dialog.setDirectory(output_folder)
        pick_dialog.setNameFilters(["Images or Video (*.jpg *.jpeg *.tif *.tiff *.mov *.exr)"])
        pick_dialog.exec_()
        l_files = pick_dialog.selectedFiles()

        for file_path in l_files:
            self.w_file.listWidget_preview.addItem(file_path.replace('\\', '/'))

        if self.page_permit < 2:
            self.page_permit = 2
            if self.w_ver.lineEdit_version_name.text() != '.v':
                self.page_permit = 3
