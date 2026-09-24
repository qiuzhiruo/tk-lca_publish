# -*- coding: utf-8 -*-
# @Time    : 7/9/24 3:34 PM
# @Author  : Liu Xiaoyu
# @Site    : 
# @File    : build_mod_usd_file.py
# @Software: PyCharm
import sys
import traceback
import os
# if sys.platform.startswith("win"):
#     os.environ["PATH"] += ';W:/software/muster8.5.7_win/'
#     os.environ["MUSTER"] = 'C:/Program Files/Virtual Vertex/Muster 8/'
#     sys.path.append('U:/linked_tools/lcatools/lib/3rd_party/Muster_win/muster8sdk/libs/win64/python27')
#     sys.path.append('U:/linked_tools/lcatools/lib/3rd_party/Muster_win/')

class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"生成usd。"
        self.description = u"生成usd。"
        return

    def proceed(self):
        try:
            # sys.path.append("U:/toolset/lib/production")
            # sys.path.append('/mnt/utility/toolset/lib/production')
            import production.python_job as ppj
            from production.farm_ip import LcaFarmIPManage
            reload(ppj)

            for asset_name in self.dialog.d_assets_info.keys():
                if self.dialog.d_assets_info[asset_name]['type'] not in ['chr','crd','asm','env','prp','flg']:
                    return ''
                publish_folder_name = self.dialog.d_assets_info[asset_name]['version_name']
                proj = self.dialog.project['name']
                generate_xmlUSD_folder_id = ppj.send_job('/mnt/work/shome/PLETEMP/PIPELINE_GITLAB/fake_utility/lca_sgtk_apps/tk-lca-publish/python/tk_lca_publish/publish_process/mod/build_mod_usd_file.py',
                                                          args=proj + ' ' + publish_folder_name,
                                                          proj=proj,
                                                          pools='centos7',
                                                          python_exe='/mnt/work/shome/PLETEMP/PIPELINE_GITLAB/fake_utility/linked_tools/lca_rez/launchers/gen/linux/lca_python',
                                                          step='MOD',
                                                          job_name_prefix='[Generate xmlUSD folder] ' + publish_folder_name,
                                                          url=LcaFarmIPManage().MASTERCACHE,
                                                          user=self.dialog.user['name'],
                                                          submitdl=True
                                                         )
                print '\n\nGenerate xmlUSD folder on farm,job id :', generate_xmlUSD_folder_id

            return ""

        except:
            return traceback.format_exc()
    def get_process_name(self):
        return self.process_name
    def get_description(self):
        return self.description


def main(proj,asset_ver,t=0):
    import lcx2u
    proj = proj.lower()
    assets = (asset_ver,)
    lcx2u.buildAssetComponentMod(proj=proj, assets=assets, time_elapsed=t)

if __name__ == '__main__':
    main(*sys.argv[1:])
