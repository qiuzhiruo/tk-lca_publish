# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
# Description: Format and send publish emial
#
############################################

import traceback
import getpass
import sys
import time
import os
import xml.dom.minidom as minidom

from sgtk.platform.qt import QtCore, QtGui
# from mail.mail import SendMail
import json, platform

try:
    import platform

    # if platform.system().lower() == 'windows':
    #     sys.path.insert(0, 'U:/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/publish_check/ani/')
    # elif platform.system().lower() == 'linux':
    #     sys.path.insert(0, '/mnt/utility/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/publish_check/ani/')
    import ani.check_tpose_frame as check_tpose_frame
except:
    pass


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"发送Publish邮件和锁版本信号"
        self.description = u"整理格式并发送Publish邮件。以及各种publish后的处理:给服务器发送锁版本文件夹信号。"
        return

    def write_cache(self, server):
        if self.dialog.entity['type'] == 'Shot':
            shot_name = self.dialog.entity['name']
            show_name = self.dialog.project['name'].lower()
            v_file = server + 'trash/log/1984/Version_Caches/' + show_name + '.txt'

            # if os.path.isfile(v_file):
            with open(v_file, 'a') as f:
                mov1 = server + 'projects/' + show_name + '/shot/' + shot_name[:3] + '/' + shot_name + '/' + \
                       self.dialog.step[
                           'name'] + '/publish/' + self.dialog.version_name + '/preview/' + self.dialog.version_name + '.mov'
                mov2 = server + 'projects/' + show_name + '/shot/' + shot_name[:3] + '/' + shot_name + '/' + \
                       self.dialog.step[
                           'name'] + '/publish/' + self.dialog.version_name + '/preview/' + self.dialog.version_name + '.stereo.mov'
                jpgl = server + 'projects/' + show_name + '/shot/' + shot_name[:3] + '/' + shot_name + '/' + \
                       self.dialog.step['name'] + '/publish/' + self.dialog.version_name + '/jpg/L'
                jpgr = server + 'projects/' + show_name + '/shot/' + shot_name[:3] + '/' + shot_name + '/' + \
                       self.dialog.step['name'] + '/publish/' + self.dialog.version_name + '/jpg/R'

                f.write(mov1.replace(server, '/mnt/proj/') + '\n')
                if os.path.isfile(mov2):
                    f.write(mov2.replace(server, '/mnt/proj/') + '\n')
                if os.path.isdir(jpgl):
                    f.write(jpgl.replace(server, '/mnt/proj/') + '\n')
                if os.path.isdir(jpgr):
                    f.write(jpgr.replace(server, '/mnt/proj/') + '\n')
            # os.chmod(v_file, 0o777)

    def writeToJson(self, jsonPath, dataDict):
        if os.path.exists(jsonPath):
            os.system("chmod 777 %s" % jsonPath)
        with open(jsonPath, 'w') as json_data:
            json_data.write(json.dumps(dataDict, indent=4))
        os.system("chmod 777 %s" % jsonPath)

    def readJson(self, jsonPath):
        os.system("chmod 777 %s" % jsonPath)
        with open(jsonPath) as json_data:
            dataJson = json.load(json_data)
            return dataJson
        os.system("chmod 777 %s" % jsonPath)

    def mkdirTpose(self, tposeDirPath):
        if not os.path.exists(tposeDirPath):
            os.mkdir(tposeDirPath)
            os.system("chmod 777 %s" % tposeDirPath)
        if os.path.exists(tposeDirPath):
            os.system("chmod 777 %s" % tposeDirPath)

    def proceed(self):
        try:
            # Query skipped checks
            server = self.dialog.version_dir.split('projects')[0]
            self.write_cache(server)
            # l_skipped_chks = []
            # if not hasattr(self.dialog, 'auto_pub') or not self.dialog.auto_pub:
            #     for publish_check in self.dialog.l_publish_checks:
            #         if not publish_check.get_skip_chk() :
            #             l_skipped_chks.append(publish_check.get_module_name())
            # else:
            #     l_skipped_chks = ['AUTO PUB SKIP ALL CHECKS']
            #
            # sg_page = 'http://shotgun.zhuiguang.com/detail/Version/' + str(self.dialog.v_info['id'])
            # sg_page2 = 'http://shotgun-internet.zhuiguang.com:401/detail/Version/' + str(self.dialog.v_info['id'])
            #
            # mail_subject = '[' + self.dialog.project['name'].upper()+ '] [Publish] '+ self.dialog.version_name +' by '+ getpass.getuser()
            # mail_body =  u'<html xmlns="http://www.w3.org/1999/xhtml">\n'
            # mail_body += '<head>\n'
            # mail_body += '<meta content="text/html; charset=utf-8" http-equiv="Content-Type" />\n'
            # #mail_body += '<title>Untitled 1</title>\n'
            # mail_body += '</head>\n'
            # mail_body += '<body style="font-family: Calibri">\n'
            #
            # mail_body += '<table style="width: 800px; background-color: #999999; ">\n'
            # mail_body += '    <tr style="background-color: #666666; font-size: large; color: #FF9900; text-align: center;">\n'
            # mail_body += '        <td colspan="2">'+mail_subject+'</td>\n'
            # mail_body += '    </tr>\n'
            # mail_body += '    <tr style="background-color: #666666;color:#DDDDDD;">\n'
            # mail_body += '        <td>'+self.dialog.entity['type']+'</td>\n'
            # mail_body += '        <td>'+self.dialog.entity['name']+'</td>\n'
            # mail_body += '    </tr>\n'
            # mail_body += '    <tr style="background-color: #666666;color:#DDDDDD;">\n'
            # mail_body += u'        <td>任务</td>\n'
            # mail_body += '        <td>'+self.dialog.task['name']+'</td>\n'
            # mail_body += '    </tr>\n'
            # mail_body += '    <tr style="background-color: #666666;color:#DDDDDD;">\n'
            # mail_body += u'        <td>设计师</td>\n'
            # mail_body += '        <td>'+ getpass.getuser() +'</td>\n'
            # mail_body += '    </tr>\n'
            # mail_body += '    <tr style="background-color: #666666;color:#DDDDDD;">\n'
            # mail_body += u'        <td>版本描述</td>\n'
            #
            # desc_txt = self.dialog.description
            #
            # if desc_txt.__class__.__name__ == 'QString':
            #     desc_txt = str(desc_txt.toUtf8())
            # elif desc_txt.__class__.__name__ == 'str':
            #     desc_txt=desc_txt.decode('utf-8')
            #
            # mail_body += '        <td>'+ desc_txt +'</td>\n'
            # mail_body += '    </tr>\n'
            # mail_body += '    <tr style="background-color: #666666;color:#DDDDDD;">\n'
            # mail_body += u'        <td>跳过的检查</td>\n'
            # mail_body += '        <td>'+ ', '.join(l_skipped_chks) +'</td>\n'
            # mail_body += '    </tr>\n'
            # mail_body += '    <tr style="background-color: #666666;color:#DDDDDD;">\n'
            # mail_body += u'        <td>公司内Shotgun页面(In LCA)</td>\n'
            # mail_body += '        <td><a href="'+sg_page+'">'+sg_page+'</a></td>\n'
            # mail_body += '    </tr>\n'
            # mail_body += '    <tr style="background-color: #666666;color:#DDDDDD;">\n'
            # mail_body += u'        <td>外网Shotgun页面(Internet)</td>\n'
            # mail_body += '        <td><a href="'+sg_page2+'">'+sg_page2+'</a></td>\n'
            # mail_body += '    </tr>\n'
            # mail_body += '    <tr style="background-color: #666666;color:#DDDDDD;">\n'
            # mail_body += u'        <td>版本文件夹</td>\n'
            # mail_body += '        <td>'+self.dialog.version_dir+'</td>\n'
            # mail_body += '    </tr>\n'
            # mail_body += '    <tr style="background-color: #666666;color:#DDDDDD;">\n'
            # mail_body += u'        <td>版本预览</td>\n'
            # mail_body += '        <td>'+self.dialog.v_preview+'</td>\n'
            # mail_body += '    </tr>\n'
            # mail_body += '</table>\n'
            #
            # mail_body += '</body>\n'
            # mail_body += '</html>\n'
            # Stop sending mails since it take too much time to connect GMail server then failed
            # SendMail(self.dialog.l_recipients, mail_subject, mail_body.encode('utf-8'), sub_type="html")
            # Send a singal to lock the version folder
            try:
                v_file = server + 'trash/versions/' + self.dialog.version_name + '.txt'
                with open(v_file, 'wb') as f:
                    f.write(self.dialog.version_dir.replace(server, '/mnt/proj/'))
            except:
                print 'Failed to Send a singal to lock the version folder.'

            # Time cost
            self.dialog.sg.update('Version', self.dialog.v_info['id'],
                                  {'sg_publish_time': int(time.time() - self.dialog.start_time)})

            # Version log
            try:
                doc = minidom.Document()
                root = doc.createElement('Version')
                doc.appendChild(root)
                tag = doc.createElement('Tag')
                root.appendChild(tag)
                tag.setAttribute('value', self.dialog.version_tag)
                tag = doc.createElement('Name')
                root.appendChild(tag)
                tag.setAttribute('value', self.dialog.version_name)

                if self.dialog.step['name'] == 'ani':
                    dataDict = {}
                    # 获取所有角色的visb ctrl及其对应的lca属性值
                    allTposeData = check_tpose_frame.TposeFrame().getAllVisibCtrl()

                    _project = self.dialog.project['name'].lower()
                    _seq = self.dialog.entity['name'][:3]
                    _shots = self.dialog.entity['name']
                    for keyy in allTposeData.keys():
                        dataDict[allTposeData[keyy]['new_name_space']] = {}
                        dataDict[allTposeData[keyy]['new_name_space']]['TposeFrame'] = allTposeData[keyy][
                            'lca_chr_frame']
                        check_tpose_frame.TposeFrame().setVisbCtrlAttr(allTposeData[keyy]['new_name_space'],
                                                                       nameSpace=True)

                    if platform.system().lower() == 'windows':
                        tposeDirPath = 'W:/projects/%s/shot/%s/%s/ani/task/maya/chr_tpose_data' % (
                        _project, _seq, _shots)
                        jsonPath = os.path.join(tposeDirPath, 'chr_tpose.json')

                        self.mkdirTpose(tposeDirPath)
                        self.writeToJson(jsonPath, dataDict)

                        for chrName in dataDict.keys():
                            tag = doc.createElement('Tpose')
                            root.appendChild(tag)
                            tag.setAttribute('chrName', chrName)
                            tag.setAttribute('frame', dataDict[chrName]['TposeFrame'])
                    elif platform.system().lower() == 'linux':
                        tposeDirPath = '/mnt/work/projects/%s/shot/%s/%s/ani/task/maya/chr_tpose_data' % (
                        _project, _seq, _shots)
                        jsonPath = os.path.join(tposeDirPath, 'chr_tpose.json')

                        self.mkdirTpose(tposeDirPath)
                        self.writeToJson(jsonPath, dataDict)

                        for chrName in dataDict.keys():
                            tag = doc.createElement('Tpose')
                            root.appendChild(tag)
                            tag.setAttribute('chrName', chrName)
                            tag.setAttribute('frame', dataDict[chrName]['TposeFrame'])

                f = open(self.dialog.version_dir + '/version_log.xml', 'w')
                f.write(doc.toprettyxml(indent='\t', encoding="utf-8"))
                f.close()
            except:
                print 'Failed to write the version log.'

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
