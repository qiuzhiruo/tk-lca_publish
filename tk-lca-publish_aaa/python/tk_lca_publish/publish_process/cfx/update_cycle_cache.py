# coding: utf-8

'''
    Date: 2025.10.29 --17:00
    Description:
                在cfx publish流程加入cycle更新，pa新版本调用动画代码去找这个cycle涉及的镜头，也进行更新

'''
__author__ = 'wenhui'

import ani.lca_cycle_info_tool.update_cycle_cfx_cache as uc

# All publish process will use StdProcess as the class name.

class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"cycle更新"
        self.description = u"识别所有cycle对应的主镜头并更新"

    def proceed(self):
        project = self.dialog.project.get("name").lower()
        shot_name = self.dialog.entity_name

        if shot_name[:3] == 'z33':
            res = uc.main(project, shot_name)
            print('result:',type(res), repr(res))
            return u''
        else:
            print('不是cycle镜头，跳过')
            return u''



    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
