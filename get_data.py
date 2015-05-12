'''Parses the DEM data, and grabs each zip file from the web page'''
import urllib
import os
import sys
import requests
import re, getopt

from BeautifulSoup import BeautifulSoup, SoupStrainer

counter = 0

definition = 'sd'

argv = sys.argv[1:]

query_endpoints={
    'sd' : 'http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/Islands/'
    ,'hd' : 'http://e4ftl01.cr.usgs.gov/SRTM/SRTMGL1.003/2000.02.11/'
}


# sys.exit();

try:
    opts, args = getopt.getopt(argv,"h")
except getopt.GetoptError:
    print 'NO HELP HERE..'
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-h"):
        definition="hd"


print 'Fetching',definition,'elevation data'


try:

    response = requests.get(query_endpoints[definition])

    #if response.status_code = 200:

    for link in BeautifulSoup(response.text, parseOnlyThese=SoupStrainer('a')):
        try:
            if link.has_key('href') and re.compile('^[\w]+\.(|[\w0-9]+\.)hgt\.zip$').match(link['href']):
                suffix = link['href']
                degrees=re.split("N|E|S|W", suffix[0:suffix.find('.')])
                # The following allows you to limit to a region by setting lat/long
                if (int(degrees[1]) >= 34) and (int(degrees[2]) > 160):
                    urllib.urlretrieve(query_endpoints[definition] + "/" + suffix, filename =  suffix )
                    print 'Success with: ' + suffix
                    counter = counter + 1
        except:
            continue
except:
    print 'Could not acquire data'
    sys.exit()

print str(counter) + ' files downloaded successfully'




#unzip all dowloaded files
print 'Unzipping downloaded files'

try:
    unzip_str = 'unzip "*.zip"'
    os.system(unzip_str)
    print 'Files unzipped'
except:
    print 'Files could not be unzipped'



print 'Removing zip files'
try:
    zipbgone  = 'rm *.zip'
    os.system(zipbgone)
    print 'Zip files removed'
except:
    print 'Zip files not removed'

#Convert the DEM data (.hgt) into a format SPLAT! can use (SDF).
print 'Converting DEM data'

try:

    #Use srtm2sdf-hd if HD is passed in
    #srtm2sdf will automatically append the .sdf files -hd, which splat-hd knows to look for
    prog = 'srtm2sdf' if definition!='hd' else 'srtm2sdf-hd';
    convert_dem = 'for f in *.hgt ; do '+prog+' "$f" ; done'
    os.system(convert_dem)



    print 'DEM data converted to SDF'
except:
    print 'DEM data could nto be converted'

print 'Removing DEM files'
try:
    remove_dem = 'rm *.hgt'
    os.system(remove_dem)
    print 'removed DEM files'
except:
    print'failed to remove DEM files'
