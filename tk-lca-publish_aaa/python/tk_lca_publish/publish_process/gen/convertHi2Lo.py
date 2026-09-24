# -*- coding:utf-8 -*-
import os

class ConvertHi2Lo():
    def __init__(self, inputfile, outputfile='', overwrite=False):

        self.input = self.osPathConvert(inputfile)
        if os.path.dirname(self.input).endswith('/res_lo'):
            self.input = os.path.dirname(self.input)[:-7] + '/' + os.path.basename(self.input)

        if overwrite:
            self.output = self.input
        else:
            self.output = self.osPathConvert(outputfile)
            if self.output == '':
                self.output = os.path.dirname(self.input) + '/res_lo/' + os.path.basename(self.input)

        if not os.path.isfile(self.input):
            raise Exception('File does not exists: '+str(self.input))

    def osPathConvert(self, path):
        path = path.replace('\\', '/')
        if os.name == 'posix':
            return path.replace('Z:/', '/mnt/proj/')
        elif os.name == 'nt':
            return path.replace('/mnt/proj/', 'Z:/')
        else:
            return path.replace('/mnt/proj/', 'Z:/')

    def convert(self):
        contents = []
        with open(self.input, 'r') as f:
            for line in f:
                contents.append(line)
        # there is no need to close f with this syntax

        for i in range(len(contents)):
            if contents[i].startswith('file '):
                buffer = contents[i].split(' ')
                ref = ''
                index = 0
                for j in range(len(buffer)):
                    if buffer[j] == '-rfn':
                        try:
                            ref = buffer[j+2]
                            index = j+2
                            break
                        except:
                            ref = ''
                            print 'Failed to find -rfn option in '+contents[i]
                            break
                if ref:
                    pathBuffer = ref.split('"')
                    if len(pathBuffer)>2 and pathBuffer[1].endswith('.ma'):
                        pathBuffer[1] = pathBuffer[1].replace('\\', '/')
                        if os.path.dirname(pathBuffer[1]).endswith('/res_lo'):
                            # it's already low resolution
                            continue
                        if '/rig/' in os.path.dirname(pathBuffer[1]):
                            # we don't replace rig asset currently
                            # TODO: delete this condition until we find solution for switching between hi and lo of rig
                            continue
                        pathBuffer[1] = os.path.dirname(pathBuffer[1]) + '/res_lo/' + os.path.basename(pathBuffer[1])
                        if not os.path.isfile( pathBuffer[1] ):
                            print 'Failed to find low res file at path: ' + pathBuffer[1] + ', ignored.'
                            continue
                    ref = '"'.join(pathBuffer)
                    try:
                        buffer[index] = ref
                        contents[i] = ' '.join(buffer)
                    except:
                        print 'Failed to overwrite line: '+contents[i]

        if not os.path.isdir(os.path.dirname(self.output)):
            os.makedirs(os.path.dirname(self.output), mode=0777)

        file_handle = open(self.output, 'w')
        file_handle.writelines(contents)
        file_handle.close()



