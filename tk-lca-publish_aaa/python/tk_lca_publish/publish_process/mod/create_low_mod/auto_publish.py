# -*- coding: utf-8 -*-
############################################
#
# Copyright (c) 2014 Light Chaser Animation
#
# Author: guanzejie
#
# Date: 2022.05
#
# Description:
#
############################################
import sys
# sys.path.append('U:/toolset/lib/3rd_party/sceneGraphXML')
# sys.path.append('/mnt/utility/toolset/lib/3rd_party/sceneGraphXML')
# sys.path.append('/Volumes/utility/toolset/lib/3rd_party/sceneGraphXML')
from xml.etree import ElementTree
import os
import pymel.core as pm
import maya.cmds as mc
from xml.dom.minidom import Document
import hashlib
import maya.api.OpenMaya as om
import shutil
import third_party.sceneGraphXML.maya2scenegraphXML as maya2scenegraphXML
import math
import srf.push_shader.push_shader as sps
import pprint
reload(sps)
# sys.path.append('/mnt/utility/toolset/lib/production')
from production.shotgun_connection import Connection
sg = Connection('get_project_info').get_sg()


def get_reduced_cnt(n):
    if n <= 6:
        return float(n)
    if 6 < n and n < 1000:
        return math.log(n + 53) * 50 - 197.87
    else:
        return 150 + (n - 1000) / 20.0


def get_bbox(n):
    bbox = n.getBoundingBox()
    return [abs(bbox[0][0] - bbox[1][0]), abs(bbox[0][1] - bbox[1][1]), abs(bbox[0][2] - bbox[1][2])]


def get_mesh_count(root_node):
    if not pm.objExists(root_node):
        return 0

    l_meshes = pm.listRelatives(root_node, ad=True, type='mesh')
    if len(l_meshes) == 0:
        return 0

    pm.select(l_meshes, r=True)
    cnt = pm.polyEvaluate(f=True)
    pm.select(cl=True)
    return cnt


def get_size_penalty(n, proxy_bbox):
    mesh_bbox = get_bbox(n)
    size_rate = []
    for j in range(3):
        if proxy_bbox[j] == 0:
            size_rate.append(0.000001)
        else:
            size_rate.append(mesh_bbox[j] / proxy_bbox[j])
    size_rate.sort()

    if size_rate[1] < 0.01:
        size_factor = size_rate[1] * 20 + 0.1
    elif size_rate[1] < 0.1:
        size_factor = (size_rate[1] - 0.01) * 7.777 + 0.3
    else:
        size_factor = 1.0

    return size_factor


def getcolor(image_path):
    from  PIL import Image,ImageStat
    if image_path.endswith('tif') or image_path.endswith('tx'):
        return [0.5,0.5,0.5]

    img=Image.open(image_path)
    color_list=ImageStat.Stat(img).mean
    cv=[c/255.0*1.2 for c in color_list]
    mc=max(cv)
    for i,c in enumerate(cv):
        if mc==c:
            cv[i]=mc*1.2
    return cv

def tex2color():
    file_list=pm.ls(type='file')
    shader_list={}
    for tex in file_list:
        tex_path=pm.getAttr(tex+'.fileTextureName')
        if not os.path.isfile(tex_path):
            continue

        color=getcolor(tex_path)
        l_shader=pm.listConnections(tex,type='lambert')

        for shader in l_shader:
            if shader.attr('color').inputs():
                pm.disconnectAttr(tex+'.outColor',shader+'.color')
                pm.setAttr(shader+'.color',color)
                shader_list[tex+'.outColor']=shader+'.color'

    return shader_list


def lock_hi():
    if not pm.objExists('|master|poly|hi'):
        return

    for node in pm.listRelatives('|master|poly|hi', ad=True, type='transform', path=True):
        for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
            node.setAttr(attr, lock=True, keyable=False)
    return


