# coding:utf-8
import sys
import os
from xml.etree import ElementTree
from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument("-a", "--abc", dest="abc_file", help="abc file path")
parser.add_argument("-m", "--mesh", dest="mesh_xml", help="output mesh xml path")
parser.add_argument("-s", "--scene", nargs=2, dest="scene_graph_xml", help="input & output scene graph xml path")
options = parser.parse_args()
if not options.abc_file:
    print 'No abc file'
    sys.exit(0)

abc_file = options.abc_file

import traceback
import maya.standalone as std
std.initialize(name='python')

# TODO: maya may crash while importing pymel. Use maya.cmds to clear the trap. 
import maya.cmds as cmds
try:
    cmds.loadPlugin('mtoa')
except:
    err = traceback.format_exc()
    if not 'was not found on MAYA_PLUG_IN_PATH' in err:
        cmds.loadPlugin('mtoa')

import pymel.core as pm
pm.loadPlugin('AbcImport', quiet=True)
pm.AbcImport(abc_file)

l_meshes = pm.ls(type='mesh')
l_top_nodes = []
for m in l_meshes:
    tokens = m.fullPath().split('|')
    l_top_nodes.append('|' + tokens[1])

l_top_nodes = list(set(l_top_nodes))

n_master = pm.createNode('transform', name='master')
n_poly = pm.createNode('transform', name='poly', parent=n_master)
n_hi = pm.createNode('transform', name='hi', parent=n_poly)

for t in l_top_nodes:
    n = pm.PyNode(t)
    n.setParent(n_hi)

# Create mesh.xml
if options.mesh_xml:
    from mesh_xml import Mesh_XML
    Mesh_XML(options.mesh_xml)

# Create scene_graph_xml
if options.scene_graph_xml:
    src = options.scene_graph_xml[0]
    dst = options.scene_graph_xml[1]
    print 'src', src
    bb = pm.PyNode('|master|poly|hi').getBoundingBox(invisible=True, space='world')

    tree = ElementTree.parse(src)
    root = tree.getroot()

    l_instances = root.getiterator("instance")
    for i in l_instances:
        if i.attrib['name'] in ['master', 'poly', 'hi']:
            i.getiterator('bounds')[0].attrib = {'minx':str(bb.min()[0]), 'miny':str(bb.min()[1]), 'minz':str(bb.min()[2]), 'maxx':str(bb.max()[0]), 'maxy':str(bb.max()[1]), 'maxz':str(bb.max()[2])}

    print 'dst', dst
    tree.write(dst)


os._exit(0)

