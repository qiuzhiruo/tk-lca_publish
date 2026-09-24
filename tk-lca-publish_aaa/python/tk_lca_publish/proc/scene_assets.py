# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2018 Light Chaser Animation
#
# Author: LCA TDs
#
# Date: 2018.03
#
# Description:
#
############################################

import pymel.core as pm

def check_asset_visible(self, asset):
    if asset.nodeType() == 'assemblyReference':
        return self.check_AR_visible(asset)
    else:
        return self.check_ref_visible(asset)


def getReferenceAssets(topNode):
    master = []
    tmp = [t for t in pm.ls('*:master', r=True, rn=True, long=True) if t.isChildOf(topNode)]
    for m in tmp:
        # begin: skip unused rra for lrs rra - tmp solution
        import maya.cmds as cmds
        m_long = cmds.ls(str(m), long=True)[0]
        if '|assets|rra|' in m_long and ':rra|' not in m_long:
            continue
        # end!

        if [p for p in m.getChildren() if ':poly' in str(p)]:
            master.append(m)

    return filter(None, set(master))


def getAssemblyReferenceAssets(topNode):
    l_ar = pm.listRelatives(topNode, ad=True, type='assemblyReference')
    l_asb_ar_name = []
    l_asset_ar = []
    l_asb_ar = []
    l_unload_ar = []

    if l_ar:
        # Get ASB assets name by ns
        for ar in l_ar:
            ar_name = ar.name()
            if ':' in ar_name:
                ar_ns = ':'.join(ar_name.split(':')[:-1])
                l_asb_ar_name.append(ar_ns + '_AR')

        l_asb_ar_name = list(set(l_asb_ar_name))

        for ar in l_ar:
            if ar.name() in l_asb_ar_name:
                l_asb_ar.append(ar)
            else:
                if len(pm.listRelatives(ar, c=True)) == 0:
                    l_unload_ar.append(ar)
                else:
                    l_asset_ar.append(ar)
    return l_asset_ar, l_unload_ar, l_asb_ar


