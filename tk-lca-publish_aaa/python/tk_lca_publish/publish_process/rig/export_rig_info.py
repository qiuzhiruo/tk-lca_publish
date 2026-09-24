# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2016 Light Chaser Animation
#
# Author: Guo JianWei
#
# Date: 2016.10.19
#
# Description: Export rigging info
#
############################################

import os
import sys
import string
import traceback
import hashlib
import pymel.core as pm
import maya.api.OpenMaya as om
import maya.cmds as cmds
import maya.cmds as mc
import xml.etree.ElementTree as ET
import json
from xml.dom.minidom import Document
import maya.api.OpenMaya as om

def convert_key_to_grp_name(key):
    """
    'facePass.default' -> 'face_default_grp'
    'facePass.face_a'  -> 'face_a_grp'
    'facePass.face_z'  -> 'face_z_grp'
    """

    name = key.split('.')[-1]

    if name == 'default':
        return 'face_default_grp'

    valid_face_names = ['face_{}'.format(ch) for ch in string.ascii_lowercase]

    if name in valid_face_names:
        return '{}_grp'.format(name)

    return None

def get_mesh_transforms_under_grp(grp, full_path=True):
    """
    获取组下面所有 mesh 的 transform 名字
    """

    if not cmds.objExists(grp):
        return []

    mesh_shapes = cmds.listRelatives(
        grp,
        allDescendents=True,
        type='mesh',
        fullPath=full_path
    ) or []

    mesh_transforms = []

    for shape in mesh_shapes:
        parent = cmds.listRelatives(
            shape,
            parent=True,
            fullPath=full_path
        )

        if parent:
            mesh_transforms.append(parent[0])

    # 去重，保持顺序
    result = []
    for mesh in mesh_transforms:
        if mesh not in result:
            result.append(mesh)

    return result

def get_face_pass_meshes(face_pass_data, full_path=True):
    """
    输入任意长度的 face_pass_data，
    返回每个 face_xxx_grp 下面的 mesh transform 名字。
    """

    result = {}

    # 期望处理顺序：default, face_a, face_b ... face_z
    ordered_names = ['default'] + ['face_{}'.format(ch) for ch in string.ascii_lowercase]

    for name in ordered_names:
        key = 'facePass.{}'.format(name)

        if key not in face_pass_data:
            continue

        grp_name = convert_key_to_grp_name(key)

        if not grp_name:
            continue

        meshes = get_mesh_transforms_under_grp(grp_name, full_path=full_path)

        result[grp_name] = meshes

    return result

def _get_long_name(node):
    result = cmds.ls(node, long=True) or []
    return result[0] if result else node

def _calc_mesh_topology(mesh):
    mesh = _get_long_name(mesh)
    face_count = cmds.polyEvaluate(mesh, face=True)
    if face_count == 0:
        return hashlib.md5(' ').hexdigest()

    sl = om.MSelectionList()
    sl.add(mesh)
    dag = sl.getDagPath(0)
    mfn = om.MFnMesh(dag)

    v = mfn.getVertices()
    v_str0 = '[' + ', '.join(map(str, v[0])) + ']'
    v_str1 = '[' + ', '.join(map(str, v[1])) + ']'

    return hashlib.md5((v_str0 + ' ' + v_str1)).hexdigest()

def _create_structure(doc, parent_elem, root_node):
    if not cmds.objExists(root_node):
        return

    children = cmds.listRelatives(
        root_node, children=True, fullPath=True
    ) or []
    children.sort()

    for node in children:
        node_type = cmds.nodeType(node)

        if node_type == 'transform':
            elem = doc.createElement('transform')
            elem.setAttribute('name', _get_long_name(node))
            parent_elem.appendChild(elem)
            _create_structure(doc, elem, node)

        elif node_type == 'mesh':
            if cmds.getAttr(node + '.intermediateObject'):
                continue

            topo = _calc_mesh_topology(node)

            elem = doc.createElement('mesh')
            elem.setAttribute('name', _get_long_name(node))
            #elem.setAttribute('vertex', str(cmds.polyEvaluate(node, vertex=True)))
            elem.setAttribute('edge', str(cmds.polyEvaluate(node, edge=True)))
            elem.setAttribute('face', str(cmds.polyEvaluate(node, face=True)))
            elem.setAttribute('topology', topo)

            parent_elem.appendChild(elem)