def add_global_ctrl(asset_type):
    if pm.objExists('|master|rig'):
        pm.delete('|master|rig')

    l_nodes = pm.importFile(os.path.dirname(os.path.dirname(__file__)) + '/global_control.ma', returnNewNodes=True)
    rig_node = l_nodes[0]
    l_lock_nodes = [rig_node]
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
        if pm.objExists('|master|poly|' + res):
            l_res_nodes.append(pm.ls('|master|poly|' + res)[0])
    try:
        l_res_nodes.append(pm.ls('|master|shape')[0])
    except:
        pass
    poly_node = pm.ls('|master|poly')[0]
    hi = pm.ls("|master|poly|hi")[0]
    vis = hi.getAttr("v")
    hi.setAttr("v", True)
    bbox = poly_node.boundingBox()
    hi.setAttr("v", vis)

    l_rig_nodes = pm.listRelatives(rig_node, ad=True, type='transform')
    l_rig_nodes.append(rig_node)
    l_locked_attr = []
    for n in l_rig_nodes:
        for attr in ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY',
                     'scaleZ']:
            if pm.getAttr(n.name() + '.' + attr, lock=True):
                l_locked_attr.append(n.name() + '.' + attr)
                pm.setAttr(n.name() + '.' + attr, lock=False)

    s = math.sqrt((bbox.max()[0] - bbox.min()[0]) ** 2 + (bbox.max()[2] - bbox.min()[2]) ** 2)
    if s < 0.7:
        s = 0.7
    pm.scale(rig_node, [s, s, s])
    pm.select(rig_node, r=True)
    pm.mel.eval('FreezeTransformations;')
    pm.delete(rig_node, ch=True)

    for attr in l_locked_attr:
        pm.setAttr(attr, lock=True)
    if global_ctrl:
        if asset_type in ['chr', 'veh', 'asb']:
            pm.connectAttr(global_ctrl.fullPath() + ".globalScale", global_ctrl.fullPath() + ".scaleX", f=True)
            pm.connectAttr(global_ctrl.fullPath() + ".globalScale", global_ctrl.fullPath() + ".scaleY", f=True)
            pm.connectAttr(global_ctrl.fullPath() + ".globalScale", global_ctrl.fullPath() + ".scaleZ", f=True)
            for attr in ['sx', 'sy', 'sz']:
                global_ctrl.setAttr(attr, lock=True, keyable=False, channelBox=False)
        else:
            global_ctrl.deleteAttr('globalScale')

    for node in l_lock_nodes:
        for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
            node.setAttr(attr, lock=True, keyable=False, channelBox=False)

    if root_ctrl_base:
        for attr in ['sx', 'sy', 'sz']:
            root_ctrl_base.setAttr(attr, lock=True, keyable=False, channelBox=False)
        for res_node in l_res_nodes:
            pm.select(root_ctrl_base, r=True)
            pm.select(res_node, tgl=True)
            pm.mel.eval('parentConstraint -mo -weight 1;')
            pm.mel.eval('doCreateScaleConstraintArgList 1 { "0","1","1","1","0","0","0","1","","1" };')

    elif root_ctrl:
        for attr in ['sx', 'sy', 'sz']:
            root_ctrl.setAttr(attr, lock=True, keyable=False, channelBox=False)
        for res_node in l_res_nodes:
            pm.select(root_ctrl, r=True)
            pm.select(res_node, tgl=True)
            pm.mel.eval('parentConstraint -mo -weight 1;')
            pm.mel.eval('doCreateScaleConstraintArgList 1 { "0","1","1","1","0","0","0","1","","1" };')

    rig_node = pm.parent(rig_node, '|master')

    for node_name in ['|master', '|master|poly']:
        node = pm.ls(node_name)[0]
        for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
            node.setAttr(attr, lock=True, keyable=False)

    return rig_node


def clean_sets_n_layers():
    l_sets = pm.ls(type='objectSet')
    d_sets = {}
    for obj_set in l_sets:
        if obj_set.type() == 'objectSet':
            d_sets[obj_set.name()] = pm.sets(obj_set, q=True)
            try:
                obj_set.clear()
            except:
                print 'Failed to clear set:', obj_set.name()

    l_layers = pm.ls(type='displayLayer')
    d_layers = {}
    for layer in l_layers:
        if layer.name() != 'defaultLayer':
            d_layers[layer.name()] = pm.editDisplayLayerMembers(layer, query=True, fullNames=True)
            try:
                pm.editDisplayLayerMembers("defaultLayer", d_layers[layer.name()], noRecurse=True)
            except:
                print 'Failed to clear layer:', layer.name()

    return

def remove_global_ctrl(rig_node):

    l_rig_nodes = pm.listRelatives(rig_node, ad=True)
    for n in l_rig_nodes:
        pm.lockNode(n, l=False)
    pm.delete(rig_node)

    if not pm.objExists('|master|poly|hi'):
        pm.createNode('transform', parent='|master|poly', name='hi')

    for node_name in ['|master', '|master|poly']:
        node = pm.ls(node_name)[0]
        for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
            node.setAttr(attr, lock=0, keyable=1 )

    n = pm.PyNode('|master|poly')
    n.setAttr("inheritsTransform", 1)
    return


