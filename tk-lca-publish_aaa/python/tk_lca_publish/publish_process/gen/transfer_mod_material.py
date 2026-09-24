# -*- coding: utf-8 -*-
# ========================================
#
# Author:
#
# Date: 2026.3
#
# Description:
#
# ========================================
TOOL_ID = u"112"
TOOL_NAME = u"导入 polyTexture"
CATEGORY = u"Local"
TOOL_TIP = u"Local artist sandbox tool"

# -*- coding:utf-8 -*-
import maya.OpenMaya as om
import maya.cmds as mc
import maya.cmds as cmds
import os

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
                    pass


class find_source():
    def __init__(self, node_name):
        self.l_processed_nodes = []
        self.l_terminals = []
        self.l_history_nodes = [n.name() for n in cmds.listHistory(node_name)]
        # try to find orig attribute,if not go recursion
        if self.find_orig_attr(node_name):
            return
        else:
            self.find_in_mesh(node_name)
        return

    def find_in_mesh(self, node_name):
        self.l_processed_nodes.append(node_name)
        l_in_meshes = []
        l_cons = cmds.listConnections(node_name, d=False, s=True, c=True, p=True)

        for con in l_cons:
            att_type = cmds.getAttr(con[0], type=True)
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
        if cmds.objExists(node_name) and cmds.attributeQuery('origShape', node=node_name, exists=True):
            tmp_terminals_list = cmds.getAttr(node_name + '.origShape').split(';')
            for tmp_terminals in tmp_terminals_list:
                if cmds.objExists(tmp_terminals):
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
            pass


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


def apply_uv(uv_file, check=True, import_node_list=[]):
    scene_name = cmds.file(q=True, sn=True)
    if scene_name and '.rig.' in scene_name:
        replace_uvmap_folliclemap()

    if check:
        if not os.path.isdir(uv_file.rsplit('/', 2)[0] + '/mat_info'):
            print 'No mat_info data,ignore.'
            return

    skip_mesh = []
    print 'Start Apply UV Process...'
    print 'UV File:', uv_file
    print 'Scene File:', scene_name

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

                if not cmds.objExists(m_path):

                    print '\tMissing:', m_path, 'Skip'
                    continue
                else:
                    n = str(m_path)

            if not cmds.objExists(n):
                print m_path, 'Skip'
                continue

            if n.isIntermediateObject():
                print '\tIntermediate Object:', m_path, 'Skip'
                continue

            # find which mesh to apply UV
            f = find_source(m_path)
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
                if not cmds.objExists(dst_mesh):
                    continue
                if cmds.attributeQuery('baduvTag', node=dst_mesh, exists=True):
                    cmds.deleteAttr(dst_mesh + '.baduvTag')

                if cmds.polyEvaluate(dst_mesh, vertex=True) != int(m_v_cnt):
                    skip_mesh.append(dst_mesh)
                    print '\t\tSkipped:', dst_mesh, cmds.polyEvaluate(dst_mesh, vertex=True), 'vtx, not match', m_v_cnt
                    continue

                if cmds.polyEvaluate(dst_mesh, edge=True) != int(m_e_cnt):
                    skip_mesh.append(dst_mesh)
                    print '\t\tSkipped:', dst_mesh, cmds.polyEvaluate(dst_mesh, edge=True), 'edges, not match', m_e_cnt
                    continue

                if cmds.polyEvaluate(dst_mesh, face=True) != int(m_f_cnt):
                    skip_mesh.append(dst_mesh)
                    print '\t\tSkipped:', dst_mesh, cmds.polyEvaluate(dst_mesh, face=True), 'faces, not match', m_f_cnt
                    continue

                all_uvsets = cmds.polyUVSet(dst_mesh, allUVSets=True, q=True)
                try:
                    cmds.polyUVSet(dst_mesh, uvSet='uv_srf', delete=True)
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

                    if not uvset in all_uvsets:
                        cmds.polyUVSet(dst_mesh, uvSet=uvset, create=True)

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
                    l_con = cmds.listConnections(dst_mesh, d=True, s=False, c=True, p=True)
                    if len(l_con) > 0:
                        l_con[0][0].disconnect(l_con[0][1])
                        l_con[0][0].connect(l_con[0][1].name(), f=True)

        except:
            print '\tFailed to apply uv to mesh:', m_path



    __add_skip_tag(skip_mesh)

    pd_list = cmds.ls(type='polyMapDel')
    if pd_list:
        cmds.delete(pd_list)

    return skip_mesh