def generate_mesh_structure_xml(root_node, output_xml):
    if not cmds.objExists(root_node):
        return
        #raise RuntimeError('Root node does not exist: {}'.format(root_node))

    doc = Document()

    root_elem = doc.createElement('transform')
    full_path = cmds.ls(root_node, long=True) or [root_node]
    root_elem.setAttribute('name', full_path[0])
    doc.appendChild(root_elem)

    _create_structure(doc, root_elem, root_node)

    with open(output_xml, 'w') as f:
        f.write(doc.toprettyxml(indent='    '))

    try:
        os.chmod(output_xml, 0o777)
    except Exception:
        pass

    return output_xml

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog=None):
        self.dialog = dialog
        self.process_name = u"导出绑定文件信息。"
        self.description = u"导出绑定文件的模型版本，帧数率，控制器数量和增减等信息"
        return

    def write_asset_data(self):
        note_text = []
        # get current asset
        asset_name = self.dialog.entity['name'].lower()
        if self.dialog.entity.has_key('sg_chinese'):
            asset_chinese_name = self.dialog.entity['sg_chinese']
            note_text.append(u'资产中文名为：{}; '.format(asset_chinese_name))
            print(u'资产中文名为：{} '.format(asset_chinese_name))

        task = self.dialog.task['name'].lower()
        note_text.append(u"绑定任务类型为：%s; " % task)
        print u"绑定任务类型为：%s; " % task

        version_dir = self.dialog.d_assets_info[asset_name]['version_dir'].lower()
        # version_dir = "D:/project_sg/blanket.rig.rigging.v067"
        try:
            chr_height = self.get_height()
            if chr_height:
                note_text.append(u"绑定高度为：%s; " %str("%.2f"% chr_height))   # add version_tag
                print u"绑定高度为：%s; " %str("%.2f"% chr_height)
            else:
                note_text.append(u"绑定高度为：None; ")   # add version_tag
        except:
            pass

        xml_file = "%s/rig_info.xml" % version_dir
        # for get ctrl all path and not influence current flow, so add a new file -- by zhangshuai
        #  *_full_path
        ##########################################################################################
        # 1. xml_file_full_path
        xml_file_full_path = "%s/rig_full_path_info.xml" % version_dir

        profiling_file = "%s/anim_rig/profilingData.txt" % version_dir

        xml_root = self._create_doc("RiggingInfo")
        ##########################################################################################
        # 2. xml_root_full_path
        xml_root_full_path = self._create_doc("RiggingInfo")

        note_text.append(u"绑定版本为：%s; " %self.dialog.version_tag)   # add version_tag

        # add model version
        mod_node = self._create_node(xml_root, "modInfo")
        ##########################################################################################
        # 3. mod_node_full_path
        mod_node_full_path = self._create_node(xml_root_full_path, "modInfo")
        if cmds.objExists("master.modVersion"):
            mod_version = cmds.getAttr("master.modVersion")
            mod_node.set("modVersion", mod_version)
            ##########################################################################################
            # 3.2  mod_node_full_path set attr
            mod_node_full_path.set("modVersion", mod_version)
            note_text.append(u"模型版本为：v%s; " % mod_version)
        # add controls name
        # CJW 吴真添加过滤
        ctrl_node = self._create_node(xml_root, "controlInfo")
        ##########################################################################################
        # 4. ctrl_node_full_path
        ctrl_node_full_path = self._create_node(xml_root_full_path, "controlInfo")
        #all_ctrls = cmds.ls("*_ctrl")
        all_ctrls = get_controllers()
        if all_ctrls:
            for item in all_ctrls:
                ctrl_name_node = self._create_node(ctrl_node, "controlName")
                ctrl_name_node.set("name", item)
                ##########################################################################################
                # 4.2 ctrl_node_full_path set attr
                ctrl_name_node_full_path = self._create_node(ctrl_node_full_path, "controlName")
                ctrl_name_node_full_path.set("name", item)
                ctrl_name_node_full_path.set("path", cmds.ls(item, long=True)[0])
            ctrl_num = len(all_ctrls)
            note_text.append(u"当前绑定有%s个控制器; " % ctrl_num)
            print u'当前绑定有%s个控制器; ' % ctrl_num
        # add FPS dada
        fps_node = self._create_node(xml_root, "profilingInfo")
        ##########################################################################################
        # 5. fps_node_full_path
        fps_node_full_path = self._create_node(xml_root_full_path, "profilingInfo")
        if os.path.isfile(profiling_file):
            file_object = open(profiling_file)
            try:
                all_the_text = file_object.readlines()
                firstline = all_the_text[2].rstrip()
                if firstline:
                    fps_node.set("FPS", firstline)
                    ##########################################################################################
                    # 5.2 fps_node_full_path set attr
                    fps_node_full_path.set("FPS", firstline)
                    fps_value = float(firstline.split(":")[-1].replace('fps', ''))
                    note_text.append(u"帧速率FPS为：%.2f fps; " % fps_value)

                    sg_rig_fps = self.dialog.sg.find_one('Asset', [['id', 'is', self.dialog.entity['id']]], ['sg_rig_fps'])[ 'sg_rig_fps']
                    if sg_rig_fps:
                        rig_fps_dict = eval(sg_rig_fps)
                    else:
                        rig_fps_dict = {}

                    # task = self.dialog.task['name'].lower()
                    if task == "rigging":
                        task = "rigging_tech"
                    rig_fps_dict[task] = "%.2f fps" % fps_value
                    rig_fps = "{"
                    for key in rig_fps_dict.keys():
                        rig_fps += "'{0}':'{1}',".format(key,rig_fps_dict[key])
                    rig_fps += "}"
                    self.dialog.sg.update('Asset',self.dialog.entity['id'], {'sg_rig_fps': rig_fps})

            finally:
                file_object.close()

        self._write_xml(xml_root, xml_file)
        ##########################################################################################
        # 7. deformed_model_count
        try:
            deformed_vertex_count_json = {}

            skinData = get_skinned_meshes_vertex_info()
            deformed_vertex_count_json.update({"skinData":skinData})

            wrapData = get_wraped_meshes_vertex_info()
            deformed_vertex_count_json.update({"wrapData":wrapData})

            lcPoseDeformerData = get_lcPoseDeformer_meshes_vertex_info()
            deformed_vertex_count_json.update({"lcPoseDeformerData":lcPoseDeformerData})

            blendShapeData = get_blendShape_meshes_vertex_info()
            deformed_vertex_count_json.update({"blendShapeData":blendShapeData})

            latticeData = get_lattice_meshes_vertex_info()
            deformed_vertex_count_json.update({"latticeData":latticeData})

            constaintNodes = 'total constraint nodes: {}'.format(count_constraint_nodes())
            deformed_vertex_count_json.update({"constaintNodes":constaintNodes})

            lcSurfaceRibbonNodes = 'total lcSurfaceRibbon nodes: {}'.format(len(cmds.ls(type='lcSurfaceRibbon')))
            deformed_vertex_count_json.update({"lcSurfaceRibbonNodes":lcSurfaceRibbonNodes})

            follicleNodes = 'total follicle nodes: {}'.format(len(cmds.ls(type='follicle')))
            deformed_vertex_count_json.update({"follicleNodes":follicleNodes})

            CPOINodes = 'total closestPointOnSurface nodes: {}'.format(len(cmds.ls(type='closestPointOnSurface')))
            deformed_vertex_count_json.update({"CPOINodes":CPOINodes})

            CPOMNodes = 'total closestPointOnMesh nodes: {}'.format(len(cmds.ls(type='closestPointOnMesh')))
            deformed_vertex_count_json.update({"CPOMNodes":CPOMNodes})

            IKHandleNodes = 'total closestPointOnSurface nodes: {}'.format(len(cmds.ls(type='ikHandle')))
            deformed_vertex_count_json.update({"IKHandleNodes":IKHandleNodes})

            visible_components_Data = get_visible_components()
            deformed_vertex_count_json.update({u"visible_vertex_face":visible_components_Data})




            get_deform_model_info_xml_path = "%s/deformed_vertex_count.json" % version_dir
            with open(get_deform_model_info_xml_path, 'w') as f:
                json.dump(deformed_vertex_count_json, f, ensure_ascii=False, indent=4)



            # 输出 customShader 信息到 json
            shader_info_json = {}
            customShader = get_customShader_info()
            shader_info_json.update({"customShader":customShader})

            if len(customShader) == 0:
                custom_Exists = False
            else:
                custom_Exists = True

            try:
                customShader_str = {'type': 'Tag', 'id': 3177, 'name': 'customShader'}
                tags_info = self.dialog.sg.find('Asset', [['id','is', self.dialog.entity['id']]], ["tags"])
                tags_array = tags_info[0]["tags"]
                if custom_Exists:
                    if not customShader_str in tags_array:
                        tags_array.append(customShader_str)
                        self.dialog.sg.update('Asset', self.dialog.entity['id'], {'tags': tags_array})
                else:
                    if customShader_str in tags_info[0]["tags"]:
                        tags_array.remove(customShader_str)
                        self.dialog.sg.update('Asset', self.dialog.entity['id'], {'tags': tags_array})
            except:
                print "shotgun tags add customShader error !!! "

            shader_info_json_path = "%s/shader_info.json" % version_dir
            with open(shader_info_json_path, 'w') as f:
                json.dump(shader_info_json, f, ensure_ascii=False, indent=4)



        except:
            pass


        # 输出 visibility 信息到 json
        visibility_json_path = "%s/visibility_info.json" % version_dir
        export_visibility_info(visibility_json_path)

        # 将绑定中所有控制器的可key帧属性输出json信息
        export_isKeyable_attr_json(version_dir)


        # 8. write lookPass and rigPass info
        print u"238 version_dir：%s; " % str(version_dir)
        print u"239 version_name：%s; " % str(self.dialog.version_name)
        print u"240 asset_name：%s; " % str(asset_name)

        passInfoFullPath = "%s/rig_pass_info.json" % version_dir
        #if 'chr' in passInfoFullPath or 'prp' in passInfoFullPath:
        rig_version_name = str(self.dialog.version_name[-3:])
        writePassInfo(passInfoFullPath, rig_version_name, asset_name)

        # if cmds.objExists('hair_grp'):
        #     ori_link1, ori_vis1, ori_lock1 = check_and_modify_group_visibility('shape')
        #     ori_link2, ori_vis2, ori_lock2 = check_and_modify_group_visibility('to_cfx')
        #     ori_link3, ori_vis3, ori_lock3 = check_and_modify_group_visibility('hair_grp')
        #     ori_link4, ori_vis4, ori_lock4 = check_and_modify_group_visibility('head_hair')
        #     ori_link5, ori_vis5, ori_lock5 = check_and_modify_group_visibility('face_hair')

        hairPassInfoFullPath = "%s/rig_hair_pass_info.json" % version_dir
        if cmds.objExists('shape'):
            cmds.setAttr('shape.v', 1)
        writeHairPassInfo(hairPassInfoFullPath, rig_version_name, asset_name) # 包含facePass信息
        if cmds.objExists('shape'):
            cmds.setAttr('shape.v', 0)
        # facePassInfoFullPath = "%s/rig_face_pass_info.json" % version_dir
        # writeFacePassInfo(facePassInfoFullPath, rig_version_name, asset_name)
        # 9. write facial geo info
        try:
            exporter_facial_geo = FacialMeshExporter()
            facial_mesh_info_path = "%s/facial_mesh.xml" % version_dir
            exporter_facial_geo.run(export_path=facial_mesh_info_path)
        except:
            print('index264 facial_mesh fail to export')

        # if cmds.objExists('hair_grp'):
        #     restore_group_visibility('shape', ori_link1, ori_vis1, ori_lock1)
        #     restore_group_visibility('to_cfx', ori_link2, ori_vis2, ori_lock2)
        #     restore_group_visibility('hair_grp', ori_link3, ori_vis3, ori_lock3)
        #     restore_group_visibility('head_hair', ori_link4, ori_vis4, ori_lock4)
        #     restore_group_visibility('face_hair', ori_link5, ori_vis5, ori_lock5)

        # 10. write shape xml
        try:
            facial_mesh_info_path = "%s/shape.xml" % version_dir
            generate_mesh_structure_xml('|master|shape', facial_mesh_info_path)
        except:
            print('index369 shape mesh fail to export')

        ##########################################################################################
        # 6. output write xml
        self._write_xml(xml_root_full_path, xml_file_full_path)
        previous_version_file = ""
        current_num = version_dir.split(".v")[-1]
        if current_num.isdigit():
            if int(current_num) > 1 :
                num = int(current_num) - 1
                previous_num = string.zfill(num, 3)
                previous_version_dir = version_dir.replace(current_num, previous_num)
                previous_version_file = "%s/rig_info.xml" % previous_version_dir
                previous_ctrls = []
                if os.path.isfile(previous_version_file):
                    previous_xml_root = self._get_root(previous_version_file)
                    control_node = previous_xml_root.findall('controlInfo')
                    if control_node:
                        nodes = control_node[0].getchildren()
                        if nodes:
                            for node in nodes:
                                ctrl = node.attrib["name"]
                                previous_ctrls.append(ctrl)
                        all_ctrls = set(all_ctrls)
                        previous_ctrls = set(previous_ctrls)
                        new = list(all_ctrls.difference(previous_ctrls))
                        old = list(previous_ctrls.difference(all_ctrls))
                        print new
                        print old
                        if new:
                            if len(new)>5:
                                note_text.append(u"和上一版比，新增加控制器：{0} ;".format(new[0:4]))
                            else:
                                note_text.append(u"和上一版比，新增加控制器：{0} ;".format(new))
                        if old:
                            if len(old)>5:
                                note_text.append(u"和上一版比，已删除控制器：{0} ;".format(old[0:4]))
                            else:
                                note_text.append(u"和上一版比，已删除控制器：{0} ;".format(old))


        text_info = "\n".join(note_text)
        self.dialog.w_publish.plainTextEdit_auto_description.setPlainText(text_info)

    # --------------------------------xml etree function
    def _get_root(self, file_path):
        if not os.path.isfile(file_path):
            print 'file_path: %s' % file_path
            raise ValueError, 'Warning: file does not exist'

        xml_tree = ET.parse(file_path)
        xml_root = xml_tree.getroot()

        return xml_root

    def _create_doc(self, doc_name="amin_cache"):
        xml_root = ET.Element(doc_name)
        return xml_root

    def _create_node(self, root, name):
        node = ET.SubElement(root, name)
        return node

    def _indent(self, elem, level=0):
        """Borrow the indent code from http://norwied.wordpress.com/
        """
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._indent(elem, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
        return

    def _write_xml(self, xml_root, file_path):
        self._indent(xml_root)

        xml_tree = ET.ElementTree(xml_root)

        xml_tree.write(file_path)

    def proceed(self):
        try:
            self.write_asset_data()

            try:
                print "import file"
                pm.newFile(f=True)
                pm.importFile(self.dialog.tank_file[:-3] + '.mb', f=True)
            except:
                pass

            try:
                print 'Facial check'
                if self.dialog.facial_points and pm.objExists("facial_CtrlGrp") and pm.objExists("facial_head_geo"):
                    head_geo = pm.PyNode("facial_head_geo")
                    head_geo_shape = head_geo.getShape()
                    attr_list = [["jaw_M_ctrl.rotateX", 30],
                    ["mouth_L_up_1_ctrl.translateY", 1],
                    ["mouth_R_up_2_ctrl.translateY", 1],
                    ["mouth_L_dn_1_ctrl.translateY", -1],
                    ["mouth_R_dn_1_ctrl.translateY", -1],
                    ["brow_R_all_ctrl.translateY", -1],
                    ["brow_L_all_ctrl.translateY", -1]]
                    facial_points = []
                    for attr,value in attr_list:
                        # Modified by Sheng Liao on 2021/11/15 ------------------
                        # Note that special characters may not have some facial controllers,
                        # like the "three ass monster" of the NYJ project.
                        if not cmds.objExists(attr):
                            continue
                        if cmds.getAttr(attr, lock=True):
                            continue
                        # ------------------ Modified by Sheng Liao on 2021/11/15
                        pm.setAttr(attr,value)
                        points_length = sum(head_geo_shape.getPoints()).length()
                        pm.setAttr(attr,0)
                        facial_points.append(points_length)
                    out_list = []
                    for index in range(len(attr_list)):
                        if self.dialog.facial_points[index]!= facial_points[index]:
                            out_list.append(attr_list[index][0])
                    if out_list:
                        # pm.confirmDialog( title='Facial check', message=u"<检测出publish文件表情存在问题>\n<请检查表情控制>\n\n"+"\n".join(out_list)+u"\n\n动态是否有问题", button=['我知道了'], defaultButton='Yes',)
                        cmds.warning(u"<检测出publish文件表情存在问题>\n<请检查表情控制>\n\n"+"\n".join(out_list)+u"\n\n动态是否有问题")
            except:
                print traceback.format_exc()
                pass

            try:
                if cmds.objExists("rig.char_type"):
                    char_type = cmds.getAttr("rig.char_type")
                    if "Biped" in char_type or  "Quadruped" in char_type or "CatWorld" in char_type:
                        animationPath=os.path.dirname(__file__).replace('\\','/')+'/biped.animation'
                        if cmds.objExists("facial_controls_grp"):
                            facialanimationPath=os.path.dirname(__file__).replace('\\','/')+'/three_facial.animation'
                            importAnim(facialanimationPath)
                        elif cmds.objExists("facial_CtrlGrp"):
                            facialanimationPath=os.path.dirname(__file__).replace('\\','/')+'/facial.animation'
                            importAnim(facialanimationPath)
                        importAnim(animationPath)
            except:
                print traceback.format_exc()
                pass
            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description


    def get_height(self):
        l_v_meshes = pm.ls(type='mesh', visible=True)

        mesh_list = []
        for m in l_v_meshes:
            if not m.fullPath().startswith('|master'):
                continue
            if m.getAttr('intermediateObject'):
                continue
            mesh_list.append(m)

        bbx = pm.exactWorldBoundingBox(mesh_list)
        if len(l_v_meshes) > 0:
            return bbx[4]-bbx[1]
        else:
            return None

def get_visible_components():
    def is_mesh_visible(mesh_name):
        visibility = cmds.getAttr("{}.visibility".format(mesh_name))
        parent = cmds.listRelatives(mesh_name, parent=True)
        while visibility and parent:
            parent_name = parent[0]
            visibility = visibility and cmds.getAttr("{}.visibility".format(parent_name))
            parent = cmds.listRelatives(parent_name, parent=True)
        return visibility

    mesh_transforms_alt = cmds.ls(type="transform", long=True)

    mesh_transforms_alt = [xform for xform in mesh_transforms_alt if
                           cmds.listRelatives(xform, shapes=True, type="mesh")]

    visible_vertex_total = 0
    visible_face_total = 0
    for i in mesh_transforms_alt:
        if is_mesh_visible(i):
            visible_vertex_total += len(cmds.ls("{}.vtx[*]".format(i), fl=True))
            visible_face_total += len(cmds.ls("{}.f[*]".format(i), fl=True))

    return "{}: {}, {}: {}".format("vertex_total", visible_vertex_total, "face_total", visible_face_total)




def export_isKeyable_attr_json(version_dir):
    ctrl_array = []
    for i in cmds.ls("*_ctrl"):
        if i.endswith("_pri_ctrl") or i.endswith("_sec_ctrl"):
            continue
        ctrl_array.append(i)
    result_dict = {}
    for each_ctrl in ctrl_array:
        attr = cmds.listAttr(each_ctrl, k=True)
        if attr == None:
            attr = []

        attr_a = []
        for i in attr:
            attr_path = "{}.{}".format(each_ctrl, i)
            if cmds.objExists(attr_path):  # 检查属性是否存在
                if not cmds.getAttr(attr_path, l=True):  # 检查是否可设置
                    attr_a.append(i)
        result_dict.update({each_ctrl: attr_a})

    isKeyable_json_path = "%s/isKeyable_attr.json" % version_dir
    with open(isKeyable_json_path, 'w') as f:
        json.dump(result_dict, f, ensure_ascii=False, indent=4)

    return result_dict


def convertEnumToList(enum_names):
    input_str = str(enum_names)

    if input_str.startswith(u"[u'") and input_str.endswith(u"']"):
        cleaned_str = input_str[3:-2]
        result_list = cleaned_str.split(':')
        return result_list
    else:
        print("Input string format doesn't match expected pattern.")


def getLookPassSwitchNode(lookPassAttr):
    connections = cmds.listConnections(lookPassAttr, destination=True, source=False, plugs=True, type='lc_switch')

    destination_nodes = []
    #print(connections)
    if connections:
        for connection in connections:
            destination_node = cmds.ls(connection, objectsOnly=True)[0]
            destination_nodes.append(destination_node)
    return destination_nodes



def getSwitchNodeConnections(lcSwitchNodeList):
    connected_attributes_list = []
    for switch_node in lcSwitchNodeList:
        for i in range(26):  # Checking for outAlpha_a to outAlpha_z
            attribute = 'outAlpha_' + chr(ord('a') + i)
            if cmds.connectionInfo(switch_node + '.' + attribute, isSource=True):
                # connected_nodes = cmds.listConnections(switch_node + '.' + attribute, plugs=True)
                if (i) not in connected_attributes_list:
                    connected_attributes_list.append(i)
    return connected_attributes_list


def get_mesh_transforms_under_group(groupName):
    # Find all 'poly' nodes in the scene
    poly_nodes = cmds.ls(str(groupName), type='transform', long=True)
    # poly_nodes = groupName

    # If no 'poly' nodes found, return an empty list
    if not poly_nodes:
        print("No 'poly' nodes found in the scene.")
        return []

    # Initialize a list to store mesh transform nodes
    mesh_transforms = []

    # Iterate through each 'poly' node
    for poly_node in poly_nodes:
        # Get all descendants of this poly node
        descendants = cmds.listRelatives(poly_node, allDescendents=True, fullPath=True) or []

        # Filter for transform nodes
        transform_nodes = cmds.ls(descendants, type='transform', long=True)

        # Iterate through each transform node
        for node in transform_nodes:
            # Get the shape nodes of this transform
            shapes = cmds.listRelatives(node, shapes=True, fullPath=True) or []

            # Check if any of the shapes is a mesh
            for shape in shapes:
                if cmds.nodeType(shape) == 'mesh':
                    mesh_transforms.append(node)
                    break  # No need to check other shapes once we find a mesh

    # Sort the list for consistent order
    mesh_transforms.sort()

    return mesh_transforms

def get_transforms_under_group(groupName):
    # Find all 'poly' nodes in the scene
    poly_nodes = cmds.ls(str(groupName), type='transform', long=True)
    # poly_nodes = groupName

    # If no 'poly' nodes found, return an empty list
    if not poly_nodes:
        print("No 'poly' nodes found in the scene.")
        return []

    # Initialize a list to store mesh transform nodes
    mesh_transforms = []

    # Iterate through each 'poly' node
    for poly_node in poly_nodes:
        # Get all descendants of this poly node
        descendants = cmds.listRelatives(poly_node, allDescendents=True, fullPath=True) or []

        # Filter for transform nodes
        transform_nodes = cmds.ls(descendants, type='transform', long=True)

        # Iterate through each transform node
        for node in transform_nodes:
            if node not in mesh_transforms:
                mesh_transforms.append(node)

    # Sort the list for consistent order
    mesh_transforms.sort()

    return mesh_transforms

def get_true_visibility(object_name):
    """
    Determine the true visibility of a Maya object by checking its own visibility
    and the visibility of all its parent objects in the hierarchy.

    :param object_name: Name of the Maya object
    :type object_name: str
    :return: True if the object and all its parents are visible, False otherwise
    :rtype: bool
    """
    # Get the full path of the object
    object_paths = cmds.ls(object_name, long=True)

    # Check if the object exists
    if not object_paths:
        raise ValueError("Object '{}' does not exist.".format(object_name))

    # If there are multiple objects with the same name, use the first one
    object_path = object_paths[0]

    # Split the path into individual object names
    objects = object_path.split('|')[1:]  # Exclude the leading '|'

    # Build paths incrementally to check each object in the hierarchy
    current_path = ""
    for obj in objects:
        current_path += "|{}".format(obj)

        # Check if the current object is visible
        is_visible = cmds.getAttr("{}.v".format(current_path))

        # If any object in the hierarchy is not visible, return False
        if not is_visible:
            return False

    # If we've made it this far, all objects in the hierarchy are visible
    return True


def remove_zero_values(d):
    return {k: v for k, v in d.items() if v != 0}

def unique_list(values):
    """去重并保持原顺序。"""
    result = []
    seen = set()

    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)

    return result


