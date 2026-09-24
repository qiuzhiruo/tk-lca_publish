# -*- coding:utf-8 -*-

import traceback
import maya.cmds as cmds
import pymel.core as pm
import os
import sys
import datetime
import glob
sys.path.append('{}/toolset/lib/production'.format(os.getenv('LC_UTILITY', '/mnt/utility')))
from production.mail.mail import SendMail
import production.mail.mail_config as mail_config

current_time = datetime.datetime.now().strftime('%Y_%m_%d')
shotgun_page = "http://shotgun.zhuiguang.com/page/19370"


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"asb子资产面数过大预警。"
        self.description = u"asb子资产面数过大预警"
        return


    def getAssetUrl(self, proj, asset):

        sg_asset = self.dialog.sg.find_one('Asset', [['project', 'name_is', proj], ['code', 'is', asset]], ['id'])
        sg_proj = self.dialog.sg.find_one('Project',  [['name', 'is', [proj]]], ['id'])

        if not sg_asset:
            return ""

        # url = 'http://shotgun.zhuiguang.com/detail/Asset/' + asset_id
        url = 'https://smk.zhuiguang.com/projects/{0}/asset/{1}'.format(str(sg_proj['id']), str(sg_asset['id']))
        return url

    def proceed(self):
        try:

            # 获取超过50万面的物体信息
            reference_list = pm.ls(type='assemblyReference')
            asset_list = []
            for ar in reference_list:
                ref_path = str(ar.getAttr("definition")).replace('\\', '/')
                asset_name = ref_path.split("/")[-1][:-3]
                if asset_name not in asset_list:
                    asset_list.append(asset_name)
            min_face_count = 500000
            ass = []
            for asset_ in asset_list:
                filters = [['project', 'name_is', self.dialog.project['name'].lower()], ['sg_status_list', 'is_not', 'omt'],
                           ['sg_poly_count_hi', 'greater_than', min_face_count],
                           ['code', 'is', asset_]]
                fields = ['project', 'code', 'sg_status_list', 'sg_poly_count_hi', 'sg_poly_count_lo',
                          'sg_asset_type', 'sg_chinese']
                asset_max = self.dialog.sg.find('Asset', filters, fields)
                if asset_max:
                    ass.append(asset_max[0])
                    print(asset_max)
            if not ass:
                return""

            # 拆分shotgun信息
            poly_list = []
            for a in ass:
                w = [a['code'], str(a["sg_chinese"]), str(a['sg_asset_type']), str(a['sg_poly_count_hi']),
                     str(a['sg_poly_count_lo']), a['project']['name']]
                poly_list.append(w)

            poly_list = (sorted(poly_list, key=lambda x: float(x[3]), reverse=True))
            poly_list_str = []
            for i in poly_list:
                proj_name = i[5].lower()
                i[3] = str(round(float(i[3])/10000, 2))
                if sys.platform.startswith('win'):
                    version_path = "Z:/projects/{proj}/asset/{asset_type}/{asset_name}/mod/publish/{asset_name}.mod.model.v*".format(proj=proj_name, asset_type=i[2], asset_name=i[0])
                elif sys.platform.startswith('linux'):
                    version_path = "/mnt/proj/projects/{proj}/asset/{asset_type}/{asset_name}/mod/publish/{asset_name}.mod.model.v*".format(proj=proj_name, asset_type=i[2], asset_name=i[0])
                version_list = glob.glob(version_path)
                if not version_list:
                    continue
                version_list.sort()
                last_ver = version_list[-1]
                mov_name = i[0] + ".mod.model." + last_ver.split(".")[-1] + ".mov"
                asset_image = last_ver + "/preview/thumbnail.jpg"
                if sys.platform.startswith('linux'):
                    asset_image = asset_image.replace("/mnt/proj/", "../../")
                if sys.platform.startswith('win'):
                    asset_image = asset_image.replace("Z:/", "../../")
                mov_path = last_ver + "/preview/" + mov_name

                usrl = self.getAssetUrl(proj_name, i[0])

                # 设置表格颜色,设置表格
                red = "#FF0000"
                green = "#00FF00"
                yellow = "#FFFF00"
                purple = '#9457EB'

                color = green

                if (float(i[3]) > 50) and (float(i[3]) < 100):
                    color = yellow

                if float(i[3]) > 100:
                    color = red

                if float(i[3]) > 1000:
                    color = purple

                asset_str = '<tr><td bgcolor="' + color + '">{}</td><td>{}</td><td>{}</td><td>{}</td>'.format(*i)
                asset_str += '<td><a href="{path}">{path}</a></td>'.format(path=usrl)
                asset_str += '<td><img src="{0}" alt="flower" width="250" height="250"></td>'.format(asset_image)
                asset_str += "<td>{0}</td></tr>\n".format(mov_path)

                poly_list_str.append(asset_str)
            # 获取work文件夹路径，创建html文件夹
            file_path = os.path.dirname(cmds.file(q=True, sceneName=True))
            html_path = file_path + '/html/'
            if not os.path.exists(html_path):
                os.makedirs(html_path)
                os.chmod(html_path, 0777)

            ticket_report = html_path + 'scn_face_count' + current_time + '.html'

            poly_list_str.insert(0,
                                 '<tr><td bgcolor="#C0C0C0">资产名</td><td bgcolor="#C0C0C0">中文名</td><td bgcolor="#C0C0C0">类型</td><td bgcolor="#C0C0C0">High_poly(单位: 万)</td><td bgcolor="#C0C0C0">sunmark_web</td><td bgcolor="#C0C0C0">mov</td></tr>')
            poly_list_str.insert(0, '<table border="1">')
            poly_list_str.append('</table>')

            # 将信息写如xml
            with open(ticket_report, 'w') as f:
                f.write(self.dialog.entity['name'] + 'asb子资产面数过大预警(黄色：>50w)<br>; 红色: >100w; 紫色: >1000w')
                for i in poly_list_str:
                    f.write(i)

            # 应yidong要求，改为一天一次， 移动到Cronsun
            # shotgun获取收件人名字
            # to_list = ['zejie', 'haojia', "haoran", "jingwei2", "liyidong", "aokang", "fanyu",'jiantao','xiaoyu2', 'qingyao', 'likun', 'lujiangli', 'zhiyuan']
            #to_list = ['zejie']

            # 发送信息到谷歌邮箱
            # for t in to_list:
                # cmd_str = 'mail -s "' + 'ASB PUBLISH BIG SCENE WARNING!!!:' + '\n'+'Content-Type: text/html" ' + t + '@lightchaseranimation.com < ' + ticket_report
                # os.system(cmd_str)
                # SendMail(to_list=[t + '@' + mail_config.EMAIL_DOMAIN], sub='ASB PUBLISH BIG SCENE WARNING!!!:', content=ticket_report, sub_type='html')
                # print(u"已经发送")

            return ""

        except:

            return ""


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description









