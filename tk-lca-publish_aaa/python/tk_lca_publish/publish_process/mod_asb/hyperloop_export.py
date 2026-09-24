import os
import sys
import shutil
import hashlib
import math
from xml.dom.minidom import Document
from lxml.etree import Element, ElementTree, parse
import maya.standalone as std
std.initialize(name='python')
import pymel.core as pm
import maya.api.OpenMaya as om

TOOL_ROOT = os.getenv('LC_UTILITY')
sys.path.append('{}/linked_tools/srf_tools'.foramt(TOOL_ROOT))
from material_library_tool import maya_material_library as mml
reload(mml)

lca_rez_path = os.getenv('LCA_REZ')
convert_py = '{}/linked_tools/srf_tools/material_library_tool/faceset2attribute.py'.format(TOOL_ROOT)
hython = '{}/launchers/nza/linux/hython'.format(lca_rez_path)

abc_path = sys.argv[1]
xml_path = sys.argv[2]
v_dir    = sys.argv[3]
v_name   = sys.argv[4]
asset    = sys.argv[5]
color_id_r = sys.argv[6]
color_id_g = sys.argv[7]
color_id_b = sys.argv[8]

gpu_ma = v_dir + 'gpu_ma/' + asset + '.ma'
gpu_all = v_dir + '/gpu_ma/' + asset + '.abc'

gpu_hi = v_dir + 'gpu/hi.abc'
gpu_proxy = v_dir + 'gpu/proxy.abc'
gpu_color_id = v_dir + 'gpu/color_id.abc'
maya_hi = v_dir + 'res/hi/' + asset + '.mb'

ma_master = v_dir + asset + '.ma'
abc_master = v_dir + 'scene_graph_xml/hi.abc'

v_sub_dirs = ['scene_graph_xml', 'assembly_definition', 'gpu', 'gpu_ma', 'preview', 'res/hi']
for sub_dir in v_sub_dirs:
    if not os.path.isdir(v_dir + sub_dir):
        os.makedirs(v_dir + sub_dir)


def new_name(name):
    tokens = []
    for c in name:
        if c.lower() != c:
            tokens.append('_' + c.lower())
        elif c == ':':
            tokens.append('_')
        else:
            tokens.append(c)

    new_name = ''.join(tokens).lstrip('_')
    return new_name


pm.loadPlugin('AbcImport', quiet=True)
pm.loadPlugin('gpuCache', quiet=True)

n = pm.createNode('transform', name='master')

pm.addAttr(n, shortName='gas_info', longName='GasInfo', dt="string")

pm.setAttr("|master.gas_info", "gas", type="string")
pm.addAttr(n, shortName='modv', longName='modVersion', dt="string")
pm.addAttr(n, shortName='modp', longName='modPath', dt="string")
pm.setAttr( "|master.modVersion", v_name.split(".v")[-1], type="string" )
pm.setAttr( "|master.modPath", ma_master, type="string" )

n = pm.createNode('transform', name='poly', parent=n)
n = pm.createNode('transform', name='hi', parent=n)
top = pm.createNode('transform', name='mesh_grp', parent=n)

pm.AbcImport(abc_path, reparent=top)
mml.init_houdini_mesh()

for n in pm.listRelatives(top, ad=True):
    newName = new_name(n.nodeName())
    if n.nodeName() != newName:
        n.rename(newName)
def add_global_ctrl():

    # Clean rig group, if it exists
    if pm.objExists('|master|rig'):
        pm.delete('|master|rig')

    l_nodes = pm.importFile(os.path.dirname(__file__).replace('mod_asb', 'mod') + '/global_control.ma', returnNewNodes=True)
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
add_global_ctrl()
# Export /<version>/<asset>.ma
pm.select('|master', r=True)

pm.exportSelected(ma_master, f=True)

# Export /<version>/res/hi/<asset>.mb
pm.exportSelected(maya_hi, f=True)



# Export /<version>/scene_graph_xml/
mml.set_shader_to_face()
pm.select(top, r=True)
pm.AbcExport(
    j="-frameRange 1 1 -uvWrite -attrPrefix lca -writeFaceSets -dataFormat ogawa -root |master|poly|hi|mesh_grp -file " + abc_master)
cmd = '{hyt} {scp} {abc}'.format(hyt=hython, scp=convert_py, abc=abc_master)
os.system(cmd)

def make_elem(tag_name, attr_list):
    master_instance_elem = Element(tag_name)

    for attr in attr_list:
        master_instance_elem.set(str(attr[0]), str(attr[1]))

    return master_instance_elem
tree = parse(xml_path)
root = tree.getroot()
master_group = root.xpath("./instanceList/instance[@name='master']")[0]
arbit_list = make_elem("arbitraryList",[])
version_element = make_elem("attribute", [["name","modVersion"], ["type", "string"],["value", "{0}".format(v_name.split(".v")[-1])]])
arbit_list.append(version_element)
master_group.append(arbit_list)
tree = ElementTree(root)
tree.write(v_dir + 'scene_graph_xml/' + asset + '.xml', pretty_print=True)


# Export /<version>/gpu/hi.abc
pm.gpuCache('|master|poly|hi', startTime=1, endTime=1, optimize=True, optimizationThreshold=40000, writeMaterials=True,
            saveMultipleFiles=False, directory=v_dir + '/gpu', fileName='hi')


