# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: model publish tool. 
#
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

    from ....ui.widget_file_no_file import Ui_Form as widget_publish_file

except:
    print traceback.format_exc()

TXT_DEFAULT = QtGui.QColor(200, 200, 200)
TXT_ORANGE = QtGui.QColor(255, 150, 30)
TXT_RED = QtGui.QColor(255, 50, 50)
TXT_BLUE = QtGui.QColor(150, 150, 255)
TXT_WHITE = QtGui.QColor(255, 255, 255)

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

            self.show_app_info()

            try:
                # customize preview picking
                import pymel.core as pm
                scene_path = str( pm.sceneName() ).replace('\\', '/')

                previz_2d = os.path.dirname(scene_path) + '/data/' + os.path.basename(scene_path)[:-3] + '.mov'
                previz_3d = os.path.dirname(scene_path) + '/data/' + os.path.basename(scene_path)[:-3] + '.stereo.mov'
                if not os.path.isfile(previz_2d):
                    previz_2d = ''
                if not os.path.isfile(previz_3d):
                    previz_3d = ''

                previz = ''
                if previz_2d and previz_3d:
                    # compare time
                    '''
                    status_2d = os.stat( previz_2d )
                    status_3d = os.stat( previz_3d )
                    if status_3d.st_mtime >= status_2d.st_mtime:
                        previz = previz_3d
                    else:
                        previz = previz_2d
                    '''
                    previz = previz_2d
                elif previz_2d:
                    previz = previz_2d
                elif previz_3d:
                    previz = previz_3d

                if previz:
                    self.w_file.listWidget_preview.addItem( previz )

                # fill the right version
                version_name = os.path.basename( scene_path ).split('.')[-2]
                if version_name[0] == 'v' and version_name[1:].isdigit():
                    self.w_ver.lineEdit_version_name.setText('.' + version_name)
            except:
                print traceback.format_exc()

        except sgtk.TankError, e:
            self._app.log_error(str(e))

        except Exception:
            print traceback.format_exc()
            self._app.log_error(traceback.format_exc())
        
        return


