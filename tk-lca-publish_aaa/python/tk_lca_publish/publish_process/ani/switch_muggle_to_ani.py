# -*- coding:utf-8 -*-
import traceback


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"切换 muggle_rig 为 ani_rig"
        self.description = u"muggle_rig层级不一样，会导致xml出错，所以需要切成ani_rig"
        return

    def proceed(self):
        try:
            import ani.lca_asset_switch.muggle_to_anim as mta
            reload(mta)
            mta.main()

            return ""
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