def get_enum_items(enum_attr):
    """
    获取 enum 属性的枚举值和枚举名称。

    支持：
        default:face_a:face_b

    也支持显式指定枚举值：
        default=0:face_a=5:face_b=8

    返回：
        [
            (0, 'default'),
            (1, 'face_a'),
            (2, 'face_b')
        ]
    """
    if not cmds.objExists(enum_attr):
        return []

    node_name, attr_name = enum_attr.split('.', 1)

    enum_data = cmds.attributeQuery(
        attr_name,
        node=node_name,
        listEnum=True
    ) or []

    if not enum_data:
        return []

    enum_items = []
    current_index = 0

    for item in enum_data[0].split(':'):
        enum_name = item

        if '=' in item:
            possible_name, possible_index = item.rsplit('=', 1)

            try:
                current_index = int(possible_index)
                enum_name = possible_name
            except ValueError:
                enum_name = item

        enum_items.append((current_index, enum_name))
        current_index += 1

    return enum_items


def get_animcurve_uu_records(rig_pass_attr):
    """
    从 rigPass 属性找到它输出连接的所有 animCurveUU，
    再从每个 animCurveUU.output 找到被驱动的 transform。

    skipConversionNodes=True 可以跳过 unitConversion 节点。

    返回：
        [
            {
                'animCurve': 'facePass_face_a',
                'transforms': [
                    '|character|face_pass_grp|face_a_grp'
                ]
            }
        ]
    """
    if not cmds.objExists(rig_pass_attr):
        return []

    anim_curves = cmds.listConnections(
        rig_pass_attr,
        source=False,
        destination=True,
        type='animCurveUU'
    ) or []

    anim_curves = unique_list(anim_curves)

    records = []

    for anim_curve in anim_curves:
        output_attr = '{}.output'.format(anim_curve)

        destination_plugs = cmds.listConnections(
            output_attr,
            source=False,
            destination=True,
            plugs=True,
            skipConversionNodes=True
        ) or []

        transform_paths = []

        for destination_plug in destination_plugs:
            destination_node = destination_plug.split('.', 1)[0]

            if not cmds.objExists(destination_node):
                continue

            if cmds.nodeType(destination_node) != 'transform':
                continue

            long_paths = cmds.ls(
                destination_node,
                long=True,
                type='transform'
            ) or []

            transform_paths.extend(long_paths)

        records.append({
            'animCurve': anim_curve,
            'transforms': unique_list(transform_paths)
        })

    return records


def is_path_under_allowed_group(long_path, allowed_groups=('hi', 'shape')):
    """
    根据 DAG 长路径判断物体是否位于指定组下面。

    支持 namespace，例如：
        |charA:root|charA:hi|charA:body_geo

    会把 charA:hi 识别为 hi。
    """
    if not long_path:
        return False

    allowed_groups = set(allowed_groups)

    path_parts = [
        part for part in long_path.split('|')
        if part
    ]

    # 排除物体自身，只检查它的祖先层级。
    parent_parts = path_parts[:-1]

    for part in parent_parts:
        # charA:hi -> hi
        short_name_without_namespace = part.rsplit(':', 1)[-1]

        if short_name_without_namespace in allowed_groups:
            return True

    return False


def get_mesh_transforms_under_groups(groups,allowed_groups=('hi', 'shape'),include_intermediate=False):
    """
    获取多个 transform 组下所有 mesh transform 的长路径。

    最终只保留处于 hi 或 shape 组下面的物体。
    """
    result = []

    for group in groups:
        if not cmds.objExists(group):
            continue

        mesh_shapes = cmds.listRelatives(
            group,
            allDescendents=True,
            type='mesh',
            fullPath=True
        ) or []

        for mesh_shape in mesh_shapes:
            if not include_intermediate:
                intermediate_attr = '{}.intermediateObject'.format(mesh_shape)

                if cmds.objExists(intermediate_attr):
                    if cmds.getAttr(intermediate_attr):
                        continue

            parents = cmds.listRelatives(
                mesh_shape,
                parent=True,
                fullPath=True
            ) or []

            if not parents:
                continue

            mesh_transform = parents[0]

            if not is_path_under_allowed_group(
                    mesh_transform,
                    allowed_groups=allowed_groups):
                continue

            result.append(mesh_transform)

    # 长路径排序，使每次输出结果稳定。
    return sorted(set(result))

