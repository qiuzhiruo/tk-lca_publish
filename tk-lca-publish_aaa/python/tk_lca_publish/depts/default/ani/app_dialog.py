# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: publish tool.
#
########################################################################################

import os
import sys
import pprint
import shutil
import traceback
import time
import getpass


import sgtk
from sgtk.platform.qt import QtCore, QtGui

# TODO
import publish_dialog
reload(publish_dialog)
from publish_dialog import PublishDialog

from ....ui.dialog_ani import Ui_Dialog
from ....ui.widget_sys import Ui_Form as widget_sys
from ....ui.widget_file import Ui_Form as widget_file
from ....ui.widget_version import Ui_Form as widget_version
from ....ui.widget_check import Ui_Form as widget_check
from ....ui.widget_publish import Ui_Form as widget_publish

from ....ui.widget_file_ani import Ui_Form as widget_publish_file



class AppDialog(PublishDialog):

    def __init__(self, app):

        try:
            PublishDialog.__init__(self, app)

            # Get environment info & production info from sgtk
            self.set_vars()
            self.set_dept_vars(__file__)

            # set up the UI, which includes the dialog and all process widgets
            self.setup_gui(Ui_Dialog, widget_sys, widget_version, widget_file, widget_check, widget_publish, widget_publish_file)

            # setup widget functions
            self.do_bind()
            #self.do_dept_bind()

            self.show_app_info()

        except sgtk.TankError, e:
            self._app.log_error(str(e))

        except Exception:
            print traceback.format_exc()
            self._app.log_error(traceback.format_exc())

        return

    def setup_tags(self):
        PublishDialog.setup_tags(self)

        # predict publish stage
        stages = list()
        for i in range(self.w_sys.comboBox_tag.count()):
            stages.append(self.w_sys.comboBox_tag.itemText(i))

        target = None
        for stage in reversed(stages):
            if not stage:
                continue

            approved = self.sg.find('Version',
                                    [['entity', 'is', self.entity],
                                     ['sg_remark', 'is', 'ok'],
                                     ['tag_list', 'is', stage]],
                                    [])
            if approved:
                target = stages.index(stage) + 1
                target = min([target, len(stages)-2])
                break

        if target is None:
            approved = self.sg.find('Task',
                                    [['entity', 'is', self.entity],
                                     ['step', 'name_is', 'ani'],
                                     ['content', 'is', 'reference'],
                                     ['sg_status_list', 'is', 'aa']])
            if approved:
                target = 0

        if target is not None:
            self.w_sys.comboBox_tag.setCurrentIndex(target)




