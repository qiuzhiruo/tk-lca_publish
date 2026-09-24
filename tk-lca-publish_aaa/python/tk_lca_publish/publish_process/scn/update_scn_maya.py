# -*- coding:utf-8 -*-

import os
import sys
import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import traceback
import time
import shutil
import xml.etree.ElementTree as ET

# sys.path.append('U:/toolset/lib/production/pipeline')
# sys.path.append('/mnt/utility/toolset/lib/production/pipeline')

import production.pipeline.mayaReferenceUtils as mru
reload(mru)

# sys.path.append('/mnt/utility/toolset/tools/gene/scene_operator')
# sys.path.append('U:/toolset/tools/gene/scene_operator')
import gene.scene_operator.sceneOperator as scnOp
reload(scnOp)

# sys.path.append('/mnt/utility/toolset/tools/gene/sgXmlParser')
# sys.path.append('U:/toolset/tools/gene/sgXmlParser')
import gene.sgXmlParser.sgXml_parser as sgxml
reload(sgxml)

import scn_assemblyOperator as asop
reload(asop)

sys.path.append( '/'.join(os.path.dirname(__file__).replace('\\','/').split('/')[:-1]) + '/gen' )
import convertHi2Lo as hi2lo
reload(hi2lo)


def open_maya(filename):
    try:
        cmds.file(filename, open=True, force=True )
    except:
        return 'Failed to open the scn file.\n' + filename
    return ''

def clearNS(ns):
    new_ns = []
    rm_ns = []
    for n in ns:
        if not pm.namespaceInfo(n, ls=True):
            try:
                pm.namespace(rm=n)
                rm_ns.append(n)
            except:
                print 'can not remove empty namespace: '+n
        else:
            new_ns.append(n)
    if len(rm_ns)>0 and len(new_ns)>0:
        clearNS(new_ns)

def clear_empty_namespace():
    try:
        namespaces = pm.namespaceInfo(lon=True, r=True)
        #exclude default system namespace
        namespaces.remove('UI')
        namespaces.remove('shared')
        clearNS(namespaces)
    except:
        return traceback.format_exc()
    return ''

def export_cache_xml(scn_name, scn_path):
    try:
        asset_selectors = pm.ls('*:asset_selector')
        asset_selectors.extend( pm.ls('*:*:asset_selector') )

        cached = []
        for a in asset_selectors:
            try:
                if a.hasAttr('activated') and a.attr('activated').get():
                    cached.append( pm.PyNode(a.name().replace(':asset_selector', ':master')) )
            except:
                print traceback.format_exc()

        if not cached:
            return ''

        xml_path = scn_path + 'cache_xml/'
        xml_name = scn_name + '.xml'

        # write to xml
        root = ET.Element('cacheXML')
        root.set('description', 'A list of the assets which should be cached in layout step')

        for c in cached:
            elem = ET.SubElement(root, 'instance')
            elem.set( 'name', c.name().replace(':master', '') )
            ET.SubElement(elem, 'path').set('value', c.fullPath() )

        tree = ET.ElementTree(root)
        if os.path.isdir(xml_path):
            shutil.rmtree(xml_path)
        os.makedirs(xml_path)
        tree.write(xml_path + xml_name)
    except:
        return traceback.format_exc()
    return ''

def import_asb(asb_path=[]):
    try:
        if not pm.objExists('|master'):
            return 'Failed to find group |master'

        # record reference path and version, used by relink step later
        try:
            asb_path.append( pm.PyNode('|master').attr('asbPath').get() )
        except:
            pass

        if not asb_path:
            return 'Failed to find the version of asb'

        mref = mru.MayaReferenceUtils()
        groups = mref.getNonReferenceNode('master', recursive=False)
        groups_parents = {}
        for g in groups:
            try:
                groups_parents[g] = g.getParent().name()
            except:
                pass

        # unparent non reference group
        for g in groups_parents.iterkeys():
            try:
                pm.parent(g, world=True)
            except:
                pass

        # import asb
        ref_file = pm.FileReference('|master')
        ref_file.importContents()

        # parent non reference back to group
        for g in groups_parents.iterkeys():
            try:
                pm.parent(g, groups_parents[g])
            except:
                pass
    except:
        return traceback.format_exc()

    return ''

def unfreeze_assets():
    try:
        topNode = None
        if '/asset/' in pm.sceneName().replace('\\', '/').lower():
            topNode = '|master'
        elif '/shot/' in pm.sceneName().replace('\\', '/').lower():
            topNode = '|assets'
        masters = mru.MayaReferenceUtils().listMasters(top=topNode)
        scnOp.AssetsActivator().activateAsset( masters )
    except:
        return traceback.format_exc()
    return ''

