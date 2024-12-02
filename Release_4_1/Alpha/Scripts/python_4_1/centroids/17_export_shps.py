#Jane Mills
#3/29/2017
#Export everything to csv and shapefile
#correct iso codes we changed

# Import Libraries
import arcpy, os, csv

root = r'D:\gpw\release_4_1\centroids'
centroids = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids_data\country_data.gdb'
template = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids_data\ancillary.gdb\template'
shpFolder = os.path.join(root,'shp')

arcpy.env.workspace = centroids
fcList = arcpy.ListFeatureClasses()
fcList.sort()

for fc in fcList:
    if fc[:3] == 'usa':
        iso = fc[:5]
        if fc[:5] == 'usaii':
            iso = 'usain'
        elif fc[:5] == 'usaog':
            iso = 'usaor'
        else:
            iso == fc[:-10]
    else:
        iso = fc[:3]
        if fc[:3] == 'anr':
            iso = 'and'
        elif fc[:3] == 'vcs':
            iso = 'vat'
        else:
            iso == fc[:-10]
    print iso

    if fc == 'usatx_centroids':
        pass
    else:
        #Save as shp
        outFC = os.path.join(shpFolder,iso+'_centroids.shp')
        arcpy.CopyFeatures_management(template,outFC)
        arcpy.Append_management(fc,outFC,"NO_TEST")

print 'done'


