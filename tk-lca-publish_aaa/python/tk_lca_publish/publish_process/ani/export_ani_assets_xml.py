import os
import sys
import sgtk
import datetime
# import shotgun_connection
import maya.standalone

maya.standalone.initialize(name='python')
import maya.cmds as cmds
import pymel.core as pm
import production.shotgun_connection as shotgun_connection

reload(shotgun_connection)
from production.tankutils import engine_from_path
import lay.lca_updatePreviewXml.utility as utility

import ani.lca_cycle_info_tool.cycle_replace_ani_asset as alc

reload(alc)


class FakeDialog(object):
    def __init__(self):
        super(FakeDialog, self).__init__()
        scene_file = pm.sceneName()
        engine_from_path(scene_file)
        sg_engine = sgtk.platform.current_engine()
        self.tk = sg_engine.tank
        self.ctx = sg_engine.context
        # self.sg = shotgun_connection.Connection('get_project_info').get_sg()
        self.entity = self.ctx.entity
        self.project = self.ctx.project

        self.sg = shotgun_connection.Connection('get_project_info').get_sg()
        # e.g. version_dir = /mnt/proj/projects/tst/shot/d10/d10010/flo/publish/d10010.flo.final_layout.v001
        base_dir = os.path.dirname(scene_file).replace('\\', '/').rsplit('/', 3)[0]
        cam_dir = os.path.join(base_dir, 'cam', 'publish')
        cam_vers = [cam_file for cam_file in os.listdir(cam_dir) if '.camera.' in cam_file]
        cam_vers.sort()
        self.cam_ver_dir = utility.osPathConvert(cam_vers[-1])
        self.version_dir = utility.osPathConvert(os.path.dirname(scene_file))


def printAndLog(info, printing=True, log=True):
    '''
    '''
    str_time = datetime.datetime.today().strftime('%Y%m%d%H%M%S')
    date_today = datetime.datetime.today().strftime('%Y%m%d')
    user_script_dir = os.path.join(pm.internalVar(userScriptDir=True), 'updatePreviewXml_log', date_today)
    if not os.path.exists(user_script_dir):
        os.makedirs(user_script_dir)
        try:
            os.chmod(user_script_dir, 0777)
        except:
            pass
    error_file = open(user_script_dir + '/updatePreviewXml_log_%s.txt' % str_time, 'w')
    if printing:
        print info
    try:
        if log:
            error_file.write(info)
            error_file.write('\n')
    except:
        pass


def main(maya_file, project_name):
    cmds.file(maya_file, open=True, force=True)
    untouched = []
    alc.main()

    path_a = utility.osPathConvert('U:/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish')

    path = utility.osPathConvert('U:/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/publish_process/ani')
    if path not in sys.path:
        sys.path.append(path_a)

    if path not in sys.path:
        sys.path.append(path)
    import list_ani_assets as laa
    reload(laa)

    # ani_assets_xml = self.osPathConvert( os.path.dirname(pm.sceneName()) ) + '/ani_assets.xml'
    # stdProcess = laa.StdProcess(dialog = FakeDialog(utility.osPathConvert( os.path.dirname(pm.sceneName()) )))
    stdProcess = laa.StdProcess(dialog=FakeDialog())
    try:
        err = stdProcess.proceed()
        print dir(stdProcess.dialog)
        if err:
            success = False
            msg = os.path.basename(pm.sceneName()) + ', failed to write ani_asset.xml data.\nError:\n{}'.format(
                err)
            untouched.append(msg)
            printAndLog(err, printing=False)
            printAndLog(msg)
        else:
            print 'Write the ani_assets.xml successfully!'
    except:
        pass

    import production.shotgun_connection as shotgun_connection
    reload(shotgun_connection)

    sg = shotgun_connection.Connection('get_project_info').get_sg()
    print(project_name)
    file_name = os.path.basename(maya_file)
    print(file_name)
    version_entity = sg.find_one('Version',
                                 [['project', 'name_is', project_name],
                                  ['code', 'is', file_name[:-3]]],
                                 ['tag_list', 'id', 'code'])
    if 'ani_assets_xml_submitted' in version_entity['tag_list']:
        version_entity['tag_list'].remove('ani_assets_xml_submitted')

    version_entity['tag_list'].append('ani_assets_xml_completed')
    sg.update("Version", version_entity["id"], {"tag_list": version_entity['tag_list']})
    file_publish = os.path.dirname(maya_file) + '/ani_assets.xml'
    print(file_publish)
    os.chmod(file_publish, 0777)


if __name__ == '__main__':
    if len(sys.argv) < 1:
        print('Usage: mayapy export_efx_preview_script.py <maya_file> <start_frame> <end_frame> <abc_dir> <abc_name>')
        sys.exit(1)
    maya_file = sys.argv[1]
    project = sys.argv[2]
    main(maya_file, project)