def getTransformation(a, space='object'):
    tran = {}
    txyz = a.getTranslation(space=space)
    rxyz = a.getRotation(space=space)
    sxyz = a.getScale()
    tran['tx'] = txyz[0] if a.hasAttr('tx') else None
    tran['ty'] = txyz[1] if a.hasAttr('ty') else None
    tran['tz'] = txyz[2] if a.hasAttr('tz') else None
    tran['rx'] = rxyz[0] if a.hasAttr('rx') else None
    tran['ry'] = rxyz[1] if a.hasAttr('ry') else None
    tran['rz'] = rxyz[2] if a.hasAttr('rz') else None
    tran['sx'] = sxyz[0] if a.hasAttr('sx') else None
    tran['sy'] = sxyz[1] if a.hasAttr('sy') else None
    tran['sz'] = sxyz[2] if a.hasAttr('sz') else None
    tran['globalScale'] = a.attr('globalScale').get() if a.hasAttr('globalScale') else None
    return tran

def setTransformation(a, tran):
    if not tran:
        return
    for attr in ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'globalScale']:
        if a.hasAttr(attr) and tran.has_key(attr) and tran[attr]!=None:
            lockState = a.attr(attr).isLocked()
            if not a.isReferenced():
                a.setAttr(attr, lock=False)
            try:
                a.attr(attr).set(tran[attr])
            except:
                pass
            if not a.isReferenced():
                a.setAttr(attr, lock=lockState)

def delete_root_rig():
    try:
        mref = mru.MayaReferenceUtils()
        masters = mref.listMasters(top='|master')

        # delete intermediate_ctrl
        for m in masters:
            ns = mref.getNamespace(m.name())
            if not pm.objExists(ns+':global_ctrl'):
                continue

            g_ctrl = pm.PyNode(ns+':global_ctrl')

            if pm.objExists(ns+':intermediate_root_ctrl'):
                try:
                    node = pm.PyNode(ns+':intermediate_root_ctrl')
                    tran = getTransformation( node, 'world' )
                    if pm.objExists(ns+':intermediate_ctrl'):
                        pm.delete( ns+':intermediate_ctrl' )
                    else:
                        pm.delete( node )
                    setTransformation(g_ctrl, tran)
                    g_ctrl.getShape().attr('visibility').set(1)
                except:
                    print traceback.format_exc()

        # delete |master|rig ctrl
        try:
            pm.delete('|master|rig')
        except:
            print traceback.format_exc()

        # delete the empty groups in case of unloading of assets
        try:
            empty_grps = []
            mref.findEmptyGrp('|master',empty_grps)
            pm.delete(empty_grps)
        except:
            print traceback.format_exc()
    except:
        return traceback.format_exc()
    return ''

def asb_scene_graph_xml(version, fullpath):
    # the filename should includes version number
    try:
        # Add version mark
        l_attrs = pm.listAttr("|master")
        if not 'asbVersion' in l_attrs:
            pm.addAttr("|master", shortName='asbv', longName='asbVersion', dt="string")
        if not 'asbPath' in l_attrs:
            pm.addAttr("|master", shortName='asbp', longName='asbPath', dt="string")

        pm.setAttr( "|master.asbVersion", version, type="string" )
        pm.setAttr( "|master.asbPath", fullpath, type="string" )

        publish_path = os.path.dirname( fullpath )
        publish_name = os.path.basename( fullpath )[:-3]
        if not publish_path.endswith('/'):
            publish_path = publish_path + '/'

        # export scene graph xml
        if os.path.isdir( publish_path + '/scene_graph_xml' ):
            shutil.rmtree( publish_path + '/scene_graph_xml' )

        os.makedirs( publish_path + '/scene_graph_xml' )
        asb_xml_path = publish_path + '/scene_graph_xml/' + publish_name + '.xml'
        # export asb xml file
        xml = sgxml.SgXmlParser()
        xml.publishAsb(asb_xml_path)
    except:
        return traceback.format_exc()
    return ''

def export_scn_file(publish_name, publish_path):
    try:
        tank_file = publish_path + publish_name + '.ma'

        # Add rig
        ctrl = asop.ScnAssemblyOperator()
        if not ctrl.add_ctrl():
            return 'Errors when adding rig and control, check the console!'

        # get all of models' references for shotgun linking
        mod_list = ctrl.listModReferences()

        # lock assets
        assetLock = scnOp.AssetsActivator2()
        assetLock.deactivateAssets(mod_list)

        # catch errors by variables and deal with them after deleting rig, as we don't want to left scraps if any failure of publish
        error_export = False
        try:
            # select and export
            pm.select('|master|asb', replace=True)
            pm.select('|master|rig', add=True)
            pm.exportSelected( tank_file, force=True, options="v=0;", type="mayaAscii", pr=True, es=True)
        except:
            error_export = True

        # delete rig
        ctrl.delete_ctrl()
        pm.select(cl=True)

        if error_export:
            return 'Failed to export .ma! Check the |master|asb name'

    except:
        return traceback.format_exc()
    return ''

