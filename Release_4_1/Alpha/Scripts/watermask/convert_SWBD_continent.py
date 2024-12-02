import arcpy, os
from arcpy import env

eFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\InputData\GlobalBoundaries\WATER MASK\SWBD_2_1\unzipped\east'
wFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\InputData\GlobalBoundaries\WATER MASK\SWBD_2_1\unzipped\west'
outFolder = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\InputData\GlobalBoundaries\WATER MASK\SWBD_2_1\merged'
outa = os.path.join(outFolder,'SWBD_Australia.gdb')
oute = os.path.join(outFolder,'SWBD_Eurasia.gdb')
outf = os.path.join(outFolder,'SWBD_Africa.gdb')
outi = os.path.join(outFolder,'SWBD_Islands.gdb')
outn = os.path.join(outFolder,'SWBD_NAmerica.gdb')
outs = os.path.join(outFolder,'SWBD_SAmerica.gdb')

env.workspace = wFolder

fca = arcpy.ListFeatureClasses("*a.shp")
fce = arcpy.ListFeatureClasses("*e.shp")
fcf = arcpy.ListFeatureClasses("*f.shp")
fci = arcpy.ListFeatureClasses("*i.shp")
fcn = arcpy.ListFeatureClasses("*n.shp")
fcs = arcpy.ListFeatureClasses("*s.shp")

if len(fca) > 0:
    arcpy.FeatureClassToGeodatabase_conversion(fca,outa)
    print "finished australia"
if len(fce) > 0:
    arcpy.FeatureClassToGeodatabase_conversion(fce,oute)
    print "finished eurasia"
if len(fcf) > 0:
    arcpy.FeatureClassToGeodatabase_conversion(fcf,outf)
    print "finished africa"
if len(fci) > 0:
    arcpy.FeatureClassToGeodatabase_conversion(fci,outi)
    print "finished islands"
if len(fcn) > 0:
    arcpy.FeatureClassToGeodatabase_conversion(fcn,outn)
    print "finished north america"
if len(fcs) > 0:
    arcpy.FeatureClassToGeodatabase_conversion(fcs,outs)
    print "finished south america"

