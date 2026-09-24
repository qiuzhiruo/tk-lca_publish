#! -*- coding:utf-8 -*-
import os
import traceback
import maya.cmds as cmds
import sceneGraphXML.scenegraphXML as sgxml
reload(sgxml)

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"检测及导出群集点云存在"
        self.description = u"检查镜头里是否有使用群集工具创建的点云,有的话导出点云abc"
        return

    def export_crd_xml(self, xml_path):
        def __create_grp(_node):
            _grp = sgxml.Group(_node.split('|')[-1])
            _grp.setXform(cmds.xform(_node, q=True, m=True, os=True))
            _grp.addArbitraryAttribute('fullpath', 'string', cmds.ls(_node, l=True)[0])
            return _grp

        def __is_hide(_node):
            _geo = cmds.listConnections('{}.t'.format(_node), s=False, d=True)
            return cmds.getAttr('{}.visibility'.format(_geo[0]))

        crd_loc_grp = '|assets|lay|CRD_GRP|LOCS'
        if cmds.objExists(crd_loc_grp):
            root = sgxml.ScenegraphRoot()
            asset_grp = __create_grp('|assets')
            lay_grp = __create_grp('|assets|lay')
            crd_grp = __create_grp('|assets|lay|CRD_GRP')
            loc_grp = __create_grp('|assets|lay|CRD_GRP|LOCS')
            root.addInstance(asset_grp)
            asset_grp.addInstance(lay_grp)
            lay_grp.addInstance(crd_grp)
            crd_grp.addInstance(loc_grp)

            for i in cmds.listRelatives(crd_loc_grp, type='transform'):
                if not __is_hide(i):
                    continue
                name = cmds.getAttr('{}.LcaAssetName'.format(i))
                is_rra = 'True' if cmds.objExists('{}.RraRigAsset'.format(i)) else 'False'
                gpu_cache = cmds.listConnections(i, s=False, d=True, type='transform')[0]
                abc_file = cmds.getAttr('{}.cacheFileName'.format(gpu_cache))
                if abc_file.lower().startswith('z:'):
                    abc_file = abc_file.replace('z:', '/mnt/proj')
                    abc_file = abc_file.replace('Z:', '/mnt/proj')
                tokens = abc_file.split('/')
                xml_file = '/'.join(tokens[:-2] + ['crd_dynamic', '{}.xml'.format(name)])
                cur_ref = sgxml.Reference(i.replace('|', '.'), xml_file, rra_mesh=is_rra)
                bb = cmds.xform(gpu_cache, q=True, bb=True)
                obj_m = cmds.xform(i, q=True, m=True, os=True)
                # wor_m = cmds.xform(i, q=True, m=True, ws=True)
                cur_ref.setBounds(bb[0], bb[3], bb[1], bb[4], bb[2], bb[5])
                cur_ref.setXform(obj_m)
                loc_grp.addInstance(cur_ref)
            root.writeXMLFile(xml_path)

    def proceed(self):
        try:
            crd_loc_grp = '|assets|lay|CRD_GRP|LOCS'
            if cmds.objExists(crd_loc_grp) and cmds.listRelatives(crd_loc_grp, ad=True):
                start_frame = cmds.playbackOptions(q=True, minTime=True)
                end_frame = cmds.playbackOptions(q=True, maxTime=True)
                abc_name = "{}.ani.crowd_loc.abc".format(self.dialog.entity['name'])
                abc_dir = os.path.join(self.dialog.version_dir, "ani_crd")
                if not os.path.isdir(abc_dir):
                    os.mkdir(abc_dir)
                cmds.select(cmds.listRelatives(crd_loc_grp, ad=True, type='transform', f=True))
                cmds.AbcExport(j="-frameRange {start} {end} -attr LcaAssetName -stripNamespaces -worldSpace -eulerFilter -dataFormat ogawa -selection -file {output}".format(
                    start=start_frame, end=end_frame, output=os.path.join(abc_dir, abc_name)))

                xml_file = os.path.join(self.dialog.version_dir, 'scene_graph_xml', '{}.crd.xml'.format(self.dialog.entity['name']))
                self.export_crd_xml(xml_file)
            else:
                print '=' * 30
                print '[Publish Info]: Not Found Crd Things, Skip!'
                print '=' * 30

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description

