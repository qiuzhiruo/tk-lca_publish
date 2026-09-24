# -*- coding: utf-8 -*-
import sys, os, shutil, platform, time, json, subprocess, csv, getpass
from xml.dom.minidom import parse
import traceback

try:
    import pymel.core as pm
    import maya.cmds as cmds
    import maya.mel as mm
except:
    pass


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"更改 scene graph xml 中 asb 的 xml路径为 Low/Hi，方便灯光部门渲染"
        self.description = u"更改 scene graph xml 中 asb 的 xml路径为 Low/Hi，方便灯光部门渲染"
        return

    def _return_cur_time(self):
        localtime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        time_fix = localtime.split(' ')[0] + '__' + localtime.split(' ')[-1].split(':')[0] + '-' + localtime.split(':')[
            -2] + '-' + localtime.split(':')[-1]
        return time_fix

    def _getSystem(self):
        system = platform.platform()
        return system

    def getCurrentSceneName(self):
        scene_file_path = cmds.file(q=True, location=True)
        if os.path.exists(scene_file_path):
            return scene_file_path
        else:
            return None

    def _writeJson(self, jsonPath, json_dict):
        with open(jsonPath, 'w') as json_file:
            json_file.write(json.dumps(json_dict, indent=4))

    def _readJson(self, jsonPath):
        with open(jsonPath) as json_file:
            json_data = json.load(json_file)
        return json_data

    def get_scene_graph_xml_path(self, scene_file_path, shotName):
        seqName = shotName[:3]
        projName = scene_file_path.split('/projects/')[-1].split('/')[0]
        versionName = os.path.splitext(os.path.basename(scene_file_path))[0]
        systemVersion = self._getSystem()
        # print scene_file_path
        if 'Window' in systemVersion:
            flo_scene_graph_xml_path = 'Z:/projects/%s/shot/%s/%s/flo/publish/%s/scene_graph_xml/%s.xml' % (
            projName, seqName, shotName, versionName, shotName)
        else:
            flo_scene_graph_xml_path = '/mnt/proj/projects/%s/shot/%s/%s/flo/publish/%s/scene_graph_xml/%s.xml' % (
            projName, seqName, shotName, versionName, shotName)

        return flo_scene_graph_xml_path

    def get_asb_cam_length_json_path(self, scene_file_path, shotName):
        seqName = shotName[:3]
        projName = scene_file_path.split('/projects/')[-1].split('/')[0]
        versionName = os.path.splitext(os.path.basename(scene_file_path))[0]
        systemVersion = self._getSystem()
        if 'Window' in systemVersion:
            asb_cam_length_json_path = 'W:/projects/%s/shot/%s/%s/flo/task/maya/asb_cam_length/asb_cam_length.json' % (
            projName, seqName, shotName)
        else:
            asb_cam_length_json_path = '/mnt/work/projects/%s/shot/%s/%s/flo/task/maya/asb_cam_length/asb_cam_length.json' % (
            projName, seqName, shotName)

        return asb_cam_length_json_path

    def proceed(self):
        try:
            systemVersion = self._getSystem()
            scene_file_path = self.getCurrentSceneName()
            shotName = scene_file_path.split('/')[-1].split('.')[0]
            # 返回 scene_graph_xml 路径
            flo_scene_graph_xml_path = self.get_scene_graph_xml_path(scene_file_path, shotName)
            print flo_scene_graph_xml_path, os.path.exists(flo_scene_graph_xml_path)
            # 备份 xml
            cur_time = self._return_cur_time()
            new_flo_scene_graph_xml_path = os.path.splitext(flo_scene_graph_xml_path)[0] + '_' + cur_time + '.xml'
            # shutil.copyfile(flo_scene_graph_xml_path,new_flo_scene_graph_xml_path)
            # 返回 asb_cam_length_json_path 路径
            asb_cam_length_json_path = self.get_asb_cam_length_json_path(scene_file_path, shotName)
            print asb_cam_length_json_path, os.path.exists(asb_cam_length_json_path)
            if os.path.exists(flo_scene_graph_xml_path) and os.path.exists(asb_cam_length_json_path):
                shutil.copyfile(flo_scene_graph_xml_path, new_flo_scene_graph_xml_path)
                asb_cam_length_dict = self._readJson(asb_cam_length_json_path)
                # 重新组装字典
                new_asb_cam_length_dict = {}
                print asb_cam_length_dict
                for hi_asb, hi_asb_xml in asb_cam_length_dict['Hi'].items():
                    print hi_asb, hi_asb_xml
                    hi_asb_xml_win_path = 'Z:/projects/' + hi_asb_xml.split('/projects/')[-1]
                    hi_asb_xml_linux_path = '/mnt/proj/projects/' + hi_asb_xml.split('/projects/')[-1]
                    new_asb_cam_length_dict[hi_asb[:-3].replace(':', '.')] = hi_asb_xml_linux_path
                for low_asb, low_asb_xml in asb_cam_length_dict['Low'].items():
                    print low_asb, low_asb_xml
                    low_asb_xml_win_path = 'Z:/projects/' + low_asb_xml.split('/projects/')[-1]
                    low_asb_xml_linux_path = '/mnt/proj/projects/' + low_asb_xml.split('/projects/')[-1]
                    if os.path.exists(low_asb_xml_win_path) or os.path.exists(low_asb_xml_linux_path):
                        new_asb_cam_length_dict[low_asb[:-3].replace(':', '.')] = low_asb_xml_linux_path
                print new_asb_cam_length_dict
                # 修改 scene_graph_xml 
                DOMTree = parse(flo_scene_graph_xml_path)
                collection = DOMTree.documentElement
                for a in collection.getElementsByTagName("instance"):
                    # print 'bbbbbbb'
                    if len(a.attributes.items()) == 4:
                        # print 'aaaaa'
                        if a.attributes.item(2).value in new_asb_cam_length_dict.keys():
                            # print a.attributes.item(2)
                            a.attributes.item(3).value = new_asb_cam_length_dict[a.attributes.item(2).value]
                            prp_name_low = \
                            new_asb_cam_length_dict[a.attributes.item(2).value].split('/')[-1].split('.')[0]
                            prp_name = prp_name_low.split('_low')[0]
                            a.attributes.item(2).value = a.attributes.item(2).value.replace(prp_name, prp_name_low)
                with open(flo_scene_graph_xml_path, 'w') as f:
                    DOMTree.writexml(f, encoding='utf-8')
            return ''
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