def get_mesh_tuple_list_v2(rigPassAttr):
    """
    新逻辑：

    1. 找到 rigPassAttr 输出连接的所有 animCurveUU。
    2. 找到所有 animCurveUU.output 驱动的 transform。
    3. 依次设置 rigPassAttr 的 enum index。
    4. 找到当前 visibility == 1 的被驱动 transform。
    5. 获取这些 transform 下的所有 mesh transform 长路径。
    6. 只保留 DAG 路径中处于 hi 或 shape 组下的 mesh。

    返回：
        rigPass_tuple_list:
            [
                ('default', 1),
                ('face_a', 1),
                ('face_b', 0)
            ]

        pass_mesh_dict:
            {
                'rigPass.default': [
                    '|character|hi|body_geo'
                ],
                'rigPass.face_a': [
                    '|character|shape|face_a_geo'
                ]
            }
    """
    if not cmds.objExists(rigPassAttr):
        return [], {}

    enum_items = get_enum_items(rigPassAttr)

    if not enum_items:
        return [], {}

    # 记录 animCurveUU 及其输出连接的 transform。
    animcurve_records = get_animcurve_uu_records(rigPassAttr)

    connected_transforms = []

    for record in animcurve_records:
        connected_transforms.extend(record['transforms'])

    connected_transforms = unique_list(connected_transforms)

    attr_short_name = rigPassAttr.split('.', 1)[1]

    pass_mesh_dict = {}
    visible_groups_by_pass = {}
    rigPass_tuple_list = []

    original_value = cmds.getAttr(rigPassAttr)
    was_locked = cmds.getAttr(rigPassAttr, lock=True)

    base_mesh_set = None

    try:
        if was_locked:
            cmds.setAttr(rigPassAttr, lock=False)

        for enum_value, enum_name in enum_items:
            cmds.setAttr(rigPassAttr, enum_value)

            visible_groups = []

            for transform in connected_transforms:
                if not cmds.objExists(transform):
                    continue

                visibility_attr = '{}.visibility'.format(transform)

                if not cmds.objExists(visibility_attr):
                    continue

                # 这里只检查 transform 自身的 visibility。
                if cmds.getAttr(visibility_attr):
                    visible_groups.append(transform)

            visible_groups = unique_list(visible_groups)

            mesh_transforms = get_mesh_transforms_under_groups(
                visible_groups,
                allowed_groups=('hi', 'shape'),
                include_intermediate=False
            )

            pass_key = '{}.{}'.format(attr_short_name, enum_name)

            visible_groups_by_pass[pass_key] = visible_groups
            pass_mesh_dict[pass_key] = mesh_transforms

            current_mesh_set = set(mesh_transforms)

            # 保持原函数的 tuple 语义：
            # 第一个枚举固定为 1，其他枚举和第一个枚举结果不同时为 1。
            if base_mesh_set is None:
                base_mesh_set = current_mesh_set
                has_change = 1
            else:
                has_change = int(current_mesh_set != base_mesh_set)

            rigPass_tuple_list.append((enum_name, enum_value))

    finally:
        # 恢复原始 enum 值及锁定状态，避免函数执行后改变场景状态。
        try:
            cmds.setAttr(rigPassAttr, original_value)
        finally:
            if was_locked:
                cmds.setAttr(rigPassAttr, lock=True)

    return rigPass_tuple_list, pass_mesh_dict

def writePassInfo(fullPassInfoPath, rig_version_name, assertName):
    # if True:
    if 1:
        # get look pass =================================================================================================================
        lookPassAttr = ""
        lookPassAttr1 = "visibility_ctrl.lookPass"
        lookPassAttr2 = "visibility_ctrl.LookPass"
        lookPassAttr3 = "visibility_ctrl.Lookpass"
        lookPassAttr4 = "visibility_ctrl.lookpass"
        lookPassAttr5 = "visibility_ctrl.look_Pass"
        lookPassAttr6 = "visibility_ctrl.Look_Pass"
        lookPassAttr7 = "visibility_ctrl.Look_pass"
        lookPassAttr8 = "visibility_ctrl.look_pass"

        if cmds.objExists(lookPassAttr1):
            lookPassAttr = lookPassAttr1
        elif cmds.objExists(lookPassAttr2):
            lookPassAttr = lookPassAttr2
        elif cmds.objExists(lookPassAttr3):
            lookPassAttr = lookPassAttr3
        elif cmds.objExists(lookPassAttr4):
            lookPassAttr = lookPassAttr4
        elif cmds.objExists(lookPassAttr5):
            lookPassAttr = lookPassAttr5
        elif cmds.objExists(lookPassAttr6):
            lookPassAttr = lookPassAttr6
        elif cmds.objExists(lookPassAttr7):
            lookPassAttr = lookPassAttr7
        elif cmds.objExists(lookPassAttr8):
            lookPassAttr = lookPassAttr8

        if lookPassAttr:
            if cmds.objExists(lookPassAttr):
                if cmds.attributeQuery(lookPassAttr.split(".")[1], node=lookPassAttr.split(".")[0], exists=True):
                    # [u'default:fantasy:c10140:c30020:c90630:c90680:c90700:c90730:gourd']
                    enum_names = cmds.attributeQuery(lookPassAttr.split(".")[1], node=lookPassAttr.split(".")[0],
                                                     listEnum=True)
                    # ['default','fantasy','c10140','c30020','c90630','c90680','c90700','c90730','gourd']
                    try:
                        result_list = convertEnumToList(enum_names)
                    except:
                        result_list = []
                    try:
                        lcSwitchNodeList = getLookPassSwitchNode(lookPassAttr)
                    except:
                        lcSwitchNodeList = []

                    linkedAttributeList = []
                    if lcSwitchNodeList:
                        linkedAttributeList = getSwitchNodeConnections(lcSwitchNodeList)

                        lookPass_tuple_list = [(name, 1 if i in linkedAttributeList else 0) for i, name in
                                               enumerate(result_list)]
                    elif result_list:
                        lookPass_tuple_list = [(name, 1 if i == 0 else 0) for i, name in enumerate(result_list)]

                    else:
                        lookPass_tuple_list = []
                else:
                    lookPass_tuple_list = []
            else:
                lookPass_tuple_list = []
        else:
            lookPass_tuple_list = []
        # get rig pass =================================================================================================================
        rigPassAttr = ""
        rigPassAttr1 = "visibility_ctrl.rigPass"
        rigPassAttr2 = "visibility_ctrl.RigPass"
        rigPassAttr3 = "visibility_ctrl.Rigpass"
        rigPassAttr4 = "visibility_ctrl.rigpass"
        rigPassAttr5 = "visibility_ctrl.rig_Pass"
        rigPassAttr6 = "visibility_ctrl.Rig_Pass"
        rigPassAttr7 = "visibility_ctrl.Rig_pass"
        rigPassAttr8 = "visibility_ctrl.rig_pass"
        rigPassAttr9 = "visibility_ctrl.pear_state"
        mesh_grp1 = 'poly'
        mesh_grp2 = 'shape'
        useLookPassDrive = 0
        model_shapes = []

        if cmds.objExists(mesh_grp1):
            # model_shapes1 = cmds.listRelatives(mesh_grp1, ad=True, type='transform', f=True)
            model_shapes1 = get_mesh_transforms_under_group(mesh_grp1)
            # print model_shapes1
            if model_shapes1:
                if len(model_shapes1) > 0:
                    model_shapes = model_shapes1

        if cmds.objExists(mesh_grp2):
            # model_shapes2 = cmds.listRelatives(mesh_grp2, ad=True, type='transform', f=True)
            model_shapes2 = get_mesh_transforms_under_group(mesh_grp2)
            # print model_shapes2
            if model_shapes2:
                if len(model_shapes2) > 0:
                    model_shapes = model_shapes2

        if cmds.objExists(mesh_grp1):
            if cmds.objExists(mesh_grp2):
                if model_shapes1:
                    if model_shapes2:
                        if len(model_shapes1) > 0:
                            if len(model_shapes2) > 0:
                                model_shapes = list(set(model_shapes1) | set(model_shapes2))
        meshTransforms = []
        meshTransforms = model_shapes

        if cmds.objExists(rigPassAttr1):
            rigPassAttr = rigPassAttr1
        elif cmds.objExists(rigPassAttr2):
            rigPassAttr = rigPassAttr2
        elif cmds.objExists(rigPassAttr3):
            rigPassAttr = rigPassAttr3
        elif cmds.objExists(rigPassAttr4):
            rigPassAttr = rigPassAttr4
        elif cmds.objExists(rigPassAttr5):
            rigPassAttr = rigPassAttr5
        elif cmds.objExists(rigPassAttr6):
            rigPassAttr = rigPassAttr6
        elif cmds.objExists(rigPassAttr7):
            rigPassAttr = rigPassAttr7
        elif cmds.objExists(rigPassAttr8):
            rigPassAttr = rigPassAttr8
        elif cmds.objExists(rigPassAttr9):
            rigPassAttr = rigPassAttr9

        setRigPassAttrAsLookPassAttr = 0
        # some chr use lookPass connect model vis
        if not rigPassAttr:
            return
            if lookPassAttr:
                rigPassAttr = lookPassAttr
                setRigPassAttrAsLookPassAttr = 1
        else:
            pass

        new_visibility_dict = {}
        new_visibility_dict1 = {}
        new_visibility_dict2 = {}
        true_visibility_dict = {}
        visibility_dict = {}
        changed_obj_list = []
        if cmds.objExists(rigPassAttr):
            if cmds.connectionInfo(rigPassAttr, isDestination=True):
                connected_attrs = cmds.listConnections(rigPassAttr, source=True, destination=False,
                                                       plugs=True)
                if lookPassAttr in connected_attrs:
                    useLookPassDrive = 1
                else:
                    pass

            rigPassAttrList = convertEnumToList(
                cmds.attributeQuery(rigPassAttr.split(".")[1], node=rigPassAttr.split(".")[0], listEnum=True))
            visibility_changes = []
            visibility_dict = {}

            # check if any objects works
            SSconnections = cmds.listConnections(rigPassAttr, plugs=True, source=True, destination=False)
            cmds.setAttr(rigPassAttr, l=0)
            print('rigPassAttr', rigPassAttr)
            print('SSconnections', SSconnections)
            print('useLookPassDrive', useLookPassDrive)
            # if SSconnections:
            #    cmds.disconnectAttr(SSconnections[0], rigPassAttr)
            #    print('disconnect ' + SSconnections)

            for index in range(len(rigPassAttrList)):
                if useLookPassDrive == 1:
                    cmds.setAttr(lookPassAttr, index)
                else:
                    cmds.setAttr(rigPassAttr, index)
                visibility_state = []
                object_visibility = {}

                for model_shape in meshTransforms:

                    """
                    # fake vis only self vis
                    visibilityAttr = cmds.getAttr(model_shape + '.visibility')
                    visibility_state.append(visibilityAttr)
                    if visibilityAttr == True:
                        visibilityAttr = 1
                    elif visibilityAttr == False:
                        visibilityAttr = 0
                    """
                    visibilityAttr = get_true_visibility(model_shape)
                    visibility_state.append(visibilityAttr)
                    if visibilityAttr == True:
                        visibilityAttr = 1
                    elif visibilityAttr == False:
                        visibilityAttr = 0
                    object_visibility[model_shape] = visibilityAttr

                visibility_dict['rigPass.' + rigPassAttrList[index]] = object_visibility

                if index == 0:
                    base_visibility_state = visibility_state
                    visibility_changes.append(index)
                else:
                    if visibility_state != base_visibility_state:
                        visibility_changes.append(index)
            # print('visibility_dict',visibility_dict)
            # print('====================================================================================')
            # print('visibility_changes', visibility_changes)

            if useLookPassDrive == 1:
                cmds.setAttr(lookPassAttr, 0)
            else:
                cmds.setAttr(rigPassAttr, 0)

            rigPass_tuple_list = [(name, 1 if i in visibility_changes else 0) for i, name in
                                  enumerate(rigPassAttrList)]

            if setRigPassAttrAsLookPassAttr == 1:
                visibility_changes.pop(0)
                if 1 not in visibility_changes:
                    rigPassAttr = ''
                    rigPass_tuple_list = []

            if visibility_dict:
                # print('visibility_dict', visibility_dict)
                # true_visibility_dict = update_true_visibility(visibility_dict)
                new_visibility_dict = fliterChangeObjectRigPass(visibility_dict)
                # print('new_visibility_dict', new_visibility_dict)

                # remove 0 value mesh
                new_visibility_dict1 = {
                    key: remove_zero_values(value)
                    for key, value in new_visibility_dict.items()
                }

                # remove value and put key in list
                new_visibility_dict2 = {}
                for category, meshes in new_visibility_dict1.items():
                    new_visibility_dict2[category] = list(meshes.keys())

                # try:
                #    changed_obj_list = get_inner_keys(new_visibility_dict)
                # except:
                #    pass

            else:
                new_visibility_dict2 = visibility_dict

        else:
            rigPass_tuple_list = []
        pass_dict = {'lookPass': lookPass_tuple_list, 'rigPass': rigPass_tuple_list, 'version': rig_version_name}
        pass_dict_name = {'lookPassName': lookPassAttr, 'rigPassName': rigPassAttr,
                          'rigPassDrivenByLookPass': useLookPassDrive}
        look_pass_state = {item[0]: item[1] for item in pass_dict["lookPass"]}
        rig_pass_state = {item[0]: item[1] for item in pass_dict["rigPass"]}

        combined_dict = {
            "version": pass_dict["version"],
            "look_pass_state": look_pass_state,
            "rig_pass_state": rig_pass_state,
            "rigPassMesh": new_visibility_dict2,
            "rigPass_name": pass_dict_name["rigPassName"],
            "lookPass_name": pass_dict_name["lookPassName"],
            "rigPassDrivenByLookPass": pass_dict_name["rigPassDrivenByLookPass"]
        }

        # Final dictionary
        final_dict = {"pass_info": combined_dict}

        # Function to write dictionary to JSON file with custom formatting

        # Write to JSON file with custom formatting
        # print(combined_dict)
        # print(final_dict)

        with open(fullPassInfoPath, 'w') as f:
            f.write(json.dumps(final_dict, indent=4, cls=CustomEncoder))
            # json.dump(pass_dict, f)
            # f.write('\n')
            # json.dump(pass_dict_name, f)
            # f.write('\n')
            # json.dump(new_visibility_dict2, f)
            # f.write('\n')
            # json.dump(changed_obj_list, f)
            # f.write('\n')
    # except:
    #    return 'manual'

    print("writeInfoFInished====================================================")

    return pass_dict


class CustomEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super(CustomEncoder, self).__init__(*args, **kwargs)
        self.indent_level = 0

    def encode(self, obj):
        if isinstance(obj, dict):
            self.indent_level += 1
            items = []
            for key, value in obj.items():
                items.append('\n{}"{}": {}'.format(' ' * (self.indent_level * 4), key, self.encode(value)))
            self.indent_level -= 1
            return '{' + ','.join(items) + '\n' + ' ' * (self.indent_level * 4) + '}'
        elif isinstance(obj, list):
            self.indent_level += 1
            items = ['\n{}{}'.format(' ' * (self.indent_level * 4), self.encode(value)) for value in obj]
            self.indent_level -= 1
            return '[' + ','.join(items) + '\n' + ' ' * (self.indent_level * 4) + ']'
        return json.dumps(obj)

def fliterChangeObjectRigPass(folders):
    # Step 1: Collect the counts of each path's value
    path_value_counts = {}

    for folder_name, folder_content in folders.items():
        for path, value in folder_content.items():
            if path not in path_value_counts:
                path_value_counts[path] = {}
            if value not in path_value_counts[path]:
                path_value_counts[path][value] = 0
            path_value_counts[path][value] += 1

    # Step 2: Identify paths to be removed
    paths_to_remove = set()
    for path, value_counts in path_value_counts.items():
        if len(value_counts) == 1:
            paths_to_remove.add(path)

    # Step 3: Remove these paths from each folder
    for folder_name in folders.keys():
        for path in paths_to_remove:
            if path in folders[folder_name]:
                del folders[folder_name][path]

    return folders


def get_inner_keys(d):
    # Get any one of the top-level keys
    top_level_key = next(iter(d))

    # Extract the keys inside the selected key
    inner_keys = list(d[top_level_key].keys())

    return inner_keys

def is_under_hair_grp(obj, grp):
    if not cmds.objExists(obj) or not cmds.objExists(grp):
        return False

    full_path = cmds.ls(obj, long=True)[0]
    if grp + '|' in full_path:
        return True
    return False


def get_mesh_tuple_list(rigPassAttr):
    new_visibility_dict = {}
    new_visibility_dict1 = {}
    new_visibility_dict2 = {}
    true_visibility_dict = {}
    visibility_dict = {}
    changed_obj_list = []

    mesh_grp1 = 'poly'
    mesh_grp2 = 'shape'
    useLookPassDrive = 0
    model_shapes = []

    if cmds.objExists(mesh_grp1):
        # model_shapes1 = cmds.listRelatives(mesh_grp1, ad=True, type='transform', f=True)
        model_shapes1 = get_mesh_transforms_under_group(mesh_grp1)
        # print model_shapes1
        if model_shapes1:
            if len(model_shapes1) > 0:
                model_shapes = model_shapes1

    if cmds.objExists(mesh_grp2):
        # model_shapes2 = cmds.listRelatives(mesh_grp2, ad=True, type='transform', f=True)
        model_shapes2 = get_mesh_transforms_under_group(mesh_grp2)
        # print model_shapes2
        if model_shapes2:
            if len(model_shapes2) > 0:
                model_shapes = model_shapes2

    if cmds.objExists(mesh_grp1):
        if cmds.objExists(mesh_grp2):
            if model_shapes1:
                if model_shapes2:
                    if len(model_shapes1) > 0:
                        if len(model_shapes2) > 0:
                            model_shapes = list(set(model_shapes1) | set(model_shapes2))
    meshTransforms = []
    meshTransforms = model_shapes

    if cmds.objExists(rigPassAttr):
        if cmds.connectionInfo(rigPassAttr, isDestination=True):
            connected_attrs = cmds.listConnections(rigPassAttr, source=True, destination=False, plugs=True)
            # if lookPassAttr in connected_attrs:
            #     useLookPassDrive = 1
            # else:
            #     pass

        rigPassAttrList = convertEnumToList(cmds.attributeQuery(rigPassAttr.split(".")[1], node=rigPassAttr.split(".")[0], listEnum=True))
        visibility_changes = []
        visibility_dict = {}

        SSconnections = cmds.listConnections(rigPassAttr, plugs=True, source=True, destination=False)
        cmds.setAttr(rigPassAttr, l=0)
        print('index1013', rigPassAttr)
        print('index1028', rigPassAttrList)
        if rigPassAttrList == []:
            return

        for index in range(len(rigPassAttrList)):
            cmds.setAttr(rigPassAttr, index)
            visibility_state = []
            object_visibility = {}

            for model_shape in meshTransforms:

                visibilityAttr = get_true_visibility(model_shape)
                visibility_state.append(visibilityAttr)
                if visibilityAttr == True:
                    visibilityAttr = 1
                elif visibilityAttr == False:
                    visibilityAttr = 0

                if is_under_hair_grp(model_shape, grp='hair_grp') or is_under_hair_grp(model_shape, grp='face_hair') or is_under_hair_grp(model_shape, grp='head_hair') or is_under_hair_grp(model_shape, grp='face_pass_grp'):
                    visibilityAttr = cmds.getAttr(model_shape + '.visibility')

                object_visibility[model_shape] = visibilityAttr

            visibility_dict['{}.'.format(rigPassAttr.split('.')[1]) + rigPassAttrList[index]] = object_visibility

            if index == 0:

                base_visibility_state = visibility_state
                visibility_changes.append(index)
            else:
                if visibility_state != base_visibility_state:
                    visibility_changes.append(index)

        rigPass_tuple_list = [(name, 1 if i in visibility_changes else 0) for i, name in enumerate(rigPassAttrList)]

        # if setRigPassAttrAsLookPassAttr == 1:
        #     visibility_changes.pop(0)
        #     if 1 not in visibility_changes:
        #         rigPassAttr = ''
        #         rigPass_tuple_list = []

        if visibility_dict:
            new_visibility_dict = fliterChangeObjectRigPass(visibility_dict)

            new_visibility_dict1 = {
                key: remove_zero_values(value)
                for key, value in new_visibility_dict.items()
            }

            new_visibility_dict2 = {}
            for category, meshes in new_visibility_dict1.items():
                new_visibility_dict2[category] = list(meshes.keys())

        else:
            new_visibility_dict2 = visibility_dict

    else:
        rigPass_tuple_list = []

    return rigPass_tuple_list, new_visibility_dict2


def get_hair_mesh_tuple_list(rigPassAttr):
    new_visibility_dict = {}
    new_visibility_dict1 = {}
    new_visibility_dict2 = {}
    true_visibility_dict = {}
    visibility_dict = {}
    changed_obj_list = []

    mesh_grp1 = 'poly'
    mesh_grp2 = 'shape'
    useLookPassDrive = 0
    model_shapes = []

    if cmds.objExists(mesh_grp1):
        # model_shapes1 = cmds.listRelatives(mesh_grp1, ad=True, type='transform', f=True)
        model_shapes1 = get_mesh_transforms_under_group(mesh_grp1)
        # print model_shapes1
        if model_shapes1:
            if len(model_shapes1) > 0:
                model_shapes = model_shapes1

    if cmds.objExists(mesh_grp2):
        # model_shapes2 = cmds.listRelatives(mesh_grp2, ad=True, type='transform', f=True)
        model_shapes2 = get_mesh_transforms_under_group(mesh_grp2)
        # print model_shapes2
        if model_shapes2:
            if len(model_shapes2) > 0:
                model_shapes = model_shapes2

    if cmds.objExists(mesh_grp1):
        if cmds.objExists(mesh_grp2):
            if model_shapes1:
                if model_shapes2:
                    if len(model_shapes1) > 0:
                        if len(model_shapes2) > 0:
                            model_shapes = list(set(model_shapes1) | set(model_shapes2))
    meshTransforms = []
    meshTransforms = model_shapes

    if cmds.objExists(rigPassAttr):
        if cmds.connectionInfo(rigPassAttr, isDestination=True):
            connected_attrs = cmds.listConnections(rigPassAttr, source=True, destination=False, plugs=True)
            # if lookPassAttr in connected_attrs:
            #     useLookPassDrive = 1
            # else:
            #     pass

        rigPassAttrList = convertEnumToList(
            cmds.attributeQuery(rigPassAttr.split(".")[1], node=rigPassAttr.split(".")[0], listEnum=True))
        visibility_changes = []
        visibility_dict = {}

        SSconnections = cmds.listConnections(rigPassAttr, plugs=True, source=True, destination=False)
        cmds.setAttr(rigPassAttr, l=0)
        print('index1013', rigPassAttr)
        print('index1028', rigPassAttrList)
        if rigPassAttrList == []:
            return

        for index in range(len(rigPassAttrList)):
            cmds.setAttr(rigPassAttr, index)
            visibility_state = []
            object_visibility = {}

            for model_shape in meshTransforms:

                visibilityAttr = get_true_visibility(model_shape)
                visibility_state.append(visibilityAttr)
                if visibilityAttr == True:
                    visibilityAttr = 1
                elif visibilityAttr == False:
                    visibilityAttr = 0

                if is_under_hair_grp(model_shape, grp='hair_grp') or is_under_hair_grp(model_shape, grp='face_hair') or is_under_hair_grp(
                        model_shape, grp='head_hair') or is_under_hair_grp(model_shape, grp='face_pass_grp'):
                    visibilityAttr = cmds.getAttr(model_shape + '.visibility')

                object_visibility[model_shape] = visibilityAttr

            visibility_dict['{}.'.format(rigPassAttr.split('.')[1]) + rigPassAttrList[index]] = object_visibility

            if index == 0:
                base_visibility_state = visibility_state
                visibility_changes.append(index)
            else:
                if visibility_state != base_visibility_state:
                    visibility_changes.append(index)

        #rigPass_tuple_list = [(name, 1 if i in visibility_changes else 0) for i, name in enumerate(rigPassAttrList)]
        rigPass_tuple_list = [(name, i) for i, name in enumerate(rigPassAttrList)]

        # if setRigPassAttrAsLookPassAttr == 1:
        #     visibility_changes.pop(0)
        #     if 1 not in visibility_changes:
        #         rigPassAttr = ''
        #         rigPass_tuple_list = []

        if visibility_dict:
            new_visibility_dict = fliterChangeObjectRigPass(visibility_dict)

            new_visibility_dict1 = {
                key: remove_zero_values(value)
                for key, value in new_visibility_dict.items()
            }

            new_visibility_dict2 = {}
            for category, meshes in new_visibility_dict1.items():
                new_visibility_dict2[category] = list(meshes.keys())

        else:
            new_visibility_dict2 = visibility_dict

    else:
        rigPass_tuple_list = []

    return rigPass_tuple_list, new_visibility_dict2



