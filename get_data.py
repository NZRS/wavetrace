'''Parses the DEM data, and grabs each zip file from the web page'''
import httplib2
import urllib
import os
import sys

from BeautifulSoup import BeautifulSoup, SoupStrainer

counter = 0


try:
    # query_url = 'http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/Australia/'
    query_url = 'http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/Islands/'
    
    http = httplib2.Http()
    status, response = http.request(query_url)
    
    
    for link in BeautifulSoup(response, parseOnlyThese=SoupStrainer('a')):
        try:
            if link.has_key('href'):
                suffix = link['href']
                # The following allows you to limit to a region by setting lat/long
                if (int(suffix[1:3]) > 34) and (int(suffix[-11:-8]) > 160) == True:
                    urllib.urlretrieve(query_url + "/" + suffix, filename =  suffix )
                    print 'Success with: ' + suffix
                    counter = counter + 1
        except:
            countinue
except:            
    print 'Could not acquire data'
    sys.exit()
    

    print str(counter) + ' files downloaded successfully'
except:
    print 'Could not download data'
    


#unzip all dowloaded files
print 'Unzipping downloaded files'
unzip_str = 'unzip "*.zip"'
os.system(unzip_str)

print 'Files unzipped'

print 'Removing zip files'
zipbgone  = 'rm *.zip'
print 'Zip files removed'

#Convert the DEM data (.hgt) into a format SPLAT! can use (SDF).
print 'Converting DEM data'

convert_dem = 'for f in *.hgt ; do srtm2sdf "$f" ; done'
os.system(convert_dem)

print 'DEM data converted to SDF'

print 'Removing zip files'
