import os
import traceback
import pymel.core as pm
import maya.api.OpenMaya as om
import maya.cmds as cmds
'''
import sys
sys.path.append('/mnt/work/home/yingjie/git_repo/tk-lca-publish/python/tk_lca_publish/proc')
import apply_uv as auv
auv.apply()
'''

def replace_uvmap_folliclemap(mapname='lcarigmap'):
    """copy uvset map1 to lcarigmap
    
    Returns:
        TYPE: Description
    """
    folliclelist=[]
    allFollicle = cmds.ls(type="follicle")
    for follicle in allFollicle:
        inputSurface = '{0}.inputMesh'.format(follicle)
        ConnectionList = cmds.listConnections(inputSurface,shapes=1,scn=1) or []
        if ConnectionList:
            origin_set = cmds.getAttr('%s.mapSetName' % follicle)
            if origin_set.startswith('lca'):
                continue
            cmds.setAttr("%s.mapSetName" % follicle, l=False)
            cmds.setAttr('%s.mapSetName' % follicle, mapname, type="string")
            folliclelist.append(follicle)

    allMesh = cmds.ls(type="mesh")
    orig=[]
    for mesh in allMesh:
        cs=cmds.listConnections(mesh+'.inMesh',s=1,d=0)
        if not cs:
            allUvSet = cmds.polyUVSet(mesh, query=True, allUVSets=1)
            if allUvSet and mapname not in allUvSet:
                try:
                    print 'Copy uv set map1 to',mapname,'in mesh',mesh
                    cmds.polyUVSet(mesh,copy=True, newUVSet=mapname,uvSet='map1')
                    orig.append(mesh)
                except:
                    traceback.print_exc()

class find_source():
    def __init__(self, node_name):
        self.l_processed_nodes = []
        self.l_terminals = []
        self.l_history_nodes = [n.name() for n in pm.listHistory(node_name)]
        #try to find orig attribute,if not go recursion
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

    def find_orig_attr(self,node_name):
        shape_node = pm.PyNode(node_name)
        if shape_node.hasAttr('origShape'):
            tmp_terminals_list = shape_node.getAttr('origShape').split(';')
            for tmp_terminals  in tmp_terminals_list:
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
                print 'Add baduvTag attribute to',m
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
        if line.startswith('//') :
            continue         # Skip comments
        #print i, line_mark, line[:-1]
        tokens = line[:-1].split(' ')
        if line_mark == 'mesh_info':
            mesh_name = tokens[0]
            uv_set = ''
            d_meshes[mesh_name] = {'m_v_cnt':tokens[1], 'm_e_cnt':tokens[2], 'm_f_cnt':tokens[3], 'UV':{}}
            if i+1 < len(l_lines):
                if l_lines[i+1][0] != '|':
                    line_mark = 'uv_u'
                
        elif line_mark == 'uv_u':
            if len(tokens) == 1 and tokens[0] != '':
                uv_set = tokens[0]
                d_meshes[mesh_name]['UV'][uv_set] = {'u':[], 'v':[], 'uv_cnt':[], 'uv_ids':[]}
            else:
                if uv_set == '':
                    uv_set = 'map1'
                d_meshes[mesh_name]['UV'][uv_set] = {'u':[float(t) for t in tokens if t != ''], 'v':[], 'uv_cnt':[], 'uv_ids':[]}
                line_mark = 'uv_v'

        elif line_mark == 'uv_v':
            d_meshes[mesh_name]['UV'][uv_set]['v'] = [float(t) for t in tokens if t != '']
            line_mark = 'uv_cnt'

        elif line_mark == 'uv_cnt':
            d_meshes[mesh_name]['UV'][uv_set]['uv_cnt'] = [int(t) for t in tokens if t != '']
            line_mark = 'uv_ids'

        elif line_mark == 'uv_ids':
            d_meshes[mesh_name]['UV'][uv_set]['uv_ids'] = [int(t) for t in tokens if t != '']
            if i+1 < len(l_lines):
                if l_lines[i+1][0] == '|':
                    line_mark = 'mesh_info'
                else:
                    uv_set = ''
                    line_mark = 'uv_u'

    return d_meshes

