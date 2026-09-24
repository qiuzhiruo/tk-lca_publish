# -*- coding:utf-8 -*-

import os
import traceback
import math
import shutil
import datetime
import pymel.core as pm

import sys

sys.path.append('/'.join(os.path.dirname(__file__).replace('\\', '/').split('/')[:-1]) + '/gen')
import sgXml_parser as sgxml

reload(sgxml)
import production.shotgun_connection as shotgun_connection

reload(shotgun_connection)
sg = shotgun_connection.Connection('get_project_info').get_sg()
from proc import shorten_shot_xml
import ani.lca_new_scene_graph_xml.new_xml_submit as xml_submit

reload(xml_submit)
sys.path.append('{}/toolset/applications/katana_v2/Scripts/auto_set'.format(os.getenv('LC_UTILITY')))
import asd_muster_submit


#
# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"输出Scene Graph Xml 文件提到农场。"
        self.description = u"Scene Graph Xml文件可以用来将abc文件组合拼装成资产和场景。"
        return

    def get_chunk(self, f_start, f_end, sample):
        l_f = range(f_start, f_end + 1)
        c_cnt = len(l_f)
        if sample < 2:
            l_frames = [l_f[0]]
        elif sample == 2:
            l_frames = [l_f[0], l_f[-1]]
        else:
            l_frames = [l_f[0], l_f[-1]]
            step = float(len(l_f)) / (sample - 1)
            for i in range(sample - 2):
                l_frames.append(l_f[int((i + 1) * step)])

        l_frames = list(set(l_frames))
        l_frames.sort()
        return l_frames

    def proceed(self):
        try:
            project_name = self.dialog.project['name']
            work_scene_path = pm.sceneName()
            scene_name = os.path.basename(pm.sceneName())
            scene_path = self.dialog.version_dir + '/' + scene_name
            scene_path = scene_path.replace('\\', '/').replace('Z:/', '/mnt/proj/')
            # for ani check output scene graph xml
            if self.dialog.publish_mode != 2 and '.ani.animation.' in scene_name:
                scene_path = work_scene_path
            shot_name = self.dialog.entity['name']
            # export scene graph xml
            if os.path.isdir(self.dialog.version_dir + '/scene_graph_xml'):
                shutil.rmtree(self.dialog.version_dir + '/scene_graph_xml')

            os.makedirs(self.dialog.version_dir + '/scene_graph_xml')
            version_name = os.path.basename(self.dialog.version_dir)

            # [NOTE]:出xml提农场
            # print(self.dialog.ui.comboBox_publish_mode.currentText()) #预提交(Checked)
            # both ani and flo need to re-export xml
            xmlJob = dict(project_name=project_name, shot_name=shot_name,
                          scene_path=scene_path, xml_path=self.dialog.version_dir + '/scene_graph_xml')

            # job name: '[NewSceneGraph]%s-%s by %s
            job_ids = xml_submit.main([xmlJob])
            print ('Submitted Xml Task: %s ,jobid:%s', shot_name, str(job_ids))

            # start xiaos for set after flo
            if 'flo.final_layout.' in scene_name:
                jobid = asd_muster_submit.send_xiaos_job(project_name, shot_name, job_ids[0],
                                                         job_name=('[xiao_s-flo] %s.%s' % (project_name, scene_name)))
                print('Submitted Set Task: [xiao_s-flo].%s ,jobid:%s', scene_name, str(jobid))

            # [NOTE]:在sg标记tag
            version_entity = sg.find_one('Version',
                                         [['project', 'name_is', project_name], ['code', 'is', version_name]],
                                         ['tag_list', 'id', 'code'])

            if 'xml_submitted' not in version_entity['tag_list']:
                version_entity['tag_list'].append('xml_submitted')
                sg.update("Version", version_entity["id"], {"tag_list": version_entity['tag_list']})
                print ("Update Tag(xml_submitted) to " + version_name)
            ''' 
            # create both long and short xml, for current project
            scene_xml_path = self.dialog.version_dir + '/scene_graph_xml/' + self.dialog.entity['name'] + '.xml'
            xml_long = self.dialog.version_dir + '/scene_graph_xml/' + self.dialog.entity['name'] + '.long.xml'
            xml_short = self.dialog.version_dir + '/scene_graph_xml/' + self.dialog.entity['name'] + '.short.xml'

            if not pm.objExists('|assets'):
                return ""

            # Query cam info
            if not pm.objExists(self.dialog.entity['name'] + u"_cam"):
                return u"没有找到相机:" + self.dialog.entity['name'] + u"_cam"
            
            shot_info = self.dialog.sg.find_one('Shot', [['id', 'is', self.dialog.entity['id']]], ['sg_motion_samples', 'sg_cam_anim', 'sg_cut_in', 'sg_cut_out'])
            if not shot_info['sg_motion_samples']:
                sample = 3
            else:
                sample = shot_info['sg_motion_samples']

            f_start = int(shot_info['sg_cut_in'])
            f_end = int(shot_info['sg_cut_out'])
            
            if shot_info['sg_cam_anim'] and shot_info['sg_cam_anim'] == 'static':
                l_frames = [f_start]
            else:
                l_frames = self.get_chunk(f_start, f_end, sample)

                       
            # export layout xml file
            xml = sgxml.SgXmlParser()

            if self.dialog.step['name'] in ['flo']:
                xml.exportXml(pm.PyNode('|assets'), xml_long, cam=self.dialog.entity['name'] + u"_cam", l_frames=l_frames, skip_unload = False)
            else:
                xml.exportXml(pm.PyNode('|assets'), xml_long, cam=self.dialog.entity['name'] + u"_cam", l_frames=l_frames, skip_unload = True)

            shorten_shot_xml.main(xml_long, xml_short)

            # pick which one?
            lgt_versions = self.dialog.sg.find('Version', [['entity', 'is', self.dialog.entity], ['code', 'contains', '.lgt.lighting.'], ['created_at', 'less_than', datetime.datetime(2016, 4, 6, 15, 0)]])
            if len(lgt_versions) > 0:
                shutil.copyfile(xml_long, scene_xml_path)
            else:
                shutil.copyfile(xml_short, scene_xml_path)
                
            '''

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