def clean_sets_n_layers():
    l_sets = pm.ls(type = 'objectSet')
    d_sets = {}
    for obj_set in l_sets:
        if obj_set.type() == 'objectSet':
            d_sets[obj_set.name()] = pm.sets( obj_set, q=True )
            try:
                obj_set.clear()
            except:
                print 'Failed to clear set:', obj_set.name()

    l_layers = pm.ls(type='displayLayer')
    d_layers = {}
    for layer in l_layers:
        if layer.name() != 'defaultLayer':
            d_layers[layer.name()] = pm.editDisplayLayerMembers(layer, query=True, fullNames=True)
            try:
                pm.editDisplayLayerMembers("defaultLayer", d_layers[layer.name()], noRecurse =True )
            except:
                print 'Failed to clear layer:', layer.name()

    return (d_sets, d_layers)


def recovery_sets_n_layers(d_sets , d_layers):
    for obj_set, l_elements in d_sets.iteritems():
        try:
            pm.sets(obj_set, forceElement=l_elements )
        except:
            print 'Failed to recovery set:', obj_set

    for layer, l_elements in d_layers.iteritems():
        try:
            pm.editDisplayLayerMembers(layer, l_elements, noRecurse =True )
        except:
            print 'Failed to recovery layer:', layer

    return



def replaceBBoxWithLo( scene_xml_path):
    '''
    modify xml, need input the path to xml file
    '''
    if pm.objExists('|master|poly|lo'):
        bb = pm.PyNode('|master|poly|lo').getBoundingBox(invisible=True, space='world')
    else:
        return

    tree = ElementTree.parse(scene_xml_path)
    root = tree.getroot()

    l_instances = root.getiterator("instance")
    for i in l_instances:
        if i.attrib['name'] in ['master', 'poly', 'hi']:
            i.getiterator('bounds')[0].attrib = {'minx': str(bb.min()[0]), 'miny': str(bb.min()[1]),
                                                 'minz': str(bb.min()[2]), 'maxx': str(bb.max()[0]),
                                                 'maxy': str(bb.max()[1]), 'maxz': str(bb.max()[2])}
    tree.write(scene_xml_path)


def create_structure(doc,root_elem, root_node):
    if not pm.objExists(root_node):
        return

    l_nodes = pm.listRelatives(root_node)
    l_nodes.sort()
    for node in l_nodes:
        if node.type() == 'transform':
            trans = doc.createElement('transform')
            trans.setAttribute('name', node.fullPath())
            root_elem.appendChild(trans)
            create_structure(doc,trans, node)
        elif node.type() == 'mesh' and (not node.isIntermediate()):
            if pm.polyEvaluate(node, face=True) == 0:
                topology = hashlib.md5(' ').hexdigest()
            else:
                sl = om.MSelectionList()
                sl.add(node.fullPath())
                mesh_dag = sl.getDagPath(0)
                mesh_mfn = om.MFnMesh(mesh_dag)
                v = mesh_mfn.getVertices()
                v_str0 = '[' + ', '.join([str(i) for i in v[0]]) + ']'
                v_str1 = '[' + ', '.join([str(i) for i in v[1]]) + ']'
                topology = hashlib.md5(v_str0 + ' ' + v_str1).hexdigest()

            mesh = doc.createElement('mesh')
            mesh.setAttribute('name', node.fullPath())
            mesh.setAttribute('vertex', str(pm.polyEvaluate(node, vertex=True)))
            mesh.setAttribute('edge', str(pm.polyEvaluate(node, edge=True)))
            mesh.setAttribute('face', str(pm.polyEvaluate(node, face=True)))
            mesh.setAttribute('topology', topology)
            root_elem.appendChild(mesh)

    return


def create_dir_on_server(publish_path):
    print "_____________________________________________________create_dir_on_server"
    try:
        if not os.path.isdir(publish_path):
            os.makedirs(publish_path)
    except:
        print("error:create_dir_on_server")


def combine_set():
    print "_____________________________________________________combine_set"
    try:
        all_sets = pm.ls(type='objectSet')

        for i in all_sets:
            if not i.name().startswith('combine_'):
                continue

            set_objs = i.members()

            dist_root = set_objs[0].getParent()

            cmb_obj = pm.polyUnite(set_objs)[0]
            cmb_obj = pm.parent(cmb_obj, dist_root)
            pm.delete(cmb_obj, ch=True)
            pm.delete(i)
            pm.rename(cmb_obj, i.name())

        scene_clear = False
        while not scene_clear:
            scene_clear = True
            all_objs = pm.ls('|master|poly|hi', dag=True, type='transform')
            for i in all_objs:
                if not i.getChildren():
                    print i.name(), 'is an empty group.'
                    pm.delete(i)
                    scene_clear = False

    except:
        print("error:combine_set")

