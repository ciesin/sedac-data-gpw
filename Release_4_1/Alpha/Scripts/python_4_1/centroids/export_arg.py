#Jane Mills
#3/29/2017
#Export everything to csv and shapefile
#correct iso codes we changed

# Import Libraries
import arcpy, os, csv, osgeo
from osgeo import ogr

inDriver = ogr.GetDriverByName("ESRI Shapefile")
outDriver = ogr.GetDriverByName("GPKG")

root = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\centroids'
fc = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb\arg_centroids'
iso = 'arg'
csvFolder = os.path.join(root,'csv')
gpkgFolder = os.path.join(root,'gpkg')

headers = ['GUBID','ISOALPHA','COUNTRYNM','NAME1','NAME2','NAME3','NAME4','NAME5','NAME6',
           'CENTROID_X','CENTROID_Y','INSIDE_X','INSIDE_Y','CONTEXT','CONTEXT_NM','WATER_CODE',
           'TOTAL_A_KM','WATER_A_KM','LAND_A_KM','UN_2000_E','UN_2005_E','UN_2010_E','UN_2015_E',
           'UN_2020_E','UN_2000_DS','UN_2005_DS','UN_2010_DS','UN_2015_DS','UN_2020_DS','B_2010_E',
           'F_2010_E','M_2010_E','A00_04B','A05_09B','A10_14B','A15_19B','A20_24B','A25_29B',
           'A30_34B','A35_39B','A40_44B','A45_49B','A50_54B','A55_59B','A60_64B','A65PLUSB','A65_69B',
           'A70PLUSB','A70_74B','A75PLUSB','A75_79B','A80PLUSB','A80_84B','A85PLUSB','A00_04F',
           'A05_09F','A10_14F','A15_19F','A20_24F','A25_29F','A30_34F','A35_39F','A40_44F','A45_49F',
           'A50_54F','A55_59F','A60_64F','A65PLUSF','A65_69F','A70PLUSF','A70_74F','A75PLUSF',
           'A75_79F','A80PLUSF','A80_84F','A85PLUSF','A00_04M','A05_09M','A10_14M','A15_19M','A20_24M',
           'A25_29M','A30_34M','A35_39M','A40_44M','A45_49M','A50_54M','A55_59M','A60_64M','A65PLUSM',
           'A65_69M','A70PLUSM','A70_74M','A75PLUSM','A75_79M','A80PLUSM','A80_84M','A85PLUSM']

#Save as csv
outcsv = os.path.join(csvFolder,iso+'_centroids.csv')
csvMem = csv.writer(open(outcsv,"wb"))
csvMem.writerow(headers)
with arcpy.da.SearchCursor(fc,headers) as cursor:
    for row in cursor:
        csvMem.writerow(row)

#Save as gpkg
outFile = os.path.join(gpkgFolder,iso+'_centroids.gpkg')
inDataSource = inDriver.Open(fc,0)
outData = outDriver.CreateDataSource(outFile)
arcpy.FeatureClassToFeatureClass_conversion(fc,outFile,iso+"_centroids")


print 'done'

