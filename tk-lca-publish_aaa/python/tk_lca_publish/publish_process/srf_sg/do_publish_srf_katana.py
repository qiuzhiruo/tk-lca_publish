__author__ = 'yingjie'

#call this script in terminal
import os
import sys

import srf_publish_tools.scan_publish as ssk
reload(ssk)

def publish_srf_katana():
    if len(sys.argv)>=5:
        sk = ssk.SrfKatana(publish_to=sys.argv[-4],
                                    katana_file=sys.argv[-3],
                                    xgen_archive=sys.argv[-2],
                                    preview_file=sys.argv[-1])
        sk.do_publish()

publish_srf_katana()
