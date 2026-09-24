# -*- coding:utf-8 -*-
import os


class HandlePreviewFile(object):
    """the handle cut preview file base class"""
    TAIL_FRAME = (u"R1 剪切帧", u"R2 剪切帧")

    @staticmethod
    def cut_frame_upload(shot_frame_range, preview_files):
        """upload the cut frame to shotgun
        Args:
            shot_frame_range (list): the frame range of shot
            preview_files (list): the list of preview files
        Returns (list): the list of preview file path
        """
        preview_start_frame = int(os.path.basename(preview_files[0]).split('.')[-2])
        preview_end_frame = int(os.path.basename(preview_files[-1]).split('.')[-2])
        shot_start_frame, shot_end_frame = int(shot_frame_range[0]), int(shot_frame_range[1])
        if preview_start_frame < shot_start_frame:
            cut_frame_length = shot_start_frame - preview_start_frame
            return preview_files[cut_frame_length:]
        elif shot_end_frame < preview_end_frame:
            cut_frame_length = preview_end_frame - shot_end_frame
            return preview_files[:-cut_frame_length]

    @staticmethod
    def get_shot_framerange(dialog):
        projFilter = [['name', 'is', str(dialog.project['name'])]]
        shotgunProjInfo = dialog.sg.find_one('Project', projFilter)

        shotFilter = [
            ['code', 'is', dialog.entity['name']],
            ['project', 'is', {'type': 'Project', 'id': shotgunProjInfo['id']}]
        ]
        info = dialog.sg.find_one('Shot', shotFilter,
                                  ['sg_sequence', 'sg_cut_in', 'sg_cut_out', 'sg_head_in', 'sg_tail_out'])

        if info:
            frame_range = [info['sg_cut_in'], info['sg_cut_out']]
            return frame_range
