
# Author: chris guest
# run splat script for QTH files in current dir starting with specified prefix.
import sys
import create_output
import os
import glob

receive_sensitivity = '-110'


if len(sys.argv) == 2:
    if int(sys.argv[1]) < 0:
        receive_sensitivity = str(sys.argv[1])

print 'modelling with a receive sensitivity of: ' + receive_sensitivity + ' dBm'


myglob = '*.qth'
#if len(sys.argv)>1:
#    myglob = sys.argv[1] + myglob

i=0
for filename in glob.glob('*.qth'):
    stub = filename[:-4]
    create_output.create(stub, receive_sensitivity)
    i+=1
    if i>300:
        break

print '%d files generated.' % i

create_output.convert_kml_to_world()

myglob = 'img/*.png'
if len(sys.argv)>1:
    myglob = sys.argv[1] + myglob
i=0
for filename in glob.glob('img/*.png'):
    stub = filename[:-4]
    create_output.convert(stub, receive_sensitivity)
    i+=1
    if i>300:
        break

print '%d files generated.' % i
