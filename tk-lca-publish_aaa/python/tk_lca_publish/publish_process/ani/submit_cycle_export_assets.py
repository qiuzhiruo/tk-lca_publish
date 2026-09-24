# -*- coding:utf-8 -*-
import os
import json
import pymel.core as pm


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"替换为动画rig,并对好位置"
        self.description = u"rig_replace 可以让动画rig 根据偏移数值 对好动画"
        self.step = self.dialog.step['name']
        return

    def proceed(self):
        ref_path_cycle = False
        ref_nodes = pm.listReferences()
        for ref in ref_nodes:
            if '/CycleCrd/' in ref.path:
                ref_path_cycle = True
                break
        if not ref_path_cycle:
            print(ref_path_cycle)
            return ''

        import production.python_job as python_job
        ma_file = str(pm.sceneName())
        maya_file = self.dialog.version_dir + '/' + os.path.basename(ma_file)
        maya_file = maya_file.replace('\\', '/').replace('Z:/', '/mnt/proj/')
        script_file = '/mnt/utility/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/publish_process/ani/export_ani_assets_xml.py'
        # script_file = '/mnt/work/shome/yuke/gitlab_projects/sgtk/tk-lca-publish/python/tk_lca_publish/publish_process/ani/export_ani_assets_xml.py'
        proj = self.dialog.project['name']
        python_exe = '{}/linked_tools/lca_rez/launchers/{}/linux/mayapy'.format('/mnt/utility',
                                                                                proj.lower())

        import platform
        system = platform.system()
        cycle_shot_list = self.get_cycle_shot_list(ref_nodes)
        cycle_shot_name_main = os.path.basename(ma_file).split('.')[0]
        cycle_json_path = ''
        for shot_name in cycle_shot_list:
            if system == 'Windows':
                cycle_json_path = 'W:/aniProjects/{0}/CycleCrd/{1}/{2}/use_in_{3}.json'.format(proj, shot_name[:3],
                                                                                               shot_name,
                                                                                               cycle_shot_name_main)

            if system == 'Linux':
                cycle_json_path = '/mnt/work/aniProjects/{0}/CycleCrd/{1}/{2}/use_in_{3}.json'.format(proj,
                                                                                                      shot_name[:3],
                                                                                                      shot_name,
                                                                                                      cycle_shot_name_main)

            if not os.path.isfile(cycle_json_path):
                data = {
                    "shot": {},
                }
                with open(cycle_json_path, 'w') as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)

        from production.farm_ip import LcaFarmIPManage
        job_name_prefix = '[EXPORT ANI ASSETS XML {0} BY {1} {2}]'.format(self.dialog.entity['name'],
                                                                          os.getenv('USER', 'unKnown'),
                                                                          self.dialog.version_dir.split('/')[-1])
        args = '"{}" "{}"'.format(maya_file, proj.lower())
        print(proj)
        job_id = python_job.send_job(script_file, proj=proj, priority=8000, step=self.step.upper(),
                                     python_exe=python_exe, job_name_prefix=job_name_prefix,
                                     url=LcaFarmIPManage().MASTERCACHE, args=args, msg=None)
        import production.shotgun_connection as shotgun_connection
        reload(shotgun_connection)
        file_name = os.path.basename(ma_file)

        sg = shotgun_connection.Connection('get_project_info').get_sg()
        print(os.path.basename(file_name))
        version_entity = sg.find_one('Version',
                                     [['project', 'name_is', proj.lower()],
                                      ['code', 'is', file_name[:-3]]],
                                     ['tag_list', 'id', 'code'])
        if 'ani_assets_xml_completed' in version_entity['tag_list']:
            version_entity['tag_list'].remove('ani_assets_xml_completed')

        version_entity['tag_list'].append('ani_assets_xml_submitted')
        sg.update("Version", version_entity["id"], {"tag_list": version_entity['tag_list']})

        script_file_sub = '/mnt/utility/toolset/tools/render/muster_auto_cache/submit_version.py'
        python_exe = '{}/linked_tools/lca_rez/launchers/{}/linux/mayapy'.format('/mnt/utility',
                                                                                proj.lower())
        job_name_prefix_sub = '[Export Cycle Cache {0} By {1} {2}]'.format(self.dialog.entity['name'],
                                                                           os.getenv('USER', 'unKnown'),
                                                                           os.path.basename(ma_file))
        maya_version_dir = self.dialog.version_dir.replace('\\', '/').replace('Z:/', '/mnt/proj/')
        args = '"{}" "{}" "{}" "{}"'.format(proj.lower(), self.step.lower(), maya_version_dir, 'True')

        python_job.send_job(script_file_sub, proj=proj, priority=8000, step=self.step.upper(), python_exe=python_exe,
                            depends=job_id,
                            job_name_prefix=job_name_prefix_sub, url=LcaFarmIPManage().MASTERCACHE, args=args, msg=None)

        return ''

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description

    def get_cycle_shot_list(self, ref_nodes):
        cycle_crd_shot_list = []
        for ref in ref_nodes:
            if '/CycleCrd/' in ref.path:
                cycle_shot_name = ref.path.split('CycleCrd/')[-1].split('/')[1]
                if cycle_shot_name not in cycle_crd_shot_list:
                    cycle_crd_shot_list.append(cycle_shot_name)

        return cycle_crd_shot_list