def get_direct_mesh_tuple_list(rigPassAttr):
    new_visibility_dict = {}
    new_visibility_dict1 = {}
    new_visibility_dict2 = {}
    true_visibility_dict = {}
    visibility_dict = {}
    changed_obj_list = []

    mesh_grp1 = 'shape'
    mesh_grp2 = 'shape'
    useLookPassDrive = 0
    model_shapes = []

    if cmds.objExists(mesh_grp1):
        # model_shapes1 = cmds.listRelatives(mesh_grp1, ad=True, type='transform', f=True)
        model_shapes1 = get_transforms_under_group(mesh_grp1)
        # print model_shapes1
        if model_shapes1:
            if len(model_shapes1) > 0:
                model_shapes = model_shapes1

    if cmds.objExists(mesh_grp2):
        # model_shapes2 = cmds.listRelatives(mesh_grp2, ad=True, type='transform', f=True)
        model_shapes2 = get_transforms_under_group(mesh_grp2)
        # print model_shapes2
        if model_shapes2:
            if len(model_shapes2) > 0:
                model_shapes = model_shapes2

    if cmds.objExists(mesh_grp1):
        if cmds.objExists(mesh_grp2):
            if model_shapes1:
                if model_shapes2:
                    if len(model_shapes1) > 0:
                        if len(model_shapes2) > 0:
                            model_shapes = list(set(model_shapes1) | set(model_shapes2))
    meshTransforms = []
    meshTransforms = model_shapes

    if cmds.objExists(rigPassAttr):
        if cmds.connectionInfo(rigPassAttr, isDestination=True):
            connected_attrs = cmds.listConnections(rigPassAttr, source=True, destination=False, plugs=True)
            # if lookPassAttr in connected_attrs:
            #     useLookPassDrive = 1
            # else:
            #     pass

        rigPassAttrList = convertEnumToList(cmds.attributeQuery(rigPassAttr.split(".")[1], node=rigPassAttr.split(".")[0], listEnum=True))
        visibility_changes = []
        visibility_dict = {}

        SSconnections = cmds.listConnections(rigPassAttr, plugs=True, source=True, destination=False)
        cmds.setAttr(rigPassAttr, l=0)
        print('index1013', rigPassAttr)
        print('index1028', rigPassAttrList)
        if rigPassAttrList == []:
            return

        for index in range(len(rigPassAttrList)):
            cmds.setAttr(rigPassAttr, index)
            visibility_state = []
            object_visibility = {}

            for model_shape in meshTransforms:

                visibilityAttr = False
                if cmds.getAttr("{}.v".format(model_shape)):
                    visibilityAttr = True
                else:
                    visibilityAttr = False

                visibility_state.append(visibilityAttr)
                if visibilityAttr == True:
                    visibilityAttr = 1
                elif visibilityAttr == False:
                    visibilityAttr = 0

                if is_under_hair_grp(model_shape, grp='hair_grp') or is_under_hair_grp(model_shape, grp='face_hair') or is_under_hair_grp(model_shape, grp='head_hair') or is_under_hair_grp(model_shape, grp='face_pass_grp'):
                    visibilityAttr = cmds.getAttr(model_shape + '.visibility')

                object_visibility[model_shape] = visibilityAttr

            visibility_dict['{}.'.format(rigPassAttr.split('.')[1]) + rigPassAttrList[index]] = object_visibility

            if index == 0:
                base_visibility_state = visibility_state
                visibility_changes.append(index)
            else:
                if visibility_state != base_visibility_state:
                    visibility_changes.append(index)

        rigPass_tuple_list = [(name, 1 if i in visibility_changes else 0) for i, name in
                              enumerate(rigPassAttrList)]

        # if setRigPassAttrAsLookPassAttr == 1:
        #     visibility_changes.pop(0)
        #     if 1 not in visibility_changes:
        #         rigPassAttr = ''
        #         rigPass_tuple_list = []

        if visibility_dict:
            new_visibility_dict = fliterChangeObjectRigPass(visibility_dict)

            new_visibility_dict1 = {
                key: remove_zero_values(value)
                for key, value in new_visibility_dict.items()
            }

            new_visibility_dict2 = {}
            for category, meshes in new_visibility_dict1.items():
                new_visibility_dict2[category] = list(meshes.keys())

        else:
            new_visibility_dict2 = visibility_dict

    else:
        rigPass_tuple_list = []

    return rigPass_tuple_list, new_visibility_dict2


def check_and_modify_group_visibility(group_name):
    if cmds.objExists(group_name):
        visibility_locked = cmds.getAttr(group_name + ".visibility", lock=True)
        visibility_value = cmds.getAttr(group_name + ".visibility")

        original_linked = cmds.listConnections(group_name + ".visibility", s=1, d=0)
        original_visibility_value = visibility_value
        original_visibility_locked = visibility_locked

        if visibility_locked:
            cmds.unlockAttr(group_name + ".visibility")

        if original_linked:
            cmds.disconnectAttr(original_linked[0], group_name + ".visibility")

        if visibility_value == 0:
            cmds.setAttr(group_name + ".visibility", 1)

        return original_linked, original_visibility_value, original_visibility_locked
    else:
        return '', '', ''


def restore_group_visibility(group_name, original_linked, original_visibility_value, original_visibility_locked):
    if cmds.objExists(group_name):
        cmds.setAttr(group_name + ".visibility", original_visibility_value)

        if original_linked:
            cmds.connectAttr(original_linked[0], group_name + ".visibility", f=1)

        if original_visibility_locked:
            cmds.lockAttr(group_name + ".visibility")
        else:
            cmds.unlockAttr(group_name + ".visibility")


def writeHairPassInfo(fullPassInfoPath, rig_version_name, assertName):
    if 1:
        # get hair pass =================================================================================================================
        rigPassAttr = ""
        rigPassAttr1 = "visibility_ctrl.faceHair"
        lookPassAttr = ""
        lookPassAttr1 = "visibility_ctrl.headHair"
        facePassAttr = ""
        facePassAttr1 = "visibility_ctrl.facePass"
        faceBeardPassAttr = ""
        faceBeardPassAttr1 = "visibility_ctrl.faceBeardPass"
        faceClothPassAttr = ""
        faceClothPassAttr1 = "visibility_ctrl.faceClothPass"
        if cmds.objExists(rigPassAttr1):
            rigPassAttr = rigPassAttr1
            rigPass_tuple_list, visibility_dict1 = get_mesh_tuple_list_v2(rigPassAttr)
        else:
            rigPass_tuple_list = []
            rig_pass_state = {}
            visibility_dict1 = {}

        if cmds.objExists(lookPassAttr1):
            lookPassAttr = lookPassAttr1
            lookPass_tuple_list, visibility_dict2 = get_mesh_tuple_list_v2(lookPassAttr)
        else:
            lookPass_tuple_list = []
            look_pass_state = {}
            visibility_dict2 = {}

        if cmds.objExists(facePassAttr1):
            facePassAttr = facePassAttr1
            facePass_tuple_list, visibility_dict3 = get_hair_mesh_tuple_list(facePassAttr)
            visibility_dict3 = get_face_pass_meshes(visibility_dict3, full_path=True)
        else:
            facePass_tuple_list = []
            face_pass_state = {}
            visibility_dict3 = {}

        if cmds.objExists(faceBeardPassAttr1):
            faceBeardPassAttr = faceBeardPassAttr1
            if cmds.objExists('shape'):
                cmds.setAttr('shape.v', 1)
            faceBeardPass_tuple_list, visibility_dict4 = get_mesh_tuple_list_v2(faceBeardPassAttr)
            print(visibility_dict4)
            if cmds.objExists('shape'):
                cmds.setAttr('shape.v', 0)
        else:
            faceBeardPass_tuple_list = []
            face_beard_pass_state = {}
            visibility_dict4 = {}

        if cmds.objExists(faceClothPassAttr1):
            faceClothPassAttr = faceClothPassAttr1
            if cmds.objExists('shape'):
                cmds.setAttr('shape.v', 1)
            faceClothPass_tuple_list, visibility_dict5 = get_mesh_tuple_list_v2(faceBeardPassAttr)
            print(visibility_dict5)
            if cmds.objExists('shape'):
                cmds.setAttr('shape.v', 0)
        else:
            faceClothPass_tuple_list = []
            face_Cloth_pass_state = {}
            visibility_dict5 = {}

        pass_dict = {'headHair': lookPass_tuple_list, 'faceHair': rigPass_tuple_list,  'facePass': facePass_tuple_list,  'faceBeardPass': faceBeardPass_tuple_list,  'faceClothPass': faceClothPass_tuple_list, 'version': rig_version_name}
        pass_dict_name = {'headHair': lookPassAttr, 'faceHair': rigPassAttr, 'facePass': facePassAttr,  'faceBeardPass': faceBeardPassAttr,  'faceClothPass': faceClothPassAttr}

        if pass_dict["{}".format(rigPassAttr1.split('.')[1])]:
            rig_pass_state = {item[0]: item[1] for item in pass_dict["{}".format(rigPassAttr1.split('.')[1])]}
        else:
            rig_pass_state = {}

        if pass_dict["{}".format(lookPassAttr1.split('.')[1])]:
            look_pass_state = {item[0]: item[1] for item in pass_dict["{}".format(lookPassAttr1.split('.')[1])]}
        else:
            look_pass_state = {}

        if pass_dict["{}".format(facePassAttr1.split('.')[1])]:
            face_pass_state = {item[0]: item[1] for item in pass_dict["{}".format(facePassAttr1.split('.')[1])]}
        else:
            face_pass_state = {}

        print(faceBeardPassAttr1)
        if pass_dict["{}".format(faceBeardPassAttr1.split('.')[1])]:
            faceBeardPass_state = {item[0]: item[1] for item in pass_dict["{}".format(faceBeardPassAttr1.split('.')[1])]}
        else:
            faceBeardPass_state = {}

        print(faceClothPassAttr1)
        if pass_dict["{}".format(faceClothPassAttr1.split('.')[1])]:
            faceClothPass_state = {item[0]: item[1] for item in pass_dict["{}".format(faceClothPassAttr1.split('.')[1])]}
        else:
            faceClothPass_state = {}

        combined_dict = {
            "version": pass_dict["version"],
            "headHair_state": look_pass_state,
            "faceHair_state": rig_pass_state,
            "facePass_state": face_pass_state,
            "faceBeardPass_state": faceClothPass_state,
            "faceClothPass_state": faceClothPass_state,

            "headHair_mesh": visibility_dict2,
            "faceHair_mesh": visibility_dict1,
            "facePass_mesh": visibility_dict3,
            "faceBeardPass_mesh": visibility_dict4,
            "faceClothPass_mesh": visibility_dict5,

            "faceHair_name": pass_dict_name["faceHair"],
            "headHair_name": pass_dict_name["headHair"],
            "facePass_name": pass_dict_name["facePass"],
            "faceBeardPass_name": pass_dict_name["faceBeardPass"],
            "faceClothPass_name": pass_dict_name["faceClothPass"]
        }

        final_dict = {"pass_info": combined_dict}

        with open(fullPassInfoPath, 'w') as f:
            f.write(json.dumps(final_dict, indent=4, cls=CustomEncoder))

    print("writeInfoFInished====================================================")

    return pass_dict


