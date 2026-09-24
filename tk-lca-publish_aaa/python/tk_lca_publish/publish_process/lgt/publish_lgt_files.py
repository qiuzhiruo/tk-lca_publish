# -*- coding:utf-8 -*-

############################################
#
# Copyright (c) 2013 Light Chaser Animation
#
# Author: Liu Lu
#
# Date: 2013.08
#
# Description: Copy publish files
#
############################################

import os
import traceback
import shutil
import subprocess
import multiprocessing
import time
import ConfigParser
import re
import glob
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
try:
    from lxml import etree as ET
except:
    import xml.etree.ElementTree as ET

KATANA_FILE_TMP = "/mnt/work/projects/{proj}/shot/{seq}/{shot}/lgt/task/katana/{ver}.katana"
KATANA_OUTPUT = "/output/projects/{proj}/shot/{seq}/{shot}/lgt/output/katana/{ver}/{layer}/{res}/{eye}"
import stereo.findStereoCamera as fsc

def change_own(path):
    os.system('chown -R root:root ' + path)


def change_mod(path):
    os.system('chmod -R 755 ' + path)


def make_link(sur, des):
    if os.path.islink(des):
        os.unlink(des)
    os.symlink(sur, des)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"拷贝文件到服务器上版本文件夹"
        self.description = u"将艺术家提交的文件拷贝到版本文件夹。"
        self.proj = str(self.dialog.project['name']).lower()
        return

    def getkatanafileformname(self, lgtversionname, lgtpass, lgtR, alinfo):
        realversionname = ''
        for LR in ["L", "R"]:
            readfilename = KATANA_OUTPUT.format(
                proj=self.proj,
                seq=lgtversionname[:3],
                shot=lgtversionname[:6],
                ver=lgtversionname,
                layer=lgtpass,
                res=lgtR,
                eye=LR)

            # print readfilename
            if os.path.exists(readfilename):
                readfilenamerealpath = os.path.realpath(readfilename)
                realversionname = readfilenamerealpath.rsplit("/")[-4]
                katanafile = KATANA_FILE_TMP.format(
                    proj=self.proj,
                    seq=realversionname[:3],
                    shot=realversionname[:6],
                    ver=realversionname)

                if os.path.exists(katanafile) and realversionname:
                    alinfo["%s@%s@%s@%s" %
                           (lgtversionname, lgtpass, lgtR, LR)] = katanafile

    def indent(self, elem, level=0):
        i = "\n" + level*"  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
        return

    def GetinfofromNk(self, nk_file):
        alinfo = {}
        ReFK = r"file.*/katana/(\w{1}\d{5}\.lgt\.lighting\.?\w?\d*)/(\w*)/(\w*)"
        with open(nk_file) as f:
            for l in f.readlines():
                if re.findall(ReFK, l):
                    lgtversionname = re.findall(ReFK, l)[0][0]
                    lgtpass = re.findall(ReFK, l)[0][1]
                    lgtR = re.findall(ReFK, l)[0][2]
                    self.getkatanafileformname(
                        lgtversionname, lgtpass, lgtR, alinfo)
        return alinfo

    def WriteLibData(self, path, NktoKInfoData):
        root = ET.Element('Info')
        tree = ET.ElementTree(root)
        for NktoKInfokey in NktoKInfoData:
            child0 = ET.Element('nukereadfile',
            {"nrlgtversion": NktoKInfokey.split("@")[0],
             "nrlgtlayer": NktoKInfokey.split("@")[1],
             "nrlgtres": NktoKInfokey.split("@")[2],
             "nrlgtside": NktoKInfokey.split("@")[3],
             "katanafile": NktoKInfoData[NktoKInfokey]})
            root.append(child0)
        self.indent(root)
        tree.write(path)

    def Getrlgetfolder(self, lgtpfilepath):
        lgetfolder = os.path.join(lgtpfilepath, "katana")
        if not os.path.exists(lgetfolder):
            os.mkdir(lgetfolder)
        return lgetfolder

    def copykatanfile(self, alinfo, lgetfolder):
        if alinfo:
            allkatanafilelist = list(set(alinfo.values()))
            for katafile in allkatanafilelist:
                shutil.copy(katafile, lgetfolder)

    def Gorunfindkatna(self, nk_file, lgtpfilepath):
        lgetfolder = self.Getrlgetfolder(lgtpfilepath)
        NtKxmlpath = os.path.join(lgetfolder, "ntok_info.xml")
        alinfo = self.GetinfofromNk(nk_file)
        self.WriteLibData(NtKxmlpath, alinfo)
        self.copykatanfile(alinfo, lgetfolder)

    def proceed(self):
        try:
            if 'R3' in self.dialog.version_tag:
                return ''

            l_folder = str(self.dialog.w_publish_file.lineEdit_lseq.text())
            r_folder = str(self.dialog.w_publish_file.lineEdit_rseq.text())
            nk_file = str(self.dialog.w_publish_file.lineEdit_nk.text())
            lossy_exr = re.sub('/L','/lossy_exr',l_folder)

            self.publish_file_data = [l_folder, r_folder, nk_file]

            publish_exr = self.dialog.version_dir+'/exr'
            publish_exr_L = self.dialog.version_dir+'/exr/L'
            publish_exr_R = self.dialog.version_dir+'/exr/R'
            publish_jpg_L = self.dialog.version_dir+'/jpg/L'
            publish_jpg_R = self.dialog.version_dir+'/jpg/R'
            publish_lossy_exr = self.dialog.version_dir+'/lossy_exr'

            # link lossless exr to publish folder
            try:
                os.makedirs(publish_exr)
            except:
                self.dialog.print_log(traceback.format_exc())

            if l_folder and self.dialog.l_seqs and os.path.isdir(publish_exr):
                make_link(l_folder, publish_exr_L)

            if r_folder and self.dialog.r_seqs and os.path.isdir(publish_exr):
                make_link(r_folder, publish_exr_R)


            # 判断项目是否是立体渲染，tgun filed : sg_no_stereo
            # true为立体
            if fsc.need_stereo(self.proj) == "True":
                # copy jpg to publish folder
                if l_folder and r_folder:
                    if os.path.isdir(publish_jpg_L):
                        shutil.rmtree(publish_jpg_L)
                    if os.path.isdir(publish_jpg_R):
                        shutil.rmtree(publish_jpg_R)
                    try:

                        shutil.copytree(re.sub('/L','/jpg_L',l_folder),publish_jpg_L)
                        shutil.copytree(re.sub('/L','/jpg_R',l_folder),publish_jpg_R)
                    except Exception as e:
                        self.dialog.print_log(str(e))
            else:#非为立体
                # copy jpg to publish folder
                if l_folder :
                    if os.path.isdir(publish_jpg_L):
                        shutil.rmtree(publish_jpg_L)

                if l_folder :
                    shutil.copytree(re.sub('/L', '/jpg_L', l_folder), publish_jpg_L)

            # copy lossy exr to publish folder
            if os.path.isdir(lossy_exr):
                try:
                    if os.path.isdir(publish_lossy_exr):
                        shutil.rmtree(publish_lossy_exr)
                    shutil.copytree(lossy_exr,publish_lossy_exr)
                except Exception, e:
                    self.dialog.print_log(str(e))
            else:
                self.dialog.print_log(u'预览用lossy exr未找到!')

            # Copy nuke file to publish version folder
            if nk_file:
                shutil.copy(nk_file, os.path.join(
                    self.dialog.version_dir, os.path.basename(nk_file)))
                # Copy related katana file to publish version folder
                try:
                    self.Gorunfindkatna(nk_file, self.dialog.version_dir)
                    self.dialog.print_log("find katnafile ok")
                except Exception, e:
                    self.dialog.print_log(str(e))
            try:
                pub_file = '/mnt/proj/trash/lgt_publish_info/' + \
                    os.path.basename(self.dialog.version_dir)+'.pub'
                with open(pub_file, 'w') as f:
                    f.writelines(self.dialog.version_dir)
            except:
                traceback.print_exc()
            return ''

        except:
            try:
                if os.path.isdir(self.dialog.version_dir):
                    shutil.rmtree(self.dialog.version_dir)
                return u'Publish 没有成功，拷贝文件出错。'+traceback.format_exc()
            except:
                return u'Publish 没有成功,试图删除版本号出错。'+traceback.format_exc()

    def get_process_name(self):
        return self.process_name

    def get_description(self):
        return self.description
