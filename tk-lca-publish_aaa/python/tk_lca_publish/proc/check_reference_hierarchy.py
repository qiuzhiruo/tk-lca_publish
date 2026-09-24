# -*- coding:utf-8 -*-

__author__ = 'lvyuedong'


import pymel.core as pm

def check():
    # reference in group that is under another reference is illegal
    ref_nodes = pm.ls('*:master', rn=True, long=True)
    find_illegal_ref = []
    for ref in ref_nodes:
        for ref2 in ref_nodes:
            if ref.isParentOf(ref2):
                find_illegal_ref.append(ref)
                find_illegal_ref.append(ref2)
                break
        if find_illegal_ref:
            break
    if find_illegal_ref:
        return u"非法的reference层级: "+find_illegal_ref[1]+u"在"+find_illegal_ref[0]+u"层级下。reference之间不能互为父子层级。"
        # why? because we move object by rig, not by transform of shapes directly, simple grouping rule simply doesn't apply to our system
    else:
        return None