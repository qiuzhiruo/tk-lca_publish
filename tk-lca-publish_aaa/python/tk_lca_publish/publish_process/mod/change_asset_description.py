# -*- coding:utf-8 -*-
import traceback

from production.shotgun_connection import Connection
import maya.cmds as cmds
import os
import getpass
from proc.function_running_time import record_time


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"修改资产描述"
        self.description = u"修改资产描述"
        return

    @record_time(__file__)
    def proceed(self):
        sg = Connection('get_project_info').get_sg()

        asset = self.dialog.sg.find_one("Asset", [['project', 'is', self.dialog.project], ['code', 'is', self.dialog.entity['name']]], ['sg_diffculty2', 'sg_asset_type'])
        user = self.dialog.sg.find_one('HumanUser', [['login', 'is', getpass.getuser()]], ['login', 'groups'])
        if not user:
            return ''
        user_grps = [grp['name'] for grp in user['groups']]

        if asset['sg_asset_type'].lower() not in ['prp', 'env'] or 'MOD' not in user_grps and 'PLE' not in user_grps and 'PMD' not in user_grps:
            return ''

        if self.dialog.asset_description:
            asset_name = os.path.basename(cmds.file(sceneName=True, q=True)).split('.')[0]

            proj_name = self.dialog.project['name'].lower()


            proj = sg.find_one('Project', [['name', 'is', proj_name]], [])

            asset_info = sg.find_one('Asset', [['project', 'is', proj], ['code', 'is', asset_name]], ['description'])
            sg.update('Asset', asset_info['id'], {'description': self.dialog.asset_description})
            self.send_note()


        return ''

    def send_note(self):
        user = self.dialog.user
        pmd_user = self.dialog.sg.find("HumanUser", [["groups", "name_is", 'PMD'], ['sg_status_list','is','act'], ['login', 'is_not', 'yuzhou']], ["id", "name"])
        noteDict={'project':self.dialog.project,
                'note_links':[self.dialog.entity],
                'content': u'{}资产描述已被{}修改.'.format(self.dialog.entity['name'], getpass.getuser()),
                'addressings_to':pmd_user,
                'sg_note_type':u'通知',
                'subject':"资产描述被修改",
                'user':user}

        self.dialog.sg.create('Note',noteDict)

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