def clean_mod_files():
    print " _____________________________________________________clean_mod_files"
    try:
        node_hi = pm.PyNode('master|poly|hi')
        mc.lockNode('initialShadingGroup', l=0, lu=0)  # unlock srf node*
        pm.select(node_hi, r=True)
        pm.mel.eval('newCluster " -envelope 1";')
        mc.lockNode('initialShadingGroup', lu=1)  # lock node
        pm.select(node_hi, r=True)
        pm.refresh()

        l_nodes = pm.listRelatives(node_hi, type='mesh', ad=True)
        for n in l_nodes:
            if n.getAttr('vertexNormal', size=True) != 0:
                pm.polyNormalPerVertex(n, ufn=True)

        pm.select(node_hi, r=True)
        pm.delete(ch=True)

    except:
        print("error:clean_mod_files")


def maya_version_attr(publish_path, file_name):
    print " _____________________________________________________maya_version_attr"

    try:

        root_node = '|master'
        tank_file = publish_path + '/' + file_name + '.ma'

        dept = "mod"

        pm.lockNode(root_node, lock=False)
        l_attrs = pm.listAttr(root_node)
        if not dept + 'Version' in l_attrs:
            pm.addAttr(root_node, shortName=dept + 'v', longName=dept + 'Version', dt="string")
        if not dept + 'Path' in l_attrs:
            pm.addAttr(root_node, shortName=dept + 'p', longName=dept + 'Path', dt="string")

        pm.setAttr(root_node + "." + dept + "Version", "001", type="string")
        tank_file_str = tank_file.replace('/mnt/proj/', 'Z:/')
        pm.setAttr(root_node + "." + dept + "Path", tank_file_str, type="string")

    except:
        print("error:maya_version_attr")

def model_mesh_xml(publish_path):
    print " _____________________________________________________model_mesh_xml"
    try:
        mesh_xml = publish_path + '/mesh.xml'
        doc = Document()
        master = doc.createElement('transform')
        master.setAttribute('name', '|master')
        doc.appendChild(master)
        poly = doc.createElement('transform')
        poly.setAttribute('name', '|master|poly')
        master.appendChild(poly)
        if pm.objExists('|master|poly|hi'):
            res_node = doc.createElement('transform')
            res_node.setAttribute('name', '|master|poly|hi')
            poly.appendChild(res_node)
            create_structure(doc,res_node, '|master|poly|hi')

        f = open(mesh_xml, 'w')
        f.write(doc.toprettyxml(indent='    '))
        f.close()

    except:
        print("error:model_mesh_xml")


def auto_proxy(asset_type_, proj, file_name):
    print("____________________________________________________________________auto_proxy")
    try:

        root = "master"

        asset_type = asset_type_

        # Create proxy res
        if not pm.objExists('|master|poly|proxy'):

            n = pm.duplicate('|master|poly|hi', rr=True)[0]
            n.rename('proxy')

            pm.addAttr(n, shortName='ap', longName='auto_proxy', dt="string")
            meshs = pm.listRelatives(root, ad=True, type='mesh')

            if asset_type != 'env' and pm.polyEvaluate(meshs, f=True) < 100000 and len(meshs) < 500:
                proxy_bbox = get_bbox(n)

                l_meshes = pm.listRelatives(n, ad=True, type='mesh')
                for i in range(len(l_meshes)):
                    mesh = l_meshes[i]
                    mesh_cnt = pm.polyEvaluate(mesh, f=True)
                    size_factor = get_size_penalty(mesh.getParent(), proxy_bbox)
                    new_cnt = get_reduced_cnt(mesh_cnt) * size_factor
                    if int(math.ceil(new_cnt)) < mesh_cnt:
                        rate = (1.0 - float(new_cnt) / mesh_cnt) * 100.0
                        pm.polyReduce(mesh, ver=1, p=rate, shp=0, symmetryTolerance=0.01, keepQuadsWeight=1,
                                      vertexMapName="", replaceOriginal=1, cachingReduce=1, ch=1)
                        mesh_cnt2 = pm.polyEvaluate(mesh, f=True)
                        pm.select(mesh, r=True)
                        pm.mel.eval('DeleteAllHistory;')
                        print i, 'of', len(l_meshes), mesh.name().split('|')[
                            -1], mesh_cnt, '>', mesh_cnt2, '(' + str(int(rate)) + '%)'

            # Create proxy lock
            else:
                proxy_node = pm.PyNode('|master|poly|proxy')
                if not proxy_node.hasAttr('mod_proxy'):
                    proxy_node.addAttr('mod_proxy')

            # updata poly low cunt face num
            lo_cnt = get_mesh_count('|master|poly|proxy')

            filters = [['project', 'name_is', proj], ['code', 'is', file_name]]
            sg_assigned = sg.find('Asset', filters, ['tank_file'])
            sg.update('Asset', sg_assigned, {'sg_poly_count_lo': lo_cnt})

            return ""

    except:
        print("error:auto_proxy")


