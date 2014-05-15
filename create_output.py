import os



splat_list = []
receive_sensitivity = '90'


def create(file_name, receive_sensitivity):

    #create ppm and KML
    #cpk = 'splat -t ' + file_name + ' -o -c 2.0 '+ file_name + '.ppm -ngs -kml -metric'
    cpk = 'splat -t ' + file_name + ' -L 8.0 -dbm -db ' + receive_sensitivity + ' -o '+ file_name + '.ppm -kml -metric -ngs'
    
    print '===================='
    print cpk
    splat_list.append(cpk)
    print '===================='
    
    #resize ppm file
    resize = 'pnmscale -xsize 1200 ' + file_name + '.ppm'

    #make opaque here


    #Convert ppm to png
    p2p = 'pnmtopng ' + file_name + '.ppm > ' + file_name + '.png'
    print p2p

    #White to transparent
    w2t = 'convert ' + file_name + '.ppm -transparent "#FFFFFF" ' + file_name + 'x.ppm'

    #replace transparent
    t2main = 'mv ' + file_name + '-0.png ' + file_name + '.png'

    #remove trans file
    #rm_trans = 'rm ' + file_name +'.png'

    #rewrite KML
    rw_kml = "sed -i 's/.ppm/.png/g' " + file_name + ".kml"






    try:
        print 'Creating coverage map'
        os.system(cpk)
        print 'Coverage map created'
    except:
        print 'Coverage map failed...'

        'Converting white to transparency failed'
    try:
        print 'Converting ppm to png'
        os.system(p2p)
        print 'Converted ppm to png'

    except:
        print 'Failed converting ppm to png'
    try:
        print 'Converting white to transparency'
        #os.system(w2t)
        print 'Converted white to transparency'
    except:
        print 'Did not convert white to transparency'
    try:
        print 'Replacing main file'
    #    os.system(t2main)
        print 'File replaced with transparency'
    except:
        print 'File not replaced'
    try:
        print 'Cleaning file'
        #os.system(rm_trans)
        print 'File cleaned'
    except:
        print 'Cleaning file failed'

    try:
        print 'Rewriting KML'
        os.system(rw_kml)
        print 'KML rewritten'
        print 'PNG filename:' + file_name +'.png'
        print 'KML filename:' + file_name +'.kml'
    except:
        print 'Rewriting KML failed'
    
    try:
        print splat_list
    except:
        print 'failed to print splat list'



def convert(file_name):
    #convert to worldfile to GeoTIFF

    #wld2gtif = 'gdalwarp ' + file_name + '.png ' + file_name + '.tif'

    wld2gtif = 'gdal_translate -a_nodata 255 -expand gray -of GTiff ' + file_name + '.png ' + file_name + '.tif'
    print wld2gtif


    #tidy up raster

    #tidy = 'gdal_translate -of GTiff -b 1 -a_nodata 255 ' + file_name + '.tif ' + file_name + '_1.tif'

    #print tidy

    try:
        print 'Converting world file to GeoTiff'
        os.system(wld2gtif)
    except:
        print 'Conversion to GeoTiff failed'

    try:
        print 'Tidying up file'
        #os.system(tidy)
    except:
        print 'File tidy failed'



def convert_kml_to_world():
    kml2wld = 'bash kml2wld.sh .'
    try:
        os.system(kml2wld)
    except:
        print 'Creating world file failed'
        

    
