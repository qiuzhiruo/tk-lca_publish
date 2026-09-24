# -*- coding:utf-8 -*-
__author__ = 'john'

"""
 finalize the ass archive.
 * change the 'pgYetiArnold.so' to include version info
 * change the .fur pass from output path to publish path
"""
import gzip
import sys, re, traceback
import production.CacheUtils.AssBatcher as ab

def changeFurPath(data, parms):
    """
    change the fur path from output path to publish path
    @param parms: 'dest' = the dest path to move to;
    """
    exp = r'.*filename ".*/cfx/output/.*\.fur".*'
    findexp = r'".*/cfx/output/'
    for line_num in xrange(len(data)):
        line = data[line_num]
        if re.match(exp, line):
            #orig_root = re.search(findexp, line).group(0)[1:]
            #if not orig_root:
            #    return line
            sub_path = line.split('/cfx/output/')[1]    # ends with "

            dest_root = parms['dest']

            # use the filename from subpath instead of from parms
            dest_path_tokens = dest_root.rstrip('/').split('/')
            if len(dest_path_tokens)<2:
                raise dest_path_tokens+' is not valid as version_dir'

            dest_root = '/'.join(dest_path_tokens[:-1])
            path = dest_root+'/'+sub_path
            data[line_num] = re.sub('".*\.fur"', '"' + path, line)


# All publish process will use StdProcess as the class name.
class StdProcess():

    def __init__(self, dialog):
        self.dialog = dialog
        self.process_name = u"修改ass序列内fur路径"
        self.description = u"目前的修改为将ass中的fur路径从output修改到publish"


    def proceed(self):
        parms={'dest':self.dialog.version_dir}
        try:
            for i in range(self.dialog.w_publish_file.listWidget_cache.count()):
                dir_path = self.dialog.w_publish_file.listWidget_cache.item(i).text()
                ab.walk(dir_path, changeFurPath, parms)

            return ""
        except:
            return traceback.format_exc()


    def get_process_name(self):
        return self.process_name


    def get_description(self):
        return self.description
