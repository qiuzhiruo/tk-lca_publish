# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
# Description: Proceed model publish files
#
############################################

import os
import traceback
import math
import shutil
import pymel.core as pm
import maya.cmds as cmds
from mod.assgin_shader_to_mod import assign_shader as ass_shader
from proc.function_running_time import record_time
reload(ass_shader)
import sys

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"提取模型，将文件拷贝到服务器。test a"
        self.description = u"根据之前的模式选择，将模型存出poly文件或者shape文件。shape模式只输出shape组下物体。poly模式会套上global_control控制器。"
        return


    def add_global_ctrl(self, asset_type):
        # Clean rig group, if it exists
        if pm.objExists('|master|rig'):
            pm.delete('|master|rig')
        if asset_type in ['prp']:
            r_nodes = pm.importFile(os.path.dirname(__file__) + '/global_control_prp.ma', returnNewNodes=True)
        else:
            r_nodes = pm.importFile(os.path.dirname(__file__) + '/global_control.ma', returnNewNodes=True)
        l_nodes = []
        for n in r_nodes:
            if n.type() == 'script':
                pm.delete(n)
                continue
            l_nodes.append(n)
        self.rig_node = l_nodes[0]
        l_lock_nodes = [self.rig_node]
        global_ctrl = None
        root_ctrl = None
        root_ctrl_base = None
        anim_rig = None
        for node in l_nodes:
            if node.fullPath().endswith('zero'):
                l_lock_nodes.append(node)
            if node.name() == ('global_ctrl'):
                global_ctrl = node
            if node.name() == ('root_ctrl'):
                root_ctrl = node
            if node.name() == ('root_base'):
                root_ctrl_base = node
            if node.name() == ('anim_rig'):
                anim_rig = node

        if anim_rig:
            l_ani_grp = pm.listRelatives(anim_rig)
            for n in l_ani_grp:
                if n.name() != 'anim_controls_grp':
                    n.setAttr("inheritsTransform", 0)
            n = pm.PyNode('|master|poly')
            n.setAttr("inheritsTransform", 0)

        l_res_nodes = []
        for res in ['hi', 'md', 'lo', 'proxy']:
            if pm.objExists('|master|poly|'+res):
                l_res_nodes.append(pm.ls('|master|poly|' + res)[0])
        try:
            l_res_nodes.append(pm.ls('|master|shape')[0])
        except:
            pass
        poly_node = pm.ls('|master|poly')[0]
        hi = pm.ls("|master|poly|hi")[0]
        vis = hi.getAttr("v")
        hi.setAttr("v", True)

        # Create Transform the global control
        bbox = poly_node.boundingBox()
        hi.setAttr("v", vis)

        #pm.move(self.rig_node, [(bbox.min()[0] + bbox.max()[0])/2, bbox.min()[1], (bbox.min()[2] + bbox.max()[2])/2])
        # Scale the global control
        l_rig_nodes = pm.listRelatives(self.rig_node, ad=True, type='transform')
        l_rig_nodes.append(self.rig_node)
        l_locked_attr = []
        for n in l_rig_nodes:
            for attr in ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']:
                if pm.getAttr(n.name()+'.' + attr, lock=True):
                    l_locked_attr.append(n.name()+'.' + attr)
                    pm.setAttr(n.name()+'.' + attr, lock=False)

        s = math.sqrt( (bbox.max()[0] - bbox.min()[0])**2 + (bbox.max()[2] - bbox.min()[2])**2 )
        if s < 0.7:
            s = 0.7
        pm.scale(self.rig_node, [s, s, s])
        pm.select(self.rig_node, r=True)
        pm.mel.eval('FreezeTransformations;')
        pm.delete(self.rig_node, ch=True)

        for attr in l_locked_attr:
            pm.setAttr(attr, lock=True)

        # lock the control if it's not a chr or an asb asset
        if global_ctrl:
            # 应绑定需求, veh, chr的大环约束一样
            if asset_type in ['asb']:
                pm.connectAttr( global_ctrl.fullPath()+".globalScale", global_ctrl.fullPath()+".scaleX", f=True)
                pm.connectAttr( global_ctrl.fullPath()+".globalScale", global_ctrl.fullPath()+".scaleY", f=True)
                pm.connectAttr( global_ctrl.fullPath()+".globalScale", global_ctrl.fullPath()+".scaleZ", f=True)
                for attr in ['sx', 'sy', 'sz']:
                    global_ctrl.setAttr(attr, lock=True, keyable=False, channelBox=False )
            else:
                if asset_type in ['prp','veh','chr']:
                    # 应绑定需求去掉一个globalScale属性
                    if pm.hasAttr(global_ctrl, 'globalScale'):
                        global_ctrl.deleteAttr('globalScale')
                    self.add_scale_offset()
                else:
                    global_ctrl.deleteAttr('globalScale')

        for node in l_lock_nodes:
            for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
                node.setAttr(attr, lock=True, keyable=False, channelBox=False )


        if root_ctrl_base:
            for attr in ['sx', 'sy', 'sz']:
                root_ctrl_base.setAttr(attr, lock=True, keyable=False, channelBox=False )
            for res_node in l_res_nodes:
                pm.select(root_ctrl_base, r=True)
                pm.select(res_node, tgl=True)
                pm.mel.eval('parentConstraint -mo -weight 1;')
                pm.mel.eval('doCreateScaleConstraintArgList 1 { "0","1","1","1","0","0","0","1","","1" };')

        elif root_ctrl:
            for attr in ['sx', 'sy', 'sz']:
                root_ctrl.setAttr(attr, lock=True, keyable=False, channelBox=False )
            for res_node in l_res_nodes:
                pm.select(root_ctrl, r=True)
                pm.select(res_node, tgl=True)
                pm.mel.eval('parentConstraint -mo -weight 1;')
                pm.mel.eval('doCreateScaleConstraintArgList 1 { "0","1","1","1","0","0","0","1","","1" };')

        self.rig_node = pm.parent(self.rig_node, '|master')

        # Lock |master and |master|poly
        for node_name in ['|master', '|master|poly']:
            node = pm.ls(node_name)[0]
            for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
                node.setAttr(attr, lock=True, keyable=False )

        # Lock env:经ani和rough商量,mod可以锁env用以防止ani和rough移动env资产

        if asset_type in ['env']:
            rig_nodes = pm.listRelatives(self.rig_node, ad=True, type='transform')
            src_lock = False
            for n in rig_nodes:
                if pm.lockNode(n, q=True)[0]:
                    pm.lockNode(n, lock=False)
                    src_lock = True
                for attr in ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']:
                    pm.setAttr(n.name()+'.' + attr, lock=True)
                if src_lock:
                    pm.lockNode(n, lock=True)

        return

    def lock_hi(self):
        if not pm.objExists('|master|poly|hi'):
            return

        for node in pm.listRelatives('|master|poly|hi', ad=True, type='transform', path=True):
            for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
                node.setLocked(False)
                node.setAttr(attr, lock=True, keyable=False )
                # 应绑定和材质要求，现在取消锁定模型
                # node.setLocked(True)
        return

    def add_scale_offset(self):
        try:
            # Unlocking the scale attributes
            cmds.setAttr("global_ctrl_zero.scaleX", lock=False)
            cmds.setAttr("global_ctrl_zero.scaleY", lock=False)
            cmds.setAttr("global_ctrl_zero.scaleZ", lock=False)

            # Adding new attributes
            if not pm.hasAttr(pm.PyNode('global_ctrl'), 'global_scale'):
                cmds.addAttr("global_ctrl", longName="global_scale", attributeType="double", defaultValue=1)
            if not pm.hasAttr(pm.PyNode('global_ctrl'), 'scale_offset'):
                cmds.addAttr("global_ctrl", longName="scale_offset", attributeType="double", defaultValue=1)

            # Connecting attributes
            cmds.connectAttr("global_ctrl.scale_offset", "root_ctrl.scaleX", force=True)
            cmds.connectAttr("global_ctrl.scale_offset", "root_ctrl.scaleY", force=True)
            cmds.connectAttr("global_ctrl.scale_offset", "root_ctrl.scaleZ", force=True)
            cmds.setAttr("root_ctrl.scaleX", keyable=False, channelBox=False, l=True)
            cmds.setAttr("root_ctrl.scaleY", keyable=False, channelBox=False, l=True)
            cmds.setAttr("root_ctrl.scaleZ", keyable=False, channelBox=False, l=True)
            cmds.setAttr("global_ctrl_PH.scaleX", keyable=False, channelBox=False, l=True)
            cmds.setAttr("global_ctrl_PH.scaleY", keyable=False, channelBox=False, l=True)
            cmds.setAttr("global_ctrl_PH.scaleZ", keyable=False, channelBox=False, l=True)
            cmds.setAttr("global_ctrl_SN.scaleX", keyable=False, channelBox=False, l=True)
            cmds.setAttr("global_ctrl_SN.scaleY", keyable=False, channelBox=False, l=True)
            cmds.setAttr("global_ctrl_SN.scaleZ", keyable=False, channelBox=False, l=True)


            # Creating nodes
            global_scale_md1 = cmds.createNode("multDoubleLinear", name="global_scale_md1")

            # Connecting more attributes
            cmds.connectAttr("global_ctrl.scale_offset", global_scale_md1 + ".input1", force=True)
            cmds.connectAttr("global_ctrl.scaleX", global_scale_md1 + ".input2", force=True)
            cmds.connectAttr(global_scale_md1 + ".output", "global_ctrl.global_scale", force=True)
        except Exception as e:
            cmds.warning("scale offset attribute fail to add")

    def remove_global_ctrl(self):
        # Delete Rig
        l_rig_nodes = pm.listRelatives(self.rig_node, ad=True)
        for n in l_rig_nodes:
            pm.lockNode(n, l=False)
        pm.delete(self.rig_node)

        if not pm.objExists('|master|poly|hi'):
            pm.createNode('transform', parent='|master|poly', name='hi')

        # Rebuild the master, poly group
        for node_name in ['|master', '|master|poly']:
            node = pm.ls(node_name)[0]
            for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
                node.setAttr(attr, lock=0, keyable=1 )

        n = pm.PyNode('|master|poly')
        n.setAttr("inheritsTransform", 1)
        return

    def clean_sets_n_layers(self):
        l_sets = pm.ls(type = 'objectSet')
        self.d_sets = {}
        for obj_set in l_sets:
            if obj_set.type() == 'objectSet':
                self.d_sets[obj_set.name()] = pm.sets( obj_set, q=True )
                try:
                    obj_set.clear()
                except:
                    print 'Failed to clear set:', obj_set.name()

        l_layers = pm.ls(type='displayLayer')
        self.d_layers = {}
        for layer in l_layers:
            if layer.name() != 'defaultLayer':
                self.d_layers[layer.name()] = pm.editDisplayLayerMembers(layer, query=True, fullNames=True)
                try:
                    pm.editDisplayLayerMembers("defaultLayer", self.d_layers[layer.name()], noRecurse =True )
                except:
                    print 'Failed to clear layer:', layer.name()

        return


    def recovery_sets_n_layers(self):
        for obj_set, l_elements in self.d_sets.iteritems():
            try:
                pm.sets(obj_set, forceElement=l_elements )
            except:
                print 'Failed to recovery set:', obj_set

        for layer, l_elements in self.d_layers.iteritems():
            try:
                pm.editDisplayLayerMembers(layer, l_elements, noRecurse =True )
            except:
                print 'Failed to recovery layer:', layer

        return

    def apply_srf_shader(self):
        asset = self.dialog.entity['name']
        proj = self.dialog.project['name']

        import srf.push_shader.push_shader as sps
        reload(sps)
        sps.push_shader(proj,asset)
        self.dialog.print_log('Apply srf pass shader for '+proj+':'+asset)

    def copy_tree(self,path,version_dir):
        for dir_path, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(dir_path, file)
                if os.path.isdir(file_path):
                    self.copy_tree(file_path)
                else:
                    if os.path.getsize(file_path) > 0:
                        shutil.copy(file_path,version_dir + '/speed_tree/' + os.path.basename(file_path))

    @record_time(__file__)
    def proceed(self):
        try:
            self.clean_sets_n_layers()
            if len(self.dialog.d_assets_info.values()) == 1 and self.dialog.d_assets_info.values()[0]['node_name'] == 'master':
                publish_mode = self.dialog.w_publish_file.comboBox_publish_mode.currentText()
                l_spm_files = [self.dialog.w_publish_file.listWidget_speed_tree.item(i).text() for i in xrange(self.dialog.w_publish_file.listWidget_speed_tree.count())]
                l_zb_files = [self.dialog.w_publish_file.listWidget_zb.item(i).text() for i in xrange(self.dialog.w_publish_file.listWidget_zb.count())]
                l_zb_view_files = [self.dialog.w_publish_file.listWidget_zb_view.item(i).text() for i in xrange(self.dialog.w_publish_file.listWidget_zb_view.count())]

            else:
                publish_mode = 'poly'
                l_spm_files = []
                l_zb_files = []
                l_zb_view_files = []

            for asset_name in self.dialog.d_assets_info.keys():
                version_dir = self.dialog.d_assets_info[asset_name]['version_dir']
                root = self.dialog.d_assets_info[asset_name]['node']
                parent = self.dialog.d_assets_info[asset_name]['parent']
                node_name = self.dialog.d_assets_info[asset_name]['node_name']
                asset_type = self.dialog.d_assets_info[asset_name]['type']
                tank_file = self.dialog.d_assets_info[asset_name]['tank_file']
                translation = self.dialog.d_assets_info[asset_name]['translation']
                rotation = self.dialog.d_assets_info[asset_name]['rotation']
                
                
                
                
                # make a master if necessary
                if parent:
                    pm.parent(root, world=True)

                # root.setRotation((0.0, 0.0, 0.0))
                # pm.xform(root, r=True, translation=(translation[0] * -1,  translation[1] * -1, translation[2] * -1))
                root.rename('master')

                if publish_mode == 'poly':
                    
                    if 'work_file' in self.dialog.d_assets_info[asset_name].keys():
                        work_file = self.dialog.d_assets_info[asset_name]['work_file']
                        print 'Export work_file:', work_file
                        pm.select(pm.PyNode('|master|poly'), r=True)
                        pm.exportSelected(work_file, force=True, options="v=0;", type="mayaAscii", pr=True, es=True)

                    self.add_global_ctrl(asset_type)

                    # push shader from srf when global ctrl
                    if asset_type == "chr":
                        srf_publish_dir = self.dialog.publish_root.replace('/mod/', '/srf/').replace('\\', '/')
                        if os.path.isdir(srf_publish_dir):
                            uv_file = srf_publish_dir.replace('Z:/', 'W:/').replace('/proj/', '/work/').replace('/publish',
                                                                                                                '/task') + '/katana/scene_graph_xml/' + \
                                      self.dialog.entity['name'] + '.uv'
                            if os.path.isfile(uv_file):
                                try:
                                    import srf.push_shader.push_shader as sps
                                    reload(sps)
                                    sps.push_shader(self.dialog.project['name'], self.dialog.entity['name'], add_pass_only=0, force=True)
                                    self.dialog.print_log('Apply srf pass shader for ' + self.dialog.project['name'] + ':' + self.dialog.entity['name'])
                                except:
                                    self.dialog.print_log('Apply srf shader failed.' + traceback.format_exc())

                    # Export all model
                    n = pm.PyNode('|master|poly')
                    # 导出之前还原模型的颜色
                    try:
                        if asset_type != 'flg' and self.dialog.publish_tool_mode != 'batch sub asset':
                            ass_shader.setup()
                            ass_shader.fresh()
                    except Exception as e:
                        traceback.print_exc()

                    pm.select(n, r=True)
                    vis = n.getAttr("v")
                    n.setAttr("v", True)
                    pm.select(self.rig_node)
                    for res in ['hi','md', 'lo']:
                        if pm.objExists('|master|poly|'+res):
                            pm.select("|master|poly|"+res, add=True)

                    if pm.objExists('|master|shape'):
                        pm.select("|master|shape", add=True)
                    pm.exportSelected(tank_file, force=True, options="v=0;", type="mayaAscii", pr=True, es=True)
                    asset_type = self.dialog.d_assets_info[asset_name]['type']

                    # 将work盘的ma文件里的贴图路径设置为work盘里的路径
                    work_tex_dir = os.path.join('/mnt/work/projects/', self.dialog.project['name'].lower(), 'asset', asset_type, asset_name, 'mod', 'task', 'images', 'tex_low')
                    if sys.platform.startswith('win'):
                        work_tex_dir = os.path.join('W:/projects/', self.dialog.project['name'].lower(), 'asset', asset_type, asset_name,'mod', 'task', 'images', 'tex_low')

                    for file_node in cmds.ls(typ='file'):
                        tex_path = cmds.getAttr(file_node + '.fileTextureName')
                        work_tex_file = os.path.join(work_tex_dir, os.path.basename(tex_path))
                        pm.setAttr(file_node + '.fileTextureName', work_tex_file)
                    try:
                        if self.dialog.switch_nodes:
                            cmds.delete(self.dialog.switch_nodes)
                    except Exception as e:
                        traceback.print_exc()
                        pass
                    n.setAttr("v", vis)
                    
                    print 'Export tank_file:', tank_file


                    if asset_type in ['asb', 'scn', 'dmt', 'efx', 'msc']:
                        print 'Don\'t need to export md/lo/proxy res model for', asset_type, 'asset.'
                        continue

                    # Export other res model
                    for res in ['hi','md', 'lo', 'proxy']:
                        if not pm.objExists('|master|poly|'+res):
                            continue

                        res_folder = version_dir + '/res/' + res
                        res_file = res_folder+'/' + asset_name + '.mb'
                        if not os.path.isdir(res_folder):
                            os.makedirs(res_folder)

                        n = pm.PyNode('|master|poly|' + res)
                        
                        pm.select(n, r=True)
                        
                        vis = n.getAttr("v")
                        n.setAttr('v', True)
                        pm.select(self.rig_node, add=True)
                        if pm.objExists("|master|shape"):
                            pm.select("|master|shape", add=True)
                            
                        # lock hi res transform
                        if res == 'hi':
                            pm.undoInfo(state=True, infinity=True)
                            pm.undoInfo(ock=True)
                            self.lock_hi()
                            pm.undoInfo(cck=True)
                            
                            pm.exportSelected(res_file, force=True, options="v=0;", type="mayaBinary", pr=True, es=True)
                            pm.undo()
                            pm.undoInfo(state=True, infinity=False)
                            
                        else:
                            pm.exportSelected(res_file, force=True, options="v=0;", type="mayaBinary", pr=True, es=True)
                        
                        
                        
                        n.setAttr("v", vis)
                        print 'Export '+res+' res:', res_file

                        if res=='proxy' and n.hasAttr('mod_proxy'):
                            print 'proxy_lock'
                            proxy_lock=os.path.join(os.path.dirname(res_file),'mod_proxy.mb')
                            shutil.copyfile(res_file,proxy_lock)



                
                elif publish_mode == 'shape':
                    pm.select("|master|shape", r=True)
                    pm.exportSelected( tank_file, force=True, options="v=0;", type="mayaAscii", pr=True, es=True)

                if l_spm_files or l_zb_files or l_zb_view_files:
                    print 'Additional files spm_file'
                    for spm_file in l_spm_files:
                        if os.path.exists(spm_file):
                            if not os.path.isdir(version_dir + '/speed_tree/'):
                                os.makedirs(version_dir + '/speed_tree/')
                            if os.path.isfile(spm_file):
                                shutil.copy(spm_file, version_dir + '/speed_tree/' + os.path.basename(spm_file) )
                            elif os.path.isdir(spm_file):
                                self.copy_tree(spm_file,version_dir)
                                # shutil.copytree(spm_file, version_dir + '/speed_tree/' + os.path.basename(spm_file) )

                    print 'Additional files zb_file'
                    for zb_file in l_zb_files:
                        if os.path.isfile(zb_file):
                            if not os.path.isdir(version_dir + '/zbrush/'):
                                os.makedirs(version_dir + '/zbrush/')
                            shutil.copyfile(zb_file, version_dir + '/zbrush/' + os.path.basename(zb_file) )

                    print 'Additional files zbv_file'
                    for zb_view_file in l_zb_view_files:
                        if os.path.isfile(zb_view_file):
                            if not os.path.isdir(version_dir + '/zbrush/'):
                                os.makedirs(version_dir + '/zbrush/')
                            shutil.copyfile(zb_view_file, version_dir + '/zbrush/' + os.path.basename(zb_view_file) )

                print 'Clean and save file'

                self.recovery_sets_n_layers()
                print ' recovery_sets_n_layers '
                self.remove_global_ctrl()
                print 'remove global ctrl'


                pm.select(cl=True)
                if cmds.objExists('|master|shape|nurbs_hair_grp'):
                    pm.delete('|master|shape|nurbs_hair_grp')

                print 'recovery root node'
                pm.xform(root, r=True, translation=(translation[0],  translation[1], translation[2]))
                root.setRotation(rotation)
                if parent:
                    pm.parent(root, parent)

                root.rename(node_name)

            return ""

        except:
            return traceback.format_exc()



    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


