import os
import sys
import re
try:
    import maya.standalone
    maya.standalone.initialize()
except:
    pass

import math
import maya.cmds as cmds
import pymel.core as pm
import shutil
import publish_mod_files
for plugin_name in ['gpuCache', 'AbcExport', 'AbcImport']:
    if not pm.pluginInfo(plugin_name, query=True, loaded=True):
        pm.loadPlugin(plugin_name)
if pm.pluginInfo('mtoa', query=True, loaded=True):
    pm.unloadPlugin('mtoa', force =1)


def add_global_ctrl(asset_type):
    if asset_type=='asb':
        return
    # Clean rig group, if it exists
    if pm.objExists('|master|rig'):
        pm.delete('|master|rig')

    l_nodes = pm.importFile(os.path.dirname(__file__) + '/global_control.ma', returnNewNodes=True)
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

    #pm.move(rig_node, [(bbox.min()[0] + bbox.max()[0])/2, bbox.min()[1], (bbox.min()[2] + bbox.max()[2])/2])
    # Scale the global control
    l_rig_nodes = pm.listRelatives(rig_node, ad=True, type='transform')
    l_rig_nodes.append(rig_node)
    l_locked_attr = []
    for n in l_rig_nodes:
        for attr in ['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']:
            if pm.getAttr(n.name()+'.' + attr, lock=True):
                l_locked_attr.append(n.name()+'.' + attr)
                pm.setAttr(n.name()+'.' + attr, lock=False)

    s = math.sqrt( (bbox.max()[0] - bbox.min()[0])**2 + (bbox.max()[2] - bbox.min()[2])**2 )
    if s < 0.7:
        s = 0.7
    print 'scale : ',s,bbox
    pm.scale(rig_node, [s, s, s])
    pm.select(rig_node, r=True)
    pm.mel.eval('FreezeTransformations;')
    pm.delete(rig_node, ch=True)

    for attr in l_locked_attr:
        pm.setAttr(attr, lock=True)

    # lock the control if it's not a chr or an asb asset
    if global_ctrl:
        if asset_type in ['chr', 'veh', 'asb']:
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

    rig_node = pm.parent(rig_node, '|master')

    # Lock |master and |master|poly
    for node_name in ['|master', '|master|poly']:
        node = pm.ls(node_name)[0]
        for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz']:
            node.setAttr(attr, lock=True, keyable=False )

    return

def delete_ai(file):
    ai_transform_re = re.compile(r'.*\"\.ai_translator"\s\-type\s\"string\".*')
    new_line=[]
    with open(file, 'r') as f:
        for line in f.readlines():
            if ai_transform_re.match(line):
                continue
            new_line.append(line)

    nf = open(file, 'w+')
    for line in new_line:
        nf.write(line)

    nf.close()
    os.chmod(file,0774)


def clear_att():
    TR_ATTRS=['translateX','translateY','translateZ','rotateX','rotateY','rotateZ','scaleX','scaleY','scaleZ']
    all_tr=pm.ls(type='transform')
    for tr in all_tr:
        for arr in TR_ATTRS:
            if 'scale' in arr:
                tr.setAttr(arr,1)
            else:
                tr.setAttr(arr,0)

def main(abc_file):
    ProjectStr=r"/projects/(\w{3})/asset/(\w+)/(\w+)/(\w{3})/"
    ProjectStrC=re.compile(ProjectStr)
    results=ProjectStrC.findall(abc_file.replace("\\","/"))
    AssetType=results[0][1]
    cmds.AbcImport(abc_file, mode="import")

    if AssetType=='asb':
        all_asset=list(set([sh.split('|proxy', 1)[0] for sh in cmds.ls(l=True, type="mesh")]))
        clear_att()
        for asset_node in all_asset:
            parent_node = asset_node.rsplit('|', 1)[0]
            cmds.delete(asset_node)
            asset_name=asset_node.split('|')[-1]
            cmds.createNode('transform',n=asset_name,parent=parent_node)
            gpu_node = cmds.createNode('gpuCache', n=asset_name+'gpu', parent=asset_node)
            cmds.setAttr(gpu_node + '.cacheFileName', abc_file, type="string")
            cmds.setAttr(gpu_node + '.cacheGeomPath', asset_node, type="string")

    else:
        for sh in cmds.ls(l=True, type="mesh"):
            parent_node = sh.rsplit('|', 1)[0]
            cmds.delete(sh)
            gpu_node = cmds.createNode('gpuCache', n=sh.rsplit('|', 1)[-1], parent=parent_node)
            cmds.setAttr(gpu_node + '.cacheFileName', abc_file, type="string")
            cmds.setAttr(gpu_node + '.cacheGeomPath', sh, type="string")
            
            for attr in ['.tx', '.ty', '.tz', '.rx', '.ry', '.rz', '.sx', '.sy', '.sz']:
                cmds.setAttr(parent_node+attr, lock=True, keyable=False )
                
    pm.gpuCache(pm.ls( type= 'gpuCache'),q=1 ,waitForBackgroundReading=1)
    add_global_ctrl(AssetType)
    ma_file=abc_file[:-3] + 'ma'
    pm.saveAs(ma_file)
    delete_ai(ma_file)

    return

if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    try:
        maya.standalone.uninitialize()
    except:
        pass
    os._exit(0)
