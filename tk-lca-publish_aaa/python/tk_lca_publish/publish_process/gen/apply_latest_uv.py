# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2014.05
#
# Description: Apply the latest UV from the srf task area
#
############################################
#
# Edited by Zhang Shirui
#
# Date: 2015.07
#
# Description: Add apply latest shader from the srf task area
#
############################################

import os
import traceback
import pymel.core as pm
import maya.cmds as cmds
import maya.api.OpenMaya as om
import shutil
import datetime
# All publish process will use StdProcess as the class name.


import sys
import os
import srf.push_shader.shader_funcs as shader_funcs
reload(shader_funcs)
import srf.push_shader.create_shaders as create_shaders
reload(create_shaders)

if sys.platform.startswith(u'win'):
    proj_path = u"Z:/projects"
else:
    proj_path = u"/mnt/proj/projects"

def get_file_info():
    proj = ''
    asset  = ''
    asset_type = ''
    if cmds.file(query=True, sceneName=True) == "":
        return proj, asset, asset_type

    projects = os.listdir(proj_path)
    file_path = cmds.file(query=True, sceneName=True)
    file_path_split = file_path.split('projects')[-1]
    asset_path = file_path_split.replace('\\', '/')
    split_ = asset_path.split('/')
    if len(split_) > 5 and split_[1] in projects:
        if split_[1] in projects:
            proj = split_[1]
            asset_type = split_[3]
            asset = split_[4]
    return proj, asset, asset_type

def check_srf_version(proj, asset, asset_type):
    version_list = []
    srf_file_path = 'Z:/projects/{}/asset/{}/{}/srf/publish'.format(proj, asset_type, asset)
    for p in os.listdir(srf_file_path):
        if '.srf.surfacing.v' in p and 'v000' not in p:
            version_list.append(p[-3:])
    if not version_list:
        return False
    return True

def apply_mod_shader_main():
    proj, asset, asset_type = get_file_info()
    if not proj:
        return ""
    # 判断材质版本
    if check_srf_version(proj, asset, asset_type):
        return ""
    shader_output_path, model_shader_mat = shader_funcs.get_model_shader_data(proj, asset)
    if shader_output_path and model_shader_mat:
        # 重新按照一个模型一个材质球的方式推送模型材质球
        create_shaders.assign_model_shader(asset, shader_output_path, model_shader_mat)
    # 重新连接透明属性
    shader_funcs.add_transparent_attr()

def get_scene_vertex_total():
    total = 0

    meshes = cmds.ls(type='mesh', long=True) or []

    for mesh in meshes:
        # 排除建模历史里的 intermediate shape
        if cmds.getAttr(mesh + ".intermediateObject"):
            continue

        total += cmds.polyEvaluate(mesh, vertex=True)

    return total

def add_shader_string(asset_name, asset_type):
    node = "master"
    attr = "pushShaderState"

    # 添加属性
    if not cmds.attributeQuery(attr, node=node, exists=True):
        cmds.addAttr(node, longName=attr, dataType="string")

    # 生成时间戳
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # 拼接数据
    value = (
        "asset={0};"
        "type={1};"
        "state=default;"
        "time={2}"
    ).format(asset_name, asset_type, timestamp)

    # 如果之前锁定过，先解锁
    if cmds.getAttr(node + "." + attr, lock=True):
        cmds.setAttr(node + "." + attr, lock=False)

    # 写入属性
    cmds.setAttr(
        node + "." + attr,
        value,
        type="string"
    )

    # 隐藏并锁定
    cmds.setAttr(
        node + "." + attr,
        keyable=False,
        channelBox=False
    )

    print(value)

def add_shader_string_no_srf_ver(asset_name, asset_type):
    node = "master"
    attr = "pushShaderState"

    # 添加属性
    if not cmds.attributeQuery(attr, node=node, exists=True):
        cmds.addAttr(node, longName=attr, dataType="string")

    # 生成时间戳
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # 拼接数据
    value = (
        "asset={0};"
        "type={1};"
        "state=no_srf_ver;"
        "time={2}"
    ).format(asset_name, asset_type, timestamp)

    # 如果之前锁定过，先解锁
    if cmds.getAttr(node + "." + attr, lock=True):
        cmds.setAttr(node + "." + attr, lock=False)

    # 写入属性
    cmds.setAttr(
        node + "." + attr,
        value,
        type="string"
    )

    # 隐藏并锁定
    cmds.setAttr(
        node + "." + attr,
        keyable=False,
        channelBox=False
    )

    print(value)

