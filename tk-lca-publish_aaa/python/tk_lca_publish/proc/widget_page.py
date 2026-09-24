# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
############################################


from sgtk.platform.qt import QtGui


def create_page(stackedWidget, widget_module ):
    widget = QtGui.QWidget()
    page = widget_module()
    page.setupUi(widget)
    stackedWidget.addWidget(widget)
    return page, widget
