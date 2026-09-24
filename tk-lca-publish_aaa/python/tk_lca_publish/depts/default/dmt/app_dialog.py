# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
# Description: Art publish tool. Create version on server and shtogun
#              This is the first publish tool in the LCA. All publish tools of
#              different departments will share:
#              Gui widgets; system check module; version check module
########################################################################################

import os
import sys
import pprint
import shutil
import traceback
import time
import getpass

try:
    import sgtk
    from sgtk.platform.qt import QtCore, QtGui

    import publish_dialog
    reload(publish_dialog)
    from publish_dialog import PublishDialog

    from ....ui.dialog import Ui_Dialog
    from ....ui.widget_sys import Ui_Form as widget_sys
    from ....ui.widget_file_dmt import Ui_Form as widget_file
    from ....ui.widget_version import Ui_Form as widget_version
    from ....ui.widget_check import Ui_Form as widget_check
    from ....ui.widget_publish import Ui_Form as widget_publish

    from ....ui.widget_file_no_file import Ui_Form as widget_publish_file

except:
    print traceback.format_exc()


class AppDialog(PublishDialog):

    def __init__(self, app):

        try:
            PublishDialog.__init__(self, app)

            # Get environment info & production info from sgtk
            self.set_vars()
            self.set_dept_vars( __file__ )
            self.select_sequences = True

            # set up the UI, which includes the dialog and all process widgets
            self.setup_gui(Ui_Dialog, widget_sys, widget_version, widget_file, widget_check, widget_publish, widget_publish_file)

            # TODO Can't use the thumbnail widget outside Maya
            self.w_file.thumbnail_widget.setEnabled(False)

            # setup widget functions
            self.do_bind()
            self.w_file.checkBox_expand_preview.stateChanged.connect(self.stateOfSelSeq)

            self.show_app_info()

            try:
                # customize preview picking
                import nuke
                root = nuke.root()['name'].getValue()
                scene_path = str( root ).replace('\\', '/')

                imgs = sorted( [ i for i in os.listdir( os.path.dirname(scene_path) + '/output/' ) if i.startswith( '.'.join(os.path.basename(scene_path).split('.')[:-1]) ) ] )

                if imgs:
                    self.w_file.listWidget_preview.addItem( os.path.dirname(scene_path) + '/output/' + imgs[0] )

                # fill the right version
                version_name = os.path.basename( scene_path ).split('.')[-2]
                if version_name[0] == 'v' and version_name[1:].isdigit():
                    self.w_ver.lineEdit_version_name.setText('.' + version_name)
            except:
                print traceback.format_exc()

        except sgtk.TankError, e:
            self._app.log_error(str(e))

        except Exception:
            self._app.log_error(traceback.format_exc())
        
        return

    def stateOfSelSeq(self):
        if self.w_file.checkBox_expand_preview.isChecked():
            self.select_sequences = True
            print 'checked!\n'
        else:
            self.select_sequences = False
            print 'unchecked!\n'


    def pick_preview(self):
        # overwrite method of base class, to prompt path picker pointing to nuke task folder, and add checkbox for sequence expanding
        pick_dialog = QtGui.QFileDialog(self)
        pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
        pick_dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)

        #########################################
        task_folder = 'W:/' if os.name == 'nt' else '/mnt/work/'
        task_folder = task_folder + 'projects/'+self.project['name'].lower()+'/shot/' + self.entity['name'][:3] + '/' + self.entity['name'] + '/'+self.step['name']+'/task/nuke'
        if os.path.isdir( task_folder ):
            pick_dialog.setDirectory( task_folder )
            ######################################################
        else:
            pick_dialog.setDirectory(self.work_root)
        # fix qfiledialog.setFilters bug(no surpport by pyside2) by tanghaojia 2022-05-19
        try:
            pick_dialog.setFilters(("Images or Video (*.jpg *.jpeg *.tif *.tiff *.mov *.exr)", "All Files(*.*)"))
        except Exception as e:
            # print e
            filters = ["Images or Video (*.jpg *.jpeg *.tif *.tiff *.mov *.exr)", "All Files(*.*)"]
            pick_dialog.setNameFilters(filters)
        pick_dialog.exec_()
        l_files = pick_dialog.selectedFiles()

        for file_path in l_files:
            # The preview file list contains either 1 mov file or some jpeg files.
            if file_path.lower().endswith('.mov'):
                # Clean the list if it's a mov file
                self.w_file.listWidget_preview.clear()
            else:
                i = self.w_file.listWidget_preview.count()
                if i == 1 and self.w_file.listWidget_preview.item(0).text().lower().endswith('.mov'):
                    self.w_file.listWidget_preview.clear()

            self.w_file.listWidget_preview.addItem(file_path.replace('\\', '/'))

        if self.page_permit < 2:
            self.page_permit = 2
            if self.w_ver.lineEdit_version_name.text() != '.v':
                self.page_permit = 3
        return