def writeFacePassInfo(fullPassInfoPath, rig_version_name, assertName):
    if 1:
        # get hair pass =================================================================================================================
        rigPassAttr = ""
        rigPassAttr1 = "visibility_ctrl.facePass"

        if cmds.objExists(rigPassAttr1):
            rigPassAttr = rigPassAttr1
            rigPass_tuple_list, visibility_dict1 = get_mesh_tuple_list(rigPassAttr)
        else:
            rigPass_tuple_list = []
            rig_pass_state = {}
            visibility_dict1 = {}

        pass_dict = {'facePass': rigPass_tuple_list, 'version': rig_version_name}
        pass_dict_name = {'facePass': rigPassAttr}

        if pass_dict["{}".format(rigPassAttr1.split('.')[1])]:
            rig_pass_state = {item[0]: item[1] for item in pass_dict["{}".format(rigPassAttr.split('.')[1])]}
        else:
            rig_pass_state = {}

        combined_dict = {
            "version": pass_dict["version"],
            "facePass_state": rig_pass_state,
            "facePass_mesh": visibility_dict1,
            "facePass_name": pass_dict_name["facePass"]
        }

        final_dict = {"pass_info": combined_dict}

        with open(fullPassInfoPath, 'w') as f:
            f.write(json.dumps(final_dict, indent=4, cls=CustomEncoder))

    print("writeInfoFInished====================================================")

    return pass_dict


def export_visibility_info(json_path=None):
    """
    导出绑定中名牌以及名牌层级下所有控制器控制显隐的参数
    """

    # 获取所有 visibility_ctrl 层级下的所有控制器，（transform节点）
    visibility_ctrl = "visibility_ctrl"
    shapes = mc.ls(mc.listRelatives(visibility_ctrl, ad=True, c=True), type="shape")
    ctrl_array = list(set(mc.listRelatives(shapes, p=True)))

    # 遍历所有控制器
    json_data = {}
    for e_ctrl in ctrl_array:
        # 获取通道栏中显示的属性，和自定义属性
        cb_attrs = []
        cb_attrs += mc.listAttr(e_ctrl, cb=True) or []
        cb_attrs += mc.listAttr(e_ctrl, k=True) or []
        cb_attrs = list(set(cb_attrs))

        # 遍历每个属性
        json_data[e_ctrl] = {}
        for e_attr in cb_attrs:
            if "_____" in e_attr:
                continue
            attr_info = {}
            # 获取属性的值
            value = mc.getAttr("{}.{}".format(e_ctrl, e_attr))
            attr_info.update({"value": value})
            # 如果是枚举类型的属性，获取枚举的各选项
            if mc.getAttr("{}.{}".format(e_ctrl, e_attr), type=True) == "enum":
                enum_str = mc.addAttr("{}.{}".format(e_ctrl, e_attr), q=True, en=True)
                enum_list = filter(None, enum_str.split(":"))
                attr_info.update({"enum": enum_list})
            # 将获取的信息整合
            json_data[e_ctrl][e_attr] = attr_info

    # 将信息输出json
    if json_path:
        with open(json_path, "w") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)
    return json_data


def importAnim(aniPath):
    with open(aniPath, 'r') as f:
        content = f.readlines()
    charInfoList = content[4].split(" ")
    for charInfo in charInfoList:
        if charInfo.startswith("namespace"):
            charName = charInfo.split("=")[1].replace("\"", "")
    ctrl_list = [a for a in content[5].split('//<objects list="')[1].split( '; ">\n')[0].split("; ") if pm.objExists(a)]
    ctrl_attr_list=[]
    for ctrl in ctrl_list:
        attrList = []
        attrList += pm.listAttr(ctrl,k=True) or []
        attrList += pm.listAttr(ctrl,cb=True) or []
        lockattr = pm.listAttr(ctrl,ud=1,cb=1,r=1,l=1) or []
        attr = list(set(attrList) - set(lockattr))
        for a in attr:
            ctrl_attr_list.append((ctrl,a,pm.getAttr(ctrl+ '.'+a)))
    cmds.file(aniPath, i=1, type="mayaAscii", ignoreVersion=1, ra=True, mergeNamespacesOnClash=True,namespace=":", options="v=0;", pr=1, importTimeRange="combine")
    pm.currentTime(1, e=1)
    tempCtrls = pm.listRelatives("MG_PoseAnim_animCache")
    for tempCtrl in tempCtrls:
        relatedCtrl = tempCtrl.ObjName.get().split(":")[-1]
        if pm.objExists(relatedCtrl):
            for lc in pm.listConnections(tempCtrl,p=1,s=1,d=0) or []:
                lcs = pm.listConnections(lc,p=1,s=0,d=1) or []
                if lcs:
                    try:
                        lc.connect("%s.%s"%(relatedCtrl,lcs[0].plugAttr()))
                    except:
                        pm.warning("%s.%s"%(relatedCtrl,lcs[0].plugAttr()))
    pm.delete("MG_PoseAnim_animCache")
    pm.setInfinity(ctrl_list, pri='cycle', poi='cycle' )
    return (ctrl_list,ctrl_attr_list)




def get_deform_model_info():
    total_vertex_count = 0
    total_face_count = 0
    shapes = cmds.ls(type='mesh')
    deformed_shape_list = []
    if shapes:
        for shape in shapes:
            if cmds.nodeType(shape) == 'mesh':
                # Check if the mesh has any deformation history
                if len(cmds.listHistory(shape)) < 2:
                    continue

                vertex_count = cmds.polyEvaluate(shape, vertex=True)
                total_vertex_count += vertex_count

                face_count = cmds.polyEvaluate(shape, face=True)
                total_face_count += face_count
    return total_vertex_count, total_face_count


def get_customShader_info():
    mesh_array = cmds.ls(type="mesh", long=True)
    result = []
    for i in mesh_array:
        if cmds.objExists("{}.customShader".format(i)):
            result.append(i)
    return result


def get_skinned_meshes_vertex_info():
    # 获取所有 skinCluster 节点
    skin_clusters = cmds.ls(type='skinCluster') or []
    processed = set()  # 用于去重
    total_vertices = 0
    model_names = []
    shape_names = []
    others_names = []
    total_cv_points = 0

    for sc in skin_clusters:
        # 获取该 skinCluster 影响的几何体（形状节点）
        geometries = cmds.deformer(sc, query=True, geometry=True) or []
        for geo_shape in geometries:
            # 获取几何体的变换节点（模型名称）
            transform = cmds.listRelatives(geo_shape, parent=True)
            transform = transform[0]
            # 去重
            if transform in processed:
                continue
            processed.add(transform)

            # 检查是否为多边形
            if cmds.objectType(geo_shape) == 'mesh':
                try:
                    # 获取顶点数量
                    vertex_count = cmds.polyEvaluate(transform, vertex=True)
                    total_vertices += vertex_count
                    model_names.append(transform)
                except:
                    # 忽略无法计算的模型
                    pass
            elif cmds.objectType(geo_shape) == 'nurbsCurve':
                shape_names.append(transform)
                total_cv_points += len(cmds.ls("{}.cv[*]".format(geo_shape), flatten=True))

            elif cmds.objectType(geo_shape) == 'nurbsSurface':
                shape_names.append(transform)
                total_cv_points += len(cmds.ls("{}.cv[*][*]".format(geo_shape), flatten=True))

            else:
                others_names.append(transform)

    return "total_skinClusters: {}, total_models: {}, total_vertices: {}, total_shapes: {}, total_cv_points: {}, model_names: {}, shape_names: {}, other_names: {}".format(len(skin_clusters), len(model_names), total_vertices, len(shape_names), total_cv_points, model_names, shape_names, others_names)

def get_wraped_meshes_vertex_info():
    # 获取所有 skinCluster 节点
    skin_clusters = cmds.ls(type='wrap') or []
    processed = set()  # 用于去重
    total_vertices = 0
    model_names = []
    shape_names = []

    for sc in skin_clusters:
        # 获取该 skinCluster 影响的几何体（形状节点）
        geometries = cmds.deformer(sc, query=True, geometry=True) or []
        for geo_shape in geometries:
            # 获取几何体的变换节点（模型名称）
            transform = cmds.listRelatives(geo_shape, parent=True)
            transform = transform[0]
            # 去重
            if transform in processed:
                continue
            processed.add(transform)

            # 检查是否为多边形
            if cmds.objectType(geo_shape) == 'mesh':
                try:
                    # 获取顶点数量
                    vertex_count = cmds.polyEvaluate(transform, vertex=True)
                    total_vertices += vertex_count
                    model_names.append(transform)
                except:
                    # 忽略无法计算的模型
                    pass
            else:
                shape_names.append(transform)

    return "total_wraps: {}, total_models: {}, total_shapes: {}, total_vertices: {}, model_names: {}, shape_names: {}".format(len(skin_clusters), len(model_names), len(shape_names), total_vertices, model_names, shape_names)

def get_lcPoseDeformer_meshes_vertex_info():
    # 获取所有 skinCluster 节点
    skin_clusters = cmds.ls(type='lcPoseDeformer') or []
    processed = set()  # 用于去重
    total_vertices = 0
    model_names = []
    shape_names = []
    others_names = []
    total_cv_points = 0

    for sc in skin_clusters:
        # 获取该 skinCluster 影响的几何体（形状节点）
        geometries = cmds.deformer(sc, query=True, geometry=True) or []
        for geo_shape in geometries:
            # 获取几何体的变换节点（模型名称）
            transform = cmds.listRelatives(geo_shape, parent=True)
            transform = transform[0]
            # 去重
            if transform in processed:
                continue
            processed.add(transform)

            # 检查是否为多边形
            if cmds.objectType(geo_shape) == 'mesh':
                try:
                    # 获取顶点数量
                    vertex_count = cmds.polyEvaluate(transform, vertex=True)
                    total_vertices += vertex_count
                    model_names.append(transform)
                except:
                    # 忽略无法计算的模型
                    pass

            elif cmds.objectType(geo_shape) == 'nurbsCurve':
                shape_names.append(transform)
                total_cv_points += len(cmds.ls("{}.cv[*]".format(geo_shape), flatten=True))

            elif cmds.objectType(geo_shape) == 'nurbsSurface':
                shape_names.append(transform)
                total_cv_points += len(cmds.ls("{}.cv[*][*]".format(geo_shape), flatten=True))


            else:
                others_names.append(transform)

    return "total_lcPoseDeformers: {}, total_models: {}, total_vertices: {}, total_shapes: {}, total_cv_points: {}, model_names: {}, shape_names: {}, other_names: {}".format(len(skin_clusters), len(model_names), total_vertices, len(shape_names), total_cv_points, model_names, shape_names, others_names)

