# -*- coding:utf-8 -*-


import traceback
import pymel.core as pm
import maya.api.OpenMaya as om
import maya.mel as mel
from proc.function_running_time import record_time


# find a sep mesh children overlap mesh , sep obj
def find_overlap_mesh(mesh_grp):
    mesh_list = pm.listRelatives(mesh_grp, ad=True, type="mesh")
    bboxStr_dict = {}
    for mesh in mesh_list:
        mesh = mesh.getParent()
        name = str(mesh.name())
        bbox = mesh.getBoundingBox()
        bboxStr = ""
        for i in bbox:
            for j in i:
                bboxStr = bboxStr + "%.4f " % j
        bboxStr_dict.setdefault(bboxStr, list())
        bboxStr_dict.get(bboxStr).append(name)
    # print bboxStr_dict
    overlap_num = 0
    for k, v in bboxStr_dict.items():
        # print k,v
        if len(v) == 1:
            continue
        else:
            overlap_num += 1
    return overlap_num


# get overlap mesh
def find_maybe_overlap_vtx_mesh():
    pm.select(cl=True)

    l_meshes = pm.listRelatives('|master|poly', ad=True, type='mesh')

    # if pm.objExists('|master|shape'):
    #     l_meshes.extend(pm.listRelatives('|master|shape', ad=True, type='mesh'))

    if not l_meshes:
        return ""
    mesh_invalid_dict = {}
    for mesh_node in l_meshes:
        trans_node = pm.listRelatives(mesh_node, parent=True, path=True)[0]
        sl = om.MSelectionList()
        sl.add(mesh_node.name())
        mesh_dag = sl.getDagPath(0)
        mesh_mfn = om.MFnMesh(mesh_dag)

        l_vertice = mesh_mfn.getPoints()

        d_coordination = {}
        one_invalid_vtx_list = []
        for i in range(len(l_vertice)):
            translation_xyz = '%.6f %.6f %.6f' % (l_vertice[i].x, l_vertice[i].y, l_vertice[i].z)
            if not d_coordination.has_key(translation_xyz):
                d_coordination[translation_xyz] = 1
            else:
                one_invalid_vtx_list.append(trans_node + '.vtx[' + str(i) + ']')

        if len(one_invalid_vtx_list):
            mesh_invalid_dict[mesh_node.getParent().name()] = one_invalid_vtx_list

    return mesh_invalid_dict


def find_overlap_mesh_main():
    pm.undoInfo(state=True, infinity=True)
    pm.undoInfo(ock=True)
    # 1  vertex overlap find  maybe overlap shape
    mesh_invalid_dict = find_maybe_overlap_vtx_mesh()
    # print mesh_invalid_dict
    # 2  seprate shape
    invalid_dict = {}
    for mesh_name, vtx_list in mesh_invalid_dict.items():
        # sep mesh_name will create mesh_name grp ,contain sep mesh
        try:
            pm.polySeparate(mesh_name, ch=False)
        except:
            pass
        overlap_num = find_overlap_mesh(mesh_grp=mesh_name)
        # print overlap_num
        if not overlap_num:
            continue
        # 3  if sep obj list overlap
        invalid_dict[mesh_name] = vtx_list

    # print invalid_dict
    pm.undoInfo(cck=True)
    pm.undo()
    pm.undoInfo(state=True, infinity=False)
    # 4  get overlap shape and return shape and face info
    return invalid_dict


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查完全重叠的面"
        self.description = u"检查是否有完全重叠的面，如果有，需要模型师确认是否为多余物体。skip tag: skip_overlap_face"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def get_asset_shotgun_info(self, asset_name):
        flt = [['project', 'name_is', self.dialog.project['name'].upper()], ['code', 'is', asset_name]]
        asset_info = self.dialog.sg.find_one('Asset', flt, ['code', 'tag_list'])
        return asset_info

    @record_time(__file__)
    def run_check(self):
        try:
            for asset_name in self.dialog.d_assets_info.keys():
                if self.dialog.d_assets_info[asset_name]['type'] != 'chr':
                    return ''

                sg_info = self.get_asset_shotgun_info(asset_name=asset_name)
                if 'skip_overlap_face' in sg_info['tag_list']:
                    print "skip_overlap_face"
                    return ''

            pm.select(cl=True)
            invalid_dict = find_overlap_mesh_main()
            if not invalid_dict:
                return ''
            for mesh_name, vtx_list in invalid_dict.items():
                # select overlap vtx
                pm.select(vtx_list, add=True)
            mel.eval('ConvertSelectionToFaces;')
            pm.select(r=True)
            mel.eval('GrowPolygonSelectionRegion;')
            mel.eval('GrowPolygonSelectionRegion;')
            mel.eval('GrowPolygonSelectionRegion;')

            return u"已选中以下疑似与其他物体完全重叠的面，请检查：{}\n".format(invalid_dict.keys())

        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