class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"加载最新的UV和Surfacing"
        self.description = u"将当前资产在srf task区的UV和shader文件，尽可能的加载到当前模型上。"
        return

    @staticmethod
    def clean_blendweight_invalid_data():
        # Clean inf/-inf values on blendweight
        l_sc = pm.ls(type='skinCluster')
        for sc in l_sc:
            for elem in sc.bw.elements():
                if 'inf' in str(pm.getAttr(sc.name() + '.' + elem)):
                    pm.setAttr(sc.name() + '.' + elem, 0.0)

    def apply_srf_shader(self):
        asset = self.dialog.entity['name']
        proj = self.dialog.project['name']

        import srf.push_shader.push_shader as sps
        reload(sps)
        sps.push_shader(proj,asset,add_pass_only=0,force=True)
        self.dialog.print_log('Apply srf pass shader for '+proj+':'+asset)

    def proceed(self):
        if cmds.referenceQuery('|master', isNodeReferenced=True):
            #print "Will not assign uv to referenced rig."
            return ''
        try:
            pm.lockNode("defaultTextureList1", lock=False, lockUnpublished=False)
            pm.lockNode('initialShadingGroup', lock=False, lockUnpublished=False)
            pm.lockNode('renderPartition', lock=False, lockUnpublished=False)
            pm.lockNode('initialParticleSE', lock=False, lockUnpublished=False)
            pm.lockNode('defaultLegacyAssetGlobals', lock=False, lockUnpublished=False)
        except:
            pass
        # Skip reference, apply lastest UV
        self.dialog.ori_shading_info = {}
        self.dialog.new_shaders = []

        dept = self.dialog.step['name']

        current_file_path = cmds.file(q=True, sceneName=True)
        # W:/projects/wuk/asset/chr/arena_yao_l/rig/task/maya/arena_yao_l.rig.rigging_body/arena_yao_l.rig.rigging_body.ma
        if "rigging" in current_file_path:
            try:
                apply_mod_shader_main()
            except Exception as e:
                try:
                    asset_name = self.dialog.entity['name'].lower()
                    from production.feishu_utils import lca_feishu
                    lca_feishu.main(to_user_list=['xiaoyu2', 'zejie', 'zhenlin', 'pangxuan', 'wangqi2'],
                                    title=u'获取模型材质 角色 {} 失败 ! 错误信息： '.format(asset_name),
                                    message='file_path: \n {} \n error message: {}'.format(current_file_path, str(e)),
                                    app='warning')
                except:
                    pass
            proj, asset, asset_type = get_file_info()
            if not check_srf_version(proj, asset, asset_type):
                add_shader_string_no_srf_ver(asset, asset_type)
                return ""

        srf_publish_dir = self.dialog.publish_root.replace('/' + dept + '/', '/srf/').replace('\\', '/')
        if not os.path.isdir(srf_publish_dir):
            # 改用模型材质
            current_file_path = cmds.file(q=True, sceneName=True)
            # W:/projects/wuk/asset/chr/arena_yao_l/rig/task/maya/arena_yao_l.rig.rigging_body/arena_yao_l.rig.rigging_body.ma
            # if "rigging" in current_file_path:
            #     mod_tex_path = current_file_path.replace('rig.rigging', 'mod.model').replace('rig', 'mod').replace('W:', 'Z:').replace('task/maya', 'publish').split('.mod.model')[0] + '.mod.model/maya_shaders/body_texture.mb'
            #     rig_tex_path = current_file_path.replace(current_file_path.split('/')[-1], 'body_texture.mb')
            #     if cmds.objExists(mod_tex_path):
            #         if '/chr/' or '/crd/' in current_file_path: # or '/prp/'
            #             if os.path.exists(mod_tex_path):
            #                 shutil.copyfile(mod_tex_path, rig_tex_path)
            #                 import transfer_mod_material
            #                 transfer_mod_material.import_mat()
            # return ""

        latest_uv = ''
        uv_file = srf_publish_dir.replace('Z:/', 'W:/').replace('/proj/', '/work/').replace('/publish',
                                                                                            '/task') + '/katana/scene_graph_xml/' + \
                  self.dialog.entity['name'] + '.uv'
        if os.path.isfile(uv_file):
            latest_uv = uv_file
        else:
            #print 'not find uv file : ', uv_file
            pass

        if latest_uv != '':
            # clean skin
            self.clean_blendweight_invalid_data()
            # apply uv
            #print "Apply the latest uv:", latest_uv
            from proc import apply_uv
            # mod user srf uv
            if self.dialog.step['name'] != 'mod':
                apply_uv.apply(latest_uv, check=0)

            elif self.dialog.step['name'] == 'mod':
                if self.dialog.w_publish_file.comboBox_copyuv_mode.currentIndex() == 0:
                    #print "Apply the latest uv: comboBox_copyuv_mode.currentIndex() ", latest_uv
                    apply_uv.apply(latest_uv, check=0)
        else:
            pass
            #print 'Find no valid uv to apply.'

        # import srf push shader
        # current_file_path = cmds.file(query=True, sceneName=True)
        # import srf push shader
        task_name = self.dialog.task['name'].lower()
        current_file_path = cmds.file(q=True, sceneName=True)
        print(' ============================ push rig shader ============================')
        print(current_file_path)


        if "rigging" in current_file_path:
            listdirTemp = cmds.file(q=True, sn=True)
            listdir = normal_path(listdirTemp)
            if '/chr/' in listdir:
                chr_index = listdir.index('chr/') + len('chr/')
                assert_type = 'chr'
            elif '/prp/' in listdir:
                chr_index = listdir.index('prp/') + len('prp/')
                assert_type = 'prp'
            elif '/crd/' in listdir:
                chr_index = listdir.index('crd/') + len('crd/')
                assert_type = 'crd'
            else:
                assert_type = ''
            proj, asset, assert_type = get_file_info()

            if assert_type == 'chr':

                try:
                    apply_uv_file(get_uv_file_path())
                except Exception as e:
                    from production.feishu_utils import lca_feishu
                    lca_feishu.main(to_user_list=['xiaoyu2', 'zejie', 'zhenlin', 'pangxuan', 'wangqi2'],
                                    title=u'apply_uv UV拉取失败 !',
                                    message='file_path: \n {} \n error message: {}'.format(current_file_path, str(e)),
                                    app='warning')

                print("latest uv is applied, push shader")
                import srf.push_shader.push_rig_shader as sp_new
                reload(sp_new)
                # get project, version, chr_id
                asset_name = self.dialog.entity['name'].lower()
                #if self.dialog.entity.has_key('sg_chinese'):
                #    asset_chinese_name = self.dialog.entity['sg_chinese']
                task_name = self.dialog.task['name'].lower()  # asset_ct = self.dialog.asset_type
                proj = self.dialog.project['name'].lower()
                projInfo = self.dialog.project['name'].upper()
                vers = self.dialog.version_name
                version = int(vers.split('.')[-1][1:])
                version_info = str(vers.split('.')[-1])

                try:
                    if task_name == 'rigging':
                        asset_ct = 'rigging'
                        try:
                            add_shader_string(asset_name, asset_ct)
                        except:
                            pass
                        return_value = sp_new.push_rig_shader(with_param=True, asset=asset_name, proj=proj, type=asset_ct, add_pass_only=False, muggle=False)
                        process_return_value(return_value, current_file_path)

                    elif task_name == 'rigging_layout':
                        asset_ct = 'rigging_layout'
                        try:
                            add_shader_string(asset_name, asset_ct)
                        except:
                            pass
                        return_value = sp_new.push_rig_shader(with_param=True, asset=asset_name, proj=proj, type=asset_ct, add_pass_only=True, muggle=False)
                        process_return_value(return_value, current_file_path)

                    elif task_name == 'rigging_blocking':
                        asset_ct = 'rigging_blocking'
                        try:
                            add_shader_string(asset_name, asset_ct)
                        except:
                            pass
                        return_value = sp_new.push_rig_shader(with_param=True, asset=asset_name, proj=proj, type=asset_ct, add_pass_only=True, muggle=False)
                        process_return_value(return_value, current_file_path)

                    elif task_name == 'rigging_lite':
                        asset_ct = 'rigging_lite'
                        try:
                            add_shader_string(asset_name, asset_ct)
                        except:
                            pass
                        return_value = sp_new.push_rig_shader(with_param=True, asset=asset_name, proj=proj, type=asset_ct, add_pass_only=False, muggle=False)
                        process_return_value(return_value, current_file_path)

                    elif task_name == 'rigging_box':
                        asset_ct = 'rigging_box'
                        try:
                            add_shader_string(asset_name, asset_ct)
                        except:
                            pass
                        asset_ct = 'rigging_box'
                        print('!============================================== passing push shader ============================================== ! asset_ct is not included', asset_ct)

                    else:
                        asset_ct = 'nonetype'
                        try:
                            add_shader_string(asset_name, asset_ct)
                        except:
                            pass
                        asset_ct = ''
                        print('!============================================== passing push shader ============================================== ! asset_ct is not included',asset_ct)

                except Exception as e:
                    try:
                        from production.feishu_utils import lca_feishu
                        lca_feishu.main(to_user_list=['xiaoyu2', 'zejie', 'zhenlin', 'pangxuan', 'wangqi2'],
                                        title=u'apply_uv 角色 {} srf拉取失败 ! 错误信息： '.format(asset_name),
                                        message='file_path: \n {} \n error message: {}'.format(current_file_path, str(e)),
                                        app='warning')
                    except:
                        pass

            elif assert_type == 'prp':

                vertex_count = get_scene_vertex_total()
                print vertex_count
                if vertex_count > 900000:
                    return ''


                try:
                    apply_uv_file(get_uv_file_path())

                except Exception as e:
                    from production.feishu_utils import lca_feishu
                    lca_feishu.main(to_user_list=['xiaoyu2', 'zejie', 'zhenlin', 'pangxuan', 'wangqi2'],
                                    title=u'apply_uv UV拉取失败 !',
                                    message='file_path: \n {} \n error message: {}'.format(current_file_path, str(e)),
                                    app='warning')

                print("latest uv is applied, push shader")
                import srf.push_shader.push_rig_shader as sp_new
                reload(sp_new)
                # get project, version, chr_id
                asset_ct = 'rigging'
                asset_name = self.dialog.entity['name'].lower()
                #if self.dialog.entity.has_key('sg_chinese'):
                #    asset_chinese_name = self.dialog.entity['sg_chinese']
                task_name = self.dialog.task['name'].lower()  # asset_ct = self.dialog.asset_type
                proj = self.dialog.project['name'].lower()
                projInfo = self.dialog.project['name'].upper()
                vers = self.dialog.version_name
                version = int(vers.split('.')[-1][1:])
                version_info = str(vers.split('.')[-1])

                try:
                    try:
                        add_shader_string(asset_name, asset_ct)
                    except:
                        pass
                    return_value = sp_new.push_rig_shader(with_param=True, asset=asset_name, proj=proj, type=asset_ct)
                    process_return_value(return_value, current_file_path)
                except Exception as e:
                    from production.feishu_utils import lca_feishu
                    lca_feishu.main(to_user_list=['xiaoyu2', 'zejie', 'zhenlin', 'pangxuan', 'wangqi2'],
                                    title=u'apply_uv 道具 {} srf拉取失败 ! 错误信息： '.format(asset_name),
                                    message = 'file_path: \n {} \n error message: {}'.format(current_file_path, str(e)),
                                    app='warning')

            elif assert_type == 'crd':
                try:
                    cmds.lockNode('initialShadingGroup', lock=False, lockUnpublished=False)
                    cmds.lockNode('renderPartition', lock=False, lockUnpublished=False)
                    cmds.lockNode('initialParticleSE', lock=False, lockUnpublished=False)
                except:
                    pass

                try:
                    apply_uv_file(get_uv_file_path())

                except Exception as e:
                    from production.feishu_utils import lca_feishu
                    lca_feishu.main(to_user_list = ['xiaoyu2', 'zejie', 'zhenlin', 'pangxuan', 'wangqi2'],
                                    title = u'apply_uv UV拉取失败 !',
                                    message = 'file_path: \n {} \n error message: {}'.format(current_file_path, str(e)),
                                    app = 'warning')

                try:
                    print("latest uv is applied, push shader")
                    import srf.push_shader.push_rig_shader as sp_new
                    reload(sp_new)
                    # get project, version, chr_id
                    asset_ct = 'crd'
                    asset_name = self.dialog.entity['name'].lower()
                    #if self.dialog.entity.has_key('sg_chinese'):
                    #    asset_chinese_name = self.dialog.entity['sg_chinese']
                    task_name = self.dialog.task['name'].lower()  # asset_ct = self.dialog.asset_type
                    proj = self.dialog.project['name'].lower()
                    projInfo = self.dialog.project['name'].upper()
                    vers = self.dialog.version_name
                    version = int(vers.split('.')[-1][1:])
                    version_info = str(vers.split('.')[-1])

                    try:
                        add_shader_string(asset_name, asset_ct)
                    except:
                        pass
                    return_value = sp_new.push_rig_shader(with_param=True, asset=asset_name, proj=proj, type=asset_ct)
                    process_return_value(return_value, current_file_path)
                except Exception as e:
                    from production.feishu_utils import lca_feishu
                    lca_feishu.main(to_user_list = ['xiaoyu2', 'zejie', 'zhenlin', 'pangxuan', 'wangqi2'],
                                    title = u'crd push_rig_shader失败 !',
                                    message = 'file_path: \n {} \n error message: {}'.format(current_file_path, str(e)),
                                    app = 'warning')

        try:
            if self.dialog.step['name'] != 'mod':
               pass
               #self.apply_srf_shader()
            return ''
        except Exception as e:
            asset = self.dialog.entity['name']
            proj = self.dialog.project['name']
            from production.feishu_utils import lca_feishu
            lca_feishu.main(to_user_list = ['xiaoyu2', 'zejie', 'aokang', 'liangyue'],
                            title = u'apply_srf_shader 模型材质拉取失败 !',
                            message = 'chr_name: {}, \n project: {} \n error message: {}'.format(asset, proj, str(e)),
                            app = 'warning')
        cmds.error('======================================= stop srf file ================================================')
        return ''

        # push_rig_shader is current only method to push shader
        # try:
        #     # Skip reference
        #     self.dialog.ori_shading_info = {}
        #     self.dialog.new_shaders = []
        #
        #     dept = self.dialog.step['name']
        #     srf_publish_dir = self.dialog.publish_root.replace('/'+dept+'/', '/srf/').replace('\\','/')
        #     if not os.path.isdir(srf_publish_dir):
        #         return ""
        #
        #
        #     latest_uv = ''
        #     uv_file = srf_publish_dir.replace('Z:/','W:/').replace('/proj/','/work/').replace('/publish','/task')+'/katana/scene_graph_xml/'+ self.dialog.entity['name'] +'.uv'
        #     if os.path.isfile(uv_file):
        #         latest_uv = uv_file
        #     else:
        #         print 'not find uv file : ',uv_file
        #
        #     if latest_uv != '':
        #         # clean skin
        #         self.clean_blendweight_invalid_data()
        #         # apply uv
        #         print "Apply the latest uv:", latest_uv
        #         from proc import apply_uv
        #         # mod user srf uv
        #         if self.dialog.step['name'] != 'mod':
        #             apply_uv.apply(latest_uv,check=0)
        #
        #         elif self.dialog.step['name'] == 'mod':
        #             if self.dialog.w_publish_file.comboBox_copyuv_mode.currentIndex() == 0:
        #                 print "Apply the latest uv: comboBox_copyuv_mode.currentIndex() ", latest_uv
        #                 apply_uv.apply(latest_uv,check=0)
        #
        #         try:
        #             if self.dialog.step['name'] != 'mod':
        #                 self.apply_srf_shader()
        #         except:
        #             self.dialog.print_log('Apply srf shader failed.'+traceback.format_exc())
        #
        #     else:
        #         print 'Find no valid uv to apply.'
        #     return ''
        #
        # except:
        #     return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description



