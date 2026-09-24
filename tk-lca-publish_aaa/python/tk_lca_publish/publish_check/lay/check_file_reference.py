# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Wang Huan
#
# Date: 2015.07
#
# Description: Check file reference
#
############################################
__maintainer__ = 'zhangzheng'

import traceback
import os
import pymel.core as pm
import re

ASSET_TYPE_PATTERN = re.compile('.*/.../asset/([a-z][a-z][a-z])/.*')

# 注意：flg 类型的资产在本次检查中允许 File Reference 和 Assembly Reference，
# 因此 GRP_NAME 中不再包含 'flg'
GRP_NAME = ['chr', 'crd', 'prp', 'veh', 'rra']


def getAssetType(path):
    path = path.replace('\\', '/')
    match = ASSET_TYPE_PATTERN.match(path)
    if match:
        return match.group(1)


def get_top_assets():
    if not pm.objExists('|assets'):
        return ''

    grps = pm.listRelatives('|assets', c=1, type='transform')
    top_level_nodes = []

    for grp in grps:
        if grp in ['lay']:
            continue
        childrens = pm.listRelatives(grp, c=1)
        if childrens:
            top_level_nodes.extend(childrens)

    assets = {}
    for m in top_level_nodes:
        mtype = ''
        if not isinstance(m, pm.nodetypes.Transform):
            continue
        ref = m.referenceFile()
        if isinstance(ref, pm.system.FileReference):
            mtype = getAssetType(ref.path)
        elif isinstance(m, pm.nt.AssemblyReference):
            path = m.getAttr('definition')
            if not path:
                continue
            mtype = getAssetType(path)
        else:
            continue

        assets.setdefault(mtype, [])
        assets[mtype].append(m)
    return assets


# All system check classes will use StdCheck as the class name.
class StdCheck:
    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u'检查哪些资产使用了File Reference'
        self.description = u'chr/crd/prp/veh/rra类型资产必须使用File Reference，flg/env/asb/scn 类资产须使用Assembly Reference。'
        self.auto_fix = False
        self.duty = u'艺术家本人。'
        return

    def run_check(self):
        if self.dialog.project['name'].lower() in ['tpr', 'tap']:
            return ""

        try:
            assets = get_top_assets()
            if not assets:
                return u"缺少资产组 |assets"
            invalid_refAssets = []
            invalid_arAssets = []
            upper_case_assets = []
            for type_, masters in assets.iteritems():
                print type_, masters
                if type_ in GRP_NAME:
                    for m in masters:
                        ref = m.referenceFile()
                        if not isinstance(ref, pm.system.FileReference):
                            invalid_refAssets.append(m)
                        if ref and (len([i for i in re.findall('([A-Z])', ref.path) if i]) > 1 or
                                    [i for i in re.findall('([A-Z])', ref.namespace) if i]):
                            if "muggle_B" not in ref.path and "muggle_C" not in ref.path :
                                upper_case_assets.append('{} {}'.format(str(m), ref.path))
                elif type_ == 'flg':  # 对 flg 类型允许 File Reference 和 Assembly Reference
                    for m in masters:
                        ref = m.referenceFile()
                        # 如果引用为空，根据实际需求可作处理，此处假设 ref 不为空时再判断
                        if ref and not isinstance(ref, (pm.system.FileReference, pm.nt.AssemblyReference)):
                            invalid_arAssets.append(m)
                else:
                    for m in masters:
                        if not isinstance(m, pm.nt.AssemblyReference):
                            invalid_arAssets.append(m)

            refError = ""
            arError = ""
            refErrorInfo = ""
            arErrorInfo = ""
            upper_err_info = ''

            if invalid_refAssets:
                for i in invalid_refAssets:
                    refError += str(i) + "\t"
                refErrorInfo = u"以下 chr/crd/prp/veh/rra 类资产使用了Assembly Reference，应该使用传统的File Reference。\n" + refError

            if invalid_arAssets:
                for j in invalid_arAssets:
                    arError += str(j)
                arErrorInfo = u"以下 flg/env/asb/scn 类资产使用了传统的File Reference，应该使用Assembly Reference。\n" + arError

            if upper_case_assets:
                upper_err_info = u'以下资产的reference路径里有多个大写字母或命名空间有大写字母,请改为小写字母:\n{}'.format(
                    '\n'.join(upper_case_assets))

            errorInfo = arErrorInfo + "\n" + refErrorInfo + u'\n{}'.format(upper_err_info)
            if invalid_arAssets or invalid_refAssets or upper_err_info:
                return errorInfo

            return ""
        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        return

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
