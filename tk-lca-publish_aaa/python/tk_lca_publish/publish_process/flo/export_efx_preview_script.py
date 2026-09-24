#! -*- coding:utf-8 -*-
import os
import sys
import json
import shutil
import traceback
import pymel.core as pm
import maya.standalone
import maya.cmds as cmds
import maya.mel
import lay.utilities.maya_common_ops as mco

reload(mco)


def mash_bake_instancer(to_efx_grp):
    mash_list = cmds.ls(type='MASH_Waiter')
    if mash_list:
        import MASHbakeInstancer
        for x in mash_list:
            if cmds.referenceQuery(x, isNodeReferenced=True):
                ns = x.split(':', 1)[0]
                mash_n = x.split(':', 1)[1]
                # mash_in = '%s_Instancer' % mash_n
                prp_v = '%s:visibility_ctrl' % ns
                # set pcube
                cmds.setAttr('%s.pCube_switch' % prp_v, 0)
                # import prp remove ns
                file_path = cmds.referenceQuery(x, filename=True)
                cmds.file(file_path, importReference=True)
                cmds.namespace(removeNamespace=":%s" % ns, mergeNamespaceWithRoot=True)
                # bake instancer
                mash_ins = cmds.listConnections(mash_n, s=0, d=1, t='instancer')
                if mash_ins:
                    mash_ins = set(mash_ins)
                    for mash_in in mash_ins:
                        cmds.select(mash_in, r=1)
                        maya.mel.eval("MASHBakeGUI;")
                        MASHbakeInstancer.MASHbakeInstancer(True)
                        ins_obj_n = '%s_objects' % mash_in
                        cmds.parent(ins_obj_n, to_efx_grp)
                        cmds.delete(mash_in)
                # unlock matser
                cmds.select('|assets|prp|master', r=1)
                mco.set_nodes_lock_status(lock_it=False)
                cmds.delete('|assets|prp|master')


def main(maya_file, start_frame, end_frame, abc_dir, abc_name):
    try:
        maya.standalone.initialize(name='python')
        cmds.file(maya_file, open=True, force=True)
        to_efx_grp = '|assets|lay|TO_EFX'
        if cmds.objExists(to_efx_grp):

            # mash bake instancer
            mash_bake_instancer(to_efx_grp)

            for sg in pm.ls(type=pm.nt.ShadingEngine):
                shapes = [i for i in sg.members()
                          if isinstance(i, pm.nt.Mesh)
                          and 'TO_EFX' in i.fullPath()
                          and i.name() not in {'shaderBallGeomShape1'}]
                for shape in shapes:
                    # 当 shape 节点面数 不为 0,才会执行下面操作,否则会报错(是因为试图内看不到)
                    if pm.polyEvaluate(shape, face=True)!=0:
                        pm.sets(sg, remove=shape)
                        pm.sets(sg, forceElement=shape.faces)
            if cmds.listRelatives(to_efx_grp, children=True):
                if os.path.isdir(abc_dir):
                    shutil.rmtree(abc_dir)
                os.makedirs(abc_dir)
                cmds.select(to_efx_grp)
                cmds.AbcExport(
                    j="-frameRange {start} {end} -worldSpace -writeVisibility -writeFaceSets -eulerFilter -dataFormat ogawa -root {grp_path} -file {output}".format(
                        start=start_frame, end=end_frame, grp_path=to_efx_grp,
                        output=os.path.join(abc_dir, abc_name)))
                json_data = '[export_efx_preview_script]: Export EFX Preview ABC Success:\n{}'.format(
                    os.path.join(abc_dir, abc_name))
                print('[export_efx_preview_script]: Export EFX Preview ABC Success:\n{}'.format(
                    os.path.join(abc_dir, abc_name)))
            else:
                print('=' * 100)
                json_data = '[export_efx_preview_script]: Nothing found in "TO_EFX", skip export efx preview!'
                print('[export_efx_preview_script]: Nothing found in "TO_EFX", skip export efx preview!')
                print('=' * 100)
        else:
            print('=' * 100)
            json_data = '[export_efx_preview_script]: Nothing found in "TO_EFX", skip export efx preview!'
            print('[export_efx_preview_script]: Nothing found in "TO_EFX", skip export efx preview!')
            print('=' * 100)
    except Exception as e:
        print(traceback.format_exc())
        json_data = traceback.format_exc()

    json_file_path = abc_dir.replace('/ani_efx', '/extra_data')
    if not os.path.isdir(json_file_path):
        os.makedirs(json_file_path)
    try:
        #[NOTE]:publish经常有无权限的错误，这里给jsonpath 解锁
        os.system("chmod 777 -R %s" % json_file_path)
        os.chmod(json_file_path, 0777)
    except Exception as e:
        print(e)
    if os.path.exists(os.path.join(json_file_path, 'Efx_preview_deadline_job.json')):
        with open(os.path.join(json_file_path, 'Efx_preview_deadline_job.json'), 'r') as fr:
            frdata = json.load(fr)

        frdata['json_data'] = json_data

        with open(os.path.join(json_file_path, 'Efx_preview_deadline_job.json'), 'w') as fw:
            json.dump(frdata, fw, ensure_ascii=False, indent=4)

    else:
        fw_data = {'json_data': json_data}
        with open(os.path.join(json_file_path, 'Efx_preview_deadline_job.json'), 'w') as ffw:
            json.dump(fw_data, ffw, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    if len(sys.argv) < 6:
        print('Usage: mayapy export_efx_preview_script.py <maya_file> <start_frame> <end_frame> <abc_dir> <abc_name>')
        sys.exit(1)
    maya_file = sys.argv[1]
    start_frame = float(sys.argv[2])
    end_frame = float(sys.argv[3])
    abc_dir = sys.argv[4]
    abc_name = sys.argv[5]
    main(maya_file, start_frame, end_frame, abc_dir, abc_name)