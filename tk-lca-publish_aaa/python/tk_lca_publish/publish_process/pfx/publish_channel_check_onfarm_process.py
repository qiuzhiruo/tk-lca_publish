#! -*- coding:utf-8 -*-
import sys
import os
import nuke
import shutil
import subprocess
from production import shotgun_connection

sg = shotgun_connection.Connection('get_project_info').get_sg()
import production.pipeline.lcShotgun as plsg
tk_lca_publish_path = os.getenv('LCA_PUBLISH_APP')
NUKE_TEMPLATE_PROJ_PATH = "{}/python/tk_lca_publish/publish_process/lgt/NukeTemplate/generate_matte_jpg.nk".format(tk_lca_publish_path)

# rvio_path='/usr/local/rv/rv-linux/bin/rvio_hw'
rvio_path = '/usr/local/rv/rv-linux/bin/rvio'


def create_channel_check_task(proj, shot):
    info = sg.find('Task',
                   [['project', 'name_is', proj.upper()], ['entity', 'name_is', shot], ['step', 'name_is', 'pfx']],
                   ['sg_status_list', 'content', 'entity.Shot.id', 'content', 'project'])
    channel_check_task = []
    for i in info:
        if i.get('content') == "channel_check":
            channel_check_task.append(i)

    if channel_check_task == []:
        # create task
        data = {
            'entity': {"type": "Shot", "id": int(info[0]['entity.Shot.id'])},
            'project': {"type": "Project", "id": int(info[0]['project']['id'])},
            'content': 'channel_check',
            'step': {'type': 'Step', 'id': 60}#pfx是task 60
        }
        sg.create('Task', data)


def create_channel_check_dir_on_server(proj, shot):
    content = "paint_fix"
    step = "pfx"
    task_info_dict = sg.find_one("Task",
                                 [
                                     ['project', 'name_is', proj], ['entity', 'name_is', shot],
                                     ['content', 'is', content], ['step', 'name_is', step]
                                 ])
    version_info_list = sg.find('Version',
                                [
                                    ['project', 'name_is', proj], ['entity', 'name_is', shot],
                                    ['sg_task', 'is', task_info_dict]
                                ],
                                ['sg_version_type', 'code', 'user', 'tags', 'sg_version_folder'])

    # 按照 'code' 进行排序

    sorted_a = sorted(version_info_list, key=lambda x: x['code'])

    # 找到 'code' 最大的版本
    latest_version = max(sorted_a, key=lambda x: x['code'])

    version = latest_version['code'].split('.')[3]  # str
    seq = shot[:3]
    target_preview_file_path = "/mnt/proj/projects/{proj}/shot/{seq}/{shot}/pfx/publish/{shot}.pfx.channel_check.{version}/preview".format(
        proj=proj, seq=seq, shot=shot, version=version)

    target_jpg_file_path     = "/mnt/proj/projects/{proj}/shot/{seq}/{shot}/pfx/publish/{shot}.pfx.channel_check.{version}/jpg".format(
        proj=proj, seq=seq, shot=shot, version=version)
    if os.path.exists(os.path.dirname(target_preview_file_path)):
        shutil.rmtree(os.path.dirname(target_preview_file_path))
    os.makedirs(target_preview_file_path)
    os.makedirs(target_jpg_file_path)
    return version, target_preview_file_path


def copy(src, dst):
    def copy_directory(src, dst):
        if not os.path.exists(dst):
            os.makedirs(dst)

        for item in os.listdir(src):
            src_item = os.path.join(src, item)
            dst_item = os.path.join(dst, item)

            if os.path.isdir(src_item):
                copy_directory(src_item, dst_item)
            else:
                copy_file(src_item, dst_item)

    def copy_file(src, dst):
        dst_dir = os.path.dirname(dst)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        shutil.copy2(src, dst)

    # 如果源路径是目录，则拷贝整个目录
    print "正在从{src}拷贝到{dst}".format(src=src, dst=dst)
    if os.path.isdir(src):
        copy_directory(src, dst)
        print "  从{src}拷贝到{dst}完成".format(src=src, dst=dst)
    # 如果源路径是文件，则拷贝文件
    elif os.path.isfile(src):
        copy_file(src, dst)
        print "  从{src}拷贝到{dst}完成".format(src=src, dst=dst)
    else:
        print "源路径 {src} 无效。请提供一个有效的文件或目录路径。".format(src=src)


