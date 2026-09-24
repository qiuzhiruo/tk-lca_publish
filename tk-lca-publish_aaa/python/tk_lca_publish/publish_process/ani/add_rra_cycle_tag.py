#! -*- coding:utf-8 -*-
import os
import shutil
import traceback
import pymel.core as pm
import maya.cmds as cmds


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"在rra cycle镜头shot字段添加对应的tag"
        self.description = u"首次使用是在lrs中nxq片段鬼魂镜头使用此tag, 后续不确定是否还会使用"

        self.proj = self.dialog.project['name'].lower()
        self.shot = self.dialog.entity['name']

        self.tag_name = 'rra_cycle'

        return

    def get_tag_list_from_shotgun(self):
        shot_tags = self.dialog.sg.find_one('Shot',
                                            [['project', 'name_is', self.proj.upper()],
                                             ['code', 'is', self.shot]],
                                            ["tag_list"])

        return shot_tags['tag_list']

    def add_tag_for_rra_shot(self):
        shotEntity = self.dialog.sg.find_one('Shot', [['project', 'name_is', self.proj],
                                                      ['code', 'is', self.shot]], ['id'])
        tag_list = self.get_tag_list_from_shotgun()
        if self.tag_name not in tag_list:
            tag_list.append(self.tag_name)
            self.dialog.sg.update('Shot', shotEntity['id'], {'tag_list': tag_list})
            print('[INFO] Add tag :%s for %s' % (self.tag_name, self.shot))
        else:
            print('[INFO]: Already add rra cycle tag, skip......')

    def proceed(self):
        try:
            add_rra_cycle_tag = False

            ref_files = pm.listReferences(recursive=True)

            for r in ref_files:
                if not r.isLoaded():
                    continue
                path = str(r.path).replace('\\', '/')
                if 'cam.camera' in path:
                    continue
                if '/asset/' not in path:
                    continue

                if '/rra/' in path:
                    add_rra_cycle_tag = True
                    break

            if add_rra_cycle_tag:
                self.add_tag_for_rra_shot()
            else:
                print('[INFO]: Not contain rra asset, skip add tag......')

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