def replace_uvmap_folliclemap(mapname='lcarigmap'):
    """copy uvset map1 to lcarigmap

    Returns:
        TYPE: Description
    """
    folliclelist = []
    allFollicle = cmds.ls(type="follicle")
    for follicle in allFollicle:
        inputSurface = '{0}.inputMesh'.format(follicle)
        ConnectionList = cmds.listConnections(inputSurface, shapes=1, scn=1) or []
        if ConnectionList:
            origin_set = cmds.getAttr('%s.mapSetName' % follicle)
            if origin_set.startswith('lca'):
                continue
            cmds.setAttr("%s.mapSetName" % follicle, l=False)
            cmds.setAttr('%s.mapSetName' % follicle, mapname, type="string")
            folliclelist.append(follicle)

    allMesh = cmds.ls(type="mesh")
    orig = []
    for mesh in allMesh:
        cs = cmds.listConnections(mesh + '.inMesh', s=1, d=0)
        if not cs:
            allUvSet = cmds.polyUVSet(mesh, query=True, allUVSets=1)
            if allUvSet and mapname not in allUvSet:
                try:
                    print 'Copy uv set map1 to', mapname, 'in mesh', mesh
                    cmds.polyUVSet(mesh, copy=True, newUVSet=mapname, uvSet='map1')
                    orig.append(mesh)
                except:
                    traceback.print_exc()


