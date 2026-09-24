# -*- coding:utf-8 -*-

########################################################################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.07
#
# Description: Art publish tool. Create version on server and shotgun
#              This is the first publish tool in the LCA. All publish tools of
#              different departments will share:
#              Gui widgets; system check module; version check module
#
########################################################################################

import os
import sys
import pprint
import shutil
import traceback
import time
import getpass
import glob
from datetime import datetime
import string
try:
    import sgtk
    from sgtk.platform.qt import QtCore, QtGui
    from proc import widget_page
    from proc import setup_sys_page
    from proc import setup_version_page
    from proc import setup_check_page
    from proc import setup_publish_page
    from proc import get_stage_list

    reload(widget_page)
    reload(setup_sys_page)
    reload(setup_version_page)
    reload(setup_check_page)
    reload(setup_publish_page)
    reload(get_stage_list)


except:
    print traceback.format_exc()

TXT_DEFAULT = QtGui.QColor(200, 200, 200)
TXT_ORANGE = QtGui.QColor(255, 150, 30)
TXT_RED = QtGui.QColor(255, 50, 50)
TXT_BLUE = QtGui.QColor(150, 150, 255)
TXT_WHITE = QtGui.QColor(255, 255, 255)
try:
    # import platform
    # if platform.system().lower() == 'windows':
    #     sys.path.insert(0,'U:/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/publish_check/ani/')
    #     sys.path.append('U:/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/publish_check/mod/')
    # elif platform.system().lower() == 'linux':
    #     sys.path.insert(0,'/mnt/utility/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/publish_check/ani/')
    #     sys.path.append('/mnt/utility/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/publish_check/mod/')

    # sys.path.insert(0, os.path.join(os.path.normpath(__file__+'/..'), 'publish_check/ani'))
    # sys.path.append(os.path.join(os.path.normpath(__file__+'/..'), 'publish_check/mod'))

    import tk_lca_publish.publish_check.ani.check_tpose_frame as check_tpose_frame
    import tk_lca_publish.publish_check.ani.check_pass as check_pass
    import tk_lca_publish.publish_check.ani.check_pass_ani_flo as check_pass_ani_flo
    reload(check_tpose_frame)
    reload(check_pass)
    reload(check_pass_ani_flo)

    import tk_lca_publish.publish_check.mod.check_head_turntable as check_head_turntable
    import tk_lca_publish.publish_check.mod.get_sg_related_assets as get_sg_related_assets
    reload(check_head_turntable)
    reload(get_sg_related_assets)
#except:
#    pass
except Exception as e:
    # 打印具体的错误信息，这对调试至关重要
    print("导入模块时发生错误：")
    print(e)
    import traceback
    traceback.print_exc() # 打印完整的堆栈信息