def asset_scene_graph_xml(publish_path, file_name):
    print " _____________________________________________________asset_scene_graph_xml"
    try:
        if not pm.objExists('|master|poly|hi'):
            return ""

        pm.loadPlugin('gpuCache', quiet=True)
        # pm.mel.eval(
        #     'python(\"import sys;sys.path.append(\\\"U:/toolset/lib/3rd_party/sceneGraphXML\\\");sys.path.append(\\\"/mnt/utility/toolset/lib/3rd_party/sceneGraphXML\\\");sys.path.append(\\\"/Volumes/utility/toolset/lib/3rd_party/sceneGraphXML\\\");import maya2scenegraphXML");')

        if os.path.isdir(publish_path + '/scene_graph_xml'):
            shutil.rmtree(publish_path + '/scene_graph_xml')

        os.makedirs(publish_path + '/scene_graph_xml')
        xmlFilePath = publish_path + '/scene_graph_xml/' + file_name + '.xml'
        md_path = publish_path + '/scene_graph_xml/md.abc'
        lo_path = publish_path + '/scene_graph_xml/lo.abc'
        proxy_path = publish_path + '/scene_graph_xml/proxy.abc'
        misc_path = publish_path + '/scene_graph_xml/misc.abc'
        shape_path = publish_path + '/scene_graph_xml/shape.abc'
        master_node = pm.PyNode('|master')

        l_trans = pm.listRelatives('|master', c=True, fullPath=True)
        for trans in l_trans:
            if not trans.fullPath() in ['|master|poly']:
                maya2scenegraphXML.setIgnore([trans.fullPath()])

        l_res = pm.listRelatives("|master|poly", c=True, fullPath=True)
        for res in l_res:
            if res.fullPath() in ['|master|poly|hi', '|master|poly|md', '|master|poly|lo']:
                maya2scenegraphXML.setComponent([res.fullPath()], refType='abc')
            else:
                maya2scenegraphXML.setIgnore([res.fullPath()])

        maya2scenegraphXML.setProxy(['|master|poly|hi'], 'proxy.abc')

        d_res = {'md': md_path, 'lo': lo_path, 'proxy': proxy_path}
        for res in ['md', 'lo', 'proxy']:
            if pm.objExists('|master|poly|' + res) and len(
                    pm.listRelatives('|master|poly|' + res, ad=True, type='mesh')) > 0:
                try:
                    pm.setAttr('|master|poly|' + res + ".visibility", True)
                except:
                    pass
                l_trans = [n.name() for n in pm.listRelatives('|master|poly|' + res)]

                pm.AbcExport(
                    j=" -writeColorSets -frameRange 1 1 -uvWrite -root " + " -root ".join(l_trans) + " -file " + d_res[res])

                if res != 'proxy':
                    maya2scenegraphXML.setProxy(['|master|poly|' + res], 'proxy.abc')
                else:
                    print ' no set proxy ', res

        if pm.objExists('|master|shape'):
            l_trans = [n.name() for n in pm.listRelatives("|master|shape")]
            pm.setAttr("|master|shape.visibility", True)
            pm.AbcExport(j="  -frameRange 1 1 -uvWrite -root " + " -root ".join(l_trans) + " -file " + shape_path)

        if pm.objExists('|master|misc'):
            pm.AbcExport(j="  -frameRange 1 1 -uvWrite -root |master|misc -file " + misc_path)

        maya2scenegraphXML.setArbAttr(['|master'], 'modVersion', master_node.attr('modVersion').get(), 'string')

        maya2scenegraphXML.maya2ScenegraphXML(['|master'], xmlFilePath, startFrame=1, endFrame=1, arbAttrs=['modVersion'])
        maya2scenegraphXML.deleteSgxmlAttrs('|master')
        master_node.deleteAttr('arbAttr_modVersion')

    except:
        print("error:asset_scene_graph_xml")

    try:
        hi = pm.PyNode('|master|poly|hi')
        if not hi.listRelatives(c=True, ad=True, type=['mesh', 'nurbsSurface', 'subdiv']):
            replaceBBoxWithLo(xmlFilePath)

    except:
        print("error:asset_scene_graph_xml")


