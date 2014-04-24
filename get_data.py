'''Parses the DEM data, and grabs each zip file from the web page'''
import httplib2
import urllib

from BeautifulSoup import BeautifulSoup, SoupStrainer

counter = 0

# query_url = 'http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/Australia/'
query_url = 'http://dds.cr.usgs.gov/srtm/version2_1/SRTM3/Islands/'

http = httplib2.Http()
status, response = http.request(query_url)


for link in BeautifulSoup(response, parseOnlyThese=SoupStrainer('a')):
    try:
        if link.has_key('href'):
            suffix = link['href']
            # The following allows you to limit to a region by setting lat/long
            if (int(suffix[1:3]) > 34) and (int(suffix[-11:-8])> 160) == True:
                urllib.urlretrieve(query_url + "/" + suffix, filename =  suffix )
                print 'Success with: ' + suffix
                counter = counter + 1
    except:
            continue

print str(counter) + ' files downloaded successfully'
