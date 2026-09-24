# -*- coding:utf-8 -*-
__author__ = 'xiangquan'

import os
import sys
import getpass
import time
import datetime
import xml.dom.minidom as minidom
import traceback

from sgtk.platform.qt import QtCore, QtGui
from production.notification_rules import downstream_tasks as downstream_tasks;reload(downstream_tasks)

DEFAULT_SENDER_LOGIN = 'keer'

# All publish process will use StdProcess as the class name.
class StdProcess():


    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"发送Publish邮件和锁版本信号"
        self.description = u"整理格式并发送Publish邮件。以及各种publish后的处理:给服务器发送锁版本文件夹信号。"
        return


    def send_message(self, entities):
        """
        entities: a shot string list, e.g. ['d60010', 'd60020']
        """
        
        filters = [['project', 'name_is', self.dialog.project['name'].upper()],['code', 'is', self.dialog.version_name]]
        #filters = [['id', 'is', audio_event['entity']['id']]]
        fields = ['sg_task', 'user', 'description', 'code', 'sg_version_type', 'created_at', 'sg_version_type', 'tag_list']
        version = self.dialog.sg.find_one("Version", filters, fields)
        
        if not (version and version['sg_task']):
            return
        
        if version['user'] and version['user']['type'] == 'HumanUser':
            sender_sg = self.dialog.sg.find_one('HumanUser', [['id', 'is', version['user']['id']]], ['sg_chinese', 'name', 'login'])
        else:
            sender_sg = self.dialog.sg.find_one('HumanUser', [['login', 'is', DEFAULT_SENDER_LOGIN]], ['sg_chinese', 'name', 'login'])
        
        if sender_sg:
            # Note to l_recipients
            receivers = []
            for recipient in self.dialog.l_recipients:
                recipient = recipient.split('@')[0]
                self.dialog.print_log('recipient: ' + recipient)
                receiver = self.dialog.sg.find_one('HumanUser', [['login', 'is', recipient]], ['sg_chinese', 'name', 'login', 'id'])
                if receiver is None:
                    receiver = self.dialog.sg.find_one('Group', [['code', 'is', recipient]], ['id', 'code'])
                self.dialog.print_log('receiver: ' + str(receiver))
                receivers.append(receiver)
            
            grp_msg = ''
            if self.dialog.confirmed_by_pc:
                grp_msg += u'****Notice****\n本次publish的镜头时长更新需要lgt pc确认。\n\n'
            
            grp_msg += u'以下音频有更新：\n'
            for entity in entities:
                grp_msg += entity + '\n'
            grp_msg += u'\n版本描述为：\n' + self.dialog.description
            mail_subject = '[' + self.dialog.project['name'].upper()+ '][Publish]'+ self.dialog.version_name
            shot_entities = self.dialog.sg.find('Shot', [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'in',entities ] ], ['code'])
            
            self.dialog.print_log('sender_sg: ' + str(sender_sg['name']))
            self.dialog.print_log('self.dialog.project: ' + str(self.dialog.project))
            self.dialog.print_log(grp_msg)
            self.dialog.print_log('subject: ' + str(mail_subject))
            self.dialog.print_log('addressings_to: ' + str(receivers))
            
            note = self.dialog.sg.create('Note', {'user': sender_sg, 'project': self.dialog.project, 
                                                                       'content': grp_msg, 'subject': mail_subject, 
                                                                       'sg_note_type': u'通知', 'addressings_to': receivers ,
                                                                       'note_links': shot_entities,  'tasks': [self.dialog.task]})
        else:
            self.dialog.print_log('Failed to find sender entity.')


    def proceed(self):
        try:
            shots = [os.path.split(wav_file)[1].split('.')[0].split('_')[0] for wav_file in self.dialog.wav_files]
            self.send_message(shots)

            # Send a singal to lock the version folder
            server = self.dialog.version_dir.split('projects')[0]
            linux_version_dir = self.dialog.version_dir.replace(server, '/mnt/proj/')
            v_file = server + 'trash/versions/' + self.dialog.version_name + '.txt'
            f = open(v_file, 'w')
            f.write(linux_version_dir)
            f.close()

            # Time cost
            self.dialog.sg.update('Version', self.dialog.v_info['id'], {'sg_publish_time': int(time.time() - self.dialog.start_time)})

            # Version log
            try:
                doc = minidom.Document()
                root = doc.createElement('Version')
                doc.appendChild(root)
                tag = doc.createElement('Tag')
                root.appendChild(tag)
                tag.setAttribute('value', self.dialog.version_tag)

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


