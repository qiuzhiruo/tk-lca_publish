# -*- coding:utf-8 -*-

import traceback
import os
import pymel.core as pm
import ani.lca_asset_switch.functions as lasf

reload(lasf)

# import ani.lca_asset_switch.switch_rig_new as srn
#
# reload(srn)

EXCEPTIONAL_ASSETS = ['axuan', 'axuan_spirit', 'axuan_tied_up', 'taoist_priest']


# All system check classes will use StdCheck as the class name.
class StdCheck():

    def __init__(self, dialog):
        self.dialog = dialog
        self.check_name = u"检查资产的reference路径是否符合规范"
        self.description = u"资产路径必须来自Z或mnt/proj盘，不可以是task任务，不能带版本号"
        self.auto_fix = True
        self.duty = u"艺术家本人。"
        self.to_fix = {}
        return

    def run_check(self):
        self.to_fix = {}
        try:
            ref_files = pm.listReferences(recursive=True)
            illegal_ref = []

            # for ani and flo to check locked rig asset for shot
            lock_asset = {}
            if self.dialog.step['name'] in ['ani', 'flo']:
                lock_asset = lasf.get_shot_lock_asset_data(proj=self.dialog.project['name'],
                                                           shot_name=self.dialog.entity['name'])

            for r in ref_files:
                if not r.isLoaded():
                    continue

                # skip rra check for lrs rra
                ref_rn = pm.referenceQuery(r, referenceNode=True, topReference=True)
                ref_path = pm.referenceQuery(ref_rn, filename=True)
                if '/asset/rra/' in ref_path:
                    continue

                ns = ''
                try:
                    ns = r.fullNamespace
                except:
                    print traceback.format_exc()
                if not ns:
                    illegal_ref.append(str(r) + u": 命名空间异常!")
                    continue
                master = ns.strip(':') + ':master'
                if not pm.objExists(master):
                    continue
                if pm.objExists('|master') and not pm.PyNode(master).isChildOf('|master'):
                    continue
                if pm.objExists('|assets') and not pm.PyNode(master).isChildOf('|assets'):
                    continue
                if pm.objExists('|assets|lay') and pm.PyNode(master).isChildOf('|assets|lay'):
                    continue

                path = str(r.path).replace('\\', '/')
                if not path.startswith('/mnt/proj') and not path.startswith('Z:'):
                    illegal_ref.append(master + u": 路径必须以/mnt/proj或Z:开头, 当前路径 " + path)
                    continue
                if '/task/' in path or not '/asset/' in path or not '/publish/' in path:
                    illegal_ref.append(master + u": 路径不可以有/task/, 必须含有/asset/和/publish/, 当前路径 " + path)
                    continue

                if "/anim_rig/" in path:
                    v_dir = path.split('/')[-3]
                else:
                    v_dir = path.split('/')[-2]
                tokens = v_dir.split('.')

                if tokens[0] in lock_asset:
                    if v_dir != lock_asset[tokens[0]]:
                        self.to_fix.setdefault('lock_asset', {})
                        self.to_fix['lock_asset'][path] = [v_dir, lock_asset[tokens[0]]]

                        illegal_ref.append(
                            u'{}: 此资产在当前镜头应该锁到这个rig版本: "{}", 当前为:"{}"'.format(master, lock_asset[tokens[0]], v_dir))

                elif len(tokens[-1]) == 4 and tokens[-1][0] == 'v' and tokens[-1][1:].isdigit():
                    if self.dialog.project['name'].upper() != 'PWS':
                        illegal_ref.append(master + u": 路径版本不可以带版本号, 当前版本为 " + v_dir)
                    else:
                        if not tokens[0] in EXCEPTIONAL_ASSETS:
                            illegal_ref.append(master + u": 路径版本不可以带版本号, 当前版本为 " + v_dir)

            if illegal_ref:
                return u"以下资产的路径非法: \n" + '\n'.join(illegal_ref)

            return ""

        except:
            return traceback.format_exc()

    def run_fix(self):
        '''Auto Fix'''
        try:
            ref_files = pm.listReferences(recursive=True)
            failed = []
            illegal = []

            for r in ref_files:
                if not r.isLoaded():
                    continue
                path = str(r.path).replace('\\', '/')
                if 'cam.camera' in path:
                    continue

                if "/anim_rig/" in path:
                    v_dir = path.split('/')[-3]
                else:
                    v_dir = path.split('/')[-2]

                if path in self.to_fix.get('lock_asset', {}):  # lock asset rig to fix
                    new_path = path.replace(self.to_fix['lock_asset'][path][0], self.to_fix['lock_asset'][path][1])
                    r.replaceWith(new_path)
                elif v_dir[-3:].isdigit():  # normal rig to fix
                    try:
                        if ':' in r.fullNamespace.strip(':'):
                            # this is a child reference
                            illegal.append(r.fullNamespace + ':master')
                            continue
                    except:
                        illegal.append(r.fullNamespace + ':master')
                    try:

                        if "/anim_rig/" in path:
                            new_path = os.path.dirname(path).replace('/anim_rig', '')[:-5] + '/' + os.path.basename(
                                path)
                        else:
                            new_path = os.path.dirname(path)[:-5] + '/' + os.path.basename(path)

                        r.replaceWith(new_path)
                    except:
                        failed.append(r.fullNamespace + ':master')
                        return traceback.format_exc()

            if illegal:
                return u"以下资产无法替换为不带版本号，因为它们属于asb或scn: \n" + '\n'.join(illegal)
        except:
            return traceback.format_exc()

        return ''

    def get_check_name(self):
        return self.check_name

    def get_description(self):
        return self.description

    def get_auto_fix(self):
        return self.auto_fix

    def get_duty(self):
        return self.duty
