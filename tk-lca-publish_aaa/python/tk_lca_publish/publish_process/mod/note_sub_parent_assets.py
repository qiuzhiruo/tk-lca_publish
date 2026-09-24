# -*- coding:utf-8 -*-
import traceback
import sys
# TOOL_ROOT = '/mnt/utility/'
# sys.path.append(TOOL_ROOT + '/toolset/lib/production')
from production.shotgun_connection import Connection
from proc.function_running_time import record_time
sg = Connection('get_shot_info').get_sg()

class StdProcess():

    def __init__(self,dialog):
        self.dialog = dialog
        self.process_name = u'发送note（有关联的父/子资产的角色改变）'
        self.description = u'当角色资产更新时，检查其有无父子资产，若有，发送note给相应的制作人员、制片与总监。'
        return

    @record_time(__file__)
    def proceed(self):
        try:
            err_info = ""

            asset_name = self.dialog.d_assets_info.keys()[0]
            proj_name = self.dialog.project['name'].upper()

            # check if chr:
            asset_type = self.dialog.d_assets_info[asset_name]['type']
            if asset_type != 'chr':
                return ''

            # check if has sub/parents assets:
            filters = [['project', 'name_is', proj_name], ['code', 'is', asset_name]]
            ass = sg.find('Asset', filters, ['assets','parents'])

            parents_list = []
            for parent in ass[0]['parents']:
                parents_list.append(parent['name'])

            subassets_list = []
            for sub in ass[0]['assets']:
                subassets_list.append(sub['name'])

            if parents_list is None and subassets_list is None:
                return ''

            # notes:
            proj_entity = sg.find_one('Asset', [['project', 'name_is', self.dialog.project['name']]], ['project'])['project']

            related_list = parents_list + subassets_list
            for name in related_list:

                sg_entity = sg.find_one('Asset',
                                        [['project', 'name_is', proj_name], ['code', 'is', name]],
                                        ['id', 'entity'])
                task = sg.find_one('Task', [['project', 'name_is', proj_name], ['entity', 'is', sg_entity],
                                            ['content', 'is', 'model']], ['id', 'type'])

                receive = []
                pmd_grp = sg.find('Group', [['code', 'is', 'pmd']],
                                  ['code', 'users', 'addressings_to', 'sg_ticket_type', 'sg_priority'])[0]
                receive.append(pmd_grp)
                jiangli = sg.find('HumanUser', [['login', 'is', "lujiangli"]],['code', 'users', 'addressings_to', 'sg_ticket_type', 'sg_priority'])[0]
                receive.append(jiangli)
                task_assignees = sg.find_one('Task', [['project', 'name_is', proj_name],
                                                      ['entity', 'is', sg_entity],
                                                      ['content', 'is', 'model']],
                                             ['task_assignees'])['task_assignees']
                for assignee_info in task_assignees:
                    assignee_name = assignee_info['name']
                    assignee = sg.find('HumanUser',[['name','is',assignee_name]],['code','users'])[0]
                    receive.append(assignee)

                if name in subassets_list:
                    content = u'请注意，该资产的父资产: %s有了版本更新，具体内容：%s。'% (asset_name,self.dialog.description)
                else:
                    content = u'请注意，该资产的子资产: %s有了版本更新，具体内容：%s。'% (asset_name,self.dialog.description)

                n = sg.create('Note',
                              {
                                  'project':proj_entity,
                                  'content':content,
                                  'sg_note_type':u'通知',
                                  'addressings_to':receive,
                                  'tasks':[task]
                              }
                              )
            return err_info

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
