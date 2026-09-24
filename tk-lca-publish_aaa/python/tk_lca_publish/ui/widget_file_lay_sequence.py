# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/mnt/public/home/wanghuan/Develop/tk-lca-publish/resources/widget_file_lay_sequence.ui'
#
# Created: Thu May 28 16:38:07 2015
#      by: PyQt4 UI code generator 4.6.2
#
# WARNING! All changes made in this file will be lost!

from sgtk.platform.qt import QtCore, QtGui

class CheckBoxHeader(QtGui.QHeaderView):
    QtCore.pyqtSignal = QtCore.Signal
    QtCore.pyqtSlot = QtCore.Slot
    clicked=QtCore.pyqtSignal(bool)

    def __init__(self, orientation = QtCore.Qt.Horizontal, parent = None):
        """
        """
        super(CheckBoxHeader, self).__init__(orientation, parent)
        logical_index = self.logicalIndex (0)
        try:
            self.setResizeMode(QtGui.QHeaderView.Interactive)
        except:
            self.setSectionResizeMode(QtGui.QHeaderView.Interactive)
        self.setStretchLastSection(True)
        self.isChecked=False
        self.parent = parent

    def paintSection(self, painter, rect, logicalIndex):
        """
        """
        painter.save()
        super(CheckBoxHeader, self).paintSection(painter, rect, logicalIndex)
        painter.restore()
        if logicalIndex == 0:
            option = QtGui.QStyleOptionButton()
            option.rect = QtCore.QRect(3, 1, 20, 20)  #may have to be adapt
            option.state = QtGui.QStyle.State_Enabled | QtGui.QStyle.State_Active
            if self.isChecked:
                option.state |= QtGui.QStyle.State_On
            else:
                option.state |= QtGui.QStyle.State_Off
            self.style().drawControl(QtGui.QStyle.CE_CheckBox, option, painter)

    def mousePressEvent(self, event):
        crnt_logical_index = self.logicalIndexAt(event.pos().x(), event.pos().y())
        #print 'mouse press event (', event.pos().x(), event.pos().y(), ') ',crnt_logical_index, self.isMovable()
        
        sec_width = self.sectionSize(crnt_logical_index)
        if crnt_logical_index  == 0:
            limited_x = sec_width - event.pos().x()
            if limited_x > 10:       #if the mouse is rather close to the border between 0 and 1, do not change check status
                if self.isChecked:
                    self.isChecked = QtCore.Qt.Unchecked
                else:
                    self.isChecked = QtCore.Qt.Checked
                self.clicked.emit(self.isChecked)
                
                # select or unselect all items in the table
                rows = self.parent.rowCount()
                for row in range(rows):
                    item = self.parent.item(row, 0)
                    item.setCheckState(self.isChecked)
        
        self.viewport().update()
        super(CheckBoxHeader, self).mousePressEvent(event)



class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(680, 320)
        self.tableWidget_shots = QtGui.QTableWidget(Form)
        self.tableWidget_shots.setGeometry(QtCore.QRect(10, 19, 660, 291))
        self.tableWidget_shots.setObjectName("tableWidget_shots")
        self.tableWidget_shots.setColumnCount(6)
        self.tableWidget_shots.setRowCount(0)
        
        self.horizon_header = CheckBoxHeader(parent = self.tableWidget_shots)
        self.tableWidget_shots.setHorizontalHeader(self.horizon_header)
        self.tableWidget_shots.verticalHeader().setVisible(False)

        self.retranslateUi(Form)
        
        self.tableWidget_shots.itemClicked.connect(self.on_itemClicked_event)
        
        self.tableWidget_shots.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tableWidget_shots.customContextMenuRequested.connect(self.test)


    def retranslateUi(self, Form):
        Form.setWindowTitle(QtGui.QApplication.translate("Form", "Form", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget_shots.setHorizontalHeaderLabels(['Shot', 'Cut In', 'Cut Out', u'阴影镜头(选择镜头外资产添加)', 'Preview', 'Top View'])
    
    def on_itemClicked_event(self, item):
        """
        """
        self.set_header_check_state()
            
    def set_header_check_state(self):
        check_header = True
        row_count = self.tableWidget_shots.rowCount()
        for row_index in range(row_count):
            item = self.tableWidget_shots.item(row_index, 0)
            if item.checkState() == QtCore.Qt.Unchecked:
                check_header = False
                self.horizon_header.isChecked = QtCore.Qt.Unchecked
                self.horizon_header.clicked.emit(self.horizon_header.isChecked)
                self.horizon_header.viewport().update()
                break
        
        if check_header:
            self.horizon_header.isChecked = QtCore.Qt.Checked
            self.horizon_header.clicked.emit(self.horizon_header.isChecked)
            self.horizon_header.viewport().update()

    def test(self, pos):
        menu = QtGui.QMenu()  # 实例化菜单
        item1 = menu.addAction(u"★ 添加所选资产到 阴影镜头(选择镜头外资产添加) ★")

        new_pos = QtCore.QPoint(pos.x() + 10, pos.y() + 20)
        action = menu.exec_(self.tableWidget_shots.mapToGlobal(new_pos))

        if action == item1:
            import maya.cmds as cmds
            import pymel.core as pm

            print u'测试 成功！！！'
            message = ''
            num = 0
            selection = pm.general.selected(referencedNodes=True)
            # print selection
            nodes = pm.general.ls(selection, referencedNodes=True)
            # print nodes
            for node in nodes:
                ref = node.namespace()
                ref_master = ref+'master'
                print ref,ref_master,cmds.objExists(ref_master)
                if cmds.objExists(ref_master):
                    message = message+ref_master+','
                    num = num+1
            # print message[:-1]
            # print num
            if num != 0:
                clickedItem_row = self.tableWidget_shots.currentRow()

                shot_item = self.tableWidget_shots.item(clickedItem_row, 0)
                shot_name = shot_item.text()

                chck = QtGui.QTableWidgetItem(message[:-1])
                # chck.setFlags(QtCore.Qt.ItemIsUserCheckable|QtCore.Qt.ItemIsEnabled)
                self.tableWidget_shots.setItem(clickedItem_row, 3, chck)
                self.set_lca_other_assets_value(shot_name,message[:-1])
                pm.confirmDialog(title="OK", message=(u"已经添加下面选中的资产到 %s 镜头\n这些资产会传递到 ani 000 版本内\n\n%s" % (shot_name,message[:-1])), bgc=[0.4, 0.8, 0.4])
            else:
                pm.confirmDialog(title="Error", message=u"未选中物体或选中的不属于Reference, 请确认后再试！", bgc=[0.8, 0.8, 0.4])
    
    def set_lca_other_assets_value(self,shot_name,message):
        import maya.cmds as cmds
        import pymel.core as pm
        
        cam_ctrl_name = shot_name+'_cam_rig:global_ctrl'
        lca_other_assets_attr = 'LCA_Other_Assets'
        if cmds.objExists(cam_ctrl_name):
            allAttrs = cmds.listAttr(cam_ctrl_name)
            if lca_other_assets_attr not in allAttrs:
                cmds.addAttr(cam_ctrl_name, ln=lca_other_assets_attr, dt='string')
            cmds.setAttr(cam_ctrl_name+'.'+lca_other_assets_attr,message,type='string')