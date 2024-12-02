import arcpy, os

inGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Country\USA\Ingest\Boundary\3_dissolved_coastlines.gdb'
arcpy.env.workspace = inGDB

hydro = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Global\Water\working\usa\usa_working.gdb\usa_hydrography'
outGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Preprocessing\Global\Water\working\usa\hydrography.gdb'

fcList = arcpy.ListFeatureClasses()
fcList.sort()

for fc in fcList:
    print fc

    outFC = os.path.join(outGDB,fc[:6]+"_hydrography")
    arcpy.Clip_analysis(hydro,fc,outFC)


