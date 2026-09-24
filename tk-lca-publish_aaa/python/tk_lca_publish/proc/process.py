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


import sys
import time,os
from sgtk.platform.qt import QtCore, QtGui

def my_import(name):
    m = __import__(name)
    for n in name.split(".")[1:]:
        m = getattr(m, n)
    return m


class Process():

    def __init__(self, parent, vbox, module_type, module_name, module_mode, id, dialog):
        ''' module_dir: where the module should be imported
            parent: page_widget
            module_name: string, check module name
            id: int
            dialog: the dialog object which carries all vairables
        '''
        # Include the module path 
        #sys.path.insert(0, module_dir)

        self.parent = parent
        self.vbox = vbox

        self.module_type = module_type
        self.module_mode = module_mode
        self.module_name = module_name
        proc_module = my_import(module_type+'.'+module_name)
        reload(proc_module)
        self.process = proc_module.StdProcess(dialog)

        self.process_name = self.process.get_process_name()
        self.description = self.process.get_description()
        self.id = id
        self.dialog = dialog

        self.str_pass = u"√"
        self.str_fail = u"×"

        self.create_buttons()
        self.do_bind()

        return


    def create_buttons(self ):
        w = QtGui.QWidget()
        w.setFixedSize(QtCore.QSize(560, 30))

        self.label = QtGui.QLabel(w)
        self.label.setGeometry(QtCore.QRect(20, 2, 25, 25))

        self.proc_button = QtGui.QPushButton(w)
        self.proc_button.setText( self.process_name)
        self.proc_button.setGeometry(QtCore.QRect(50, 2, 500, 25))

        l=QtGui.QHBoxLayout()
        l.addWidget(w)
        l.addStretch(1)
        self.vbox.addLayout(l) 

        return


    def do_bind(self):
        self.proc_button.clicked.connect(self.show_description)
        return

    def record_time(self,timecost):
        import datetime
        import getpass
        logtime = datetime.datetime.now().strftime('%Y%m%d-%H:%M')
        login = getpass.getuser()
        key='{},{},{},{},{}'.format(self.module_type, self.module_name,timecost,login,logtime)
        #logtime = str(datetime.datetime.now())
        date = datetime.datetime.today().strftime('%Y%m%d')
        filename='.publishAll_log_{login}_{date}.txt'.format(login=login,date=date)
        if os.path.isdir( self.dialog.work_root):
            try:
                logfile = os.path.join(self.dialog.work_root,filename  )
                with open(logfile,'a' ) as f:
                    f.write( key+'\n' )
            except:
                pass
    def run_process(self):
        t = time.time()
        result = self.process.proceed()
        self.record_time(time.time() - t)
        print 'Process Time Cost:', self.module_type+'.'+self.module_name, ("%.2f sec" % (time.time() - t))

        if result == '':
            self.label.setText(self.str_pass)
            self.label.repaint()
            self.dialog.print_log( self.module_name+ u' 完成\n')
            return True
        else:
            self.label.setText(self.str_fail)
            self.label.repaint()
            if isinstance(result, str):
                result = result.decode('utf-8')
            self.dialog.print_log( self.module_name+ u' 失败:\n' + result, txt_color = QtGui.QColor(255, 50, 50))
            self.dialog.print_log( u"解决问题请找 TD\n", txt_color = QtGui.QColor(255, 160, 50))
            return False

        return


    def show_description(self):
        QtGui.QMessageBox.about(self.parent, u"描述", self.module_type+'.'+self.module_name+":<br>"+self.description)
        return


    def clear_result(self):
        self.label.setText("")
        self.valid = False
        return


    def get_output(self):
        return self.check.get_output()


    def enable(self):
        self.proc_button.setEnabled(True)
        self.proc_button.setStyleSheet('QPushButton {color: rgb(200, 200, 200)}')
        return


    def disable(self):
        self.proc_button.setEnabled(False)
        self.proc_button.setStyleSheet('QPushButton {color: rgb(140, 140, 140)}')
        return
