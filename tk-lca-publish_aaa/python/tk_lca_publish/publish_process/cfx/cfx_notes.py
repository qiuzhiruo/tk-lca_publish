# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2017 Light Chaser Animation
#
# Author: chengshun
#
# Date: 2017.04
#
# Description: send notes to downstream artist and pmd
#
############################################

import os
import traceback
import shutil

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"发送notes给下游相关艺术家及pmd"
        self.description = u"发送notes给下游相关艺术家及pmd"
        return
    
    def proceed(self):
        try:
            l_lighting_task = self.dialog.sg.find_one('Task', [['project', 'name_is', self.dialog.project['name']], ['entity', 'is', self.dialog.entity], ['content', 'is', 'lighting']], ['task_assignees'])
            if l_lighting_task:
                if l_lighting_task['task_assignees']:
                    users = l_lighting_task['task_assignees'] + [{'type': 'Group', 'id': 4, 'name': 'PMD'}]
        
                    links = [self.dialog.v_info]

                    subject = u'%s 提交了 %s 的新版'%(
                        self.dialog.user['name'],
                        self.dialog.entity['name']
                    )

                    note = self.dialog.sg.create(
                        'Note',
                        {'user':self.dialog.user,
                         'content':self.dialog.description,
                         'subject':subject,
                         'addressings_to':users,
                         'project':self.dialog.project,
                         'note_links':links,
                         'sg_note_type':u'通知',
                         'tasks':[self.dialog.task]},
                    )

                    thumbnail_path = self.dialog.version_dir + '/preview/thumbnail.jpg'
                    if os.path.isfile(thumbnail_path):
                        self.dialog.sg.upload('Note', note['id'], thumbnail_path)
                    return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


