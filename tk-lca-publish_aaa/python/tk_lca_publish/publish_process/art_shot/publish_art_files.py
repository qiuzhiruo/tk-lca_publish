# -*- coding:utf-8 -*-
import datetime
import getpass
import os
import shutil
import subprocess
import tempfile
import sys
import traceback
import create_sg_version

if sys.platform.startswith('win'):
    # WORK_ROOT = 'W:'
    OUTPUT_ROOT = 'O:'
    PUBLISH_ROOT = 'Z:'
    # TOOL_ROOT = 'U:'
elif sys.platform.startswith('linux'):
    # WORK_ROOT = '/mnt/work'
    OUTPUT_ROOT = '/output'
    PUBLISH_ROOT = '/mnt/proj'
    # TOOL_ROOT = '/mnt/utility'

WORK_ROOT = os.getenv('LC_WORK')
TOOL_ROOT = os.getenv('LC_UTILITY')

class StdProcess():
    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"批量拷贝colorkey文件到服务器上版本文件夹"
        self.description = u"将艺术家提交的文件拷贝到版本文件夹。"
        return

    def convert_file(self, src, dst):
        self.dialog.print_log('"' + self.dialog.rvls_path + '" -l ' + src)
        p = subprocess.Popen('"' + self.dialog.rvls_path + '" -l ' + src, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)
        tokens = p.communicate()[0].split('\n')[1].split(' ')
        tokens = [i for i in tokens if i != '']

        img_w = int(tokens[0])
        img_h = int(tokens[2])

        if not (tokens[0].isdigit() and tokens[2].isdigit()):
            ratio = 1

        elif img_w == 0 or img_h == 0:
            ratio = 1

        else:
            ratio = min(900 / float(float(img_w)), 600 / float(img_h))

        cmd = '"' + self.dialog.rvio_path + '" ' + src + ' -scale ' + str(ratio) + ' -o ' + dst
        temp = tempfile.gettempdir()
        with open('%s/art_pub_log.txt' % temp, 'a') as f:
            f.write(cmd)

        ext_src = src.lower().split('.')[-1]
        if ext_src == 'exr':
            cmd += ' -outsrgb'

        os.system(cmd)
        return

    def proceed(self):
        try:
            proj_name = self.dialog.project['name'].lower()
            step_name = self.dialog.step['name']
            task_name = self.dialog.task['name']

            for file_path in self.dialog.l_preview_files:
                shot_name = os.path.basename(file_path).split('.')[0]
                publish_dir = PUBLISH_ROOT + '/projects/' + proj_name.lower() + '/shot/' + shot_name[
                                                                                           :3] + '/' + shot_name + '/' + step_name + '/publish/'
                self.dialog.print_log('----------------', publish_dir)
                v000_dir = '.'.join([shot_name, step_name, task_name, 'v000'])

                # create v000 dir
                all_image_folder = os.path.join(publish_dir, v000_dir)
                if not os.path.isdir(all_image_folder):
                    os.makedirs(all_image_folder, 0777)

                # create v000 icon dir
                all_image_icon_folder = os.path.join(all_image_folder, 'icon')
                if not os.path.isdir(all_image_icon_folder):
                    os.makedirs(all_image_icon_folder, 0777)

                # create v000 preview
                v000_preview_dir = os.path.join(all_image_folder, 'preview')
                if not os.path.isdir(v000_preview_dir):
                    os.makedirs(v000_preview_dir, 0777)
                    os.system('chmod 777 ' + v000_preview_dir)

                # info
                version_num = sorted(os.listdir(publish_dir))[-1].split('.')[-1].split('v')[-1]
                new_version_num = 'v%03d' % (int(version_num[-3:]) + 1)
                version_name = '.'.join([shot_name, step_name, task_name, new_version_num])
                version_dir = publish_dir + version_name

                # create version dir and preview dir
                if not os.path.isdir(version_dir):
                    os.makedirs(version_dir)
                if not os.path.isdir(version_dir + '/preview'):
                    os.makedirs(version_dir + '/preview')
                v_preview = version_dir + '/preview/' + version_name + '.mov'

                # create version thumbnail dir
                thumbnail_dir = version_dir + '/thumbnail/'
                if not os.path.isdir(thumbnail_dir):
                    os.makedirs(thumbnail_dir)

                # convert version preview(.mov)
                # self.convert_file(file_path, v_preview)

                # convert version thumbnail(.png)
                dst = thumbnail_dir + os.path.basename(file_path) + '.png'
                self.convert_file(file_path, dst)
                self.dialog.print_log('convert version thumbnail')

                # copy thumbnail to v000 icon dir
                shutil.copyfile(dst, all_image_icon_folder + '/' + version_name + '.' + os.path.basename(dst))

                # copy version file
                shutil.copyfile(file_path, version_dir + '/' + os.path.basename(file_path))

                # create tmp******* jinjin-
                tmp_dir = version_dir + '/tmp/'
                if not os.path.isdir(tmp_dir):
                    os.makedirs(tmp_dir)
                name, ext = os.path.splitext(os.path.basename(file_path))
                tmp_file_name = '{}.{}{}'.format(name, 1001, ext)
                tmp_file = tmp_dir + '/' + tmp_file_name
                shutil.copyfile(file_path, tmp_file)

                first_frame = 1001
                cmd = '"' + self.dialog.rvio_path + '" [ ' + tmp_file + ' -pa 1.0 ] -o ' + v_preview
                cmd += ' -outparams comment="author ' + getpass.getuser() + '" timecode=' + str(first_frame)
                print(cmd)
                p = subprocess.Popen(cmd, shell=True)
                p.communicate()

                # create v000 backup dir
                new_file_path = all_image_folder + '/' + version_name + '.' + os.path.basename(file_path)
                if os.path.isfile(new_file_path):
                    backup_dir = os.path.join(all_image_folder, 'backup')
                    if not os.path.isdir(backup_dir):
                        os.makedirs(backup_dir, 0777)
                    backup_image_name = new_file_path[:-3] + datetime.datetime.now().strftime(
                        "%Y%m%d%H%M%S") + new_file_path[-4:]
                    os.rename(new_file_path, os.path.join(backup_dir, os.path.basename(backup_image_name)))

                if 'delete_image' in file_path:
                    continue
                # copy v000 file
                shutil.copyfile(file_path, new_file_path)

                file_path = str(file_path)
                if file_path.endswith('.mov'):
                    continue
                if 'delete_image' in file_path:
                    continue
            return ''
        except:
            return traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