class find_source():
    def __init__(self, node_name):
        self.l_processed_nodes = []
        self.l_terminals = []
        self.l_history_nodes = [n.name() for n in pm.listHistory(node_name)]
        # try to find orig attribute,if not go recursion
        if self.find_orig_attr(node_name):
            return
        else:
            self.find_in_mesh(node_name)
        return

    def find_in_mesh(self, node_name):
        self.l_processed_nodes.append(node_name)
        l_in_meshes = []
        l_cons = pm.listConnections(node_name, d=False, s=True, c=True, p=True)

        for con in l_cons:
            att_type = pm.getAttr(con[0], type=True)
            if att_type == 'mesh':
                src_name = con[1].split('.')[0]
                l_in_meshes.append(src_name)

        l_in_meshes = list(set(l_in_meshes))
        if len(l_in_meshes) == 0 and node_name in self.l_history_nodes:
            self.l_terminals.append(node_name)
        else:
            for src_name in l_in_meshes:
                if not src_name in self.l_processed_nodes:
                    self.find_in_mesh(src_name)

        return

    def find_orig_attr(self, node_name):
        shape_node = pm.PyNode(node_name)
        if shape_node.hasAttr('origShape'):
            tmp_terminals_list = shape_node.getAttr('origShape').split(';')
            for tmp_terminals in tmp_terminals_list:
                if pm.objExists(tmp_terminals):
                    self.l_terminals.append(tmp_terminals)
            return True
        else:
            return False


