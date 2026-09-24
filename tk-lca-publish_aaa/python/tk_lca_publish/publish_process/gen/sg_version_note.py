# -*- coding:utf-8 -*-
# import sys
# sys.path.append("/home/haojia/Work/SoftWare/pycharm-2022.1.3/debug-eggs/pydevd-pycharm.egg_FILES/")
# import pydevd_pycharm
# import pydevd
# pydevd.stoptrace()
# pydevd_pycharm.settrace('localhost', port=5555, stdoutToServer=True, stderrToServer=True)
import sys
# TOOL_ROOT = '/mnt/utility/'
# sys.path.append(TOOL_ROOT + '/toolset/lib/production')
from production.shotgun_connection import Connection
from production.notification_rules import recipients

sg = Connection('get_shot_info').get_sg()

class StdProcess():
    def __init__(self,dialog):
        self.dialog = dialog
        self.process_name = u'发送note(mod-srf-cfx)'
        self.description = u'MOD或CFX更新时发送note给SRF，SRF更新时发送给CFX'

    def proceed(self):

        step_name = self.dialog.step['name']#mod
        if step_name not in ['mod','srf','cfx']:
            return ''
        proj_entity = sg.find_one('Asset', [['project', 'name_is', self.dialog.project['name']]], ['project'])['project'] #TSM
        t = recipients.TaskRecipients()
        receive = []
        pmd_users = sg.find('Group', [['code', 'is', 'pmd']],
                                  ['code', 'users', 'addressings_to', 'sg_ticket_type', 'sg_priority'])[0]
        receive.append(pmd_users)
        if step_name =='mod' or step_name == 'cfx':
            if step_name=='mod':
                import pymel.core as pm
                work_path = pm.sceneName().replace('\\', '/')
                if '/asb/' in work_path:
                    self.dialog.d_assets_info={}
                    self.dialog.d_assets_info[self.dialog.entity['name']]={'version_name':self.dialog.version_name}
                    print 'initial asb d_assets_info...'
            if step_name == 'cfx':
                self.dialog.d_assets_info={}
                self.dialog.d_assets_info[self.dialog.entity['name']]={'version_name':self.dialog.version_name}
            for asset_name in self.dialog.d_assets_info.keys():#['fuyong_caocao']
                version_name = self.dialog.d_assets_info[asset_name]['version_name']#asset_name
                sg_entity = sg.find_one('Asset',
                                        [['project', 'is', proj_entity], ['code', 'is', asset_name]],
                                        ['id', 'entity'])
                content = u'请注意：' + asset_name + u'进行了' + step_name.upper() + u'版本更新,更新至' + version_name
                task = sg.find_one('Task', [['project', 'is', proj_entity], ['entity', 'is', sg_entity],
                                            ['content', 'is', 'surfacing']], ['id', 'type'])
                if not task:
                    return ''
                assignees_info = sg.find_one('Task', [['project', 'is', proj_entity],
                                                      ['entity', 'is', sg_entity],
                                                      ['content', 'is', 'surfacing']],
                                             ['task_assignees'])
                if assignees_info:
                    task_assignees = assignees_info['task_assignees']
                    for assignee_info in task_assignees:
                        assignee_name = assignee_info['name']
                        assignee = sg.find('HumanUser', [['name', 'is', assignee_name]], ['code', 'users'])[0]
                        if assignee:
                            receive.append(assignee)
                leads = t.get_dept_lead('srf')
                for lead in leads:
                    receive.append(sg.find('HumanUser', [['login', 'is', lead]],['code', 'users', 'addressings_to', 'sg_ticket_type', 'sg_priority'])[0])

        if step_name == 'srf' or step_name == 'mod':
            asset_name = self.dialog.entity['name']
            version_name = self.dialog.version_name
            sg_entity = sg.find_one('Asset',
                                    [['project', 'is', proj_entity], ['code', 'is', asset_name]],
                                    ['id', 'entity'])
            if step_name == 'mod':
                cloth_task = sg.find_one('Task',[['entity','is',sg_entity],['content','is','cloth']],['id','sg_status_list'])
                if not cloth_task:
                    return ''
                if cloth_task['sg_status_list'] == 'omt':
                    return ''
            content = u'请注意：' + asset_name + u'进行了' + step_name.upper() + u'版本更新,更新至' + version_name
            task = sg.find_one('Task', [['project', 'is', proj_entity], ['entity', 'is', sg_entity],
                                        ['content', 'in', ['hair', 'cloth']]], ['id', 'type'])
            if not task:
                return ''
            assignees_infos = sg.find('Task', [['project', 'is', proj_entity],
                                                  ['entity', 'is', sg_entity],
                                                  ['content', 'in', ['hair','cloth']]],
                                         ['task_assignees'])
            for assignees_info in assignees_infos:
                task_assignees = assignees_info['task_assignees']
                for assignee_info in task_assignees:
                    assignee_name = assignee_info['name']
                    assignee = sg.find('HumanUser', [['name', 'is', assignee_name]], ['code', 'users'])[0]
                    if assignee:
                        receive.append(assignee)
            leads = t.get_dept_lead('cfx')
            for lead in leads:
                receive.append(sg.find('HumanUser', [['login', 'is', lead]],['code', 'users', 'addressings_to', 'sg_ticket_type', 'sg_priority'])[0])

        n = sg.create('Note',
                      {
                          'project': proj_entity,
                          'note_links': [self.dialog.entity],
                          'content': content,
                          'sg_note_type': u'通知',
                          'addressings_to': receive,
                          'tasks': [task]
                      }
                      )
        return ''

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description