def apply(uv_file,check=True,import_node_list=[]):
    
    if pm.sceneName() and '.cfx.' in pm.sceneName():
        replace_uvmap_folliclemap('lcacfxmap')
        
    elif pm.sceneName() and '.rig.' in pm.sceneName():
        replace_uvmap_folliclemap()
    
    if check:
        if not os.path.isdir(uv_file.rsplit('/',2)[0]+'/mat_info'):
            print 'No mat_info data,ignore.'
            return

    skip_mesh=[]
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
                    node_shape = node.name(long=1).split('|',2)[-1].split(':master|')[-1]
                    if ':' in node_shape:
                        node_shape = '|'.join([sp.split(':')[-1] for sp in node_shape.split('|')])

                    if m_path.split('|',2)[-1] == node_shape:
                        n = node
                        m_path=node.name(long=1)
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
            l_dst_meshes = list(set(f.l_terminals ))
            if len(l_dst_meshes) == 0:
                print '\tError: failed to find the source mesh for', m_path
                l_dst_meshes=[m_path]

            #l_dst_meshes.append(m_path)
            print '\tTry to apply UV to:', m_path
            print '\tCandidates:', l_dst_meshes
            
            if len(m_info['UV'].keys()) == 0:
                skip_mesh.extend(l_dst_meshes)
                print '\t\tSkipped:', ' '.join(l_dst_meshes), ',no uv set for mesh',m_path,'in the uv file.'
                continue

            print 'check baduvTag  : ',m_path
            if cmds.attributeQuery('baduvTag', node=m_path, exists=True):
                    cmds.deleteAttr(m_path+'.baduvTag')

            for dst_mesh in l_dst_meshes:
                if not pm.objExists(dst_mesh):
                    continue
                if cmds.attributeQuery('baduvTag', node=dst_mesh, exists=True):
                    cmds.deleteAttr(dst_mesh+'.baduvTag')

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
                    pm.polyUVSet(dst_mesh, uvSet='uv_srf',delete=True)
                    print '\t\tDelete [uv_srf] uvset',dst_mesh
                    if 'uv_srf' in all_uvsets: all_uvsets.remove('uv_srf')
                except:
                    pass


                for uvset in m_info['UV'].keys():
                    if uvset=='lcarigmap':
                        print '\t\tSkipped uv set [lcarigmap] for rig in mesh [',dst_mesh,'].'
                        continue

                    elif uvset == 'lcacfxmap':
                        print '\t\tSkipped uv set [lcacfxmap] for cfx in mesh [',dst_mesh,'].'
                        continue

                    orig_uv_set=uvset

                    # Create/Clean UV Sets
                    # if dst_mesh in l_follicles_mesh:
                    #     uvset = 'uv_srf'

                    if not uvset in all_uvsets:
                        pm.polyUVSet(dst_mesh, uvSet=uvset, create=True)

                    # if uvset == 'map1' and 'uv_srf' in all_uvsets:
                    #     pm.polyUVSet(dst_mesh, uvSet='uv_srf', delete=True)

                    if not m_info['UV'].has_key(uvset):
                        uvset=orig_uv_set

                    l_u = m_info['UV'][uvset]['u']
                    l_v = m_info['UV'][uvset]['v']
                    l_uv_cnt = m_info['UV'][uvset]['uv_cnt']
                    l_uv_ids = m_info['UV'][uvset]['uv_ids']

                    sl = om.MSelectionList()
                    sl.add(dst_mesh)
                    mesh_dag = sl.getDagPath(0)
                    mesh_mfn = om.MFnMesh(mesh_dag)

                    print '\t\tApplied (UV Set ' + uvset + '):', dst_mesh
                    mesh_mfn.clearUVs(uvSet = uvset)
                    mesh_mfn.setUVs(l_u, l_v, uvSet = uvset)
                    mesh_mfn.assignUVs(l_uv_cnt, l_uv_ids, uvSet = uvset)
                    # update uv set
                    cmds.polyUVSet(dst_mesh, cr=True, uvs="update")
                    cmds.undo()

                #refresh
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