def __add_skip_tag(skip_mesh):
    for m in skip_mesh:
        if cmds.attributeQuery('baduvTag', node=m, exists=True):
            continue
        try:
            if not m.endswith('ShapeOrig'):
                print 'Add baduvTag attribute to', m
                cmds.addAttr(m, ln='baduvTag', at='bool')
        except:
            traceback.print_exc()


def parse_uv_file(uv_file):
    f = open(uv_file, 'r')
    l_lines = f.readlines()
    f.close()

    d_meshes = {}
    line_mark = 'mesh_info'
    mesh_name = ''
    uv_set = ''
    for i, line in enumerate(l_lines):
        if line.startswith('//'):
            continue  # Skip comments
        # print i, line_mark, line[:-1]
        tokens = line[:-1].split(' ')
        if line_mark == 'mesh_info':
            mesh_name = tokens[0]
            uv_set = ''
            d_meshes[mesh_name] = {'m_v_cnt': tokens[1], 'm_e_cnt': tokens[2], 'm_f_cnt': tokens[3], 'UV': {}}
            if i + 1 < len(l_lines):
                if l_lines[i + 1][0] != '|':
                    line_mark = 'uv_u'

        elif line_mark == 'uv_u':
            if len(tokens) == 1 and tokens[0] != '':
                uv_set = tokens[0]
                d_meshes[mesh_name]['UV'][uv_set] = {'u': [], 'v': [], 'uv_cnt': [], 'uv_ids': []}
            else:
                if uv_set == '':
                    uv_set = 'map1'
                d_meshes[mesh_name]['UV'][uv_set] = {'u': [float(t) for t in tokens if t != ''], 'v': [], 'uv_cnt': [],
                                                     'uv_ids': []}
                line_mark = 'uv_v'

        elif line_mark == 'uv_v':
            d_meshes[mesh_name]['UV'][uv_set]['v'] = [float(t) for t in tokens if t != '']
            line_mark = 'uv_cnt'

        elif line_mark == 'uv_cnt':
            d_meshes[mesh_name]['UV'][uv_set]['uv_cnt'] = [int(t) for t in tokens if t != '']
            line_mark = 'uv_ids'

        elif line_mark == 'uv_ids':
            d_meshes[mesh_name]['UV'][uv_set]['uv_ids'] = [int(t) for t in tokens if t != '']
            if i + 1 < len(l_lines):
                if l_lines[i + 1][0] == '|':
                    line_mark = 'mesh_info'
                else:
                    uv_set = ''
                    line_mark = 'uv_u'

    return d_meshes


