#-*- coding=utf-8 -*-

import time
import os
import json
from collections import OrderedDict
import subprocess


def path_change_chmod(path):
    """
    解路径权限
    """
    cmd = 'su -'
    root_cmd = '''chmod 777 -R %s''' % path
    p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.stdin.write('20150312')
    p.stdin.write('\n')
    out, err = p.communicate(root_cmd)
    if err is None:
        # print('change chmod ok')
        return True
    else:
        # print ('change chmod error')
        return False


def record_time(py='process'):
    def decorator(func):
        def wrapper(*args, **kwargs):
            # time_info = OrderedDict()
            # start_time = time.time()
            result = func(*args, **kwargs)
            # end_time = time.time()
            # py_name = os.path.basename(py)
            # fun_type = os.path.basename(os.path.dirname(os.path.dirname(py)))
            # try:
            #     import pymel.core as pm
            #     cur_scn = pm.sceneName()
            # except ImportError as e:
            #     try:
            #         from Katana import FarmAPI
            #         cur_scn = FarmAPI.GetKatanaFileName()
            #     except:
            #         return result
            # if not cur_scn:
            #     return result
            # cur_dir = os.path.dirname(cur_scn)
            # file_name = os.path.basename(cur_scn).replace('.', '_')
            # time_json = os.path.join(cur_dir, 'function_time', file_name + '_function_time.json')
            # if os.path.exists(time_json):
            #     with open(time_json, 'r') as f:
            #         time_info = OrderedDict(json.loads(f.read()))
            #     if fun_type not in time_info:
            #         time_info[fun_type] = {}
            #     time_info[fun_type].update({py_name: end_time - start_time})
            #     with open(time_json, 'w') as f:
            #         f.write(json.dumps(time_info, indent=4))
            #     try:
            #         os.chmod(time_json, 0o777)
            #     except Exception as e:
            #         path_change_chmod(time_json)
            #
            # else:
            #     if not os.path.exists(os.path.join(cur_dir, 'function_time')):
            #         os.mkdir(os.path.join(cur_dir, 'function_time'))
            #         os.chmod(os.path.join(cur_dir, 'function_time'), 0o777)
            #     with open(time_json, 'w') as f:
            #         if fun_type not in time_info:
            #             time_info[fun_type] = {}
            #         time_info[fun_type].update({py_name: end_time - start_time})
            #         f.write(json.dumps(time_info, indent=4))
            #     os.chmod(time_json, 0o777)
            return result
        return wrapper
    return decorator


@record_time(py=__file__)
def my_def(n):
    time.sleep(1)
    return sum(range(n))
