#! -*- coding:utf-8 -*-
import os
# import shutil
import sys
import traceback
# import pymel.core as pm
import pymel.core as pm
import maya.cmds as cmds


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"导出TO_EFX组下的特效示意"
        self.description = u"如果TO_EFX组下存在特效示意,则会导出一个abc预备给下游EFX使用"
        return

    def proceed(self):
        try:
            start_frame = cmds.playbackOptions(q=True, minTime=True)
            end_frame = cmds.playbackOptions(q=True, maxTime=True)
            abc_name = "{}.ani.efx_preview.abc".format(self.dialog.entity['name'])
            abc_dir = os.path.join(self.dialog.version_dir, "ani_efx")

            # to_efx_grp = '|assets|lay|TO_EFX'
            # if cmds.objExists(to_efx_grp):
            #     for sg in pm.ls(type=pm.nt.ShadingEngine):
            #         shapes = [i for i in sg.members()
            #                   if isinstance(i, pm.nt.Mesh)
            #                   and 'TO_EFX' in i.fullPath()
            #                   and i.name() not in {'shaderBallGeomShape1'}]
            #         for shape in shapes:
            #             pm.sets(sg, remove=shape)
            #             pm.sets(sg, forceElement=shape.faces)
            #     if cmds.listRelatives(to_efx_grp, children=True):
            #         if os.path.isdir(abc_dir):
            #             shutil.rmtree(abc_dir)
            #         os.makedirs(abc_dir)
            #         os.system("chmod 777 -R script_file* %s" % self.dialog.version_dir)
            #
            #         cmds.select(to_efx_grp)
            #         cmds.AbcExport(
            #             j="-frameRange {start} {end} -worldSpace -writeVisibility -writeFaceSets -eulerFilter -dataFormat ogawa -root {grp_path} -file {output}".format(
            #                 start=start_frame, end=end_frame, grp_path=to_efx_grp,
            #                 output=os.path.join(abc_dir, abc_name)))
            #         os.system("chmod 777 -R * %s" % self.dialog.version_dir)
            #         print '[export_efx_preview]: Export EFX Preview ABC Success:\n{}'.format(
            #             os.path.join(abc_dir, abc_name))
            # else:
            #     print '=' * 100
            #     print '[export_efx_preview]: Nothing found in "TO_EFX", skip export efx preview!'
            #     print '=' * 100
            import production.python_job as python_job
            abc_dir = abc_dir.replace('\\', '/')
            abc_dir = abc_dir.replace('Z:/', '/mnt/proj/')
            ma_file = str(pm.saveFile())

            script_file = '/mnt/utility/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/publish_process/flo/export_efx_preview_script.py'
            proj = self.dialog.project['name']
            python_exe = '{}/linked_tools/lca_rez/launchers/{}/linux/mayapy'.format('/mnt/utility',
                                                                                    proj.lower())
            from production.farm_ip import LcaFarmIPManage
            job_name_prefix = '[EFX PREVIEW {0} BY {1} {2}]'.format(self.dialog.entity['name'], os.getenv('USER', 'unKnown'),
                                                                   self.dialog.version_dir.split('/')[-1])
            args = '"{}" {} {} "{}" "{}"'.format(ma_file, start_frame, end_frame, abc_dir, abc_name)
            python_job.send_job(script_file, proj=proj, priority=2000, step='ANI', python_exe=python_exe,
                                job_name_prefix=job_name_prefix, url=LcaFarmIPManage().MASTERCACHE, args=args, msg=None)

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
