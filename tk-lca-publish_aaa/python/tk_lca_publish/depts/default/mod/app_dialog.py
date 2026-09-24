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
import pymel.core as pm

try:
    import sgtk
    from sgtk.platform.qt import QtCore, QtGui

    # TODO
    import publish_dialog

    reload(publish_dialog)
    from publish_dialog import PublishDialog

    from ....ui.dialog import Ui_Dialog
    from ....ui.widget_sys import Ui_Form as widget_sys
    from ....ui.widget_file import Ui_Form as widget_file
    from ....ui.widget_version import Ui_Form as widget_version
    from ....ui.widget_check import Ui_Form as widget_check
    from ....ui.widget_publish import Ui_Form as widget_publish

    from ....ui.widget_file_mod import Ui_Form as widget_publish_file

except:
    print traceback.format_exc()


class AppDialog(PublishDialog):
    def __init__(self, app):
        try:
            PublishDialog.__init__(self, app)

            # Get environment info & production info from sgtk
            self.set_vars()
            self.set_dept_vars(__file__)

            # set up the UI, which includes the dialog and all process widgets            
            self.setup_gui(Ui_Dialog, widget_sys, widget_version, widget_file, widget_check, widget_publish,
                           widget_publish_file)

            # setup widget functions
            self.do_bind()

            self.w_sys.comboBox_tag.currentIndexChanged.connect(self.set_publish_mode_tag)

            self.w_publish_file.pushButton_speed_tree.clicked.connect(self.on_pick_spm)
            self.w_publish_file.pushButton_zb.clicked.connect(self.on_pick_zbrush)
            self.w_publish_file.pushButton_zb_view.clicked.connect(self.on_pick_zbrush_view)
            self.w_publish_file.pushButton_dy.clicked.connect(self.on_pick_dynamic)
            self.w_publish_file.pushButton_dy_export.clicked.connect(self.on_pick_dynamic_export)

            self.w_publish_file.listWidget_zb_view.itemPressed.connect(self.select_zbv)
            self.w_publish_file.listWidget_zb.itemPressed.connect(self.select_zb)
            self.w_publish_file.listWidget_speed_tree.itemPressed.connect(self.select_spt)
            self.w_publish_file.listWidget_dy.itemPressed.connect(self.select_dy)
            
            self.show_app_info()
            self.auto_dynamic()
            self.export_dynamic = False

        except sgtk.TankError, e:
            self._app.log_error(str(e))

        except Exception:
            print traceback.format_exc()
            self._app.log_error(traceback.format_exc())
        
        return


    def select_zbv(self):
        l_items = self.w_publish_file.listWidget_zb_view.selectedItems()
        if self.w_publish_file.listWidget_zb_view._mouse_button != QtCore.Qt.LeftButton:
            for item in l_items:
                i = self.w_publish_file.listWidget_zb_view.indexFromItem(item).row()
                self.w_publish_file.listWidget_zb_view.takeItem(i)
    
        return

    def select_zb(self):
        l_items = self.w_publish_file.listWidget_zb.selectedItems()
        if self.w_publish_file.listWidget_zb._mouse_button != QtCore.Qt.LeftButton:
            for item in l_items:
                i = self.w_publish_file.listWidget_zb.indexFromItem(item).row()
                self.w_publish_file.listWidget_zb.takeItem(i)
    
        return

    def select_spt(self):
        l_items = self.w_publish_file.listWidget_speed_tree.selectedItems()
        if self.w_publish_file.listWidget_speed_tree._mouse_button != QtCore.Qt.LeftButton:
            for item in l_items:
                i = self.w_publish_file.listWidget_speed_tree.indexFromItem(item).row()
                self.w_publish_file.listWidget_speed_tree.takeItem(i)
    
        return

    def select_dy(self):
        l_items = self.w_publish_file.listWidget_dy.selectedItems()
        if self.w_publish_file.listWidget_dy._mouse_button != QtCore.Qt.LeftButton:
            for item in l_items:
                i = self.w_publish_file.listWidget_dy.indexFromItem(item).row()
                self.w_publish_file.listWidget_dy.takeItem(i)
    
        return
    
    def set_publish_mode_tag(self):
        if self.ui.comboBox_publish_mode.currentIndex() in [0,1]:
            self.set_publish_mode()


    def get_omit_check(self,check):
        if self.step['name'] in ['mod'] and self.w_sys.comboBox_tag.currentIndex() == 0:
            mod_type=self.sg.find_one('Asset', [['id', 'is', self.entity['id']]], ['sg_asset_type'])['sg_asset_type']

            omit_mod_list = ['chr_camera_check', 'light_check', 'check_hair_patch', 'dynamic_file_name', 'lod_match',
                             'one_shader_per', 'extremely_short_edge', 'uv_holes', 'light_check',
                             'exceed_range_uv', 'asm_mesh',"light_check"]
            
            
            
            if check.module_name in omit_mod_list and mod_type in ['asm','chr','crd']:
                return True

        if self.step['name'] in ['mod','asm'] and self.w_sys.comboBox_tag.currentIndex() == 2:

            mod_type = self.sg.find_one('Asset', [['id', 'is', self.entity['id']]], ['sg_asset_type'])['sg_asset_type']
            omit_mod_list = ["mesh_name","pivot_on_orgion","no_empty_trans",'exceed_range_uv',"unknown_nodes",
                              "light_check","symmetrical_check","chr_camera_check","normal_is_checked","character_shaders"]

            if check.module_name in omit_mod_list and mod_type in ['asm', 'chr', 'crd']:
                return True

            
        return False


    def on_pick_spm(self):
        spm_dir = QtGui.QFileDialog.getExistingDirectory(self, "File a speed tree dir", self.work_root)
        self.w_publish_file.listWidget_speed_tree.addItem(spm_dir.replace('\\', '/'))

        return

    def on_pick_zbrush(self):
        zb_file_list = QtGui.QFileDialog.getOpenFileNames(self, "File a zbrush file", self.work_root, "ZBrush File (*.zpr *.ztl)")[0]
        for zb_file in zb_file_list:
            if os.path.isfile(zb_file):
                self.w_publish_file.listWidget_zb.addItem(zb_file.replace('\\', '/'))

        return

    def on_pick_zbrush_view(self):
        zb_view_file_list = QtGui.QFileDialog.getOpenFileNames(self, "File a zbrush view file", self.work_root, "JPG File (*.jpg)")[0]
        for zb_view_file in zb_view_file_list:
            if os.path.isfile(zb_view_file):
                self.w_publish_file.listWidget_zb_view.addItem(zb_view_file.replace('\\', '/'))

        return


    def on_pick_dynamic(self):
        dy_file_list = QtGui.QFileDialog.getOpenFileNames(self, "File a dynamic abc file", self.work_root, "Alembic (*.abc)")[0]

        for dy_file in dy_file_list:
            if os.path.isfile(dy_file):
                if not  '.dynamic.' in dy_file:
                    error_text=u'文件名必须有 ".dynamic."+层级 : '+dy_file
                    print error_text
                    self._app.log_error(error_text)
                    return error_text
                self.w_publish_file.listWidget_dy.addItem(dy_file.replace('\\', '/'))
                self.export_dynamic = False
                
                
        return

    def on_pick_dynamic_export(self):
        try:
            import pymel.core as pm
            l_bad_faces = []
            l_bad_vertex = []
            l_short_edges = []
            l_bad_meshes = []

            l_meshes = pm.listRelatives('|master|poly', ad=True, type='mesh')
            for n in l_meshes:
                result = pm.polyInfo(n, nmv=True, nme=True )
                if result:
                    l_bad_vertex.extend(result)
                    l_bad_faces.append(n)



                pm.select(n, r=True)
                pm.polySelectConstraint( m=3, t=0x8000, l=True, lb=(0, 0.000010))
                sel = pm.ls(sl=True)
                if len(sel) > 0:
                    l_short_edges.extend(sel)
                    l_bad_meshes.append(n)

            if len(l_bad_faces)>0:
                l_names = [n.name() for n in l_bad_faces]
                pm.select(l_bad_vertex, r=True)
                error_text=u"发现 non-manifold 面:" + u" ".join(l_names)
                print error_text
                self._app.log_error(error_text)
                return error_text

            if len(l_short_edges) >0:
                pm.select(l_short_edges, r=True)
                error_text= u"长度小于 0.000010 的边: \n" + u'\n'.join([str(e) for e in l_short_edges])
                print error_text
                self._app.log_error(error_text)
                return error_text

            for le in ['hi','md','lo','proxy']:
                if len(pm.ls('|master|poly|'+le))!=0 and len(pm.ls('|master|poly|'+le+'|mesh_grp'))==0:
                    error_text= u"|master|poly|%s 下 mesh_grp 组不存在，请打组" % le
                    print error_text
                    self._app.log_error(error_text)
                    return error_text

            scene_name = pm.sceneName()
            scene_path = os.path.dirname(scene_name)
            start_frame = self.w_publish_file.start_f.text()
            end_frame = self.w_publish_file.end_f.text()

            alembic_path = os.path.join(scene_path, 'cache', 'alembic')
            if not os.path.isdir(alembic_path):
                os.makedirs(alembic_path)

            l_versions = sorted(os.listdir(alembic_path))
            l_mtl_v = [v for v in l_versions if v.startswith('v') and v[-3:].isdigit()]
            if len(l_mtl_v) == 0:
                dynamic_path = os.path.join(alembic_path, 'v001')
            else:
                dynamic_path =  os.path.join(alembic_path,('v%03d' % (int(l_mtl_v[-1][-3:]) + 1)))

            if not os.path.isdir(dynamic_path):
                os.makedirs(dynamic_path)


            level_list=[]

            for le in ['hi','md','lo']:
                if len(pm.ls('|master|poly|'+le))!=0:
                    level_list.append(le)


            for level in level_list:

                new_name = '{0}.dynamic.{3}.{1}_{2}.abc'.format(self.entity['name'], '%03d' % int(start_frame),
                                                            '%03d' % int(end_frame),level)

                dynamic_file = os.path.join(dynamic_path, new_name)

                level_list=pm.ls('|master|poly|{0}|*'.format(level))
                level_str=''.join(['-root '+l+' ' for l in level_list])
                pm.AbcExport(j="  -frameRange {0} {1} -uvWrite {3} -file {2}".format(start_frame,
                                                                                     end_frame,
                                                                                     dynamic_file,
                                                                                     level_str))

                self.w_publish_file.listWidget_dy.addItem(dynamic_file.replace('\\', '/'))

            self.export_dynamic = True
            print 'abc export ok '

        except Exception:
            print traceback.format_exc()
            self._app.log_error(traceback.format_exc())


    def auto_dynamic(self):
        #asset_info = self.sg.find_one('Asset', [['id', 'is', self.entity['id']]], ['sg_asset_type'])
        #if asset_info['sg_asset_type'] == 'flg':
        self.w_publish_file.pushButton_dy.setEnabled(1)
        self.w_publish_file.pushButton_dy_export.setEnabled(1)
        self.w_publish_file.start_f.setEnabled(1)
        self.w_publish_file.end_f.setEnabled(1)
        self.w_publish_file.label_s.setEnabled(1)
        self.w_publish_file.label_e.setEnabled(1)
        return
