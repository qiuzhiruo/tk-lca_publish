#!-*- coding:utf-8 -*-
import pymel.core as pm


class StdCheck(object):
    def __init__(self, dialog):
        super(StdCheck, self).__init__()
        self.dialog = dialog
        self.check_name = u"检查镜头的stage pivot是否为空"
        self.description = u"镜头的stage pivot不应为空, 且assets组和cameras组的位移应该和镜头的stage pivot一致 ( 群集 z1* 场次，会直接设置 sg_stage_pivot 为 0 0 0 )"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        return

    def run_check(self):
        shot_name = self.dialog.entity['name']
        sg_pivot = self.dialog.sg.find_one('Shot', [['project', 'is', self.dialog.project], ['code', 'is', shot_name]],
                                           ['sg_stage_pivot'])['sg_stage_pivot']
        self.dialog.print_log('{} sg_pivot: {}'.format(shot_name, str(sg_pivot)))
        if not sg_pivot:
            return u'镜头 {} 的stage pivot为空, 请先尝试自动修复!'.format(shot_name)
        else: # z1* 场次 stage pivot 需要 为 0 0 0
            if self.dialog.step['name'] == 'ani' and self.dialog.entity['name'].startswith('z1'):
                z1_sg_pivot = sg_pivot['name']
                if z1_sg_pivot != '0 0 0':
                    return u'z1* 场次 镜头 {} 的 stage pivot 不为 0 0 0 , 请先尝试自动修复!'.format(shot_name)
        return ''

    def run_fix(self):
        '''Auto Fix'''
        # z1* 场次 stage pivot 需要 为 0 0 0
        if self.dialog.step['name'] == 'ani' and self.dialog.entity['name'].startswith('z1'):
            sp_name = '0 0 0'
            sp = self.dialog.sg.find_one('CustomEntity05', [['project', 'name_is', 'nza'], ['code', 'is', sp_name]])
            if not sp:
                sp = self.dialog.sg.create('CustomEntity05',
                                           {'project': {'type': 'Project', 'id': self.dialog.project['id']},
                                            'code': sp_name})
            self.dialog.sg.update('Shot', self.dialog.entity['id'], {'sg_stage_pivot': sp})
        else:
            asset_tran = pm.PyNode('|assets').getTranslation()
            camera_tra = pm.PyNode('|cameras').getTranslation()
            if asset_tran == camera_tra:
                # auto update the shot stage_pivot for some new shot whose stage_pivot is empty
                sp_name = ' '.join([str(-int(i)) for i in list(asset_tran)]).replace('-0', '0')
                sp = self.dialog.sg.find_one('CustomEntity05', [['project', 'name_is', 'nza'], ['code', 'is', sp_name]])
                if not sp:
                    sp = self.dialog.sg.create('CustomEntity05',
                                            {'project': {'type': 'Project', 'id': self.dialog.project['id']},
                                                'code': sp_name})
                self.dialog.sg.update('Shot', self.dialog.entity['id'], {'sg_stage_pivot': sp})
            else:
                return u'|assets组和|cameras组的位移不相等, 无法自动修复, 请联系PC设置{}的stage pivot!'.format(self.dialog.entity['name'])

        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