def generate_mov(proj, shot, version, target_preview_file_path):
    target_nuke_proj_path = os.path.dirname(target_preview_file_path)
    seq = shot[:3]
    # bug nuke读取软连有问题，素材缺少，得采用真实路径
    # target_lighting_exr_path = "/mnt/proj/projects/{proj}/shot/{seq}/{shot}/lgt/publish/{shot}.lgt.lighting.{version}/exr/L/{shot}.lgt.comp.####.exr".format(
    #     proj=proj, seq=seq, shot=shot, version=version)
    target_lighting_exr_path = "/mnt/proj/projects/{proj}/shot/{seq}/{shot}/pfx/publish/{shot}.pfx.paint_fix.{version}/exr/L".format(
        proj=proj, seq=seq, shot=shot, version=version)

    target_link_lighting_exr_path = os.readlink(target_lighting_exr_path) + "/{shot}.pfx.paint_fix.####.exr".format(
        shot=shot)
    # print "target_link_lighting_exr_path:",target_link_lighting_exr_path
    copy(NUKE_TEMPLATE_PROJ_PATH, target_nuke_proj_path)
    nuke.load(target_nuke_proj_path + "/generate_matte_jpg.nk")

    lcg = plsg.lcShotgun(proj, shot)
    lcg.initShotgunInfo()
    # print "lcg.getTimeIn():",lcg.getTimeIn()
    # print "lcg.getTimeOut():",lcg.getTimeOut()
    nuke.root().knob('first_frame').setValue(lcg.getTimeIn())
    nuke.root().knob('last_frame').setValue(lcg.getTimeOut())
    nuke.frame(lcg.getTimeIn())

    read_node = nuke.toNode('Read_exr')
    read_node['file'].setValue(target_link_lighting_exr_path)
    read_node['first'].setValue(lcg.getTimeIn())
    read_node['last'].setValue(lcg.getTimeOut())

    target_preview_mov_path = target_preview_file_path + "/{shot}.pfx.channel_check.{version}.mov".format(shot=shot,
                                                                                                          version=version)
    target_preview_jpg_path = target_nuke_proj_path + "/jpg/{shot}.pfx.channel_check.####.jpg".format(shot=shot,
                                                                                                      version=version)

    write_node = nuke.toNode('Write_jpg')
    write_node['file'].setValue(target_preview_jpg_path)
    write_node['views'].setValue('{L}')

    nuke.scriptSave(target_nuke_proj_path + "/generate_matte_jpg.nk")
    nuke.execute(write_node, int(nuke.root().knob('first_frame').getValue()),
                 int(nuke.root().knob('last_frame').getValue()), continueOnError=True, views=['L'])
    # nuke.execute(write_node,  continueOnError=True)

    # rv

    cmd = "{rvio_path} {source_jpg} -pa 1.0  -quality 1 -outrgb -o {target_preview_mov_path}".format(
        rvio_path=rvio_path,
        source_jpg=target_preview_jpg_path,
        target_preview_mov_path=target_preview_mov_path)

    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    std_out, std_err = p.communicate()
    print 'stdout : ', std_out
    print 'stderr : ', std_err

    # os.system(cmd)

    print 'cmd : ', cmd
    # os.system(cmd)
    return target_preview_mov_path


def delete_sg_repeat_version(proj, shot, version):
    task_info_dict = sg.find_one("Task",
                                 [
                                     ['project', 'name_is', proj], ['entity', 'name_is', shot],
                                     ['content', 'is', 'channel_check'], ['step', 'name_is', 'pfx']
                                 ])
    version_info_list = sg.find('Version',
                                [
                                    ['project', 'name_is', proj], ['entity', 'name_is', shot],
                                    ['sg_task', 'is', task_info_dict]
                                ],
                                ['sg_version_type', 'code', 'user', 'tags', 'sg_version_folder'])
    print version_info_list
    target_version_code = "{shot}.pfx.channel_check.lighting.{version}".format(shot=shot, version=version)
    delete_code_list = []
    for version in version_info_list:
        if version['code'] == target_version_code:
            delete_code_list.append(version['id'])

    for i in delete_code_list:
        sg.delete('Version', int(i))