def publish_mod_files(publish_path, file_name,asset_type_in):
    print " _____________________________________________________publish_mod_file"
    try:
        d_sets, d_layers = clean_sets_n_layers()

        publish_mode = 'poly'

        version_dir = publish_path
        asset_type = asset_type_in
        tank_file = publish_path+"/"+file_name+".ma"
        if publish_mode == 'poly':

            rig_node = add_global_ctrl(asset_type)
            print(5)
            n = pm.PyNode('|master|poly')
            pm.select(n, r=True)
            vis = n.getAttr("v")
            n.setAttr("v", True)
            pm.select(rig_node)
            for res in ['hi', 'md', 'lo']:
                if pm.objExists('|master|poly|' + res):
                    pm.select("|master|poly|" + res, add=True)

            if pm.objExists('|master|shape'):
                pm.select("|master|shape", add=True)
            pm.exportSelected(tank_file, force=True, options="v=0;", type="mayaAscii", pr=True, es=True)
            n.setAttr("v", vis)

            print 'Export tank_file:', tank_file

            if asset_type in ['asb', 'scn', 'dmt', 'efx', 'msc']:
                print 'Don\'t need to export md/lo/proxy res model for', asset_type, 'asset.'

            for res in ['hi', 'md', 'lo', 'proxy']:
                if not pm.objExists('|master|poly|' + res):
                    continue

                res_folder = version_dir + '/res/' + res
                res_file = res_folder + '/' + file_name + '.mb'
                if not os.path.isdir(res_folder):
                    os.makedirs(res_folder)

                n = pm.PyNode('|master|poly|' + res)

                pm.select(n, r=True)

                vis = n.getAttr("v")
                n.setAttr('v', True)
                pm.select(rig_node, add=True)
                if pm.objExists("|master|shape"):
                    pm.select("|master|shape", add=True)


                print(8)
                if res == 'hi':
                    pm.undoInfo(state=True, infinity=True)
                    pm.undoInfo(ock=True)
                    lock_hi()
                    pm.undoInfo(cck=True)

                    pm.exportSelected(res_file, force=True, options="v=0;", type="mayaBinary", pr=True, es=True)
                    pm.undo()
                    pm.undoInfo(state=True, infinity=False)

                else:
                    pm.exportSelected(res_file, force=True, options="v=0;", type="mayaBinary", pr=True, es=True)
                print(9)
                n.setAttr("v", vis)
                print 'Export ' + res + ' res:', res_file

                if res == 'proxy' and n.hasAttr('mod_proxy'):
                    print 'proxy_lock'
                    proxy_lock = os.path.join(os.path.dirname(res_file), 'mod_proxy.mb')
                    shutil.copyfile(res_file, proxy_lock)

            print(10)

            print 'Clean and save file'
            recovery_sets_n_layers(d_sets, d_layers)
            remove_global_ctrl(rig_node)

            pm.select(cl=True)


        return ""

    except:
        print("error:ublish_mod_file")