def get_uv_and_srf():
    print('======================================= push uv shader ==============================================')
    listdirTemp = cmds.file(q=True, sn=True)
    listdir = normal_path(listdirTemp)
    try:
        cmds.lockNode('initialShadingGroup', lock=False, lockUnpublished=False)
        cmds.lockNode('renderPartition', lock=False, lockUnpublished=False)
        cmds.lockNode('initialParticleSE', lock=False, lockUnpublished=False)
    except:
        pass

    try:
        apply_uv(get_uv_file_path())

        cmds.file(save=True)
    except:
        from production.feishu_utils import lca_feishu
        lca_feishu.main(to_user_list=['xiaoyu2', 'zejie', 'zhenlin', 'pangxuan', 'wangqi2'],
                        title=u'apply_uv UV拉取失败 !',
                        message='file_path: \n {}'.format(listdir),
                        app='warning')

    try:
        print("latest uv is applied, push shader")
        import srf.push_shader.push_rig_shader as sp
        reload(sp)
        sp.push_rig_shader()

        cmds.file(save=True)
    except:
        from production.feishu_utils import lca_feishu
        lca_feishu.main(to_user_list=['xiaoyu2', 'zejie', 'zhenlin', 'pangxuan', 'wangqi2'],
                        title=u'push_rig_shader 材质拉取失败 !',
                        message='file_path: \n {}'.format(listdir),
                        app='warning')

    print('======================================= push uv shader end ==============================================')
    return ''

def reconnect_mod_transparent(mesh, transparentAttr):
    """
    Reconnect mesh.mod_transparent to all shaders used by this mesh
    """
    src_attr = mesh + '.' + transparentAttr

    if not mc.objExists(mesh + '.' + transparentAttr):
        return

    # 找到 mesh 的 shape
    shapes = mc.listRelatives(mesh, shapes=True, fullPath=True) or []
    if not shapes:
        return

    # 找 shadingEngine
    shading_groups = mc.listConnections(shapes, type='shadingEngine') or []
    shading_groups = list(set(shading_groups))

    for sg in shading_groups:
        shaders = mc.listConnections(sg + '.surfaceShader', s=True, d=False) or []
        for shader in shaders:
            # Arnold aiStandardSurface
            if mc.nodeType(shader) == 'aiStandardSurface':
                target_attr1 = shader + '.opacity'   # 或 transmission，看你项目定义
                if not mc.isConnected(src_attr, target_attr1):
                    if mc.nodeType(shader) == 'aiStandardSurface':
                        mc.connectAttr(src_attr, target_attr1, force=True)
            else:
                # Maya 标准材质
                if mc.attributeQuery('transparencyR', node=shader, exists=True):
                    target_attr1 = shader + '.transparencyR'
                    if not mc.isConnected(src_attr, target_attr1):
                        mc.connectAttr(src_attr, target_attr1, force=True)
                if mc.attributeQuery('transparencyG', node=shader, exists=True):
                    target_attr2 = shader + '.transparencyG'
                    if not mc.isConnected(src_attr, target_attr2):
                        mc.connectAttr(src_attr, target_attr2, force=True)
                if mc.attributeQuery('transparencyB', node=shader, exists=True):
                    target_attr3 = shader + '.transparencyB'
                    if not mc.isConnected(src_attr, target_attr3):
                        mc.connectAttr(src_attr, target_attr3, force=True)

                    # try:
                    #     print('Reconnect:', src_attr, '->', target_attr1)
                    # except Exception as e:
                    #     print('Failed connect:', src_attr, target_attr1, e)

