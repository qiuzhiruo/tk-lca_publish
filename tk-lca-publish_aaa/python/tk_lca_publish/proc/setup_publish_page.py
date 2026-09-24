# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
############################################

import os
import sys
# if sys.platform.startswith('win'):
#     sys.path.append("U:/toolset/lib/production")
# elif sys.platform.startswith('linux'):
#     sys.path.append("/mnt/utility/toolset/lib/production")
from xml.etree import ElementTree

from sgtk.platform.qt import QtGui, QtCore

import process
reload(process)
from process import Process

def build(form, process_xml, dialog):

    l_publish_process = []

    f = open(process_xml, 'r')
    xml_text = f.read()
    f.close()
    root = ElementTree.fromstring(xml_text)

    '''l=QtGui.QVBoxLayout(form)
    l.setContentsMargins(0,0,0,0)
    l.setSpacing(0)

    s=QtGui.QScrollArea()
    l.addWidget(s)'''

    w=QtGui.QWidget(form)        
    vbox=QtGui.QVBoxLayout(w)

    l_processes = root.getiterator("process")

    for i in range(len(l_processes)):
        process = l_processes[i]
        module_type = process.attrib['type']
        module_name = process.attrib['name']
        module_mode = process.attrib['mode']
        proc = Process( form, vbox, 'publish_process.'+module_type, module_name, module_mode, i, dialog)
        l_publish_process.append(proc)

    dialog.w_publish.verticalLayout.setSpacing(1)
    dialog.w_publish.scrollArea_process.setWidget(w)

    l_fixed_recipient = []
    # Fill in mail recipients
    if os.path.isfile(dialog.recipient_txt):
        f = open(dialog.recipient_txt, 'r')
        lines = f.readlines()
        f.close()
        l_fixed_recipient = lines[0].replace('\n', '').split(' ')
        #dialog.w_publish.lineEdit_email.setText(lines[0].replace('\n', ''))
    else:
        dialog.print_log('Missing ' + dialog.recipient_txt)

    from production.notification_rules.recipients import TaskRecipients
    # from notification_rules.recipients import TaskRecipients
    r = TaskRecipients()
    l_recipients = r.get_recipients(dialog.task, ['self', 'assigned', 'td', 'downstream', 'pc'])
    l_recipients.extend(l_fixed_recipient)
    l_recipients = list(set(l_recipients))
    dialog.w_publish.lineEdit_email.setText(' ' + ' '.join(l_recipients))

    return l_publish_process

