import csv
reader = csv.reader(file('abc_data.csv'), delimiter=',')
header = reader.next()
print header

# ['Area Served', 'Callsign', 'Frequency(kHz)', 'Purpose', 'Polarisation', 'Mast Height (m)', 'Antenna Pattern', 'Maximum CMF (V)', 'Transmitter Power (W)', 'Technical Specification Number', 'Licence Number', 'Site Id', 'Site Name', 'Zone', 'Easting', 'Northing', 'Latitude', 'Longitude', 'State', 'BSL', 'Licence Area', 'Licence Area ID', 'Hours of Operation', 'Status']

headerMap=dict([(h,i) for i,h in enumerate(header)])
headerMapInv=dict([(i,h) for i,h in enumerate(header)])

for row in reader:
    #print '%r' % row
    base_filename = '%s_%s' % (row[headerMap['Area Served']].replace(' ','').replace('/',''), row[headerMap['Callsign']])
    lat = '-' + row[headerMap['Latitude']].strip().replace('S','')
    lon = '-' + row[headerMap['Longitude']].strip().replace('E','')
    height = row[headerMap['Mast Height (m)']].strip() + 'm'
    g = file('%s.qth' % base_filename, 'w')
    print >> g, base_filename
    print >> g, lat
    print >> g, lon
    print >> g, height
    g.close()

    g = file('%s.lrp' % base_filename, 'w')
    print >> g, """15.000 ; Earth Dielectric Constant (Relative permittivity)
0.005 ; Earth Conductivity (Siemens per meter)
301.000 ; Atmospheric Bending Constant (N-units)
%0.3f; Frequency in MHz (20 MHz to 20 GHz)
5 ; Radio Climate (5 = Continental Temperate)
1 ; Polarization (0 = Horizontal, 1 = Vertical)
0.5 ; Fraction of situations (50%% of locations)
0.5 ; Fraction of time (50%% of the time)
""" % (float(row[headerMap['Frequency(kHz)']])/1000.0)
    g.close()
