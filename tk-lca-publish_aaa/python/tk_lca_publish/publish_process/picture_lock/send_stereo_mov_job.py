# -*- coding:utf-8 -*-

import os
import traceback
import production.rv_submit as rvj


class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"发送合成立体mov任务"
        self.description = u"发送合成立体mov的农场(311)任务"
        return

    def proceed(self):
        try:
            # send a job to merge a stereo mov
            job = {
                'name': '[Picture Lock] Merge Stereo MOV {}'.format(self.dialog.version_name),
                'project': self.dialog.project['name'],
                'input': '[ {left} {right} {audio} ]'.format(
                    left=os.path.join(self.dialog.version_dir, 'jpg', 'L', '{}.@@@@@@.jpg'.format(self.dialog.entity['name'])),
                    right=os.path.join(self.dialog.version_dir, 'jpg', 'R', '{}.@@@@@@.jpg'.format(self.dialog.entity['name'])),
                    audio=os.path.join(self.dialog.version_dir, self.dialog.version_name + '.wav')
                ),
                'output': os.path.join(self.dialog.version_dir, 'preview', '{}.stereo.mov'.format(self.dialog.version_name)),
                'args': '-audiorate 48000 -outstereo -outfps 24.0 -outparams comment="{}" timecode=1'.format(self.dialog.version_dir)
            }
            # print '>'*30, job
            rvj.send_rv_job_convert(job)
            return ""

        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
