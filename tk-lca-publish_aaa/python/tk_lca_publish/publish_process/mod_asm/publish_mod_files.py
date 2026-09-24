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
import sys
import traceback
import hashlib
from xml.dom.minidom import Document
import maya.api.OpenMaya as om

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"提取模型，将文件拷贝到服务器。"
        self.description = u"根据之前的模式选择，将模型存出poly文件或者shape文件。shape模式只输出shape组下物体。poly模式会套上global_control控制器。"
        return


    def add_global_ctrl(self, asset_type):
        # Clean rig group, if it exists
        if pm.objExists('|master|rig'):
            pm.delete('|master|rig')

        l_nodes = pm.importFile(os.path.dirname(__file__)[:-4] + '/global_control.ma', returnNewNodes=True)
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
            if asset_type in ['chr', 'veh', 'asb','crd']:
                pm.connectAttr( global_ctrl.fullPath()+".globalScale", global_ctrl.fullPath()+".scaleX", f=True)
                pm.connectAttr( global_ctrl.fullPath()+".globalScale", global_ctrl.fullPath()+".scaleY", f=True)
                pm.connectAttr( global_ctrl.fullPath()+".globalScale", global_ctrl.fullPath()+".scaleZ", f=True)
                for attr in ['sx', 'sy', 'sz']:
                    global_ctrl.setAttr(attr, lock=True, keyable=False, channelBox=False )
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
                pm.mel.eval('doCreateParentConstraintArgList 1 { "1","0","0","0","0","0","0","1","","1" };')
                pm.mel.eval('doCreateScaleConstraintArgList 1 { "0","1","1","1","0","0","0","1","","1" };')
            
        elif root_ctrl:
            for attr in ['sx', 'sy', 'sz']:
                root_ctrl.setAttr(attr, lock=True, keyable=False, channelBox=False )
            for res_node in l_res_nodes:
                pm.select(root_ctrl, r=True)
                pm.select(res_node, tgl=True)
                pm.mel.eval('doCreateParentConstraintArgList 1 { "1","0","0","0","0","0","0","1","","1" };')
                pm.mel.eval('doCreateScaleConstraintArgList 1 { "0","1","1","1","0","0","0","1","","1" };')

        self.rig_node = pm.parent(self.rig_node, '|master')

        # Lock |master and |master|poly
        for node_name in ['|master', '|master|poly']:
            node = pm.ls(node_name)[0]
            for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
                node.setAttr(attr, lock=True, keyable=False )

        return

    def remove_global_ctrl(self):
        # Delete Rig
        if pm.objExists('|master|rig'):
            rig_node=pm.PyNode('|master|rig')
            l_rig_nodes = pm.listRelatives(rig_node, ad=True)
            for n in l_rig_nodes:
                pm.lockNode(n, l=False)
            pm.delete(rig_node)

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
            if obj_set.type() == 'objectSet' and self.dialog.asm_set and pm.objExists('asm_set'):

                if obj_set.name() not in self.dialog.asm_set and obj_set.name()!='asm_set':
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

    def unlock_node(self,node):
        TR_ATTRS=['translateX','translateY','translateZ','rotateX','rotateY','rotateZ','scaleX','scaleY','scaleZ','visibility']
        l_meshes = pm.listRelatives(node, ad=True, type='transform', path=True)
        l_meshes.append(node)
        for mesh in l_meshes:
            pm.lockNode(mesh,lock=0)
            for attr in TR_ATTRS:
                pm.setAttr(mesh+'.'+attr,l=False)

    def import_body_master(self, body_asset):
        master_node = None
        Version = self.dialog.sg.find_one('Version',
                                          [['entity.Asset.code', 'is', body_asset],
                                           ['sg_task.Task.step', 'name_is', 'mod'],
                                           ['sg_version_type', 'is', 'Downstream'],
                                           ['project', 'name_is', self.dialog.project['name']]],
                                          ['code','sg_version_folder'], order=[{'field_name': 'created_at', 'direction': 'desc'}])
        if not Version:
            return
        ma_file = os.path.join(Version['sg_version_folder']['local_path'], Version['code'].split('.')[0] + '.ma')

        if not os.path.exists(ma_file):
            return

        print 'import body file : ',ma_file
        body_node_list = pm.importFile(ma_file, returnNewNodes=1)


        for node in body_node_list:
            if node.type() == 'transform' and node.name().endswith('master'):
                master_node = node

        if pm.objExists('|%s|rig'%master_node.name()):
            rig_node=pm.PyNode('|%s|rig'%master_node.name())
            l_rig_nodes = pm.listRelatives(rig_node, ad=True)
            for n in l_rig_nodes:
                pm.lockNode(n, l=False)
            pm.delete(rig_node)

        return master_node


    def combine_body(self,master_node):
        res_list=['|poly|hi|mesh_grp','|poly|md|mesh_grp','|poly|lo|mesh_grp','|poly|proxy|mesh_grp','|shape']

        for res in res_list:
            if not pm.objExists(master_node.name()+res):
                continue
            res_node=pm.PyNode(master_node.name()+res)

            res_children=res_node.getChildren()
            if pm.objExists('master'+res):
                pm.parent(res_children,'master'+res)
            else:

                master_res='master'+res
                if res=='|shape':
                    tmp_res=master_res.rsplit('|',1)[0]
                else:
                    tmp_res=master_res.rsplit('|',2)[0]
                pm.parent(res_node,tmp_res)

    def edit_modPath(self,tank_file):
        version=tank_file.split('/')[-2][-3:]

        master_node=pm.PyNode('|master')
        master_node.setAttr('modPath',tank_file)
        master_node.setAttr('modVersion',version)

    def create_structure(self, root_elem, root_node):
        if not pm.objExists(root_node):
            return

        l_nodes = pm.listRelatives(root_node)
        l_nodes.sort()
        for node in l_nodes:
            if node.type() == 'transform':
                trans = self.doc.createElement('transform')
                trans.setAttribute('name', node.fullPath())
                root_elem.appendChild(trans)
                self.create_structure(trans, node)
            elif node.type() == 'mesh' and (not node.isIntermediate()):
                if pm.polyEvaluate(node, face=True) == 0:
                    topology = hashlib.md5(' ').hexdigest()
                    topology_p = hashlib.md5(' ').hexdigest()
                else:
                    sl = om.MSelectionList()
                    sl.add(node.fullPath())
                    mesh_dag = sl.getDagPath(0)
                    mesh_mfn = om.MFnMesh(mesh_dag)
                    v = mesh_mfn.getVertices()
                    v_str0 = '[' + ', '.join([str(i) for i in v[0]]) + ']'
                    v_str1 = '[' + ', '.join([str(i) for i in v[1]]) + ']'
                    v_str2 = '[' + ', '.join(
                            ['%.4f %.4f %.4f' % (i.getPosition()[0], i.getPosition()[1], i.getPosition()[2]) for i in
                             node.vtx]) + ']'

                    topology = hashlib.md5(v_str0 + ' ' + v_str1).hexdigest()
                    topology_p = hashlib.md5(v_str0 + ' ' + v_str1 + ' ' + v_str2).hexdigest()

                mesh = self.doc.createElement('mesh')
                mesh.setAttribute('name', node.fullPath())
                mesh.setAttribute('vertex', str(pm.polyEvaluate(node, vertex=True)))
                mesh.setAttribute('edge', str(pm.polyEvaluate(node, edge=True)))
                mesh.setAttribute('face', str(pm.polyEvaluate(node, face=True)))
                mesh.setAttribute('topology', topology)
                mesh.setAttribute('topology_p', topology_p)
                root_elem.appendChild(mesh)

        return

    def mod_mesh_xml(self,asset_name):

        version_dir = self.dialog.d_assets_info[asset_name]['version_dir']
        root = self.dialog.d_assets_info[asset_name]['node']
        node_name = self.dialog.d_assets_info[asset_name]['node_name']

        # make a master if necessary
        if self.dialog.d_assets_info[asset_name]['parent']:
            pm.parent(root, world=True)

        if node_name != 'master':
            root.rename('master')

        mesh_xml = version_dir + '/mesh.xml'
        self.doc = Document()
        master = self.doc.createElement('transform')
        master.setAttribute('name', '|master')
        self.doc.appendChild(master)
        poly = self.doc.createElement('transform')
        poly.setAttribute('name', '|master|poly')
        master.appendChild(poly)
        if pm.objExists('|master|poly|hi'):
            res_node = self.doc.createElement('transform')
            res_node.setAttribute('name', '|master|poly|hi')
            poly.appendChild(res_node)
            self.create_structure(res_node, '|master|poly|hi')

        if pm.objExists('|master|poly|md'):
            res_node = self.doc.createElement('transform')
            res_node.setAttribute('name', '|master|poly|md')
            poly.appendChild(res_node)
            self.create_structure(res_node, '|master|poly|md')

        if pm.objExists('|master|poly|lo'):
            res_node = self.doc.createElement('transform')
            res_node.setAttribute('name', '|master|poly|lo')
            poly.appendChild(res_node)
            self.create_structure(res_node, '|master|poly|lo')

        f = open(mesh_xml, 'w')
        f.write(self.doc.toprettyxml(indent='    '))
        f.close()

        # recovery root node
        if self.dialog.d_assets_info[asset_name]['parent']:
            pm.parent(root, self.dialog.d_assets_info[asset_name]['parent'])

        if node_name != 'master':
            root.rename(node_name)



    def proceed(self):
        try:
            #self.clean_sets_n_layers()
            if len(self.dialog.d_assets_info.values()) == 1 and self.dialog.d_assets_info.values()[0]['node_name'] == 'master':
                publish_mode = self.dialog.w_publish_file.comboBox_publish_mode.currentText()
                l_spm_files = [self.dialog.w_publish_file.listWidget_speed_tree.item(i).text() for i in xrange(self.dialog.w_publish_file.listWidget_speed_tree.count())]
                l_zb_files = [self.dialog.w_publish_file.listWidget_zb.item(i).text() for i in xrange(self.dialog.w_publish_file.listWidget_zb.count())]
            else:
                publish_mode = 'poly'
                l_spm_files = []
                l_zb_files = []

            assets_poly=[]
            
            d_assets_info_list=[]

            for k,v in self.dialog.d_assets_info.items():
                if v['type'] in ['chr','crd']:
                    assets_poly.extend(pm.ls('master|poly|hi|mesh_grp|'+k))
                    d_assets_info_list.append(k)

                elif v['type']=='asm':
                    d_assets_info_list.insert(0,k)

            try:
                self.apply_srf_shader()
            except:
                self.dialog.print_log('Apply srf shader failed.\n'+traceback.format_exc())


            scale_tmp=1

            for asset_name in d_assets_info_list:

                version_dir = self.dialog.d_assets_info[asset_name]['version_dir']
                root = pm.PyNode('|master')
                parent = self.dialog.d_assets_info[asset_name]['parent']
                node_name = self.dialog.d_assets_info[asset_name]['node_name']
                asset_type = self.dialog.d_assets_info[asset_name]['type']
                tank_file = self.dialog.d_assets_info[asset_name]['tank_file']
                translation = self.dialog.d_assets_info[asset_name]['translation']
                rotation = self.dialog.d_assets_info[asset_name]['rotation']
                scale = self.dialog.d_assets_info[asset_name]['scale']

                pm.undoInfo( state=True, infinity=True )
                pm.undoInfo(ock=True)

                if scale!=1.0:
                    root.setScale((scale/scale_tmp,scale/scale_tmp,scale/scale_tmp))
                    scale_tmp=scale
                    pm.makeIdentity(root,apply=1,t=1,r=1,s=1,n=0,pn=1)

                    
                if asset_name != self.dialog.entity['name']:
                    print 'asset_name :',asset_name

                    self.edit_modPath(tank_file)
                    for asset_poly in assets_poly:
                        if asset_poly.name().split('|')[-1]==asset_name:

                            if not asset_poly.getParent():
                                pm.parent(asset_poly,'master|poly|hi|mesh_grp')
                        elif asset_poly.getParent():
                            pm.parent(asset_poly,w=1)



                if pm.objExists('rig'):
                    self.remove_global_ctrl()
                self.unlock_node(root)


                pm.undoInfo(cck=True)

                all_mesh=pm.ls(type='mesh')
                for mesh in all_mesh:
                    pm.polySmooth( mesh, dv=0 )
                pm.select(all_mesh)


                pm.mel.eval('DeleteAllHistory;')


                # make a master if necessary
                if parent:
                    pm.parent(root, world=True)

                root.setRotation((0.0, 0.0, 0.0))
                pm.xform(root, r=True, translation=(translation[0] * -1,  translation[1] * -1, translation[2] * -1))


                if publish_mode == 'poly':
                    

                    # Export all model
                    n = pm.PyNode('|master|poly')
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
                    self.mod_mesh_xml(asset_name)


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
                        res_file = res_folder+'/' + asset_name + '.ma'
                        if not os.path.isdir(res_folder):
                            os.makedirs(res_folder)

                        n = pm.PyNode('|master|poly|' + res)
                        pm.select(n, r=True)
                        vis = n.getAttr("v")
                        n.setAttr('v', True)
                        pm.select(self.rig_node, add=True)
                        pm.exportSelected(res_file, force=True, options="v=0;", type="mayaAscii", pr=True, es=True)
                        n.setAttr("v", vis)
                        print 'Export '+res+' res:', res_file

                    pm.undo()
                    pm.undoInfo( state=True, infinity=False )

                    if asset_name != self.dialog.entity['name']:
                        continue

                # Additional files
                elif publish_mode == 'shape':
                    pm.select("|master|shape", r=True)
                    pm.undoInfo(cck=True)
                    pm.exportSelected( tank_file, force=True, options="v=0;", type="mayaAscii", pr=True, es=True)
                    pm.undo()
                    pm.undoInfo( state=True, infinity=False )

                for spm_file in l_spm_files:
                    if os.path.isfile(spm_file):
                        if not os.path.isdir(version_dir + '/speed_tree/'):
                            os.makedirs(version_dir + '/speed_tree/')
                        shutil.copyfile(spm_file, version_dir + '/speed_tree/' + os.path.basename(spm_file) )
                
                for zb_file in l_zb_files:
                    if os.path.isfile(zb_file):
                        if not os.path.isdir(version_dir + '/zbrush/'):
                            os.makedirs(version_dir + '/zbrush/')
                        shutil.copyfile(zb_file, version_dir + '/zbrush/' + os.path.basename(zb_file) )

                # Clean and save file
                #self.recovery_sets_n_layers()

                self.remove_global_ctrl()

                pm.select(cl=True)
                if cmds.objExists('|master|shape|nurbs_hair_grp'):
                    pm.delete('|master|shape|nurbs_hair_grp')

                # recovery root node
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


