# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2019 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2019.06
#
############################################

import os
import sys
import traceback
import shutil
import subprocess

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"建立子资产版本"
        self.description = u"建立子资产版本"
        return


    def proceed(self):
        try:
            for asset in sorted(self.dialog.hyperloop.keys()):
                xml = self.dialog.hyperloop[asset]['xml']
                abc = self.dialog.hyperloop[asset]['abc']
                v_name = self.dialog.hyperloop[asset]['v_name']
                v_dir = self.dialog.hyperloop[asset]['v_dir']
                task = self.dialog.hyperloop[asset]['task']

                if sys.platform.startswith('win'):
                    v_dir =  v_dir.replace('/', '\\')
                if self.dialog.hyperloop[asset]['group'] != "shotgun":
                    d_version = {'project':self.dialog.project,
                                 'entity':self.dialog.hyperloop[asset],
                                 'sg_task': task,
                                 'code': v_name,
                                 'description': 'Hyper Loop published',
                                 'user':self.dialog.user,
                                 'sg_version_folder':{ 'local_path': v_dir, 'name':v_name, 'content_type':None, 'link_type':'local'},
                                 'sg_version_type': 'Downstream',
                                 'created_by':self.dialog.user
                                }

                    v_info = self.dialog.sg.create('Version', d_version)
                    v_preview =  v_dir + 'preview/' + v_name + '.mov'
                    if v_info and os.path.isfile(v_preview):
                        self.dialog.sg.upload('Version', v_info['id'], v_preview, "sg_uploaded_movie")

                        asset_entity = self.dialog.hyperloop[asset]
                        scene_type = self.dialog.sg.find_one("PublishedFileType", [["code", "is", "Maya Scene"]])
                        asb_type = self.dialog.sg.find_one("PublishedFileType", [["code", "is", "Maya Assembly"]])
                        version_name = v_dir.split("/")[-2]
                        assembly_file = v_dir + "assembly_definition/" + \
                                    asset_entity["code"] + ".ma"

                        maya_file = v_dir + asset_entity["code"] + ".ma"
                        
                        path_cache = maya_file.split("/projects/")[-1]


                        self.dialog.sg.create("PublishedFile", {"entity": self.dialog.hyperloop[asset],
                                                    "name": version_name.split(".v")[0],
                                                    "description": "Hyper Loop published",
                                                    "project": self.dialog.project,
                                                    "published_file_type": scene_type,

                                                    "version_number": int(float(version_name.split(".v")[-1])),
                                                    "version": v_info,
                                                    "task": v_info["sg_task"],
                                                    "code": version_name,
                                                    "path_cache": path_cache,
                                                    "path": {'local_path': maya_file,
                                                             'name': asset_entity["code"] + ".ma", \
                                                             'content_type': None, 'link_type': 'local'}})
                        self.dialog.sg.create("PublishedFile", {"entity": self.dialog.hyperloop[asset],
                                                    "name": version_name.split(".v")[0],
                                                    "description": "Hyper Loop published",
                                                    "project": self.dialog.project,
                                                    "published_file_type": asb_type,
                                                    "version_number": int(float(version_name.split(".v")[-1])),
                                                    "version": v_info,
                                                    "task": v_info["sg_task"],
                                                    "code": version_name,
                                                    "path_cache": path_cache,
                                                    "path": {'local_path': assembly_file,
                                                             'name': asset_entity["code"] + ".ma", \
                                                             'content_type': None, 'link_type': 'local'}})


            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