def apply_uv_file(uv_file, check=True, import_node_list=[]):
    if pm.sceneName() and '.cfx.' in pm.sceneName():
        replace_uvmap_folliclemap('lcacfxmap')

    elif pm.sceneName() and '.rig.' in pm.sceneName():
        replace_uvmap_folliclemap()

    if check:
        if not os.path.isdir(uv_file.rsplit('/', 2)[0] + '/mat_info'):
            print 'No mat_info data,ignore.'
            return

    skip_mesh = []
    print 'Start Apply UV Process...'
    print 'UV File:', uv_file
    print 'Scene File:', pm.sceneName()

    # Get mesh nodes which are connected with follicles
    # l_follicles = pm.ls(type = "follicle")
    # print '\tGet', len(l_follicles), 'follicle nodes.'
    # l_follicles_mesh = []
    # for n in l_follicles:
    #     l_cons = pm.listConnections(n.name()+".inputMesh", plugs=True, connections=True, s=True, d=False)
    #     if len(l_cons) > 0:
    #         in_mesh = l_cons[0][1].node()
    #         f = find_source(in_mesh.name())
    #         l_follicles_mesh.extend(f.l_terminals)
    #
    # l_follicles_mesh = list(set(l_follicles_mesh))
    # print '\tGet', len(l_follicles_mesh), 'follicle related meshes.'

    d_meshes = parse_uv_file(uv_file)

    for m_path, m_info in d_meshes.iteritems():
        try:
            m_v_cnt = m_info['m_v_cnt']
            m_e_cnt = m_info['m_e_cnt']
            m_f_cnt = m_info['m_f_cnt']
            n = None
            if import_node_list:
                for node in import_node_list:
                    node_shape = node.name(long=1).split('|', 2)[-1].split(':master|')[-1]
                    if ':' in node_shape:
                        node_shape = '|'.join([sp.split(':')[-1] for sp in node_shape.split('|')])

                    if m_path.split('|', 2)[-1] == node_shape:
                        n = node
                        m_path = node.name(long=1)
                        break

            else:

                if not pm.objExists(m_path):

                    print '\tMissing:', m_path, 'Skip'
                    continue
                else:
                    n = pm.PyNode(m_path)

            if not n:
                print m_path, 'Skip'
                continue

            if n.isIntermediateObject():
                print '\tIntermediate Object:', m_path, 'Skip'
                continue

            # find which mesh to apply UV
            f = find_source(pm.PyNode(m_path).name())
            l_dst_meshes = list(set(f.l_terminals))
            if len(l_dst_meshes) == 0:
                print '\tError: failed to find the source mesh for', m_path
                l_dst_meshes = [m_path]

            # l_dst_meshes.append(m_path)
            print '\tTry to apply UV to:', m_path
            print '\tCandidates:', l_dst_meshes

            if len(m_info['UV'].keys()) == 0:
                skip_mesh.extend(l_dst_meshes)
                print '\t\tSkipped:', ' '.join(l_dst_meshes), ',no uv set for mesh', m_path, 'in the uv file.'
                continue

            print 'check baduvTag  : ', m_path
            if cmds.attributeQuery('baduvTag', node=m_path, exists=True):
                cmds.deleteAttr(m_path + '.baduvTag')

            for dst_mesh in l_dst_meshes:
                if not pm.objExists(dst_mesh):
                    continue
                if cmds.attributeQuery('baduvTag', node=dst_mesh, exists=True):
                    cmds.deleteAttr(dst_mesh + '.baduvTag')

                if pm.polyEvaluate(dst_mesh, vertex=True) != int(m_v_cnt):
                    skip_mesh.append(dst_mesh)
                    print '\t\tSkipped:', dst_mesh, pm.polyEvaluate(dst_mesh, vertex=True), 'vtx, not match', m_v_cnt
                    continue

                if pm.polyEvaluate(dst_mesh, edge=True) != int(m_e_cnt):
                    skip_mesh.append(dst_mesh)
                    print '\t\tSkipped:', dst_mesh, pm.polyEvaluate(dst_mesh, edge=True), 'edges, not match', m_e_cnt
                    continue

                if pm.polyEvaluate(dst_mesh, face=True) != int(m_f_cnt):
                    skip_mesh.append(dst_mesh)
                    print '\t\tSkipped:', dst_mesh, pm.polyEvaluate(dst_mesh, face=True), 'faces, not match', m_f_cnt
                    continue

                all_uvsets = pm.polyUVSet(dst_mesh, allUVSets=True, q=True)
                try:
                    pm.polyUVSet(dst_mesh, uvSet='uv_srf', delete=True)
                    print '\t\tDelete [uv_srf] uvset', dst_mesh
                    if 'uv_srf' in all_uvsets: all_uvsets.remove('uv_srf')
                except:
                    pass

                for uvset in m_info['UV'].keys():
                    if uvset == 'lcarigmap':
                        print '\t\tSkipped uv set [lcarigmap] for rig in mesh [', dst_mesh, '].'
                        continue

                    elif uvset == 'lcacfxmap':
                        print '\t\tSkipped uv set [lcacfxmap] for cfx in mesh [', dst_mesh, '].'
                        continue

                    orig_uv_set = uvset

                    # Create/Clean UV Sets
                    # if dst_mesh in l_follicles_mesh:
                    #     uvset = 'uv_srf'

                    if not uvset in all_uvsets:
                        pm.polyUVSet(dst_mesh, uvSet=uvset, create=True)

                    # if uvset == 'map1' and 'uv_srf' in all_uvsets:
                    #     pm.polyUVSet(dst_mesh, uvSet='uv_srf', delete=True)

                    if not m_info['UV'].has_key(uvset):
                        uvset = orig_uv_set

                    l_u = m_info['UV'][uvset]['u']
                    l_v = m_info['UV'][uvset]['v']
                    l_uv_cnt = m_info['UV'][uvset]['uv_cnt']
                    l_uv_ids = m_info['UV'][uvset]['uv_ids']

                    sl = om.MSelectionList()
                    sl.add(dst_mesh)
                    mesh_dag = sl.getDagPath(0)
                    mesh_mfn = om.MFnMesh(mesh_dag)

                    print '\t\tApplied (UV Set ' + uvset + '):', dst_mesh
                    mesh_mfn.clearUVs(uvSet=uvset)
                    mesh_mfn.setUVs(l_u, l_v, uvSet=uvset)
                    mesh_mfn.assignUVs(l_uv_cnt, l_uv_ids, uvSet=uvset)
                    # update uv set
                    cmds.polyUVSet(dst_mesh, cr=True, uvs="update")
                    cmds.undo()

                # refresh
                if dst_mesh.endswith('Orig'):
                    l_con = pm.listConnections(dst_mesh, d=True, s=False, c=True, p=True)
                    if len(l_con) > 0:
                        l_con[0][0].disconnect(l_con[0][1])
                        l_con[0][0].connect(l_con[0][1].name(), f=True)

        except:
            print '\tFailed to apply uv to mesh:', m_path
            print traceback.format_exc()

    # Query uv sets command won't return correct result if the mesh node is in a container.
    # Also there is no need to check if the uv_srf exists, since set current uv command won't return any error
    # print '\n\tSet poly meshes to uv_srf if the uv set exists.'
    # if pm.objExists('|master|poly'):
    #     l_meshes = pm.listRelatives('|master|poly', ad=True, type='mesh')
    #     for mesh in l_meshes:
    #         #all_uvsets = pm.polyUVSet(mesh, allUVSets=True, q=True)
    #         #if 'uv_srf' in all_uvsets:
    #         pm.polyUVSet(mesh, uvSet='uv_srf', currentUVSet=True)

    __add_skip_tag(skip_mesh)

    pd_list = pm.ls(type='polyMapDel')
    if pd_list:
        pm.delete(pd_list)

    return skip_mesh


