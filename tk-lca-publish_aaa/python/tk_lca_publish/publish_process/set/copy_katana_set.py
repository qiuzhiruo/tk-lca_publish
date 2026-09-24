__author__ = 'yingjie'

import shutil
import os
import getpass

import sgtk
from sgtk.platform.qt import QtCore, QtGui


def get_lgt_shot_maker_node():
    import NodegraphAPI as ngapi

    all_grp_nodes = ngapi.GetAllNodesByType('Group')
    for gn in all_grp_nodes:
        if gn.getName() == 'LgtShotMaker_Lc':
            return gn

def copy_katana_set(dialog,extra_data=None):
    from Katana import KatanaFile
    from Katana import FarmAPI

    out_path = dialog.version_dir

    if not os.path.isdir(out_path):
        dialog.print_log('Invalid out path '+out_path+'\n', txt_color=QtGui.QColor(255, 50, 50))
        raise Exception('Invalid out path '+out_path)

    st_node = get_lgt_shot_maker_node()
    if not st_node:
        dialog.print_log('Cannot find  LgtShotMaker_Lc node.\n', txt_color=QtGui.QColor(255, 50, 50))
        raise Exception('Cannot find  LgtShotMaker_Lc node.')

    ani_xml = st_node.getParameter('user.aniXml').getValue(0)
    dir,file=os.path.split(ani_xml)
    file = file.split('.')[0]+'.xml'
    new_ani_xml = os.path.join(out_path,file)

    srf_xml = st_node.getParameter('user.srfXml').getValue(0)
    dir,file = os.path.split(srf_xml)
    file = file.split('.')[0]+'.xml'
    new_srf_xml = os.path.join(out_path,file)

    shutil.copy(ani_xml,new_ani_xml)
    shutil.copy(srf_xml,new_srf_xml)


    st_node.getParameter('user.aniXml').setValue(new_ani_xml,0)
    st_node.getParameter('user.srfXml').setValue(new_srf_xml,0)

    k_file = dialog.entity['name']+'.katana'
    out_file = os.path.join(out_path,k_file)

    st_node.getParameter('user.katanaFile').setValue(out_file,0)

    if st_node.getParameter('user.verbose.fromSetUser'):
        st_node.getParameter('user.verbose.fromSetUser').setValue(getpass.getuser(),0)

    if extra_data and extra_data.has_key('status') and st_node.getParameter('user.setStatus'):
        st_node.getParameter('user.setStatus').setValue(extra_data['status'],0)

    KatanaFile.Export(out_file,[st_node])