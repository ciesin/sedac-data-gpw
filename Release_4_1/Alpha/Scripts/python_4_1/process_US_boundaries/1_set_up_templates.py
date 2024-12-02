import arcpy, os
from arcpy import env

inGDB = r'F:\GPW\us_boundaries_working\usa_boundaries_hi_res.gdb'
outGDB = r'F:\GPW\us_boundaries_working\usa_boundaries_load.gdb'
template = os.path.join(outGDB,'template')

env.workspace = inGDB

fcList = arcpy.ListFeatureClasses()
fcList.sort()

for fc in fcList:
    iso = os.path.basename(fc)[:6]
    print iso

    outFD = os.path.join(outGDB,iso.upper())
    WGS84 = arcpy.SpatialReference(4326)
    arcpy.CreateFeatureDataset_management(outGDB,iso.upper(),WGS84)

    outFC = os.path.join(outFD,iso+'_admin5_boundaries_2010')
    arcpy.CopyFeatures_management(template,outFC)

    arcpy.Append_management(fc,outFC,schema_type="NO_TEST")
    print "appended"
