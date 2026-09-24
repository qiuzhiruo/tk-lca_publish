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

from sgtk.platform.qt import QtCore, QtGui

def build(dialog):

    dialog.w_ver.tableWidget_old_versions.setColumnWidth(0, 260)
    dialog.w_ver.tableWidget_old_versions.setColumnWidth(1, 70)
    dialog.w_ver.tableWidget_old_versions.setColumnWidth(2, 100)
    dialog.w_ver.tableWidget_old_versions.setColumnWidth(3, 200)

    dialog.w_ver.label_version_name_b.setText(dialog.version_key)
    l_versions = dialog.sg.find('Version', [['project', 'is', dialog.project], ['sg_task', 'is', dialog.task]], ['code', 'user', 'created_at', 'description'])
    l_versions.reverse()
    dialog.l_old_versions = []
    dialog.w_ver.tableWidget_old_versions.setRowCount(len(l_versions))
    v_max = 0
    for i in range(len(l_versions)):
        version = l_versions[i]
        newItem = QtGui.QTableWidgetItem(version['code'])

        dialog.w_ver.tableWidget_old_versions.setItem(i, 0, newItem)

        if not version['user']:
            newItem = QtGui.QTableWidgetItem('')
        else:
            newItem = QtGui.QTableWidgetItem(version['user']['name'])
        dialog.w_ver.tableWidget_old_versions.setItem(i, 1, newItem)

        newItem = QtGui.QTableWidgetItem(version['created_at'].ctime())
        dialog.w_ver.tableWidget_old_versions.setItem(i, 2, newItem)

        if not version['description']:
            newItem = QtGui.QTableWidgetItem('')
        else:
            newItem = QtGui.QTableWidgetItem(version['description'].decode("utf-8"))
        dialog.w_ver.tableWidget_old_versions.setItem(i, 3, newItem)

        dialog.l_old_versions.append(version['code'])

        if version['code'][-3:].isdigit() and int(version['code'][-3:]) > v_max:
            v_max = int(version['code'][-3:])

    if v_max < 999 and str(dialog.w_ver.lineEdit_version_name.text()) == '.v':
        dialog.w_ver.lineEdit_version_name.setText('.v%03d' % (v_max+1))
    return