def reconnect_imported_mod_transparent(mesh, transparentAttr):
    """
    Reconnect mesh.mod_transparent to all shaders used by this mesh
    """
    orig_mesh =  mesh.replace('tex:', '')
    if not mc.objExists(orig_mesh):
        return

    import_mesh_shape = mc.listRelatives(mesh, shapes=True, fullPath=True) or []
    if not import_mesh_shape:
        return

    # 找到 mesh 的 shape
    shapes = mc.listRelatives(orig_mesh, shapes=True, fullPath=True) or []
    if not shapes:
        return

    src_attr = import_mesh_shape[0] + '.' + transparentAttr
    tar_attr = shapes[0] + '.' + transparentAttr

    if not mc.objExists(src_attr):
        return
    else:
        if not mc.objExists(tar_attr):
            print(shapes[0] + 'transparentAttr')
            cmds.addAttr(shapes[0], ln=transparentAttr, at='double', min=0, max=1, dv=0)
        cmds.setAttr(shapes[0] + '.' + transparentAttr, k=0)
        cmds.setAttr(shapes[0] + '.' + transparentAttr, e=1, cb=1)
        transparentValue = cmds.getAttr(src_attr)
        cmds.setAttr(tar_attr, transparentValue)

    # 找 shadingEngine
    shading_groups = mc.listConnections(shapes, type='shadingEngine') or []
    shading_groups = list(set(shading_groups))

    for sg in shading_groups:
        shaders = mc.listConnections(sg + '.surfaceShader', s=True, d=False) or []
        for shader in shaders:
            # Arnold aiStandardSurface
            if mc.nodeType(shader) == 'aiStandardSurface':
                target_attr1 = shader + '.opacity'   # 或 transmission，看你项目定义
                if not mc.isConnected(tar_attr, target_attr1):
                    if mc.nodeType(shader) == 'aiStandardSurface':
                        mc.connectAttr(tar_attr, target_attr1, force=True)
            else:
                # Maya 标准材质
                if mc.attributeQuery('transparencyR', node=shader, exists=True):
                    target_attr1 = shader + '.transparencyR'
                    if not mc.isConnected(tar_attr, target_attr1):
                        mc.connectAttr(tar_attr, target_attr1, force=True)

                if mc.attributeQuery('transparencyG', node=shader, exists=True):
                    target_attr2 = shader + '.transparencyG'
                    if not mc.isConnected(tar_attr, target_attr2):
                        mc.connectAttr(tar_attr, target_attr2, force=True)
                if mc.attributeQuery('transparencyB', node=shader, exists=True):
                    target_attr3 = shader + '.transparencyB'
                    if not mc.isConnected(tar_attr, target_attr3):
                        mc.connectAttr(tar_attr, target_attr3, force=True)