def create_sg_version(proj, shot, version, target_preview_mov_path):
    local_path = os.path.dirname(target_preview_mov_path)

    description = "代码自动生成，对应paint_fix publish盘的{version}版本".format(version=version)

    d_v_type = {0: 'Daily', 1: 'Downstream'}

    from production.shotgun_connection import Connection
    sg = Connection('get_project_info').get_sg()

    project = sg.find_one('Project', [['name', 'is', proj]], [])

    shot_entity = sg.find_one('Shot', [['project', 'is', project], ['code', 'is', shot]], ['id'])

    task = sg.find_one('Task',
                       [['project', 'is', project], ['entity', 'is', shot_entity], ['content', 'is', 'channel_check'],
                        ['step', 'name_is', 'pfx']],
                       ['id', 'task_assignees'])

    target_code = "{shot}.pfx.channel_check.{version}".format(shot=shot, version=version)

    user = {'email': 'haojia@lightchaseranimation.com',
            'firstname': 'Tang',
            'id': 1145,
            'image': 'http://shotgun.zhuiguang.com/thumbnail/api_image/3299605?AccessKeyId=lNY89UmO1HoWeRP6zqp6&Expires=1679388625&Signature=QiRrf6AbbVVbtOGiMhLB0mOfgbCimMbZLsGh3Q4F5%2B8%3D',
            'lastname': 'Haojia',
            'login': 'haojia',
            'name': 'Tang Haojia',
            'type': 'HumanUser'}

    d_version = {
        'project': project,
        'entity': shot_entity,
        'sg_task': task,
        'code': target_code,
        'description': description,
        'user': user,
        'sg_version_folder':
            {'local_path': local_path,
             'name': target_code,
             'content_type': None,
             'link_type': 'local'
             },
        'sg_version_type': 'Downstream',
        'tag_list': [u'R1 L'],
        'created_by': user}

    d_version_str = __dict_qstr2str(d_version)
    # print  "local_path\n",local_path
    # print 'd_version_str\n', d_version_str
    v_info = sg.create('Version', d_version_str)
    # if not v_info:
    #     return  pprint.pformat(d_version_str)

    # v_info = v_info
    # Set related tasks
    task_info = sg.find_one('Task', [['id', 'is', task['id']]], ['step'])
    l_tasks = sg.find('Task', [['entity', 'is', shot_entity]], ['step'])
    l_related_tasks = [task_info]

    # print 'local_path : '+local_path
    # print d_version

    for task in l_tasks:
        if shot_entity['type'] == 'Shot' and task_info['step']['name'] == 'lay':
            if task['step']['name'] != 'lay':
                l_related_tasks.append(task)

    sg.update('Version', v_info['id'], {'sg_related_tasks': l_related_tasks})

    # Link to the 'last version' field of task
    sg.update('Task', task['id'], {'sg_last_version': v_info})
    # Update sg_uploaded_movie
    sg.upload('Version', v_info['id'], target_preview_mov_path, "sg_uploaded_movie")


def __dict_qstr2str(dict_data):
    result = {}
    for k, v in dict_data.items():
        if v.__class__.__name__ == 'QString':
            result[k] = unicode(v)
        elif v.__class__.__name__ == 'list':
            new_v = []
            for vv in v:
                if vv.__class__.__name__ == 'QString':
                    new_v.append(unicode(vv))
                else:
                    new_v.append(vv)
            result[k] = new_v
        else:
            result[k] = v
    return result


def refresh_1984(proj, shot, target_preview_mov_path):
    cache_path = "/mnt/proj/trash/log/1984/Version_Caches/{proj}.txt".format(proj=proj)
    # cache_path="/mnt/work/shome/tanghaojia/test/lrs.txt"
    try:
        with open(cache_path, 'a') as f:
            f.write(target_preview_mov_path + '\n')
    except:
        print 'Failed to Send a singal to lock the version folder.'
        print "cache_path:"
        print cache_path
        os._exit(0)
    os._exit(0)


if __name__ == '__main__':
    proj = sys.argv[1]
    print "proj:", proj
    shot = sys.argv[2]
    print "shot:", shot

    # proj = "lrs"
    # shot = "z88888"

    create_channel_check_task(proj, shot)
    # #####muster#####
    version, target_preview_file_path = create_channel_check_dir_on_server(proj, shot)
    delete_sg_repeat_version(proj, shot, version)
    target_preview_mov_path = generate_mov(proj, shot, version, target_preview_file_path)
    # # target_preview_mov_path="/mnt/proj/projects/lrs/shot/z88/z88888/lgt/publish/z88888.lgt.channel_check.v000/preview/z88888.lgt.channel_check.v000.mov"
    # # version="v000"
    create_sg_version(proj, shot, version, target_preview_mov_path)
    refresh_1984(proj, shot, target_preview_mov_path)





