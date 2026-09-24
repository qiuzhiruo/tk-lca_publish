

import os
import sys
import pickle
from xml.etree import ElementTree
import shutil
import math

import maya.standalone as std
std.initialize(name='python')
import pymel.core as pm

pm.loadPlugin('sceneAssembly', quiet=True)
pm.loadPlugin('gpuCache', quiet=True)


pkl_file = sys.argv[1]
xml_file = sys.argv[2]
maya_file = sys.argv[3]
v_name = sys.argv[4]
asset = sys.argv[5]
version_dir = os.path.dirname(maya_file)


f = open(pkl_file, 'r')
d_hyperloop = pickle.load(f)
f.close()

def get_xform(n):
    for c in n.getchildren():
        if c.tag == 'xform':
            return c.attrib['value']

def build_instance(i_root, i_node, name_list):
    for c in i_root.getchildren():
        if c.tag != 'instance':
            build_instance(c, i_node, name_list)
        else:
            xform_str = get_xform(c)
            m = [float(a) for a in xform_str.split(' ')]
            if c.attrib['type'] == 'reference':


                if c.attrib['name'].startswith("hyper_asset_"):
                    asset_info_list = c.attrib['name'].split("_")
                    asset_info = "_".join(asset_info_list[2:-1])
                    asset_name = asset_info.rstrip('0123456789')


                elif c.attrib['name'].startswith("shotgun_asset_"):
                    asset_info_list = c.attrib['name'].split("_")
                    asset_info = "_".join(asset_info_list[2:-1])
                    asset_name = asset_info.rstrip('0123456789')

                else:
                    asset_name = asset_info.rstrip('0123456789')

                asset_fina_name = asset_name + str(name_list.count(asset_name)+1)
                name_list.append(asset_name)




                assembly_file = d_hyperloop[asset_name]['ma']

                ar = pm.createNode("assemblyReference")
                hl = pm.createNode("hyperLayout", n="hyperLayout_" + asset_fina_name)
                pm.connectAttr(hl.name()+".msg", ar.name()+".hl")
                ar.setAttr("definition", assembly_file)
                pm.mel.eval('source "/mnt/usr/autodesk/maya2017/scripts/others/AEassemblyNamespaceUtil.mel";')
                pm.mel.eval('AEassemblyChangeAttrNamespace "'+ar.name()+'.repNamespace" "'+asset_fina_name+'";')
                ar.rename(asset_fina_name + '_AR')
                pm.parent(ar, i_node)
                pm.xform(ar, m=m)
            else:
                new_node = pm.createNode('transform', name=c.attrib['name'].lower(), parent=i_node)
                pm.xform(new_node, m=m)
                build_instance(c, new_node, name_list)

tree = ElementTree.parse(xml_file)
root = tree.getroot()

for i in root.getiterator('instance'):
    if i.attrib['name'] == 'master':
        i_root = i

root = pm.createNode('transform', name='master')
i_node = pm.createNode('transform', name='asb', parent=root)
pm.addAttr(root, shortName='asbv', longName='asbVersion', dt="string")
pm.addAttr(root, shortName='asbp', longName='asbPath', dt="string")
pm.setAttr( "|master.asbVersion", version_dir.split('.')[-1][-3:], type="string" )
pm.setAttr( "|master.asbPath", maya_file, type="string" )
name_list = []
build_instance(i_root, i_node, name_list)

pm.gpuCache(pm.ls( type= 'gpuCache'),q=1 ,waitForBackgroundReading=1)

pm.saveAs(maya_file, f=True)

# Playblaster for preview
bbox = root.boundingBox()
x = math.sqrt((bbox[1][0] - bbox[0][0])**2 + (bbox[1][1] - bbox[0][1])**2 + (bbox[1][2] - bbox[0][2])**2 )
cam = pm.PyNode('persp')
cam.setTranslation(cam.getTranslation() * x / 100)

pm.playblast(startTime = 1, endTime=1, format='image', filename=version_dir + '/preview/test', viewer=False, compression='jpg', offScreen=True)
if os.path.isfile(version_dir + '/preview/test.0001.jpg'):
    shutil.move(version_dir + '/preview/test.0001.jpg', version_dir + '/preview/' + v_name + '.jpg')

pm.gpuCache('|master', startTime=1, endTime=1, optimize=True, optimizationThreshold=40000, writeMaterials=True, dir=version_dir + '/gpu', fileName='proxy')

import sys
sys.path.append( '/'.join(os.path.dirname(__file__).replace('\\','/').split('/')[:-1]) + '/gen' )
import sgXml_parser as sgxml

asb_xml_path = version_dir + '/scene_graph_xml/' + asset + '.xml'
xml = sgxml.SgXmlParser()
xml.exportXml(root, asb_xml_path)

os._exit(0)