class transferMaterialsCls(object):
    def __init__(self):
        self.materialList = []
        self.OriMeshes = []
        self.NewMeshes = []
        self.OriMaterial = []
        self.NewMaterial = []

    def get_objects_with_selected_material(self):
        # Get the active selection list
        selection = om.MSelectionList()
        om.MGlobal.getActiveSelectionList(selection)

        # Check if a node is selected
        if selection.length() == 0:
            print("Please select a material.")
            return []

        # Get the first selected node
        mobject = om.MObject()
        selection.getDependNode(0, mobject)
        node_fn = om.MFnDependencyNode(mobject)
        material_name = node_fn.name()

        # Get the shading groups for material
        shading_groups = cmds.listConnections(material_name, type='shadingEngine')

        if not shading_groups:
            return []

        # Get the connected meshes
        connected_meshes = []
        for sg in shading_groups:
            meshes = cmds.sets(sg, q=True)
            if meshes:
                connected_meshes.extend(meshes)

        return connected_meshes

    def replace_objects_with_nameSpace(self, nameSpace, meshList):
        newList = []
        nameSpaces = str(nameSpace) + ":"
        for each in meshList:
            if cmds.objExists(str(each).replace(nameSpaces ,"")) == 1:
                newList.append(str(each).replace(nameSpaces ,""))
            else:
                cmds.warning("no mesh found")
        return newList


    def give_objects_materials(self, material, selected_objects):
        # get the selected objects
        # selected_objects = cmds.ls(selection=True)

        # check if any objects are selected
        if not selected_objects:
            print("No objects selected.")
        else:
            # create a new material, in this case, a Lambert material
            # material = cmds.shadingNode('lambert', asShader=True)

            # create a shading group
            # shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True)
            shading_group = cmds.listConnections('%s.outColor' % material, s=0, d=1)[0]
            # rint(shading_group)
            # connect the material to the shading group
            # cmds.connectAttr('%s.outColor' % material, '%s.surfaceShader' % shading_group)

            # assign material to selected objects
            for obj in selected_objects:
                # rint(obj, selected_objects)
                cmds.sets(obj, edit=True, forceElement=shading_group)

    def duplicate_material(self, material):
        # Get shading group connected to material.
        shading_groups = cmds.listConnections(material, type='shadingEngine')
        if shading_groups:
            shading_group = shading_groups[0]
            duplicated_material = cmds.listConnections(shading_group + '.surfaceShader', source=True)[0]
        else:
            cmds.warning('No shading group connected to material')
        return duplicated_material

    def run_function(self, nameSpace):
        selMaterial = cmds.ls(sl=1)
        allMaterialList = cmds.ls(type="shadingEngine")
        materialList = []
        for node in selMaterial:
            if cmds.objExists('%s.outColor' % str(node)):
                shaderSet = cmds.listConnections('%s.outColor' % str(node), s=0, d=1)[0]
                if shaderSet in allMaterialList:
                    materialList.append(node)
        print("selected material List: " + str(materialList))

        for OriMaterial in materialList:
            # Use the function
            OriMeshes = []
            NewMeshes = []
            NewMaterial = []

            cmds.select(cl=1)
            cmds.select(OriMaterial)
            OriMeshes = self.get_objects_with_selected_material()
            # rint OriMeshes
            if OriMeshes != [] or NewMaterial != None:
                #rint(OriMeshes)
                NewMeshes = self.replace_objects_with_nameSpace(nameSpace, OriMeshes)
                if NewMeshes != [] or NewMaterial != None:
                    # rint(NewMeshes)
                    try:
                        NewMaterial = self.duplicate_material(OriMaterial)
                        if NewMaterial != [] or NewMaterial != None:
                            #rint(NewMaterial, NewMeshes)
                            self.give_objects_materials(NewMaterial, NewMeshes)
                        else:
                            cmds.warning("NewMeshes transfer fail")
                    except:
                        pass
                else:
                    cmds.warning("find no NewMeshes")
            else:
                cmds.warning("find no OriMeshes")