# Export /<version>/mesh.xml
def create_structure(doc, root_elem, root_node):
    if not pm.objExists(root_node):
        return

    l_nodes = pm.listRelatives(root_node)
    l_nodes.sort()
    for node in l_nodes:
        if node.type() == 'transform':
            trans = doc.createElement('transform')
            trans.setAttribute('name', node.fullPath())
            root_elem.appendChild(trans)
            create_structure(doc, trans, node)
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


doc = Document()
master = doc.createElement('transform')
master.setAttribute('name', '|master')
doc.appendChild(master)
poly = doc.createElement('transform')
poly.setAttribute('name', '|master|poly')
master.appendChild(poly)

res_node = doc.createElement('transform')
res_node.setAttribute('name', '|master|poly|hi')
poly.appendChild(res_node)
create_structure(doc, res_node, '|master|poly|hi')

f = open(v_dir + 'mesh.xml', 'w')
f.write(doc.toprettyxml(indent='    '))
f.close()


# Export /<version>/gpu/color_id.abc
def create_n_assign_shader(l_meshes, shader_name, color, transparency):
    new_color = [float(c) / 255.0 for c in color]
    shader = pm.shadingNode('lambert', asShader=True, name=shader_name)
    shader_sg = pm.sets(renderable=True, noSurfaceShader=True, empty=True, name=shader_name + 'SG')
    pm.connectAttr(shader.name() + '.outColor', shader_sg.name() + '.surfaceShader', f=True)

    shader.setAttr('transparency', transparency)
    shader.setAttr('color', new_color)

    pm.select(l_meshes, r=True)
    pm.sets(shader_sg, e=True, forceElement=True)


create_n_assign_shader(['|master'], 'opacity_s', [color_id_r, color_id_g, color_id_b], (0, 0, 0))
pm.gpuCache('|master', startTime=1, endTime=1, optimize=True, optimizationThreshold=40000, writeMaterials=True,
            directory=v_dir + 'gpu', fileName='color_id')

# Export /<version>/gpu/proxy.abc
pm.gpuCache('|master|poly|hi', startTime=1, endTime=1, optimize=True, optimizationThreshold=40000, writeMaterials=True,
            saveMultipleFiles=False, directory=v_dir + '/gpu', fileName='proxy')

pm.gpuCache('|master', startTime=1, endTime=1, optimize=False, writeMaterials=True, saveMultipleFiles=False, directory=v_dir + '/gpu_ma', fileName= asset)


# Export /<version>/gpu_ma/<asset>.ma (A faked gpu ma)


if sys.platform.startswith('win'):
    version = pm.about(v=True)
    maya_py = r'"C:/Program Files/Autodesk/Maya{}/bin/mayapy.exe"'.format(version)
else:
    maya_py = '{}/launchers/nyj/linux/mayapy'.format(lca_rez_path)

build_py = os.path.join(os.path.dirname(__file__), 'build_gpu_ma.py')
cmd_str = maya_py + ' ' + build_py + ' ' + gpu_all
print cmd_str
os.system(cmd_str)

# pm.sets('initialShadingGroup', e=True, forceElement='|master')
# for n in pm.listRelatives('|master', ad=True, type='mesh'):
#     pm.select(n, r=True)
#     try:
#         pm.polyReduce(p=50)
#     except:
#         continue
# pm.gpuCache('|master|poly|hi', startTime=1, endTime=1, optimize=True, optimizationThreshold=40000, writeMaterials=True, saveMultipleFiles=False, directory=v_dir + '/gpu', fileName='proxy')

# Export preview
pm.setFocus('modelPanel4')
# pm.lookThru('persp')
# pm.viewFit()
pm.playblast(startTime=1, endTime=1, format='image', filename=v_dir + 'preview/test', viewer=False, compression='jpg',
             offScreen=True)
if os.path.isfile(v_dir + 'preview/test.0001.jpg'):
    os.system('rvio_hw ' + v_dir + 'preview/test.0001.jpg -o ' + v_dir + 'preview/' + v_name + '.mov')
    shutil.move(v_dir + 'preview/test.0001.jpg', v_dir + 'preview/' + v_name + '.jpg')

# Export /<version>/assembly_definition/<asset>.ma
assembly_file = v_dir + 'assembly_definition/' + asset + '.ma'

shutil.copyfile(os.path.dirname(__file__).replace('mod_asb', 'mod') + '/assembly_definition.ma', assembly_file)
f = open(assembly_file, 'r')
l_lines = f.readlines()
f.close()

f = open(assembly_file, 'w')
for line in l_lines:
    new_line = line.replace('{ASSET}', asset)
    new_line = new_line.replace('{MAYA_FILE}', gpu_ma)
    new_line = new_line.replace('{GPU_CACHE_HI}', gpu_hi)
    new_line = new_line.replace('{GPU_CACHE_PROXY}', gpu_proxy)
    new_line = new_line.replace('{GPU_CACHE_COLOR_ID}', gpu_color_id)
    new_line = new_line.replace('{MAYA_FILE_hi}', maya_hi)
    f.write(new_line)
f.close()

os._exit(0)
