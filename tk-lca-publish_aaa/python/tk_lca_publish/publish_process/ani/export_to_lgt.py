#! -*- coding:utf-8 -*-
import os
import shutil
import traceback
# import pymel.core as pm
import maya.cmds as cmds


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"导出TO_LGT组下的的灯光示意等"
        self.description = u"如果TO_LGT组下存在示意, 则会导出一个abc预备给下游LGT使用"
        return

    def proceed(self):
        try:
            start_frame = cmds.playbackOptions(q=True, minTime=True)
            end_frame = cmds.playbackOptions(q=True, maxTime=True)
            abc_name = "{}.ani.lgt_mesh.abc".format(self.dialog.entity['name'])
            abc_dir = os.path.join(self.dialog.version_dir, "ani_lgt")

            to_lgt_grp = '|assets|lay|TO_LGT'
            if cmds.objExists(to_lgt_grp):
                # for sg in pm.ls(type=pm.nt.ShadingEngine):
                #     shapes = [i for i in sg.members()
                #               if isinstance(i, pm.nt.Mesh)
                #               and 'TO_LGT' in i.fullPath()
                #               and i.name() not in {'shaderBallGeomShape1'}]
                #     for shape in shapes:
                #         pm.sets(sg, remove=shape)
                #         pm.sets(sg, forceElement=shape.faces)
                if cmds.listRelatives(to_lgt_grp, children=True):
                    if os.path.isdir(abc_dir):
                        shutil.rmtree(abc_dir)
                    os.makedirs(abc_dir)
                    os.system("chmod 777 -R * %s" % self.dialog.version_dir)

                    cmds.select(to_lgt_grp)
                    cmds.AbcExport(
                        j="-frameRange {start} {end} -worldSpace -writeVisibility -writeFaceSets -eulerFilter -dataFormat ogawa -root {grp_path} -file {output}".format(
                            start=start_frame, end=end_frame, grp_path=to_lgt_grp,
                            output=os.path.join(abc_dir, abc_name)))
                    os.system("chmod 777 -R * %s" % self.dialog.version_dir)
                    print '[export_lgt_preview]: Export LGT Preview ABC Success:\n{}'.format(
                        os.path.join(abc_dir, abc_name))
            else:
                print '=' * 100
                print '[export_lgt_preview]: Nothing found in "TO_LGT", skip export lgt preview!'
                print '=' * 100

            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