def transfer_shaders_new(source_obj, target_obj):
    """
    Transfers all shader assignments from source_obj to target_obj
    Works with face-level assignments and multiple materials
    """
    print("Transferring shaders from {} to {}...".format(source_obj, target_obj))

    # Verify that both objects exist
    if not cmds.objExists(source_obj):
        print("Error: Source object {} does not exist.".format(source_obj))
        return False

    if not cmds.objExists(target_obj):
        print("Error: Target object {} does not exist.".format(target_obj))
        return False

    # Get all shading engines connected to the source object
    shading_groups = cmds.listSets(type=1, object=source_obj) or []

    if not shading_groups:
        print("No shading groups found on the source object.")
        return False

    # For each shading group, find which faces it's assigned to on the source object,
    # then assign it to the corresponding faces on the target object
    for sg in shading_groups:
        # Get the members of this shading group that belong to the source object
        members = cmds.sets(sg, query=True) or []
        source_members = [m for m in members if source_obj in m]

        if not source_members:
            continue

        # Get just the face indices for each member
        for source_member in source_members:
            # Handle face-level assignments
            if '.f[' in source_member:
                # Extract the face indices
                prefix = source_obj + '.f['
                start_idx = source_member.find(prefix) + len(prefix)
                end_idx = source_member.find(']', start_idx)

                # Get the face range
                face_range = source_member[start_idx:end_idx]

                # Create corresponding target face selection
                if ':' in face_range:  # It's a range
                    target_faces = target_obj + '.f[' + face_range + ']'
                else:  # It's a single face
                    target_faces = target_obj + '.f[' + face_range + ']'

                # Assign the shader to the target faces
                print("  Assigning {} to {}".format(sg, target_faces))
                cmds.sets(target_faces, edit=True, forceElement=sg)

            # Handle object-level assignments
            elif source_member == source_obj:
                print("  Assigning {} to entire object {}".format(sg, target_obj))
                cmds.sets(target_obj, edit=True, forceElement=sg)

    print("Shader transfer complete!")
    return True

def import_and_redirect(file_path):
    mc.file(file_path,
            i=True,
            namespace="tex",
            force=True,
            preserveReferences=True,
            returnNewNodes=True)

def delete_materials_except_defaults():
    # Materials to keep
    materials_to_keep = ["lambert1", "particleCloud1", "shaderGlow"]

    # Get all shading engines
    shading_engines = mc.ls(type="shadingEngine")

    # Find all materials/shaders in the scene
    all_materials = []

    # Find materials from common shader types
    shader_types = [
        "aiStandard", "aiFlat", "aiSkin", "aiHair", "aiVolume",  # Arnold
        "blinn", "lambert", "phong", "phongE", "anisotropic", "surfaceShader",  # Maya standard
        "surfaceShader", "volumeShader", "useBackground",  # Maya other
        "rampShader", "displacementShader",  # Special shaders
        "VRayMtl", "VRayLightMtl", "VRayBlendMtl",  # VRay
        "RedshiftMaterial", "RedshiftArchitectural",  # Redshift
        "standardSurface"  # Arnold standard
    ]

    for shader_type in shader_types:
        if mc.pluginInfo(shader_type, query=True, registered=True) or shader_type in ["blinn", "lambert", "phong",
                                                                                        "phongE", "anisotropic",
                                                                                        "surfaceShader"]:
            materials = mc.ls(type=shader_type)
            if materials:
                all_materials.extend(materials)

    # Find other potential materials through connections to shading engines
    for sg in shading_engines:
        if sg != "initialParticleSE" and sg != "initialShadingGroup":
            connections = mc.listConnections(sg + ".surfaceShader", source=True, destination=False) or []
            all_materials.extend(connections)

    # Remove duplicates and filter out materials to keep
    all_materials = list(set(all_materials))
    materials_to_delete = [mat for mat in all_materials if mat not in materials_to_keep]

    # Delete the materials
    if materials_to_delete:
        print("Deleting the following materials:")
        for mat in materials_to_delete:
            print("  - " + mat)

        # Delete the materials
        try:
            mc.delete(materials_to_delete)
            print("\nSuccessfully deleted {} materials.".format(len(materials_to_delete)))
        except Exception as e:
            print("\nError deleting materials: {}".format(str(e)))
    else:
        print("No materials to delete. Only default materials exist in the scene.")