class PublishDialog(QtGui.QWidget):

    def __init__(self, app):
        QtGui.QWidget.__init__(self)
        # super(PublishDialog, self).__init__()
        self._app = app
        self.__debug = False
        return

    def write_log(self, log):
        import tempfile
        tmpdir = tempfile.gettempdir()
        name = os.path.basename(__file__)
        logf = os.path.join(tmpdir, name)
        logtime = str(datetime.now())
        with open('%s.txt' % logf, 'a') as f:
            f.write('\r\n debug:' + log + '\t @' + logtime)

    def print_log(self, msg, txt_color=TXT_DEFAULT):
        # Move the cursor to the end of the text editor
        self.ui.textEdit_log.moveCursor(QtGui.QTextCursor.End)
        self.ui.textEdit_log.setTextColor(txt_color)
        self.ui.textEdit_log.insertPlainText(msg + '\n')
        return

    def get_path_from_ctx(self):
        d_templates = {'Asset': ["asset_work_area_maya", "asset_publish", "asset_output"], \
                       'Shot': ["shot_work_area_maya", "shot_publish", "shot_output"], \
                       'Sequence': ["seq_work_area_maya", "seq_publish", "seq_output"]}
        paths_list = []
        if self.entity_type in d_templates.keys():
            for key in d_templates[self.entity_type]:
                path = None
                templates = self.tk.templates.get(key)


                search_field = {self.entity_type: self.entity_name, 'Step': self.step['name']}
                if self.entity_type == 'Asset':
                    search_field = {self.entity_type: self.entity_name,
                                    'sg_asset_type': self.asset_type,
                                    'Step': self.step['name']}

                elif self.entity_type=='Shot':
                    seq = self.entity_name[:3]
                    search_field = {self.entity_type: self.entity_name, 'Step': self.step['name'],'Sequence':seq}
                self.write_log('\n%s:' % key + str(search_field))
                paths = self.tk.paths_from_template(templates, search_field)
                if paths:
                    path = paths[0]
                    path = path.replace('\\', '/')
                paths_list.append(path)
                self.write_log('\n%s:' % key + str(path))
        self.work_root, self.publish_root, self.output_root = paths_list
        self.write_log('work_root:' + str(self.work_root))
        self.write_log('publish_root:' + str(self.publish_root))
        self.write_log('output_root:' + str(self.output_root))

    def set_vars(self):
        # Set LCA studio tools path
        # if sys.platform.startswith('win'):
        #     self.tool_root = 'U:/'
        #     self.log_root = 'Z:/trash/log/sg_publish/publish_check/'
        # elif sys.platform.startswith('linux'):
        #     self.tool_root = '/mnt/utility/'
        #     self.log_root = '/mnt/proj/trash/log/sg_publish/publish_check/'
        # else:
        #     self.tool_root = '/Volumes/utility/'
        #     self.log_root = '/mnt/proj/trash/log/sg_publish/publish_check/'
        self.tool_root = os.getenv('LC_UTILITY') + '/'
        self.log_root = os.getenv('LC_PROJ') + '/trash/log/sg_publish/publish_check/'

        # Get the task related info from sgtk
        self.tk = self._app.sgtk
        self.ctx = self._app.context
        self.sg = self._app.shotgun
        self.project = self.ctx.project
        self.task = self.ctx.task
        self.entity = self.ctx.entity
        self.entity_type = self.entity['type']
        if self.entity_type == 'Asset':
            asset_info = self.sg.find_one(self.entity_type, [['id', 'is', self.entity['id']]], ['sg_asset_type'])
            self.asset_type = asset_info['sg_asset_type']
        self.entity_name = self.entity['name']  # usually 'Asset' or 'Shot'
        self.step = self.ctx.step
        self.write_log('step:' + str(self.step) + ' type:' + self.entity_type + ' name:' + self.entity_name)
        self.get_path_from_ctx()
        self.user = sgtk.util.get_current_user(self.tk)
        self.user_name = getpass.getuser()
        self.version_key = self.entity['name'] + '.' + self.step['name'] + '.' + self.task['name'].lower()
        print 'self.step', self.step

        # This variable locks the next step button so artists can't go too deep
        # if he/she hasn't finish the goal of the current page.
        self.page_permit = 0
        self.page_achieve = 0
        self.publish_process_previous = 0

        self.default_preview_mov = ''
        self.published_file_type = 'Maya Scene'
        self.dependency_paths = []
        self.cam_dir = ''
        self.asset_description = None

        # if this is a USD standard project
        self.usd = True
        proj = self.sg.find_one('Project', [['id', 'is', self.project['id']]], ['tag_list'])
        for tag in proj['tag_list']:
            if tag == 'No USD':
                self.usd = False
        return

    def set_dept_vars(self, dept_file):
        # Those three config files decide which check will be embeded on the check list of the publish tool.
        dept_dir = os.path.split(dept_file)[0].replace('\\', '/')
        self.check_parent_name = os.path.basename(dept_dir)
        self.sys_check_xml = dept_dir + '/sys_checks.xml'
        self.publish_check_xml = dept_dir + '/publish_checks.xml'
        self.publish_processes_xml = dept_dir + '/publish_processes.xml'
        self.default_preview_jpg = dept_dir + '/default_preview.jpg'
        self.recipient_txt = dept_dir + '/recipient.txt'
        print 'self.publish_check_xml', self.publish_check_xml
        print 'self.publish_processes_xml', self.publish_processes_xml
        print 'self.default_preview_jpg', self.default_preview_jpg
        print 'self.recipient_txt', self.recipient_txt
        return

    def setup_tags(self):
        self.w_sys.comboBox_tag.insertItem(0, '')
        l_stages = get_stage_list.get_stages()

        t_step = self.step['name']
        t_entity = self.entity['type'].lower()
        if t_entity == 'asset':
            asset_info = self.sg.find_one('Asset', [['id', 'is', self.entity['id']]], ['sg_asset_type'])
            self.asset_type = asset_info['sg_asset_type']
        else:
            self.asset_type = ''

        task_info = self.sg.find_one('Task', [['id', 'is', self.task['id']]], ['content'])
        t_task = task_info['content']

        # print "test"
        # print t_step
        # print t_entity
        # print self.asset_type
        # print t_task

        # rig
        # asset
        # chr/asm
        # rigging_layout

        if t_step == 'rig' and self.asset_type != 'chr' and self.asset_type != 'asm' or t_task == 'rigging_layout':
            self.w_sys.comboBox_tag.insertItems(0, [u"完整版"])
            return
        else:
            for stage in l_stages:
                if t_step.startswith(stage[0]) and t_entity.startswith(stage[1]) and self.asset_type.startswith(
                        stage[2]) and t_task.startswith(stage[3]):
                    self.w_sys.comboBox_tag.insertItems(0, stage[4])
                    return

        return

    def setup_gui(self, Ui_Dialog, widget_sys, widget_version, widget_file, widget_check, widget_publish,
                  widget_publish_file):
        '''Setup the GUI'''
        # Create the dialog as the main canvas
        self.ui = Ui_Dialog()
        self.is_confirm_description = False

        self.ui.setupUi(self)
        # self.ui.pushButton_cancel.hide()
        self.ui.pushButton_prev.hide()

        # Build up the standard 5 pages for the check
        self.w_sys, w_sys_form = widget_page.create_page(self.ui.stackedWidget, widget_sys)
        self.w_file, w_file_form = widget_page.create_page(self.ui.stackedWidget, widget_file)
        self.w_ver, w_ver_form = widget_page.create_page(self.ui.stackedWidget, widget_version)
        self.w_check, w_check_form = widget_page.create_page(self.ui.stackedWidget, widget_check)
        self.w_publish, w_publish_form = widget_page.create_page(self.ui.stackedWidget, widget_publish)

        # Build the checks and processes
        self.l_sys_checks = setup_sys_page.build(w_sys_form, self.sys_check_xml, self)
        # Insert department specific publish file widget
        self.w_publish_file = widget_publish_file()
        self.w_publish_file.setupUi(self.w_file.groupBox_publish_files)

        self.l_publish_checks,self.tabWidget_sys_check,self.grp_tab = setup_check_page.build(w_check_form, self.publish_check_xml, self)
        self.l_publish_processes = setup_publish_page.build(w_publish_form, self.publish_processes_xml, self)

        # self.asset_description = self.grp_tab.description_edit.toPlainText()

        # self.w_file.listWidget_preview.setStyleSheet('QListWidget {color: rgb(250, 150, 30)}')
        self.ui.comboBox_publish_mode.setStyleSheet('QComboBox {color: rgb(250, 150, 30)}')
        if self.step['name'] == 'ani' and self.entity_type == 'Shot':
            print 'set_publish_mode_ani'
            self.set_publish_mode_ani()
        else:
            print 'set_publish_mode'
            self.set_publish_mode()

        self.w_sys.comboBox_tag.setStyleSheet('QComboBox {color: rgb(250, 150, 30)}')
        self.setup_tags()

        if os.path.isfile(self.default_preview_jpg):
            self.w_file.listWidget_preview.addItem(self.default_preview_jpg)
        else:
            self.print_log('Missing ' + self.default_preview_jpg)

        return

    def lock_publish_mode(self, v_type=''):
        for i in range(self.ui.comboBox_publish_mode.count()):
            publish_mode = unicode(self.ui.comboBox_publish_mode.itemText(i))
            if publish_mode.startswith(v_type):
                self.ui.comboBox_publish_mode.setCurrentIndex(i)
                self.ui.comboBox_publish_mode.setEnabled(False)
                return
        return

    def do_bind(self):
        if self.step['name'] == 'ani' and self.entity_type == 'Shot':
            self.ui.comboBox_publish_mode.currentIndexChanged.connect(self.set_publish_mode_ani)
        else:
            self.ui.comboBox_publish_mode.currentIndexChanged.connect(self.set_publish_mode)
        self.ui.pushButton_next.clicked.connect(self.next_page)
        self.ui.pushButton_prev.clicked.connect(self.prev_page)
        self.w_sys.pushButton_check.clicked.connect(self.check_sys)
        self.w_ver.lineEdit_version_name.textEdited.connect(self.set_version)
        self.w_file.pushButton_pick_preview.clicked.connect(self.pick_preview)
        self.w_file.thumbnail_widget.thumbnail_changed.connect(self.snapshot)
        self.w_file.listWidget_preview.itemPressed.connect(self.select_preview)
        self.w_check.pushButton_check.clicked.connect(self.check_publish)
        self.w_check.cancle_check.clicked.connect(self.cancle_check)
        if self.get_gas_group():
            self.w_check.cancle_check.setEnabled(True)
        else:
            self.w_check.cancle_check.setEnabled(False)
        if self.step['name'] != 'mod':
            self.w_check.cancle_check.setVisible(False)
        try:
            if self.step['name'] == 'mod' and self.check_parent_name == 'mod':
                self.grp_tab.confirm_btn.clicked.connect(self.user_confirm_description)
        except Exception as e:
            pass

        # self.ui.pushButton_cancel.clicked.connect(self.cancel_publish)
        return

    def set_publish_mode(self):
        self.page_permit = 0
        self.page_achieve = 0
        # self.w_file.listWidget_preview.clear()

        # Publish preview (for daily) or publish files for downstream
        self.publish_mode = self.ui.comboBox_publish_mode.currentIndex()
        print 'self.publish_mode', self.publish_mode

        # Daily
        if self.publish_mode == 0:
            for check in self.l_sys_checks:
                if not check.tab_name.startswith('Generic'):
                    check.disable()

            for check in self.l_publish_checks:
                if not check.tab_name.startswith('Generic'):
                    check.disable()

            for process in self.l_publish_processes:
                if process.module_mode != 'daily':
                    process.disable()

            if self.step['name'] not in ['aud', 'art', 'srf', 'cfx', 'plt']:
                self.w_file.groupBox_publish_files.setEnabled(False)
            # # 此处进行判定，当 rough lay 趴文件时，提交 daily 清除 添加的所有 button 和 lineedit
            # if self.ui.comboBox_publish_mode.currentIndex() == 0 and self.step['name'] == 'lay' and self.entity_type == 'Sequence':
            #     print '||||||||||||||||||||'
            #     grp_tab_children = self.grp_tab.findChildren(QtGui.QWidget)
            #     if len(grp_tab_children) != 0:
            #         for gtc in grp_tab_children:
            #             gtc.deleteLater()
            #     print len(self.grp_tab.findChildren(QtGui.QWidget))
            #     print '||||||||||||||||||||'
            
        # Publish for downstream & Checked(ani only)
        else:
            for check in self.l_sys_checks:
                if not check.tab_name.startswith('Generic'):
                    check.enable()

            for check in self.l_publish_checks:
                if not check.tab_name.startswith('Generic'):
                    if self.get_omit_check(check):
                        check.disable()
                    else:
                        check.enable()

            for process in self.l_publish_processes:
                if process.module_mode != 'daily':
                    process.enable()


            for process in self.l_publish_processes:
                if process.module_mode == "mod3th":
                    process.disable()
                    if self.w_sys.comboBox_tag.currentIndex() == 2:
                        process.enable()

                if process.module_name=="color_id_cache" and self.w_sys.comboBox_tag.currentIndex() == 2:
                    process.disable()
            # # 此处进行判定，当 rough lay 趴文件时，提交 downstream 添加对应的 button 和 lineedit
            # if self.ui.comboBox_publish_mode.currentIndex() == 1 and self.step['name'] == 'lay' and self.entity_type == 'Sequence':
            #     print '//////////////////'
            #     print self.tabWidget_sys_check.tabText(0)
            #     print '//////////////////'
                
            #     # print self.w_file.listWidget_preview.count()
            #     # for data in self.shots_preview_data:
            #     #     print pm.nt.Shot(data['shot_node'])
            #     #     print data['shot_info']['code']


            self.w_file.groupBox_publish_files.setEnabled(True)

        return

    def set_publish_mode_ani(self):
        self.page_permit = 0
        self.page_achieve = 0
        # self.w_file.listWidget_preview.clear()

        # z1 场次默认只可以趴ds(z1 是群集 cycle 场次，z33 是给 缓存减面使用的
        if self.step['name'] == 'ani' and (self.entity['name'].startswith('z1') or self.entity['name'].startswith('z33')):
            self.ui.comboBox_publish_mode.setCurrentIndex(2)
            self.ui.comboBox_publish_mode.setEnabled(False)

        # Publish preview (for daily) or publish files for downstream
        self.publish_mode = self.ui.comboBox_publish_mode.currentIndex()

        # Daily
        if self.publish_mode == 0:
            for check in self.l_sys_checks:
                if not check.tab_name.startswith('Generic'):
                    check.disable()

            for check in self.l_publish_checks:
                if not check.tab_name.startswith('Generic'):
                    check.disable()

            for process in self.l_publish_processes:
                if process.module_mode != 'daily':
                    process.disable()

            if self.step['name'] not in ['aud']:
                self.w_file.groupBox_publish_files.setEnabled(False)

        # Checked(ani only)
        elif self.publish_mode == 1:
            for check in self.l_sys_checks:
                check.enable()

            for check in self.l_publish_checks:
                check.enable()

            for process in self.l_publish_processes:
                if process.module_mode in ['daily', 'checked']:
                    process.enable()
                else:
                    process.disable()

            self.w_file.groupBox_publish_files.setEnabled(True)

        else:
            for check in self.l_sys_checks:
                check.enable()

            for check in self.l_publish_checks:
                check.enable()

            for process in self.l_publish_processes:
                process.enable()

            self.w_file.groupBox_publish_files.setEnabled(True)

        # add ani playblast mov as default preview, if it exists
        import pymel.core as pm
        cur_scene = str(pm.sceneName())
        template = self.tk.templates['maya_shot_playblast_movie']
        fields = self.ctx.as_template_fields(template)
        fields.update(version=int(cur_scene.split('.')[-2].replace('v', '')))
        pb_mov_path = template.apply_fields(fields)
        # render_mov_path = pb_mov_path.replace('/data/', '/render/')
        self.w_file.listWidget_preview.clear()
        pb_mov_path = pb_mov_path.replace('\\','/')
        print 'pb_mov_path ---',pb_mov_path,os.path.isfile(pb_mov_path)
        if os.path.isfile(pb_mov_path):
            self.w_file.listWidget_preview.addItem(pb_mov_path)
        else:
            self.w_file.listWidget_preview.clear()
        # print 'self.w_file.listWidget_preview. ---',self.w_file.listWidget_preview.item(0).text()
        # publish file don't need render mov file because of edt dept
        # elif os.path.isfile(render_mov_path):
        #     self.w_file.listWidget_preview.addItem(render_mov_path)
        return

    def get_omit_check(self, check):
        print 'get_omit_check pass: ', check.module_name
        return False

    def show_app_info(self):

        # Print version and release date
        app_v = "unknown"
        app_time = "unknown"

        # self.print_log(__file__)

        folders = __file__.replace("\\", "/").split("/")

        for f in folders:
            tokens = f.split('.')
            if len(tokens) == 3 and tokens[0].startswith('v') and tokens[0][1:].isdigit() and tokens[1].isdigit() and \
                    tokens[2].isdigit():
                app_v = f

        app_time = time.ctime(os.path.getmtime(__file__))

        self.print_log("App Version: " + app_v)
        self.print_log("App Release Time: " + app_time)
        self.print_log("App Full Path: " + os.path.dirname(__file__.replace("\\", "/")) + '\n')
        return

    def user_confirm_description(self):
        print(u'已经确认描述')
        self.is_confirm_description = True

    def next_page(self):
        i = self.ui.stackedWidget.currentIndex()
        # self.print_log(str(i)+" "+str(self.page_permit) + " " + str(self.page_achieve) )
        print '>' * 50, 'page:', i
        if i == 4:
            # do publish
            self.on_publish()
            return

        if i + 1 > self.page_permit:
            self.print_log(u"请先完成本页的目标才能进入下一页。", txt_color=TXT_BLUE)
        else:
            self.ui.comboBox_publish_mode.setEnabled(False)

            if self.page_achieve < self.page_permit and i == self.page_achieve:
                if i == 1:
                    # setup version page and grand permission to the publish check page
                    setup_version_page.build(self)
                    if str(self.w_ver.lineEdit_version_name.text()) != '.v':
                        self.page_permit = 3
                # 增加判断情况 当所有检查项都过的时候，看是否确认了所有角色的tpose
                if i == 3: 
                    # 针对 ani 角色 tpose 检查，如果没有全部确认，则无法进入下一个 pub 页面
                    if self.ui.comboBox_publish_mode.currentIndex()>0 and self.task['name'] == 'animation' and self.step['name'] == 'ani':
                        # 获取所有角色的visb ctrl及其对应的lca属性值
                        allTposeData = check_tpose_frame.TposeFrame().getAllVisibCtrl()

                        allSure = [allTposeData[ii]['lca_sure_tpose'] for ii in allTposeData.keys()]
                        # 都为1才能跳到趴文件的页面
                        if len(set(allSure)) == 1:
                            if allSure[0]=='1':
                                pass
                            else:
                                self.print_log(u"请先 确认所有角色的 Tpose 所在帧 才能进入下一页。", txt_color=TXT_BLUE)
                                return
                        elif len(set(allSure)) > 1:
                            self.print_log(u"请先 确认所有角色的 Tpose 所在帧 才能进入下一页。", txt_color=TXT_BLUE)
                            return
                        # 针对 ani 角色 pass 检查，如果没有全部确认，则无法进入下一个 pub 页面(提交 check ，downstream 时才会判定)
                        if self.ui.comboBox_publish_mode.currentIndex() >= 1:
                            surePassChecked = check_pass_ani_flo.TposeFrame().getSurePassChecked(self)
                            allSure = []
                            for ii in surePassChecked.keys():
                                allSure = allSure + surePassChecked[ii].values()
                            # 都为1才能跳到趴文件的页面
                            if len(set(allSure)) == 1:
                                if allSure[0]=='1':
                                    pass
                                else:
                                    self.print_log(u"请先 检查并确认 所有角色的 Pass 才能进入下一页。", txt_color=TXT_BLUE)
                                    return
                            elif len(set(allSure)) > 1:
                                self.print_log(u"请先 检查并确认 所有角色的 Pass 才能进入下一页。", txt_color=TXT_BLUE)
                                return
                    # 只有当是 Lay 环节才会去判断
                    elif self.ui.comboBox_publish_mode.currentIndex()==1 and self.step['name'] == 'lay' and self.entity_type == 'Sequence':
                        shot_names = [data['shot_info']['code'] for data in self.shots_preview_data]
                        # 获取所有角色的visb ctrl及其对应的lca pass属性值
                        allPassData = check_pass.TposeFrame().getAllVisibCtrl(shot_names,self)
                        print
                        print allPassData
                        print
                        allSure = []
                        for ii in allPassData.keys():
                            allSure = allSure + allPassData[ii].values()
                        # 都为1才能跳到趴文件的页面
                        if len(set(allSure)) == 1:
                            if allSure[0]=='1':
                                pass
                            else:
                                self.print_log(u"请先 检查并确认 所有角色的 Pass 才能进入下一页。", txt_color=TXT_BLUE)
                                return
                        elif len(set(allSure)) > 1:
                            self.print_log(u"请先 检查并确认 所有角色的 Pass 才能进入下一页。", txt_color=TXT_BLUE)
                            return
                    # 针对 flo 角色 pass 检查，如果没有全部确认，则无法进入下一个 pub 页面(提交 check ，downstream 时才会判定)
                    elif self.ui.comboBox_publish_mode.currentIndex() == 1 and self.step['name'] == 'flo' and self.entity_type == 'Shot' and self.task['name'] == 'final_layout':
                        surePassChecked = check_pass_ani_flo.TposeFrame().getSurePassChecked(self)
                        allSure = []
                        for ii in surePassChecked.keys():
                            allSure = allSure + surePassChecked[ii].values()
                        # 都为1才能跳到趴文件的页面
                        if len(set(allSure)) == 1:
                            if allSure[0]=='1':
                                pass
                            else:
                                self.print_log(u"请先 检查并确认 所有角色的 Pass 才能进入下一页。", txt_color=TXT_BLUE)
                                return
                        elif len(set(allSure)) > 1:
                            self.print_log(u"请先 检查并确认 所有角色的 Pass 才能进入下一页。", txt_color=TXT_BLUE)
                            return
                    elif self.ui.comboBox_publish_mode.currentIndex() == 1 and self.task['name'] == 'model' and self.step['name'] == self.check_parent_name == 'mod':
                        try:
                            if self.grp_tab.confirm_btn.isEnabled() and not self.is_confirm_description:
                                self.print_log(u'请先确认描述。', txt_color=TXT_RED)
                                self.grp_tab.confirm_btn.setStyleSheet('color: rgb(202, 125, 125);')
                                return
                            self.grp_tab.confirm_btn.setStyleSheet('color: rgb(132, 143, 186);')
                            if u'不' not in self.grp_tab.reuse_cbbx.currentText():
                                self.asset_description = self.grp_tab.description_edit.toPlainText()
                        except Exception as e:
                            pass

                # To mark "I have been here!"
                self.page_achieve += 1
            # 增加情况 当所有检查项都过的时候，看是否确认了所有角色的tpose，这个是考虑到了 self.page_achieve 和 self.page_permit 的关系
            elif self.page_achieve >= self.page_permit and i == 3: 
                # 只有当是动画环节才会去判断
                if self.ui.comboBox_publish_mode.currentIndex()>0 and self.task['name'] == 'animation' and self.step['name'] == 'ani':
                    # 获取所有角色的visb ctrl及其对应的lca属性值
                    allTposeData = check_tpose_frame.TposeFrame().getAllVisibCtrl()

                    allSure = [allTposeData[ii]['lca_sure_tpose'] for ii in allTposeData.keys()]

                    if len(set(allSure)) == 1:
                        if allSure[0]=='1':
                            pass
                        else:
                            self.print_log(u"请先 确认所有角色的 Tpose 所在帧 才能进入下一页。", txt_color=TXT_BLUE)
                            return
                    elif len(set(allSure)) > 1:
                        self.print_log(u"请先 确认所有角色的 Tpose 所在帧 才能进入下一页。", txt_color=TXT_BLUE)
                        return
                    # 针对 ani 角色 pass 检查，如果没有全部确认，则无法进入下一个 pub 页面(提交 check ，downstream 时才会判定)
                    if self.ui.comboBox_publish_mode.currentIndex() >= 1:
                        surePassChecked = check_pass_ani_flo.TposeFrame().getSurePassChecked(self)
                        allSure = []
                        for ii in surePassChecked.keys():
                            allSure = allSure + surePassChecked[ii].values()
                        # 都为1才能跳到趴文件的页面
                        if len(set(allSure)) == 1:
                            if allSure[0]=='1':
                                pass
                            else:
                                self.print_log(u"请先 检查并确认 所有角色的 Pass 才能进入下一页。", txt_color=TXT_BLUE)
                                return
                        elif len(set(allSure)) > 1:
                            self.print_log(u"请先 检查并确认 所有角色的 Pass 才能进入下一页。", txt_color=TXT_BLUE)
                            return
                # 只有当是 Lay 环节才会去判断
                elif self.ui.comboBox_publish_mode.currentIndex()==1 and self.step['name'] == 'lay' and self.entity_type == 'Sequence':
                    shot_names = [data['shot_info']['code'] for data in self.shots_preview_data]
                    # 获取所有角色的visb ctrl及其对应的lca pass属性值
                    allPassData = check_pass.TposeFrame().getAllVisibCtrl(shot_names,self)
                    print
                    print allPassData
                    print
                    allSure = []
                    for ii in allPassData.keys():
                        allSure = allSure + allPassData[ii].values()
                    # 都为1才能跳到趴文件的页面
                    if len(set(allSure)) == 1:
                        if allSure[0]=='1':
                            pass
                        else:
                            self.print_log(u"请先 检查并确认 所有角色的 Pass 才能进入下一页。", txt_color=TXT_BLUE)
                            return
                    elif len(set(allSure)) > 1:
                        self.print_log(u"请先 检查并确认 所有角色的 Pass 才能进入下一页。", txt_color=TXT_BLUE)
                        return
                # 针对 flo 角色 pass 检查，如果没有全部确认，则无法进入下一个 pub 页面(提交 check ，downstream 时才会判定)
                elif self.ui.comboBox_publish_mode.currentIndex() == 1 and self.step['name'] == 'flo' and self.entity_type == 'Shot' and self.task['name'] == 'final_layout':
                    surePassChecked = check_pass_ani_flo.TposeFrame().getSurePassChecked(self)
                    allSure = []
                    for ii in surePassChecked.keys():
                        allSure = allSure + surePassChecked[ii].values()
                    # 都为1才能跳到趴文件的页面
                    if len(set(allSure)) == 1:
                        if allSure[0]=='1':
                            pass
                        else:
                            self.print_log(u"请先 检查并确认 所有角色的 Pass 才能进入下一页。", txt_color=TXT_BLUE)
                            return
                    elif len(set(allSure)) > 1:
                        self.print_log(u"请先 检查并确认 所有角色的 Pass 才能进入下一页。", txt_color=TXT_BLUE)
                        return
                
                self.page_achieve += 1

            ##########################
            # 此处进行判定，当 rough lay 趴文件时，提交 downstream 添加对应的 button 和 lineedit(根据所选的镜头来)
            if i == 1 and self.ui.comboBox_publish_mode.currentIndex()==1 and self.step['name'] == 'lay' and self.entity_type == 'Sequence':
                self.clear_check_pass_ui()
                import ani.lca_cleanup_file as cf
                reload(cf)
                cf.fixNamespaces_before_checkPass()
                self.set_check_pass_ui_rough_lay()
            # 此处进行判定，当 rough lay 趴文件时，提交 daily 清除 添加的所有 button 和 lineedit
            if i == 1 and self.ui.comboBox_publish_mode.currentIndex()==0 and self.step['name'] == 'lay' and self.entity_type == 'Sequence':
                self.clear_check_pass_ui()
            # 此处进行判定，当 ani 趴文件时，提交 check ，downstream 添加对应的 button 和 lineedit
            if i == 1 and self.ui.comboBox_publish_mode.currentIndex() >= 1 and self.step['name'] == 'ani' and self.entity_type == 'Shot' and self.task['name'] == 'animation':
                self.clear_check_pass_ui()
                import ani.lca_cleanup_file as cf
                reload(cf)
                if cf.check_current_shot_big():
                    cf.fixBigSceneNamespaces()
                else:
                    cf.fixNamespaces_before_checkPass()
                self.set_check_pass_ui_ani_flo()
            # 此处进行判定，当 ani 趴文件时，提交 daily 清除对应的 button 和 lineedit
            if i == 1 and self.ui.comboBox_publish_mode.currentIndex() == 0 and self.step['name'] == 'ani' and self.entity_type == 'Shot' and self.task['name'] == 'animation':
                self.clear_check_pass_ui()
            # # 此处进行判定，当 ani 趴文件时,不是提交 animation 时 清除对应的 button 和 lineedit
            # if i == 1 and self.w_sys.comboBox_tag.currentIndex() != 2 and self.step['name'] == 'ani' and self.entity_type == 'Shot' and self.task['name'] == 'animation':
            #     self.clear_check_pass_ui()
            # print 
            # print 'self.w_sys.comboBox_tag.currentIndex() >',self.w_sys.comboBox_tag.currentIndex()
            # print 'self.ui.comboBox_publish_mode.currentIndex() >',self.ui.comboBox_publish_mode.currentIndex()
            # print "self.step['name'] >",self.step['name']
            # print 'self.entity_type >',self.entity_type
            # print "self.task['name'] >",self.task['name']
            # print 
            # 此处进行判定，当 flo 趴文件时，提交 downstream 添加对应的 button 和 lineedit
            if i == 1 and self.ui.comboBox_publish_mode.currentIndex() == 1 and self.step['name'] == 'flo' and self.entity_type == 'Shot' and self.task['name'] == 'final_layout':
                self.clear_check_pass_ui()
                import ani.lca_cleanup_file as cf
                reload(cf)
                if cf.check_current_shot_big():
                    cf.fixBigSceneNamespaces()
                else:
                    cf.fixNamespaces_before_checkPass()
                self.set_check_pass_ui_ani_flo()
            # 此处进行判定，当 flo 趴文件时，提交 daily 清除对应的 button 和 lineedit
            if i == 1 and self.ui.comboBox_publish_mode.currentIndex() == 0 and self.step['name'] == 'flo' and self.entity_type == 'Shot' and self.task['name'] == 'final_layout':
                self.clear_check_pass_ui()
            ##########################

            # Always show the "previous" button
            self.ui.pushButton_prev.show()

            # Go to the next page

            self.ui.stackedWidget.setCurrentIndex(i + 1)
            self.ui.progressBar_publish_process.setValue((i + 1) * 20)

            # if i == 3:
            #     if self.step['name'] == 'mod' and self.publish_mode == 1 and self.asset_type == 'chr':
            #         # check turntable:
            #         turntable_result = check_head_turntable.check_head_turntable().run_check()
            #         if turntable_result:
            #             self.print_log(u"当角色高度小于1.4米时，自动生成的turntable可能比例不合适，需要模型师手动检查!", txt_color=TXT_ORANGE)
            #             QtGui.QMessageBox.about(self, "Note!", u"当角色高度小于1.4米时，自动生成的turntable可能比例不合适，需要模型师手动检查! "
            #                                                    u"打开turntable看看比例合不合适，不合适进行调整，若合适则忽略此提示")
            #         # check sg_related_assets:
            #         related_assets = get_sg_related_assets.check_related_assets().get_related_assets(self.entity_name)
            #         if related_assets:
            #             related_assets.insert(0,u'<请选择>')
            #             if related_assets:
            #                 asset,ok = QtGui.QInputDialog.getItem(self,u'相关资产选择',u'当前资产有相关资产，请选择要publish的资产，若不pu请点击取消，记得不要忘了继续publish当前资产',related_assets,0,True)
            #                 if ok and asset!=u'<请选择>':
            #                     t = get_sg_related_assets.check_related_assets().open_related_assets(self.project['name'],asset)

            # if the version has already been publishd, lock the "next" button on the publish page
            if i == 3:
                self.ui.pushButton_next.setText(u"提交 >>")
                if self.page_achieve == 5:
                    self.ui.pushButton_next.setEnabled(False)

        return

    def prev_page(self):
        i = self.ui.stackedWidget.currentIndex()
        self.ui.stackedWidget.setCurrentIndex(i - 1)
        self.ui.progressBar_publish_process.setValue((i - 1) * 20)

        # Hide the "previous" button on the first page
        # Enable the publish mode on the first page
        if i == 1:
            self.ui.pushButton_prev.hide()
            self.ui.comboBox_publish_mode.setEnabled(True)

        # Always set the "next" button's label back to "the next step" and enabled
        self.ui.pushButton_next.setText(u"下一步 >>")
        self.ui.pushButton_next.setEnabled(True)
        return

    # Page 1: system check
    def check_sys(self):

        '''self.version_tag = self.w_sys.comboBox_tag.currentText()

        if self.version_tag == '':
            self.print_log(u"还没有选择版本的标签。\n", txt_color = TXT_RED)
            return'''

        check_result = True
        for sys_check in self.l_sys_checks:
            # Skip downstream publish checks
            if self.publish_mode == 0 and not sys_check.tab_name.startswith('Generic'):
                continue

            sys_check.run_check()
            if not sys_check.get_valid():
                check_result = False

        if not check_result:
            self.print_log(u"系统检查不通过。\n", txt_color=TXT_RED)
            return

        self.print_log(u"系统检查通过。\n", txt_color=TXT_BLUE)

        if os.path.isfile(self.default_preview_mov):
            # ============= change ani pub pick data mov at window =============
            if self.step['name'] == 'ani' and self.entity_type == 'Shot':
                ani_default_preview_mov = self.default_preview_mov.replace('\\','/')
                if '/render/' in ani_default_preview_mov:
                    ani_default_preview_mov = ani_default_preview_mov.replace('/render/', '/data/')
                if os.path.isfile(ani_default_preview_mov):
                    self.w_file.listWidget_preview.clear()
                    self.w_file.listWidget_preview.addItem(ani_default_preview_mov)
                print 'ani_default_preview_mov ---',ani_default_preview_mov,os.path.isfile(ani_default_preview_mov)
                # ============= change ani pub pick data mov at window =============
            else:
                print 'self.default_preview_mov ---',self.default_preview_mov,os.path.isfile(self.default_preview_mov)
                self.w_file.listWidget_preview.clear()
                self.w_file.listWidget_preview.addItem(self.default_preview_mov)

        if self.page_permit < 1:
            self.page_permit = 1
            if self.w_file.listWidget_preview.count() > 0:
                self.page_permit = 2

        return

    def pick_preview_folder(self):
        # sys.path.append('u:/toolset/lib')
        import production.pipeline.utils as pplu

        pick_dialog = QtGui.QFileDialog(self)
        pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
        pick_dialog.setFileMode(QtGui.QFileDialog.Directory)
        pick_dialog.setOption(QtGui.QFileDialog.ShowDirsOnly, on=True)
        output_path = self.work_root.replace('/task/maya', '/output/nuke')
        output_path = output_path.replace('/mnt/work', '/output')
        pick_dialog.setDirectory(output_path)
        res = pick_dialog.exec_()

        if res != QtGui.QDialog.Accepted:
            return

        render_dir = str(pick_dialog.selectedFiles()[0])
        if os.path.isdir(render_dir):
            exr_dir = render_dir.replace('\\', '/')
            try:
                version_tag = exr_dir.split('/')[-2]
                self.w_ver.lineEdit_version_name.setText('.' + version_tag)
            except:
                pass
            exrs = pplu.findFiles(render_dir, file_type='')
            self.w_file.listWidget_preview.clear()
            for s in exrs:
                if os.path.isfile(s):
                    self.w_file.listWidget_preview.addItem(s)
        return

    # Page 2: provide files
    def pick_preview(self):
        modifiers = QtGui.QApplication.keyboardModifiers()
        if modifiers == QtCore.Qt.ControlModifier:
            self.pick_preview_folder()
        else:
            pick_dialog = QtGui.QFileDialog(self)
            pick_dialog.setViewMode(QtGui.QFileDialog.Detail)
            pick_dialog.setFileMode(QtGui.QFileDialog.ExistingFiles)

            if (self.ctx.step['name'] == 'lgt' or self.ctx.step['name'] == 'pfx') \
                    and self.entity['type'] == 'Shot':
                if self.ctx.step['name'] == 'pfx':
                    output_path = self.work_root.replace('/task/maya', '/output')
                else:
                    output_path = self.work_root.replace('/task/maya', '/output/nuke')
                output_path = output_path.replace('/mnt/work', '/output')
                pick_dialog.setDirectory(output_path)
            elif self.ctx.step['name'] == 'efx' and self.entity['type'] == 'Shot':
                output_path = self.work_root.replace('/task/maya', '/task/houdini/hip/preview')
                pick_dialog.setDirectory(output_path)
            elif self.ctx.step['name'] == 'lay' and self.entity['type'] == 'Sequence':
                output_path = os.path.join(self.work_root, 'data')
                # print 'output_path:', output_path
                pick_dialog.setDirectory(output_path)
            elif self.ctx.step['name'] == 'plt' \
                    or (self.ctx.step['name'] == 'cfx' and self.entity['type'] == 'Shot'):
                output_path = self.work_root.replace('/task/maya', '/output/render_images')
                output_path = output_path.replace('/mnt/work', '/output')
                pick_dialog.setDirectory(output_path)
            elif self.ctx.step['name'] == 'cfx' and self.entity['type'] == 'Asset':
                output_path = self.work_root.replace('/task/maya', '/output/turntable')
                output_path = output_path.replace('/mnt/work', '/output')
                pick_dialog.setDirectory(output_path)
            else:
                pick_dialog.setDirectory(self.work_root)

            pick_dialog.setNameFilters(
                ["Images/Video(*.jpg  *.jpeg *.tiff *.tiff *.exr *.png *.mov)", "All Files(*.*)"])
            pick_dialog.exec_()
            l_files = pick_dialog.selectedFiles()

            for file_path in l_files:
                # The preview file list contains either 1 mov file or some jpeg files.
                file_path_str = str(file_path)
                if file_path_str.lower().endswith('.mov'):
                    # Clean the list if it's a mov file
                    self.w_file.listWidget_preview.clear()
                else:
                    i = self.w_file.listWidget_preview.count()
                    if i == 1 and str(self.w_file.listWidget_preview.item(0).text()).lower().endswith('.mov'):
                        self.w_file.listWidget_preview.clear()

                self.w_file.listWidget_preview.addItem(file_path_str.replace('\\', '/'))

        if self.w_file.listWidget_preview.count() > 0 and self.page_permit < 2:
            self.page_permit = 2

        return

    def snapshot(self):

        # TODO add a check later
        if not os.path.isdir(self.work_root + "/snapshots"):
            os.mkdir(self.work_root + "/snapshots")

        if self.w_file.thumbnail_widget.thumbnail:
            snap_jpg = self.work_root + "/snapshots/snapshot." + str(int(time.time())) + ".jpg"
            self.w_file.thumbnail_widget.thumbnail.save(snap_jpg, format='JPG')

            # Clean the mov file before add the snapshot to the list
            i = self.w_file.listWidget_preview.count()
            if i == 1 and str(self.w_file.listWidget_preview.item(0).text()).lower().endswith('.mov'):
                self.w_file.listWidget_preview.clear()
            self.w_file.listWidget_preview.addItem(snap_jpg.replace('\\', '/'))

        if self.page_permit < 2:
            self.page_permit = 2

        self.print_log('self.page_permit' + str(self.page_permit))
        return

    def select_preview(self):

        l_items = self.w_file.listWidget_preview.selectedItems()

        if self.w_file.listWidget_preview._mouse_button == QtCore.Qt.LeftButton:
            self.w_file.thumbnail_widget.thumbnail_changed.disconnect(self.snapshot)
            img_path = str(l_items[-1].text())
            if os.path.isfile(img_path):
                self.w_file.thumbnail_widget.thumbnail = QtGui.QPixmap(img_path)

            self.w_file.thumbnail_widget.thumbnail_changed.connect(self.snapshot)
        else:
            for item in l_items:
                i = self.w_file.listWidget_preview.indexFromItem(item).row()
                self.w_file.listWidget_preview.takeItem(i)

        return

    # Page 3: version number
    def set_version(self):
        if self.page_permit < 3:
            self.page_permit = 3
        return

    # Page 4: publish check
    def cancle_check(self):
        for publish_check in self.l_publish_checks:
            if publish_check.allow_skip:
                publish_check.skip_checkbox.setCheckState(QtCore.Qt.Unchecked)

    def get_gas_group(self):
        name_list = self.sg.find('HumanUser', [['sg_status_list', 'is', 'act'], ['department.Department.code', 'is', "gas"]], ['login'])
        code = [i['login'] for i in name_list]
        if self.user_name not in code:
            return False
        return True

    def check_publish(self):

        check_result = u''
        if self.step['name'] == 'mod' and self.publish_mode == 1:
            self.w_check.cancle_check.setEnabled(True)
        for publish_check in self.l_publish_checks:
            # Skip downstream publish checks
            if self.publish_mode == 0 and not publish_check.tab_name.startswith('Generic'):
                continue

            # if not publish_check.get_skip_chk() == QtCore.Qt.CheckState.Checked:
            if not publish_check.get_skip_chk():
                continue

            if not publish_check.check_button.isEnabled() :
                continue

            publish_check.run_check()
            if not publish_check.get_valid():
                check_result += publish_check.module_type + '.' + publish_check.module_name + '\n'
                check_result += publish_check.result + '\n'
                check_result += '\n' + '*' * 50 + '\n\n'

        if check_result != '':
            v_name = self.version_key + self.w_ver.lineEdit_version_name.text()
            time_str = datetime.now().isoformat().split('.')[0].replace(':', '-').replace('T', '-')
            log_path = self.log_root + time_str + '.' + v_name + '.txt'
            try:
                f = open(log_path, 'w')
                f.write(check_result.encode('utf-8'))
                f.close()
            except:
                self.print_log(u"没有输出错误日志", txt_color=TXT_ORANGE)
                self.print_log(traceback.format_exc(), txt_color=TXT_ORANGE)

            return

        if self.page_permit < 4:
            self.page_permit = 4

        return

    # Page 5: publish
    def format_recipients(self, recipients):
        # TODO check if the recipents are valid
        self.l_recipients = []
        tokens = recipients.split(" ")
        for t in tokens:
            if t == '':
                continue

            user = t.split('@')[0]
            self.l_recipients.append(user + '@lightchaseranimation.com')

        return

    def on_publish(self):
        desc_txt = self.w_publish.plainTextEdit_description.toPlainText()
        if desc_txt.__class__.__name__ == 'QString':
            desc_txt = str(desc_txt.toUtf8())
        elif desc_txt.__class__.__name__ == 'str':
            desc_txt = desc_txt.decode('utf-8')

        self.description = desc_txt

        if len(self.description) < 2:
            self.print_log(u"版本描述太短,请详细描述一下再提交。", txt_color=TXT_BLUE)
            return

        recipient = str(self.w_publish.lineEdit_email.text())
        if not recipient or len(recipient) == 0:
            self.print_log(u"请提供邮件收件人。", txt_color=TXT_BLUE)
            return

        self.start_time = time.time()

        self.format_recipients(recipient)

        if self.step['name'] == 'mod':
            import maya.cmds as cmds
            if sys.platform.startswith('win'):
                log_root = 'Z:/trash/log/sg_publish/publish_process/'+self.project['name'].lower()
            elif sys.platform.startswith('linux'):
                log_root = '/mnt/proj/trash/log/sg_publish/publish_process/'+self.project['name'].lower()
            if not os.path.exists(log_root):
                os.makedirs(log_root)
            v_name = self.version_key + self.w_ver.lineEdit_version_name.text()
            time_str = datetime.now().isoformat().split('.')[0].replace(':', '-').replace('T', '-')
            log_file = os.path.join(log_root, v_name + '.'+ time_str+ '.txt')
            print 'publish_process_log_file:'
            print log_file
            cmds.scriptEditorInfo(historyFilename=log_file, writeHistory=True)

        for i in range(self.publish_process_previous, len(self.l_publish_processes)):
            process = self.l_publish_processes[i]

            # Skip some process if this is a publish for daily
            if self.publish_mode == 0 and process.module_mode != 'daily':
                continue

            if not process.proc_button.isEnabled() and process.module_mode != 'mod':
                continue

            if self.step['name'] == 'ani' and self.entity_type == 'Shot':
                if self.publish_mode == 1 and process.module_mode not in ['daily',
                                                                          'checked']:  # edt daily, for ani only currently
                    continue
            # 回上游没有使用，去除回上游提交
            # else:
            #     if self.publish_mode == 1 and process.module_mode != 'daily':  # downstream & the process belones to downstream
            #         if '/flo/' in self.publish_processes_xml and self.w_sys.comboBox_tag.currentIndex() == 1 and \
            #                 process.module_name in ['set_stereo_status', 'lay_scene_graph_xml', 'list_ani_assets',
            #                                         'copy_stereo_preview', 'copy_to_stereo']:  # tag: upstream
            #             print 'jump flo process: ', process.module_name
            #             continue

            if not process.run_process():
                self.publish_process_previous = i
                self.print_log(u"Publish停止。", txt_color=TXT_RED)
                return
            # else:
            #     # for debug mod shader missing:
            #     if self.step['name'] == 'mod' and self.asset_type in ['prp','env'] and getpass.getuser()=='likun':
            #         import maya.cmds as cmds
            #         import shutil
            #         v_name = self.version_key + self.w_ver.lineEdit_version_name.text()
            #         back_up_path = os.path.join(self.work_root,'process_backup',v_name)
            #         if not os.path.exists(back_up_path):
            #             os.makedirs(back_up_path)
            #         back_up_ma_file = os.path.join(back_up_path,(process.module_name)+'ma')
            #         cmds.file(save=True)
            #         current_file = cmds.file(q=True, sn=True)
            #         shutil.copy(current_file,back_up_ma_file)

        # A mark to show the publish is done.
        self.page_achieve = 5
        self.ui.pushButton_next.setEnabled(False)

        self.ui.progressBar_publish_process.setValue(100)
        self.print_log(u"文件提交成功!。", txt_color=TXT_WHITE)
        if self.step['name'] == 'mod':
            cmds.scriptEditorInfo(writeHistory=False)
        QtGui.QMessageBox.about(self, "Published!", u"文件提交成功!。")

        return

    def cancel_publish(self):
        self.print_log(u"删除提交的版本文件夹: " + self.version_dir, txt_color=TXT_BLUE)

        if os.path.isdir(self.version_dir):
            shutil.rmtree(self.version_dir)
        return
    # set pass or clear pass ui
    def set_check_pass_ui_rough_lay(self):
        print
        print '>> set_check_pass_ui_rough_lay <<'
        print 
        proj = self.project['name'].lower() # lrs
        # print
        # print self.shots_preview_data # [{'camera': nt.Transform(u'z99996_cam'), 'cut_in': 1001, 'overlap': 0, 'shot_info': {u'sg_cut_in': 1001, u'code': u'z99996', u'sg_sequence': {u'type': u'Sequence', u'id': 792, u'name': u'z99'}, u'sg_cut_out': 1016, u'sg_ani_cut_in': None, u'sg_ani_cut_out': None, u'type': u'Shot', u'id': 40501}, 'cut_out': 1016, 'preview': u'/mnt/work/projects/lrs/shot/z99/z99996/lay/task/maya/data/z99996.lay.rough_layout.v068.mov', 'topview': u'/mnt/work/projects/lrs/shot/z99/z99996/lay/task/maya/topview/z99996.lay.rough_layout.v068.mov', 'shot_node': nt.Shot(u'z99996_shot'), 'audio_node': nt.Audio(u'z99996_audio')}, {'camera': nt.Transform(u'z99997_cam'), 'cut_in': 1001, 'overlap': -1, 'shot_info': {u'sg_cut_in': 1001, u'code': u'z99997', u'sg_sequence': {u'type': u'Sequence', u'id': 792, u'name': u'z99'}, u'sg_cut_out': 1100, u'sg_ani_cut_in': None, u'sg_ani_cut_out': None, u'type': u'Shot', u'id': 40502}, 'cut_out': 1100, 'preview': u'/mnt/work/projects/lrs/shot/z99/z99997/lay/task/maya/data/z99997.lay.rough_layout.v068.mov', 'topview': u'/mnt/work/projects/lrs/shot/z99/z99997/lay/task/maya/topview/z99997.lay.rough_layout.v068.mov', 'shot_node': nt.Shot(u'z99997_shot'), 'audio_node': nt.Audio(u'z99997_audio')}]
        # print
        import pymel.core as pm
        shot_nodes = sorted([pm.nt.Shot(data['shot_node']) for data in self.shots_preview_data]) # [nt.Shot(u'z99996_shot'), nt.Shot(u'z99997_shot')]
        shot_names = sorted([data['shot_info']['code'] for data in self.shots_preview_data]) # [u'z99996', u'z99997']
        all_ref_nodes = [] # [nt.Reference(u'nxq_niexiaoqianRN'), nt.Reference(u'wang_wifeRN')]
        all_ref_nsps = [] # [u'nxq_niexiaoqian', u'wang_wife']
        allRefNodes = pm.ls(rf=1)
        for ref in allRefNodes:
            if ref.referenceFile():
                if ref.isLoaded():
                    ref_filename = pm.referenceQuery(ref,f=1).replace('\\','/')
                    ref_namespace = pm.referenceQuery(ref,ns=1)[1:]
                    # 此处先卡一下，是防止获取的 ref node 会有有问题的，返回的路径是空
                    if '/chr/' in ref_filename or '/prp/' in ref_filename:
                        if '_rra' not in ref.name() and ':' not in ref.name():
                            all_ref_nodes.append(ref)
                            all_ref_nsps.append(ref_namespace)
        all_ref_nodes = sorted(all_ref_nodes)
        all_ref_nsps = sorted(all_ref_nsps)
        print
        print 'shot_nodes',shot_nodes
        for sn in shot_nodes:
            print sn.name()
        print 'shot_names',shot_names
        print 'all_ref_nodes',all_ref_nodes
        print 'all_ref_nsps',all_ref_nsps
        print 
        ###############################
        # 返回场景内所有镜头内角色的数据
        QtGui.QApplication.processEvents()
        allRoughShotAssetDict = check_pass.TposeFrame().getAllRoughShotAsset(self,shot_nodes,shot_names,all_ref_nodes,all_ref_nsps) # {u'z99996': {u'wangcheng': {'rigPass': {'name': None, 'value': None}, 'lookPass': {'name': None, 'value': None}}}, u'z99997': {u'wangcheng': {'rigPass': {'name': None, 'value': None}, 'lookPass': {'name': None, 'value': None}}}}
        # 增加返回角色 shotgun 上 和 shot 的 link，新逻辑，和 ani，flo 一致，只做检查，不更新 shotgun上 的 link
        allRoughShotAssetDict = check_pass_ani_flo.TposeFrame().getSgAssetPassLink(self,allRoughShotAssetDict)

        QtGui.QApplication.processEvents()
        allRoughShots = sorted(allRoughShotAssetDict.keys()) # [u'z99996', u'z99997']
        allRoughShotAssets = []
        for ii in allRoughShots:
            if allRoughShotAssetDict[ii]:
                for iii in allRoughShotAssetDict[ii].keys():
                    # 判定，只有1级,2级角色才符合，并且勾选 sg_is_reference_one_time
                    aseet_difficulty = self.sg.find_one("Asset",[['project', 'is', self.project],
                                                                            ['code', 'is', iii.rstrip(string.digits)]],['sg_diffculty2','sg_is_reference_one_time','sg_asset_type'])
                    if aseet_difficulty:
                        if aseet_difficulty['sg_asset_type']=='chr':
                            if aseet_difficulty['sg_diffculty2']=='1' or aseet_difficulty['sg_diffculty2']=='2':
                                if aseet_difficulty['sg_is_reference_one_time']:
                                    allRoughShotAssets.append(iii) # [u'wangcheng', u'wangcheng']
        # 设置行数
        self.grp_tab.setMinimumSize(630, ((len(allRoughShots)+(len(allRoughShotAssets))*2+2)*30))

        # 循环每个镜头每个角色的数据并创建一行控件，包括：确认button，角色button，提示button，帧Linedit，修改button
        # key为角色命名空间
        
        checkButtonGroup = QtGui.QButtonGroup(self.grp_tab)
        uploadButtonGroup = QtGui.QButtonGroup(self.grp_tab)
        
        # # 给 QTabWidget 添加 Chr Tpose Checks 的 tab
        # tabWidget_sys_check.addTab(grp_tab_sa, grp.attrib['name'])
        # 依次循环 把每个角色及其对应的 pass 显示出来
        # 这里为了留余添加 ‘全部确认‘ 按钮
        buttonKeys = [None]
        # 返回一个列表
        for shot_name in sorted(allRoughShotAssetDict.keys()):
            buttonKeys.append(shot_name+'_shot')
            if allRoughShotAssetDict[shot_name]:
                for ii in sorted(allRoughShotAssetDict[shot_name].keys()):
                    # 判定，只有1级,2级角色才符合，并且勾选 sg_is_reference_one_time
                    aseet_difficulty = self.sg.find_one("Asset",[['project', 'is', self.project],
                                                                            ['code', 'is', ii.rstrip(string.digits)]],['sg_diffculty2','sg_is_reference_one_time','sg_asset_type'])
                    if aseet_difficulty:
                        if aseet_difficulty['sg_asset_type']=='chr':
                            if aseet_difficulty['sg_diffculty2']=='1' or aseet_difficulty['sg_diffculty2']=='2':
                                if aseet_difficulty['sg_is_reference_one_time']:
                                    buttonKeys.append(ii+'_asset_lookpass_'+shot_name)
                                    buttonKeys.append(ii+'_asset_rigpass_'+shot_name)
        all_button = {}
        # 以角色为key，加入字典
        for key in buttonKeys:
            shot_button,chr_button,pass_button,pass_lineEdit,sg_pass_button,sg_pass_lineEdit = check_pass.TposeFrame().aa(self.grp_tab,allRoughShotAssetDict,key,self,buttonKeys)
            if not key:
                checkAllButton = shot_button
                sure_chr_button = chr_button
            else:
                all_button[key]={}
                all_button[key]['shot_button']=shot_button
                all_button[key]['chr_button']=chr_button
                all_button[key]['pass_button']=pass_button
                all_button[key]['pass_lineEdit']=pass_lineEdit
                all_button[key]['sg_pass_button']=sg_pass_button
                all_button[key]['sg_pass_lineEdit']=sg_pass_lineEdit

        # 信号事件
        # 点击全部检查：重新检查 chr-shot-pass之间的关联，并更改界面颜色显示
        checkAllButton.clicked.connect(lambda : check_pass.TposeFrame().checkAllChrPass(all_button,self,proj,sure_chr_button))
        self.tabWidget_sys_check.setTabEnabled(0,True)
        self.tabWidget_sys_check.setCurrentIndex(0)
    def clear_check_pass_ui(self):
        print
        print '>> clear_check_pass_ui <<'
        print 
        print
        grp_tab_children = self.grp_tab.findChildren(QtGui.QWidget)
        if len(grp_tab_children) != 0:
            for gtc in grp_tab_children:
                gtc.deleteLater()
        self.tabWidget_sys_check.setTabEnabled(0,False)
        # set pass or clear pass ui
    def set_check_pass_ui_ani_flo(self):
        print
        print '>> set_check_pass_ui_ani_flo <<'
        print 
        proj = self.project['name'].lower() # lrs
        seq_name = self.entity['name'][:3] # z99
        shot_name = self.entity['name'] # z99996
        task = self.task['name'] # animation
        print 
        print 'proj >',proj
        print 'seq_name >',seq_name
        print 'shot_name >',shot_name
        print 'task >',task
        print
        import pymel.core as pm
        all_ref_nodes = [] # [nt.Reference(u'nxq_niexiaoqianRN'), nt.Reference(u'wang_wifeRN')]
        all_ref_nsps = [] # [u'nxq_niexiaoqian', u'wang_wife']
        allRefNodes = pm.ls(rf=1)
        for ref in allRefNodes:
            if ref.referenceFile():
                if ref.isLoaded():
                    ref_filename = pm.referenceQuery(ref,f=1).replace('\\','/')
                    ref_namespace = pm.referenceQuery(ref,ns=1)[1:]
                    # 此处先卡一下，是防止获取的 ref node 会有有问题的，返回的路径是空
                    if '/chr/' in ref_filename or '/prp/' in ref_filename:
                        # if '_rra' not in ref.name() and ':' not in ref.name():
                        
                            all_ref_nodes.append(ref)
                            all_ref_nsps.append(ref_namespace)
        all_ref_nodes = sorted(all_ref_nodes)
        all_ref_nsps = sorted(all_ref_nsps)
        print
        print 'all_ref_nodes',all_ref_nodes
        print 'all_ref_nsps',all_ref_nsps
        print 
        ###############################
        # 返回场景内所有角色的数据
        allRoughShotAssetDict = check_pass_ani_flo.TposeFrame().getShotAsset(self,all_ref_nodes,all_ref_nsps) # {u'z99996': {u'wangcheng': {'rigPass': {'name': None, 'value': None}, 'lookPass': {'name': None, 'value': None}}}, u'z99997': {u'wangcheng': {'rigPass': {'name': None, 'value': None}, 'lookPass': {'name': None, 'value': None}}}}
        if self.__debug:
            print("[scene allRoughShotAssetDict]",allRoughShotAssetDict)
        # 增加返回角色 shotgun 上 和 shot 的 link
        allRoughShotAssetDict = check_pass_ani_flo.TposeFrame().getSgAssetPassLink(self,allRoughShotAssetDict)
        print 
        print 'allRoughShotAssetDict >',allRoughShotAssetDict # {'z99996': {u'bazaar_pear_pits': {'sg_lookPass': None, 'rigPass': {'name': u'Incomplete_1', 'value': 1, 'rigPass_name': 'pear_state'}, 'sg_rigPass': None, 'lookPass': {'name': u'default', 'value': 0, 'lookPass_name': 'lookPass'}}, u'wang_wife': {'sg_lookPass': None, 'rigPass': {'name': 'pear_state attr not find', 'value': 'pear_state attr not find'}, 'sg_rigPass': None, 'lookPass': {'name': 'lookPass attr not find', 'value': 'lookPass attr not find'}}, u'nxq_niexiaoqian': {'sg_lookPass': 'h30_darn_hurt', 'rigPass': {'frame': '1002.0 | 1004.0', 'name': u'default | suture', 'value': '0 | 1', 'rigPass_name': 'rigPass'}, 'sg_rigPass': 'suture', 'lookPass': {'name': u'h30_darn_hurt', 'value': 6, 'lookPass_name': 'lookPass'}}}}
        print

        allRoughShots = sorted(allRoughShotAssetDict.keys()) # [u'z99996', u'z99997']
        allRoughShotAssets = []
        for ii in allRoughShots:
            if allRoughShotAssetDict[ii]:
                for iii in allRoughShotAssetDict[ii].keys():
                    # 判定，只有1级,2级角色才符合，并且勾选 sg_is_reference_one_time
                    #[NOTE]: remove rra namespace
                    asset_name = iii  
                    if ":" in iii:
                        asset_name = str(iii).split(":")[-1]
                      
                    aseet_difficulty = self.sg.find_one("Asset",[['project', 'is', self.project],
                                                                            ['code', 'is', asset_name.rstrip(string.digits)]],['sg_diffculty2','sg_is_reference_one_time','sg_asset_type'])
                    # print '>>>>>>>>>>>>>>>>>>>>>>>>>'
                    # print iii,aseet_difficulty
                    # print '>>>>>>>>>>>>>>>>>>>>>>>>>'
                    if aseet_difficulty:
                        if aseet_difficulty['sg_asset_type']=='chr':
                            if aseet_difficulty['sg_diffculty2']=='1' or aseet_difficulty['sg_diffculty2']=='2':
                                if aseet_difficulty['sg_is_reference_one_time']:
                                    allRoughShotAssets.append(iii) # [u'wangcheng', u'wangcheng']
        # print 'allRoughShotAssets >',allRoughShotAssets # [u'wang_wife', u'nxq_niexiaoqian']
        # 设置行数
        if self.__debug:
            print("allRoughShots",allRoughShots)
            print("allRoughShotAssets",allRoughShotAssets)
        self.grp_tab.setMinimumSize(630, ((len(allRoughShots)+(len(allRoughShotAssets))*2+2)*30))

        # 依次循环 把每个角色及其对应的 pass 显示出来
        # 这里为了留余添加 ‘全部确认‘ 按钮
        buttonKeys = [None]
        # 返回一个列表
        for shot_name in sorted(allRoughShotAssetDict.keys()):
            # buttonKeys.append(shot_name+'_shot')
            if allRoughShotAssetDict[shot_name]:
                for ii in sorted(allRoughShotAssetDict[shot_name].keys()):
                    # 判定，只有1级,2级角色才符合，并且勾选 sg_is_reference_one_time
                    # [NOTE]: rra remove namespaces
                    asset_name = ii
                    if ":" in ii:
                        asset_name = str(ii).split(":")[-1]
                    aseet_difficulty = self.sg.find_one("Asset",[['project', 'is', self.project],
                                                                            ['code', 'is', asset_name.rstrip(string.digits)]],['sg_diffculty2','sg_is_reference_one_time','sg_asset_type'])
                    if aseet_difficulty:
                        if aseet_difficulty['sg_asset_type']=='chr':
                            if aseet_difficulty['sg_diffculty2']=='1' or aseet_difficulty['sg_diffculty2']=='2':
                                if aseet_difficulty['sg_is_reference_one_time']:
                                    buttonKeys.append(ii+'_asset_lookpass_'+shot_name)
                                    buttonKeys.append(ii+'_asset_rigpass_'+shot_name)
        all_button = {}
        # 以角色为key，加入字典
        for key in buttonKeys:
            chr_button,file_pass_button,file_pass_lineEdit,sg_pass_button,sg_pass_lineEdit = check_pass_ani_flo.TposeFrame().aa(self.grp_tab,allRoughShotAssetDict,key,self,buttonKeys)
            if not key:
                checkAllButton = chr_button
                sure_chr_button = file_pass_button
            else:
                all_button[key]={}
                all_button[key]['chr_button']=chr_button
                all_button[key]['file_pass_button']=file_pass_button
                all_button[key]['file_pass_lineEdit']=file_pass_lineEdit
                all_button[key]['sg_pass_button']=sg_pass_button
                all_button[key]['sg_pass_lineEdit']=sg_pass_lineEdit

        # 信号事件
        # 点击全部检查：重新检查 chr-shot-pass之间的关联，并更改界面颜色显示
        checkAllButton.clicked.connect(lambda : check_pass_ani_flo.TposeFrame().checkAllChrPass(all_button,self,proj,shot_name,sure_chr_button))
        
        self.tabWidget_sys_check.setTabEnabled(0,True)
        self.tabWidget_sys_check.setCurrentIndex(0)
