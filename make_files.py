import sys
import csv


def usage():
    print '''
    make_files.py <csv file>
    Lorem ipsum
    '''


'''field_list =[bearing,
antenna_height,
site_name,
polarisation,
power_eirp,
longitude,
downtilt,
vertical_beamwidth,
frequency_mhz,
latitude,
network_name,
horizontal_beamwidth,
]
'''

parameter_list = []

print 'Executing.... ' + sys.argv[0]

if len(sys.argv) == 1:
    print '''
    Parameters lacking'''
    usage()
if '.csv' not in sys.argv[1]:
    print '''
    This does not appear to be a csv file
    '''
    usage()


my_file = sys.argv[1]


reader = csv.DictReader(open(my_file, 'rU'))

for row in reader:
    parameter_list.append(row)


for thing in parameter_list:
    inner_dict = thing

#qth file
    base_filename = inner_dict['network_name'].replace(' ', '') + '_' + inner_dict['site_name'].replace(' ', '')

    lat = inner_dict['latitude']
    lng = '-' + inner_dict['longitude']
    height = inner_dict['antenna_height'] + ' meters'

    f = file(base_filename + '.qth' , 'w')
    print >> f, base_filename
    print >> f, lat
    print >> f, lng
    print >> f, height

    f.close()

#lrp file

    f = file(base_filename + '.lrp', 'w')

    if inner_dict['polarisation'].upper() == 'H':
        pol = '1'
    else:
        pol = '0'


    print >> f, '''15.000 ; Earth Dielectric Constant (Relative permittivity)
0.005 ; Earth Conductivity (Siemens per meter)
301.000 ; Atmospheric Bending Constant (N-units)
'''+ inner_dict['frequency_mhz'] + ''' ; Frequency in MHz (20 MHz to 20 GHz)
6 ;  Maritime Temperate, over land (UK and west coasts of US & EU)
''' + pol + ''' ; Polarization (0 = Horizontal, 1 = Vertical)
0.5 ; Fraction of situations (50% of locations)
0.5 ; Fraction of time (50% of the time)
''' + inner_dict['power_eirp'] + ''' ; ERP in watts'''

    f.close()

    try:
    #create .az file
        bearing = float(inner_dict['bearing'])
        beam = float(inner_dict['horizontal_beamwidth'])

        left = int(round(360 - (beam/2)))
        right = int(round(0 + (beam/2)))


        pattern_dict = {}
        for x in range(0,360):
            normal = 0.1
            if left <= x or x <= right:
                normal = 0.9
            pattern_dict[x] = float(normal)

        f = file(base_filename + '.az', 'w')
        print >> f, bearing
        for k,v in pattern_dict.iteritems():
            print >> f, str(k) + '   ' + str(v)
        f.close()
    except:
        f = file(base_filename + '.az', 'w')
        print >> f, '0    0'
        f.close()

    try:
        #cretae .el file

        f = file(base_filename + '.el', 'w')
        print >> f, str(inner_dict['downtilt'])+ '\t' + str(bearing)
        counter = 0
        for x in range(-10,91):
            if counter < int(inner_dict['vertical_beamwidth']):
                print >> f, str(x) + '\t' + '0.9'
            else:
                print >> f, str(x) + '\t' + '0.1'
            counter += 1
        f.close()
    except:
        f = file(base_filename + '.el', 'w')
        print >> f, '0    0'
        f.close()


f.close()