def on_exportModBtn_clicked():
    try:
        print('exportModBtn is clicked' )
        locked_nodes = mc.ls(lockedNodes=True)
        if locked_nodes:
            for node in locked_nodes:
                mc.lockNode(node, lock=False)
            print("Unlocked all nodes.")
        else:
            print("No locked nodes found.")

        poly_grp = 'poly'
        shape_grp = 'shape'
        nodeAttr = 'visibility_ctrl.lookPass'
        nodeAttr1 = 'visibility_ctrl.facial_tex_vis'
        export_name = poly_grp + '_texture'
        export_shape = poly_grp + '_shape'
        node = nodeAttr.split('.')[0]
        attr = nodeAttr.split('.')[1]
        attr1 = nodeAttr1.split('.')[1]

        # 选择poly组，复制一套模型
        duplicated = mc.duplicate(
            poly_grp,
            returnRootsOnly=True,  # 返回根节点（类似 -rr）
            renameChildren=False,  # 重命名子节点
            n=export_name
        )
        if duplicated:
            new_group = duplicated[0]
            mc.parent(new_group, world=True)
            mc.select(cl=1)
        else:
            new_group = ''
            mc.warning("copy poly error")

        poly_children = cmds.listRelatives(poly_grp, allDescendents=True, fullPath=True)

        if shape_grp not in poly_children:
            if mc.objExists(shape_grp):
                duplicated = mc.duplicate(
                    shape_grp,
                    returnRootsOnly=True,  # 返回根节点（类似 -rr）
                    renameChildren=False,  # 重命名子节点
                    n=export_shape
                )
                if duplicated:
                    new_group1 = duplicated[0]
                    mc.parent(new_group1, export_name)
                    mc.select(cl=1)
                else:
                    mc.warning("copy shape error")

        # 如果有lookPass，把visibility_ctrl放在大纲里
        if mc.objExists('visibility_ctrl'):
            if mc.attributeQuery(attr, node=node, exists=True):
                try:
                    enum_items = mc.attributeQuery(attr, node=node, listEnum=True)[0]
                    enum_list = str(enum_items).split(':')
                    clean_enum_list = [item for item in enum_list if item != 'default']
                    if enum_items:
                        enum_count = len(clean_enum_list)
                    else:
                        enum_count = 0
                except:
                    enum_count = 0
            else:
                enum_count = 0
            if enum_count > 0 or mc.attributeQuery(attr1, node=node, exists=True):
                if new_group:
                    mc.parent(node, new_group)
                children = mc.listRelatives(node, children=True, fullPath=True) or []
                objects_to_delete = []
                for child in children:
                    if not mc.objectType(child, isType="nurbsCurve"):
                        objects_to_delete.append(child)
                if objects_to_delete:
                    for obj in objects_to_delete:
                        if mc.objExists(obj):
                            mc.delete(objects_to_delete)
                else:
                    print("No objects to delete under {}".format(node))

        mc.delete('master')
        containers = mc.ls(type='container') or []
        if containers:
            for container in containers:
                try:
                    if mc.objExits(container):
                        mc.delete(container)
                except Exception as e:
                    pass
        if mc.objExists('visibility_ctrl'):
            mc.rename('visibility_ctrl', 'visibility_ref')

        # 在 exportSelected 之前，加这段
        all_meshes = mc.listRelatives(export_name, ad=True, type='transform') or []
        for mesh in all_meshes:
            reconnect_mod_transparent(mesh, 'lc_transparent')

        current_file = mc.file(query=True, sceneName=True)

        mc.select(export_name, r=1)
        if not current_file:
            mc.warning("场景尚未保存，请先保存文件")
        else:
            dir_path = os.path.dirname(current_file)
            export_path = os.path.join(dir_path, export_name + ".mb")
            options = '"v=0;" "constructionHistory=0;" "shaders=1;" "textures=1;" "referencedContainers=0"'
            mc.file(
                export_path,
                force=True,
                type="mayaBinary",
                options=options,
                exportSelected=True,
                preserveReferences=False
            )

        if current_file:
            directory = os.path.dirname(current_file)
            target_file = os.path.join(directory, export_name + ".mb")
        else:
            mc.error('not find the target file')
        if not os.path.exists(target_file):
            mc.error('not find the target file')
            return
        mc.file(target_file, open=True, force=True)
        print("export successfully to : {}".format(export_path))
        return export_path
    except:
        return ""