def gpu_cache(publish_path,file_name,asset_type_m, version_name_m, publish_dir_m):
    print " _____________________________________________________gpu_cache"
    try:
        shader_list = tex2color()

        pm.loadPlugin('gpuCache', quiet=True)

        l_meshes = pm.ls(type='mesh')
        for mesh in l_meshes:
            if '_SUBD|' in mesh.fullPath():
                pm.displaySmoothness(mesh, polygonObject=3)

        version_dir = publish_path
        asset_name = file_name
        asset_type = asset_type_m
        publish_dir = publish_dir_m
        version_name = version_name_m

        if not os.path.isdir(version_dir + '/gpu'):
            os.makedirs(version_dir + '/gpu')
        if not os.path.isdir(version_dir + '/assembly_definition'):
            os.makedirs(version_dir + '/assembly_definition')

        for res in ['|master|poly|hi', '|master|poly|proxy']:
            if pm.objExists(res):
                if len(pm.listRelatives(res, ad=True, type='mesh')) == 0:
                    continue
                try:
                    proxy = pm.listRelatives(res, ad=True)
                    for p in proxy:
                        try:
                            pm.setAttr(p + '.visibility', 1)
                        except:
                            pass
                except:
                    print 'Faild to set vis for', res
                res_and_shape = [res]
                if pm.objExists('|master|shape') and asset_type == 'env':
                    res_and_shape.append('|master|shape')
                if pm.objExists('|master|shape|efx_grp') and asset_type == 'prp':
                    res_and_shape.append('|master|shape|efx_grp')
                pm.gpuCache(res_and_shape, startTime=1, endTime=1, optimize=True, optimizationThreshold=40000,
                            writeMaterials=True, saveMultipleFiles=False, directory=version_dir + '/gpu',
                            dataFormat='ogawa', fileName=res.split('|')[-1])

        res_list = []
        for res in ['md', 'lo', 'proxy']:
            res_path = '|master|poly|' + res
            if pm.objExists(res_path):
                res_list.append(pm.PyNode(res_path))
                pm.parent(res_path, world=True)

        if pm.objExists('|master|rig'):
            pm.parent('|master|rig', world=True)

        pm.gpuCache('|master', startTime=1, endTime=1, optimize=False, writeMaterials=True, saveMultipleFiles=False,
                    directory=version_dir + '/gpu_ma', dataFormat='ogawa', fileName=asset_name)

        for res in res_list:
            if pm.objExists(res):
                pm.parent(res, '|master|poly|')

        if pm.objExists('rig'):
            pm.parent('rig', '|master')

        gpu_hi = version_dir + '/gpu/hi.abc'
        gpu_proxy = version_dir + '/gpu/proxy.abc'
        gpu_color_id = version_dir + '/gpu/color_id.abc'

        maya_proxy = version_dir + '/res/proxy/' + asset_name + '.mb'
        assembly_file = version_dir + '/assembly_definition/' + asset_name + '.ma'

        maya_hi = version_dir + '/res/hi/' + asset_name + '.mb'

        gpu_all = version_dir + '/gpu_ma/' + asset_name + '.abc'
        gpu_ma = version_dir + '/gpu_ma/' + asset_name + '.ma'

        rig_publish_dir = publish_dir.replace('mod', 'rig')
        rig_lay_file_path = rig_publish_dir + '/' + version_name + '/' + '{}.ma'.format(asset_name)

        if sys.platform.startswith('win'):
            version = pm.about(v=True)
            maya_py = r'"C:/Program Files/Autodesk/Maya{version}/bin/mayapy.exe"'.format(version=version)
        else:
            lca_rez_path = os.getenv('LCA_REZ')
            project = self.dialog.project['name']
            maya_py = '{}/launchers/{}/linux/mayapy'.format(lca_rez_path, project)

        build_py = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'build_gpu_ma.py')
        cmd_str = maya_py + ' ' + build_py + ' ' + gpu_all
        print cmd_str
        os.system(cmd_str)

        if not os.path.isfile(gpu_proxy):
            gpu_proxy = gpu_hi

        if asset_type == 'flg':
            gpu_cache = gpu_proxy
        else:
            gpu_cache = gpu_hi

        shutil.copyfile(os.path.dirname(os.path.dirname(__file__)) + '/assembly_definition.ma', assembly_file)
        f = open(assembly_file, 'r')
        l_lines = f.readlines()
        f.close()
        f = open(assembly_file, 'w')
        for line in l_lines:
            new_line = line.replace('{ASSET}', asset_name)
            new_line = new_line.replace('{GPU_CACHE}', gpu_cache)
            new_line = new_line.replace('{MAYA_FILE}', gpu_ma)
            new_line = new_line.replace('{GPU_CACHE_HI}', gpu_hi)
            new_line = new_line.replace('{MAYA_FILE_HI}', gpu_ma)
            if 'rep[0].rda' in line and asset_type == 'env':
                new_line = new_line.replace('{GPU_CACHE_PROXY}', gpu_hi)
            else:
                new_line = new_line.replace('{GPU_CACHE_PROXY}', gpu_proxy)
            new_line = new_line.replace('{GPU_CACHE_COLOR_ID}', gpu_color_id)
            new_line = new_line.replace('{MAYA_FILE_PROXY}', maya_proxy)
            new_line = new_line.replace('{MAYA_FILE_hi}', maya_hi)
            new_line = new_line.replace('{MAYA_FILE_Lay_rig}', rig_lay_file_path)
            f.write(new_line)
        f.close()

        for mesh in l_meshes:
            pm.displaySmoothness(mesh, polygonObject=0)

        for key in shader_list.keys():
            pm.connectAttr(key, shader_list[key])
        return ""
    except:
        print("error:gpu_cache")


