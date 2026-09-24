# -*- coding:utf-8 -*-

import os
import traceback
import shutil


def main(dialog):
    info = dialog.sg.find_one('Task', [['project', 'name_is', dialog.project['name'].lower()],
                                            ['id', 'is', dialog.task['id']]], ['sg_status_list'])
    if not info: return ""

    links = []
    links.append(dialog.entity)
    # subject = u'%s 提交了 %s 的新版动画' % (
    #     dialog.user['name'],
    #     dialog.entity['name']
    # )
    subject = u'通知 Mod PC：%s 有新版本 相机 生成' % dialog.entity['name']

    users = ''
    mod_pc = dialog.sg.find(
            'HumanUser',
            [{'filter_operator': 'all',
                'filters': [['department_sg_coordinator_departments','name_contains','Model'],['sg_status_list','is','act']]}]
        )
    mod_td = dialog.sg.find(
            'HumanUser',
            [{'filter_operator': 'all',
                'filters': [['department_sg_tds_departments','name_contains','Model'],['sg_status_list','is','act']]}]
        )
    mod_grp = dialog.sg.find(
            'HumanUser',
            [{'filter_operator': 'all',
                'filters': [['department','name_contains','Model'],['sg_status_list','is','act']]}]
        )
    users = mod_pc+mod_td+mod_grp

    note = dialog.sg.create(
        'Note',
        {'user': dialog.user,
            'content': dialog.description,
            'subject': subject,
            'addressings_to': users,
            'project': dialog.project,
            'note_links': links,
            'sg_note_type': u'通知',
            'tasks': [dialog.task]},
    )

    return ""