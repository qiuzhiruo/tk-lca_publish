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
import time
import os
from sgtk.platform.qt import QtCore, QtGui

def my_import(name):
    m = __import__(name)
    for n in name.split(".")[1:]:
        m = getattr(m, n)
    return m


class Check():

    def __init__(self, parent, tab_name, module_type, module_name, allow_skip, id, dialog):
        ''' module_dir: where the module should be imported
            parent: page_widget
            module_name: string, check module name
            check_name: string, the text displayed on the button
            auto_fix: bool
            description: string
            id: int
            input_vars: a dictionary of variables, passed from the release tool. e.g. the path need to be checked
        '''
        # Include the module path so we can the check
        #sys.path.append(module_dir)

        # Reload the module every time to make the change work without reopenning Maya
        self.tab_name = tab_name
        self.module_type = module_type
        self.module_name = module_name
        chk_module = my_import(module_type + '.' + module_name)
        reload(chk_module)
        self.check = chk_module.StdCheck(dialog)

        self.parent = parent
        self.check_name = self.check.get_check_name()
        self.description = self.check.get_description()
        self.allow_skip = {'true':True, 'false':False}[allow_skip]
        self.auto_fix = self.check.get_auto_fix()
        self.duty = self.check.get_duty()
        self.id = id
        self.dialog = dialog
        self.result = ''

        # check result
        self.valid = False

        self.create_buttons()

        self.do_bind()

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
        #os.chmod( filename, 0o777)


    def create_buttons(self ):
        self.skip_checkbox = QtGui.QCheckBox(self.parent)
        self.skip_checkbox.setGeometry(QtCore.QRect(10, 20+30*self.id, 25, 25))
        self.skip_checkbox.setCheckState(QtCore.Qt.Checked)
        if not self.allow_skip:
            self.skip_checkbox.setEnabled(False)

        self.check_button = QtGui.QPushButton( self.parent)
        self.check_button.setText( self.check_name)
        self.check_button.setGeometry(QtCore.QRect(35, 20+30*self.id, 530, 25))

        if self.auto_fix:
            self.fix_button = QtGui.QPushButton( self.parent)
            self.fix_button.setText(u"自动修复")
            self.fix_button.setGeometry(QtCore.QRect(575, 20+30*self.id, 60, 25))
            self.fix_button.setEnabled(False)

        self.descript_button = QtGui.QPushButton( self.parent)
        self.descript_button.setText("?")
        self.descript_button.setGeometry(QtCore.QRect(645, 20+30*self.id, 25, 25))
        return


    def do_bind(self):
        self.check_button.clicked.connect(self.run_check)
        if self.auto_fix:
            self.fix_button.clicked.connect(self.run_fix)
        self.descript_button.clicked.connect(self.show_description)
        return


    def run_check(self):
        t = time.time()
        self.result = self.check.run_check()
        if isinstance(self.result, str):
            self.result = self.result.decode('utf-8')
        self.record_time(time.time() - t )
        print 'Check Time Cost:', self.module_type+'.'+self.module_name, ("%.2f sec" % (time.time() - t))
        if self.result == '':
            self.valid = True
            self.check_button.setStyleSheet('QPushButton {color: rgb(160, 180, 255)}')
            self.check_button.repaint()
            self.dialog.print_log( self.module_name+ u' 检查通过\n')

        else:
            self.valid = False
            self.check_button.setStyleSheet('QPushButton {color: rgb(255, 140, 140)}')
            self.dialog.print_log( self.module_type + u"." + self.module_name+ u' 检查不通过:\n' + self.result, txt_color = QtGui.QColor(255, 50, 50))
            self.dialog.print_log( u"解决问题请找: "+self.duty + u", 如果无法理解错误信息请找 TD\n", txt_color = QtGui.QColor(255, 160, 50))
            if self.auto_fix:
                self.dialog.print_log( u"请先试用 自动修复 功能。\n", txt_color = QtGui.QColor(255, 160, 50))
                self.fix_button.setEnabled(True)

        return


    def run_fix(self):

        result = self.check.run_fix()
        if result == '':
            self.dialog.print_log( u"自动修复 结束，请重新检查。\n", txt_color = QtGui.QColor(150, 150, 255))
        else:
            self.dialog.print_log( result, txt_color = QtGui.QColor(255, 50, 50))
            self.dialog.print_log( u"无法自动修复。\n", txt_color = QtGui.QColor(255, 160, 50))

        self.fix_button.setEnabled(False)
        return


    def show_description(self):
        QtGui.QMessageBox.about(self.parent, u"描述", self.module_type+ '.' + self.module_name + ":<br>"+self.description)
        return


    def clear_result(self):
        self.label.setText("")
        self.valid = False
        self.result = ''
        return


    def get_module_name(self):
        return self.module_name

    def get_valid(self):
        return self.valid

    def get_result(self):
        return self.result

    def get_output(self):
        return self.check.get_output()


    def get_skip_chk(self):
        return self.skip_checkbox.checkState()


    def enable(self):

        if self.allow_skip:
            self.skip_checkbox.setEnabled(True)

        self.check_button.setEnabled(True)
        self.check_button.setStyleSheet('QPushButton {color: rgb(200, 200, 200)}')

        if self.auto_fix:
            self.fix_button.setEnabled(False)

        self.descript_button.setEnabled(True)
        return


    def disable(self):
        self.skip_checkbox.setEnabled(False)

        self.check_button.setEnabled(False)
        self.check_button.setStyleSheet('QPushButton {color: rgb(140, 140, 140)}')

        if self.auto_fix:
            self.fix_button.setEnabled(False)

        self.descript_button.setEnabled(False)

        return