def delete_auto_proxy():
    print("____________________________________________________________________delete_auto_proxy")
    try:

        # Create proxy res
        if pm.objExists('|master|poly|proxy'):
            n = pm.PyNode('|master|poly|proxy')
            if n.hasAttr('auto_proxy'):
                pm.delete(n)
                print 'delete auto proxy success'
            else:
                print 'delete auto proxy fail', n

        return ""

    except:
        print("error:delete_auto_proxy")


def create_sg_version(publish_path, file_name,proj,version_name,asset_type):
    print " _________________________________________________________create_sg_version"
    try:

        local_path = publish_path + '/'

        desc_txt = "AUTO PUBLISH"
        desc_txt = desc_txt.decode('utf-8')
        description = desc_txt

        filters = [ ['name', 'is', proj]]
        project_ = sg.find_one('Project', filters, ['name'])

        filters1 = [['name', 'is', "Guan Zejie"]]
        user_ = sg.find_one('HumanUser', filters1, ['name'])

        filters2 = [['project', 'name_is', proj], ['code', 'is', file_name]]
        sg_diffculty = sg.find_one('Asset', filters2, ['tank_file'])

        filters3 = [['project.Project.name', 'is', proj], ['entity', 'name_is', file_name],["content", "is", "model"]]
        task_= sg.find_one('Task', filters3, ['content'])

        print(project_,user_,sg_diffculty,task_)

        d_version = {'project': project_, 'entity': sg_diffculty, \
                     'code': version_name, \
                     'description': description, 'user': user_, \
                     'sg_version_folder': {'local_path':local_path,'name': file_name+".ma", 'content_type': None, 'link_type': 'local'}, \
                     'sg_task': task_, 'sg_version_type': "Downstream", \
                     'tag_list': [],'created_by': user_}

        v_info = sg.create('Version', d_version)

        task_info = sg.find_one('Task', filters3, ['step'])
        l_tasks = sg.find('Task', filters3 , ['step'])
        l_related_tasks = [task_info]

        print d_version

        for task in l_tasks:

            l_related_tasks.append(task)

        sg.update('Version', v_info['id'], {'sg_related_tasks': l_related_tasks})

        return ""

    except:
        print("error:create_sg_version")


def lock_transtorm():
    print"____________________________________________________________________lock_transtorm"
    TR_ATTRS = ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ',
                'visibility']

    try:
        if not mc.objExists('|master|poly|hi'):
            return u'没有找到 |master|poly|hi 组。'

        l_meshes = mc.listRelatives('|master|poly|hi', ad=True, type='transform', path=True)
        if not l_meshes:
            return ""

        for mesh in l_meshes:
            pm.lockNode(mesh, lock=0)
            for attr in TR_ATTRS:
                pm.setAttr(mesh + '.' + attr, l=True)

        return ""

    except:
        print("error:lock_transtorm")


def setup(version_one):

    list_path_brok = version_one.split("/")

    file_name = list_path_brok[-5]

    version_name = list_path_brok[-1][:-3]

    asset_type = list_path_brok[-6]

    projcet_m = list_path_brok[-8].upper()

    publish_path = os.path.join("/mnt/proj", list_path_brok[3], list_path_brok[4], list_path_brok[5], list_path_brok[6],
                                list_path_brok[7], list_path_brok[8], "publish", list_path_brok[-1][:-3])

    publish_dir_m = os.path.join("/mnt/proj", list_path_brok[3], list_path_brok[4], list_path_brok[5], list_path_brok[6],
                                list_path_brok[7], list_path_brok[8], "publish")
    print(publish_path)

    on_publish(publish_path,file_name,asset_type, version_name, publish_dir_m, projcet_m)


def on_publish(publish_path,file_name,asset_type, version_name, publish_dir_m, projcet_m):
    create_dir_on_server(publish_path)
    combine_set()
    clean_mod_files()
    maya_version_attr(publish_path, file_name)
    model_mesh_xml(publish_path)
    auto_proxy(asset_type, projcet_m, file_name)
    asset_scene_graph_xml(publish_path, file_name)
    publish_mod_files(publish_path, file_name, asset_type)
    gpu_cache(publish_path, file_name, asset_type, version_name, publish_dir_m)
    create_sg_version(publish_path, file_name, projcet_m, version_name,asset_type)
    lock_transtorm()
    mc.file(save=True, force=True)

# version_one = "/mnt/work/projects/can/asset/prp/td_prp_test_a/mod/task/maya/td_prp_test_a.mod.model.v018.ma"
#
# setup(version_one)