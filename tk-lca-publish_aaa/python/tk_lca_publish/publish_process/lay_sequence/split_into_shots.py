# -*- coding:utf-8 -*-

import traceback
import sys
import os
import json
import shutil
import pprint

import tank
import pymel.core as pm

import production.mayautils.animation as manim
import lay.lca_camera_sequencer.functions as functions_cs;reload(functions_cs)
import lay.lca_camera_loader.functions as functions_cl;reload(functions_cl)
import lay.lca_camera_loader.camera_export_funcs as functions_ce;reload(functions_ce)
import lay.lca_mash_process.offset_mash_network as omn;reload(omn)
import lay.lca_mash_process.functions as mash_func;reload(mash_func)
import stereo.commonFunc as cf;reload(cf)
import ani.lca_pass_manager.pass_manager_model as pmm


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拆分输出各镜头工程文件并输出anim相机。"
        self.description = u"偏移动画到镜头起始帧，拆分成独立的镜头工程文件并输出anim相机，供下游环节按正常镜头流程制作。"
        return

    def proceed(self):
        try:
            for data in self.dialog.shots_preview_data:
                data['version_file'] = os.path.join(data['version_dir'], data['version_name']+'.ma')
                shot_node = pm.nt.Shot(data['shot_node'])
                data['offset'] = data['cut_in'] - shot_node.getSequenceStartTime()

                # move anim curves to shot cut_in
                curves = functions_cs.get_anim_curves()
                print data['version_file']
                pprint.pprint(data)
                print 'curve'
                # pprint.pprint(curves)
                functions_cs.move_anim_curves(curves, data['offset'])
                # 设置MASH的偏移时间, 解决MASH传递到动画后效果不对的问题
                omn.add_time_offset_to_mash_node(offset_value=int(-data['offset']))
                # 设置 instancer inheritsTransform 0
                mash_func.fix_mash_instancer_inherits_transform()

                # mark kept lay purple circles, export anim cam & delete shot cam
                shot_name = data['shot_info']['code']
                cam_name = shot_name + '_cam'
                lay_rig = cam_name + '_rig:global_ctrl'

                constraints_objs = functions_ce.get_constraints_objs(lay_rig)
                print '** constraints_objs:'
                print str(constraints_objs) + '\n'
                functions_ce.bake_constraints2(constraints_objs, shot_name, data['cut_in'], data['cut_out'], self.dialog)

                # purples_kept = functions_ce.bake_constraints(constraints_objs, data['cut_in'], data['cut_out'])
                # functions_ce.add_keepIt_attr(purples_kept, functions_ce.PURPLE_ATTR)

                data['project'] = self.dialog.project['name']
                new_cam_v, log, _ = functions_ce.export_anim_cam(self.dialog.sg, data, lay_rig)    # export & delete shot cam, return: e.g. 'v001' and str
                print 'new_cam_v', new_cam_v
                functions_ce.add_attr(new_cam_v, lay_rig)                               # add 'cameraVersion' attr to the lay rig
                self.dialog.print_log(log)
                # self.create_new_cam(shot_name)

                # write_asset_uuid_to_json
                self.write_asset_uuid_to_json(data['version_dir'])

                # save as the shot ma file
                pm.saveAs(data['version_file'])

                # move anim curves back & delete unused attrs, prepare for the next shot's saving
                curves = functions_cs.get_anim_curves()
                functions_cs.move_anim_curves(curves, -data['offset'])
                # 还原MASH的时间偏移, 以继续拆分镜头
                omn.set_mash_waiter_time_offset(offset_value=0)
                # functions_ce.del_keepIt_attr(purples_kept, functions_ce.PURPLE_ATTR)

                # if backup file exists, replace it (for color id)
                print 'back up layout ma'
                origin_lay_file = data['version_file'] + '.origin'
                if os.path.exists(origin_lay_file):
                    os.remove(origin_lay_file)
                shutil.copyfile(data['version_file'], origin_lay_file)

            return ""

        except:
            return traceback.format_exc()

    def write_asset_uuid_to_json(self, version_dir):
        extra_data_dir_shot = os.path.join(version_dir, 'extra_data')
        if not os.path.exists(extra_data_dir_shot):
            try:
                os.makedirs(extra_data_dir_shot)
            except OSError as e:
                import errno
                if e.errno != errno.EEXIST:
                    raise
        pmm_cm = pmm.CharacterModel()
        asset_uuid_result = pmm_cm.convert_uuid_pass_info_to_json(register_all_asset=True)
        asset_uuid_json = os.path.join(extra_data_dir_shot, 'assets_uuid.json.origin').replace('\\', '/')

        self._writeJson(asset_uuid_json, asset_uuid_result)

    def _writeJson(self, jsonPath, json_dict):
        with open(jsonPath, 'w') as json_file:
            json_file.write(json.dumps(json_dict, indent=4))

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description



