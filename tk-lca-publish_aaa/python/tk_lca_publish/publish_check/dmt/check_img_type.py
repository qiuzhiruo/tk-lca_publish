# -*- coding:utf-8 -*-
import traceback


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查素材类型是否为EXR/MOV"
        self.description = u"ACES下publish素材必须为EXR OR MOV"
        self.auto_fix = False
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        try:
            illegal_files = []
            color_space_info = self.dialog.sg.find_one('Project',
                                                       [['name', 'is', self.dialog.project['name']]],
                                                       ['sg_color_space'])
            if color_space_info['sg_color_space'] == "ACES":
                for f in self.dialog.l_preview_files:
                    if not f.endswith('exr') and not f.endswith('mov'):
                        illegal_files.append(f)

            if len(illegal_files) > 0:
                return u"ACES素材必须为EXR, 以下素材不是EXR:\n" + '\n'.join(illegal_files)

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