def convert_to_low(fullpath):
    try:
        hi2lo.ConvertHi2Lo( fullpath, overwrite=True ).convert()
    except:
        return 'Failed to convert asb to low resolution file!'
    return ''

def close_maya():
    try:
        cmds.file(new=True, force=True)
    except:
        return traceback.format_exc()
    return ''

def asb_version_modify(fullpath, asb_path):
    contents = []
    with open(fullpath, 'r') as f:
        for line in f:
            contents.append(line)
    # there is no need to close f with this syntax

    asb_name = os.path.basename(asb_path)
    for i in range(len(contents)):
        if contents[i].startswith('file ') and asb_name in contents[i]:
            buffer = contents[i].replace('\\', '/').split('/')
            for b in range(len(buffer)):
                if asb_name in buffer[b]:
                    buffer[b-1] = asb_path.replace('\\', '/').split('/')[-2]
            contents[i] = '/'.join( buffer )

    file_handle = open(fullpath, 'w')
    file_handle.writelines(contents)
    file_handle.close()

def main(filename_work_old):
    scn_task_path = os.path.dirname( filename_work_old )
    scn_task_name = os.path.basename( filename_work_old )   # task file name with version number and .ma
    scn_name = scn_task_name.split('.')[0]  # scn name without version number
    version = scn_task_name.split('.')[-2].replace('v', '')
    if not scn_task_path.endswith('/'):
        scn_task_path = scn_task_path + '/'

    time_folder = time.strftime('%y%m%d%H%M%S', time.localtime())
    # backup publish file firstly
    scn_publish_path = scn_task_path.replace('task/maya', 'publish').replace('work', 'proj') + scn_task_name[:-3] + '/'
    backup_path = scn_publish_path + '/backup/' + time_folder + '/'
    print backup_path
    if not os.path.isdir( backup_path ):
        os.makedirs( backup_path )
    try:
        shutil.copyfile( scn_publish_path + scn_name + '.ma', backup_path + scn_name + '.ma' )
        if os.path.isfile( scn_publish_path + 'scene_graph_xml/' + scn_name + '.xml' ):
            shutil.copyfile( scn_publish_path + 'scene_graph_xml/' + scn_name + '.xml', backup_path + scn_name + '.xml' )
        if os.path.isfile( scn_publish_path + 'cache_xml/' + scn_name + '.xml' ):
            shutil.copyfile( scn_publish_path + 'cache_xml/' + scn_name + '.xml', backup_path + scn_name + '.cache.xml' )
    except:
        return traceback.format_exc()
    # backup task file
    backup_path = os.path.dirname(filename_work_old) + '/backup/' + time_folder + '/'
    print backup_path
    if not os.path.isdir( backup_path ):
        os.makedirs( backup_path )
    try:
        shutil.copyfile( filename_work_old, backup_path + os.path.basename(filename_work_old) )
    except:
        return traceback.format_exc()

    # we need open the upper version because that the older version was locked for the specified asb versoin
    filename_work_latest = scn_task_path + '.'.join(scn_task_name.split('.')[:-2]) + '.v' + format(int( scn_task_name.split('.')[-2][1:] )+1, '03d' ) + '.ma'
    if not os.path.isfile(filename_work_latest):
        return 'Failed to find latest version: ' + filename_work_latest

    err = open_maya(filename_work_latest)
    if err:
        return err, '\nFailed to open file ' + filename_work_latest

    err = clear_empty_namespace()
    if err:
        return err, '\nFailed to clear namespace'

    if not os.path.isfile( scn_publish_path + scn_name + '.ma' ):
        return 'Failed to find the publish version: ' + scn_publish_path + scn_name + '.ma'

    err = export_cache_xml(scn_name, scn_publish_path)
    if err:
        return err, '\nFailed to export cache xml'

    latest_asb_path = []
    err = import_asb( latest_asb_path )
    if err:
        return err, '\nFailed to import asb'

    err = unfreeze_assets()
    if err:
        return err, '\nFailed to unfreeze assets'

    err = delete_root_rig()
    if err:
        return err, '\nFailed to delete root rig'

    err = asb_scene_graph_xml(version, scn_publish_path+scn_name+'.ma')
    if err:
        return err, '\nFailed to export asb xml'

    err = export_scn_file( scn_name, scn_publish_path )
    if err:
        return err, '\nFailed to export scn file'

    err = convert_to_low( scn_publish_path+scn_name+'.ma' )
    if err:
        return err, '\nFailed to convert model from hi to low'

    close_maya()

    # modify asb version in old task file, to match the old publish version
    asb_version_modify( filename_work_old, latest_asb_path[0] )

    return ''