def get_blendShape_meshes_vertex_info():
    # 获取所有 skinCluster 节点
    skin_clusters = cmds.ls(type='blendShape') or []
    processed = set()  # 用于去重
    total_vertices = 0
    model_names = []
    shape_names = []

    for sc in skin_clusters:
        # 获取该 skinCluster 影响的几何体（形状节点）
        geometries = cmds.deformer(sc, query=True, geometry=True) or []
        for geo_shape in geometries:
            # 获取几何体的变换节点（模型名称）
            transform = cmds.listRelatives(geo_shape, parent=True)
            transform = transform[0]
            # 去重
            if transform in processed:
                continue
            processed.add(transform)

            # 检查是否为多边形
            if cmds.objectType(geo_shape) == 'mesh':
                try:
                    # 获取顶点数量
                    vertex_count = cmds.polyEvaluate(transform, vertex=True)
                    total_vertices += vertex_count
                    model_names.append(transform)
                except:
                    # 忽略无法计算的模型
                    pass
            else:
                shape_names.append(transform)

    return "total_blendShapes: {}, total_models: {}, total_shapes: {}, total_vertices: {}, model_names: {}, shape_names: {}".format(len(skin_clusters), len(model_names), len(shape_names), total_vertices, model_names, shape_names)

def get_lattice_meshes_vertex_info():
    # 获取所有 skinCluster 节点
    skin_clusters = cmds.ls(type='ffd') or []
    processed = set()  # 用于去重
    total_vertices = 0
    model_names = []
    shape_names = []

    for sc in skin_clusters:
        # 获取该 skinCluster 影响的几何体（形状节点）
        geometries = cmds.deformer(sc, query=True, geometry=True) or []
        for geo_shape in geometries:
            # 获取几何体的变换节点（模型名称）
            transform = cmds.listRelatives(geo_shape, parent=True)
            transform = transform[0]
            # 去重
            if transform in processed:
                continue
            processed.add(transform)

            # 检查是否为多边形
            if cmds.objectType(geo_shape) == 'mesh':
                try:
                    # 获取顶点数量
                    vertex_count = cmds.polyEvaluate(transform, vertex=True)
                    total_vertices += vertex_count
                    model_names.append(transform)
                except:
                    # 忽略无法计算的模型
                    pass
            else:
                shape_names.append(transform)

    return "total_lattices: {}, total_models: {}, total_shapes: {}, total_vertices: {}, model_names: {}, shape_names: {}".format(len(skin_clusters), len(model_names), len(shape_names), total_vertices, model_names, shape_names)

def count_constraint_nodes():
    # 定义所有已知的约束节点类型
    constraint_types = [
        'pointConstraint',  # 点约束
        'orientConstraint',  # 方向约束
        'parentConstraint',  # 父子约束
        'scaleConstraint',  # 缩放约束
        'aimConstraint',  # 目标约束
        'poleVectorConstraint',  # 极向量约束
        'normalConstraint',  # 法线约束
        'tangentConstraint',  # 切线约束
        'geometryConstraint',  # 几何体约束
        'surfaceConstraint'  # 曲面约束
    ]

    all_constraints = []
    for c_type in constraint_types:
        # 查找当前类型的所有约束节点
        nodes = cmds.ls(type=c_type)
        all_constraints.extend(nodes)

    return len(all_constraints)

def is_world_visibility_always_off(obj):
    segments = cmds.ls(obj, long=True)[0].split('|')[1:]
    transforms = ['|'.join(segments[:i]) for i in xrange(1, 1 + len(segments))]
    for x in transforms:
        if not cmds.listConnections("{}.visibility".format(x), s=True, d=False) and not cmds.getAttr("{}.visibility".format(x)):
            return True
    return False

# 吴真提供控制器过滤
def get_enum_field(plug):
    result = []
    cursor = -1
    for name_value in cmds.addAttr(plug, q=True, enumName=True).split(':'):
        # if there is a custom value, we use that value
        if '=' in name_value:
            name, value = name_value.rsplit('=', 1)
        else:
            # if there is no custom value, we use the previous value + 1
            name, value = name_value, cursor + 1
        result.append((name, int(value)))
        # update cursor
        cursor = int(value)
    return result
def list_channel_box(obj):
    _attributes = (cmds.listAttr(obj, k=True) or []) + (cmds.listAttr(obj, cb=True) or [])
    attributes = []
    for attr in _attributes:
        plug = '{}.{}'.format(obj, attr)
        if cmds.getAttr(plug, lock=True):
            continue
        attr_type = cmds.getAttr(plug, type=True)
        if attr_type in {'string', 'double3'}:
            continue
        if attr_type == 'enum' and attr != 'rotateOrder' and len(get_enum_field(plug)) == 1:
            continue
        attributes.append(attr)
    return attributes
def is_channel_box_locked(ctrl):
    for x in list_channel_box(ctrl):
        if not cmds.getAttr("{}.{}".format(ctrl, x), lock=True) and x != "visibility":
            return False
    return True
def get_shapes():
    return cmds.ls(cmds.ls(type='mesh', ni=True), v=True) + cmds.ls(cmds.ls(type='nurbsSurface', ni=True), v=True)
def get_controllers():
    controllers = cmds.ls("*_ctrl")
    if controllers:
        controllers = [ctrl for ctrl in controllers if any(cmds.nodeType(x) == 'nurbsCurve' for x in cmds.listRelatives(ctrl, shapes=True) or [])]
        controllers = [ctrl for ctrl in controllers if not is_channel_box_locked(ctrl)]
        controllers = [ctrl for ctrl in controllers if not is_world_visibility_always_off(ctrl)]
        return controllers


class FacialMeshExporter(object):
    def __init__(self):
        self.doc = None
        self.path_map = {}  # 用于存储已经创建过的 XML 元素，避免重复创建父级

    def get_replaced_names(self, transform_nodes):
        """2. 替换 'facial_' 前缀并返回新名称列表"""
        new_names = []
        for node in transform_nodes:
            original_name = node.nodeName()
            new_name = original_name[7:] if original_name.startswith('facial_') else original_name
            if pm.objExists(new_name):
                new_names.append(new_name)
        if pm.objExists('facial_head_geo'):
            new_names.append('facial_head_geo')
        return new_names

    def get_mesh_transforms(self, root_group='facial_model_grp'):
        """1. 获取指定组下所有 mesh 的 transform 节点"""
        if not pm.objExists(root_group):
            pm.warning(u"未找到节点: %s" % root_group)
            return []

        # 获取组下所有的 mesh 类型节点
        meshes = pm.listRelatives(root_group, ad=True, type='mesh')
        # 获取 transform 节点并去重
        transforms = list(set([m.getTransform() for m in meshes]))
        new_names = self.get_replaced_names(transforms)
        return new_names

    def get_mesh_data(self, node_name):
        """获取 Mesh 的拓扑和统计信息"""
        node = pm.PyNode(node_name)
        shapes = node.getShapes()
        valid_meshes = [s for s in shapes if isinstance(s, pm.nt.Mesh) and not s.isIntermediate()]

        if not valid_meshes:
            return None

        mesh_node = valid_meshes[0]
        face_count = pm.polyEvaluate(mesh_node, face=True)
        vertex_count = pm.polyEvaluate(mesh_node, vertex=True)

        # 计算 Topology MD5
        topology_hash = ""
        position_hash = ""
        position_sum = 0.0
        vertex_indices_str = ""

        # 计算空网格的回退哈希
        if face_count == 0:
            topology_hash = hashlib.md5(' '.encode('utf-8')).hexdigest()
            position_hash = hashlib.md5(' '.encode('utf-8')).hexdigest()
        else:
            sl = om.MSelectionList()
            sl.add(mesh_node.fullPath())
            mesh_dag = sl.getDagPath(0)
            mesh_mfn = om.MFnMesh(mesh_dag)

            # --- 原始功能：Topology MD5 ---
            v = mesh_mfn.getVertices()
            v_str = "[%s] [%s]" % (', '.join(map(str, v[0])), ', '.join(map(str, v[1])))
            topology_hash = hashlib.md5(v_str.encode('utf-8')).hexdigest()

            # --- 功能 2：所有模型的哈希数值及顶点数值叠加 ---
            # 获取基于对象空间的顶点坐标
            points = mesh_mfn.getPoints(om.MSpace.kObject)
            pos_list = []

            for pt in points:
                # 保留4位小数，避免浮点精度误差导致哈希雪崩效应
                pos_list.append("{:.4f},{:.4f},{:.4f}".format(pt.x, pt.y, pt.z))
                # 将 xyz 坐标值叠加，用作数值特征
                position_sum += (pt.x + pt.y + pt.z)

            # 组合所有的顶点坐标并生成哈希，作为模型形状的校验值
            pos_str_full = "|".join(pos_list)
            position_hash = hashlib.md5(pos_str_full.encode('utf-8')).hexdigest()

        data = {
            'vertex': str(vertex_count),
            'edge': str(pm.polyEvaluate(mesh_node, edge=True)),
            'face': str(face_count),
            'topology': topology_hash,
            'position_hash': position_hash,
            'position_sum': "{:.4f}".format(position_sum)
        }

        return data

    def run(self, export_path=None):

        # 1. 获取需要处理的 transform 节点 (PyNode 列表)
        root_group = 'facial_model_grp'
        if not pm.objExists(root_group):
            return "Root group not found"

        origin_nodes = self.get_mesh_transforms('facial_model_grp')
        #print('=' * 100)
        #print(origin_nodes)
        origin_nodes.sort(key=lambda x: (cmds.listRelatives(x, shapes=True, fullPath=True) or [x])[0])  # 按路径排序，确保父节点先处理

        if not origin_nodes:
            return "No nodes found"

        # 2. 初始化 XML
        self.doc = Document()
        root_xml = self.doc.createElement('root')
        self.doc.appendChild(root_xml)

        # 初始化路径映射，根节点对应的 XML 元素是 root_xml
        self.path_map = {pm.PyNode(root_group).fullPath(): root_xml}

        #print(origin_nodes)
        # 3. 核心：非递归构建层级
        for node in origin_nodes:
            # 1. Get the shape path. Handle cases where no shape exists to avoid errors.
            shapes = cmds.listRelatives(node, shapes=True, fullPath=True)
            if not shapes:
                continue

            full_path = shapes[0]
            #print(full_path)

            # 拆分路径，例如 ['facial_model_grp', 'sub_grp', 'head_mesh']
            parts = full_path.split('|')[1:]

            current_parent_xml = root_xml
            current_partial_path = ""

            for i, part in enumerate(parts):
                current_partial_path += "|" + part

                if current_partial_path in self.path_map:
                    current_parent_xml = self.path_map[current_partial_path]
                    continue

                is_last_part = (i == len(parts) - 1)

                if is_last_part:
                    data = self.get_mesh_data(node)
                    new_elem = self.doc.createElement('mesh')

                    # FIX: In cmds, 'node' is already a string.
                    # To get just the short name (like nodeName), we split by '|'
                    short_name = node.split('|')[-1]

                    new_elem.setAttribute('name', short_name)
                    new_elem.setAttribute('fullPath', full_path)

                    if data:
                        for key, val in data.items():
                            new_elem.setAttribute(key, str(val))  # Ensure value is a string for XML
                else:
                    new_elem = self.doc.createElement('transform')
                    new_elem.setAttribute('name', part)

                current_parent_xml.appendChild(new_elem)
                self.path_map[current_partial_path] = new_elem
                current_parent_xml = new_elem

        # 4. 保存文件
        if export_path:
            dir_name = os.path.dirname(export_path)
            if dir_name and not os.path.exists(dir_name):
                os.makedirs(dir_name)
            with open(export_path, 'w') as f:
                f.write(self.doc.toprettyxml(indent='    '))
            #print(u"Successfully exported to: %s" % export_path)
        else:
            pass
            #print(self.doc.toprettyxml(indent='    '))

        return "Success"

if __name__ == '__main__':
    main = StdProcess()
    main.write_asset_data()
