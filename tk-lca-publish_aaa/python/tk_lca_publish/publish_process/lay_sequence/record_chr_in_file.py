# -*- coding:utf-8 -*-
__author__ = 'xiangquan'
import os
import traceback

import pymel.core as pm
# import ani.lca_pass_manager.pass_manager_model as pmm;reload(pmm)

# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"记录此次publish时，文件里的chr资产名字。"
        self.description = u"记录此次publish时，文件里的chr资产名字。"
        return


    def proceed(self):
        try:
            chr_txt = os.path.join(self.dialog.version_dir, 'chr_list.txt').replace('\\', '/')
            # # function 1: get all assets under |assets|chr
            # chrs = pm.listRelatives('|assets|chr', children = True)
            # chr_assets = []
            # for chr in chrs:
            #     chr_ref_file = chr.referenceFile()
            #     chr_asset = os.path.splitext(os.path.basename(chr_ref_file.path))[0]
            #     chr_assets.append(chr_asset)
            #
            # chr_assets = list(set(chr_assets))
            # chr_assets_str = '\n'.join(chr_assets)

            # function 2: get assets under [shot]_assets.
            assets_objSets = [objSet for objSet in pm.ls(type = 'objectSet') if objSet.name().endswith('_assets')]
            all_chrs = pm.listRelatives('|assets|chr', children = True)
            chr_assets = []
            for assets_objSet in assets_objSets:
                objSet_chrs = [asset for asset in pm.listConnections(assets_objSet, source = True, destination = False)
                              if asset in all_chrs]
                # print objSet_chrs
                for chr in objSet_chrs:
                    chr_ref_file = chr.referenceFile()
                    chr_asset = os.path.splitext(os.path.basename(chr_ref_file.path))[0]
                    chr_assets.append(chr_asset)

            chr_assets = list(set(chr_assets))
            chr_assets_str = '\n'.join(chr_assets)

            # write to file
            with open(chr_txt, 'w') as op:
                op.write(chr_assets_str)

            # # add 添加角色 UUID信息
            # pmm_cm = pmm.CharacterModel()
            # pmm_cm.register_all_characters()

            return ""

        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description

