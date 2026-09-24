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

import os
import sys
from xml.etree import ElementTree

from sgtk.platform.qt import QtCore, QtGui

import check
reload(check)
from check import Check


def build(form, check_xml, dialog):

    l_sys_check = []

    tabWidget_sys_check = QtGui.QTabWidget(form)
    tabWidget_sys_check.setGeometry(QtCore.QRect(10, 50, 680, 380))

    f = open(check_xml, 'r')
    xml_text = f.read()
    f.close()
    root = ElementTree.fromstring(xml_text)

    l_grps = root.getiterator("check_group")

    for i in range(len(l_grps)):
        grp = l_grps[i]
        grp_tab = QtGui.QWidget()
        tabWidget_sys_check.addTab(grp_tab, grp.attrib['name'])
        #tabWidget_sys_check.setTabText(i, )
        
        l_checks = grp.getiterator("check")
        for j in range(len(l_checks)):
            check = l_checks[j]
            module_type = check.attrib['type']
            module_name = check.attrib['name']
            allow_skip  = check.attrib['allow_skip']
            chk = Check( grp_tab, grp.attrib['name'], 'sys_check.'+module_type, module_name, allow_skip, j, dialog)
            l_sys_check.append(chk)

    return l_sys_check