def normal_path(input_path):
    cur_path = os.path.normpath(input_path)
    cur_path = cur_path.replace("\\", "/")
    return cur_path


def get_uv_file_path():
    listdirTemp = cmds.file(q=True, sn=True)
    listdir = normal_path(listdirTemp)
    if '/chr/' in listdir:
        chr_index = listdir.index('chr/') + len('chr/')
        assert_type = 'chr'
    elif '/prp/' in listdir:
        chr_index = listdir.index('prp/') + len('prp/')
        assert_type = 'prp'
    elif '/crd/' in listdir:
        chr_index = listdir.index('crd/') + len('crd/')
        assert_type = 'crd'
    else:
        return
    charName = listdir[chr_index:].split('/')[0]
    # Find the name after 'projects/'
    projects_index = listdir.index('projects/') + len('projects/')
    project = listdir[projects_index:].split('/')[0]
    uv_path = "Z:projects/{}/asset/{}/{}/srf/publish/{}.srf.surfacing/scene_graph_xml/{}.uv".format(project,
                                                                                                    assert_type,
                                                                                                    charName, charName,
                                                                                                    charName)

    return uv_path

def process_return_value(return_value, current_file_path):
    try:
        if return_value:
            if return_value[0] == False:
                from production.feishu_utils import lca_feishu
                lca_feishu.main(to_user_list=['xiaoyu2', 'zejie', 'zhenlin', 'pangxuan', 'wangqi2'],
                                title=u'push_rig_shader 材质拉取失败，返回值False !',
                                message='file_path: \n {}{}'.format(current_file_path, return_value[1]),
                                app='warning')
    except:
        pass