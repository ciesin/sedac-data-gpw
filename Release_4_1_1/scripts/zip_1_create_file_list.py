#Jane Mills
#10/03/17
#zip netCDF

import os, csv

zipF = r'F:\gpw\v411\zips'

outCSV = os.path.join(zipF,"fileList.csv")
csvFile = csv.writer(open(outCSV,"w"))
csvFile.writerow(["folder","file"])

asciiF = r'F:\gpw\v411\ascii'
centroidsF = r'F:\gpw\v411\centroids'
centroids1 = os.path.join(centroidsF,'csv')
centroids2 = os.path.join(centroidsF,'global')
centroids3 = os.path.join(centroidsF,'gpkg')
centroids4 = os.path.join(centroidsF,'shp')
netcdfF = r'F:\gpw\v411\netcdf'
tifF = r'F:\gpw\v411\rasters_translate'
natid = r'\\dataserver1\gpw\GPW4\Release_411\data\national_identifier_polygons'

folders = [asciiF, centroids1, centroids2, centroids3, centroids4, netcdfF, tifF, natid]

for folder in folders:
    print(folder)
    fileList = os.listdir(folder)
    for f in fileList:
        csvFile.writerow([folder,f])
    


repo = r'\\Winserver1\Repo\gpw-v4'
outCSV = os.path.join(zipF,"repoList.csv")
csvFile = csv.writer(open(outCSV,"w"))
csvFile.writerow(["folder","zip"])

folderList = [os.path.join(repo, f) for f in os.listdir(repo) if 'rev10' in f]

for f in folderList:
    zips = os.listdir(os.path.join(f,"data"))
    
    for z in zips:
        csvFile.writerow([f,z])

    
