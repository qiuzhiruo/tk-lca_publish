__author__ = 'yingjie'

import sys
import os

r = nuke.nodes.Read(file = sys.argv[1])
r['on_error'].setValue(1)
w = nuke.nodes.Write(file = sys.argv[2])
w.setInput(0, r)
w['use_limit'].setValue(True)

read_name=os.path.basename(sys.argv[1])
image_formmat=read_name.split('.')[-1]
image_prefix_name=read_name.split('####')[0]
read_dir=os.path.dirname(sys.argv[1])
all_files=os.listdir(read_dir)
img_files=[]
for im in all_files:
    if im.endswith('.'+image_formmat) and im.startswith(image_prefix_name):
        img_files.append(im)
img_files=sorted(img_files)

start=int(img_files[0].split('.')[-2])
end=int(img_files[-1].split('.')[-2])
print '[Seq Range] :',start,end

w['first'].setValue(start)
w['last'].setValue(end)

if sys.argv[2].endswith('.jpg'):
    w['file_type'].setValue('jpeg')
    w['_jpeg_quality'].setValue(1)

nuke.root()['first_frame'].setValue(start)
nuke.root()['last_frame'].setValue(end)
r['first'].setValue(start)
r['last'].setValue(end)

nuke.execute(w)