def on_replaceModBtn_clicked():
    print('replaceModBtn is clicked' )
    export_name = 'poly_texture'
    current_file = mc.file(query=True, sceneName=True)
    if not current_file:
        mc.warning("场景尚未保存，请先保存文件")
        return
    else:
        # 删除所有材质
        delete_materials_except_defaults()
        meshList = []
        if mc.objExists('poly'):
            meshes = mc.listRelatives('poly', allDescendents=True, type='mesh', fullPath=True) or []
            for each in meshes:
                mesh_transform = mc.listRelatives(each, parent=1)[0]
                if mesh_transform not in meshList:
                    meshList.append(mesh_transform)
        dir_path = os.path.dirname(current_file)
        export_path = os.path.join(dir_path, export_name + ".mb")
        import_and_redirect(export_path)

        if mc.objExists('tex:visibility_ref') and mc.objExists('visibility_ctrl'):
            nodeA = 'tex:visibility_ref'
            nodeB = 'visibility_ctrl'
            output_conns = mc.listConnections(nodeA, source=False, destination=True, plugs=True, connections=True)
            if output_conns:
                for i in range(0, len(output_conns), 2):
                    src_plug = output_conns[i]
                    dst_plug = output_conns[i + 1]
                    if not src_plug.startswith(nodeA + '.'):
                        continue
                    new_src_plug = src_plug.replace(nodeA, nodeB, 1)
                    try:
                        mc.disconnectAttr(src_plug, dst_plug)
                        mc.connectAttr(new_src_plug, dst_plug, force=True)
                    except:
                        pass
            mc.delete(nodeA)

        input_value = 'tex'
        print("Input NameSpace: " + str(input_value))

        # old transfer functions:
        versionTag = 1
        if versionTag:
            transferM = transferMaterialsCls()
            shader_types = [
                "aiStandard", "aiFlat", "aiSkin", "aiHair", "aiVolume",  # Arnold
                "blinn", "lambert", "phong", "phongE", "anisotropic",  # Maya standard
                "surfaceShader", "volumeShader", "useBackground",  # Maya other
                "rampShader", "displacementShader",  # Special shaders
                "VRayMtl", "VRayLightMtl", "VRayBlendMtl",  # VRay
                "RedshiftMaterial", "RedshiftArchitectural",  # Redshift
                "standardSurface"  # Arnold standard
            ]
            shading_nodes = sum([mc.ls(type=t) for t in shader_types], [])
            mc.select(shading_nodes, r=True)
            print('index535', shading_nodes)
            transferM.run_function(str(input_value))
        else:
            for eachMesh in meshList:
                print eachMesh #transfer_materials_by_shader()
                transfer_shaders_new("tex:{}".format(eachMesh), "{}".format(eachMesh))

        print('add transparentcy connections')
        all_meshes = mc.listRelatives('tex:' + export_name, ad=True, type='transform') or []
        print('index2119', all_meshes)
        for mesh in all_meshes:
            reconnect_imported_mod_transparent(mesh, 'lc_transparent')

        mc.delete('tex:poly_texture')
        mc.namespace(removeNamespace='tex', mergeNamespaceWithRoot=True)

    print('replace all mod and textures successfully!')


def export_mat(): # 导出poly和shape组下所有模型和材质以及与visibility_ctrl的lookPass相连的属性链接
    mat_file_path = on_exportModBtn_clicked()
    return mat_file_path


def import_mat(): # 导入poly和shape组下所有模型和材质以及与visibility_ctrl的lookPass相连的属性链接
    #todo. 若口腔没有材质，给一个默认颜色
    on_replaceModBtn_clicked()


