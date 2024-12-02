import arcpy, os

inWS = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\country_boundaries_hi_res.gdb'
outWS = r'D:\gpw\release_4_1\water\water_inputs\boundary_water_features_v2'

arcpy.env.workspace = inWS
fcs = arcpy.ListFeatureClasses("*")
fcs.sort()

isos = ['aut','bgr','bih','bra','che','cod','deu','egy','fra','hrv','hun','irl','kos',
        'moz','mys','nam','prt','rou','srb','svn','twn','ven','zaf','zmb','zwe']

for fc in fcs:
    if fc[:3] in isos:
        fcPath = os.path.join(inWS, fc)
        iso = fc[:3]
        print iso
        outFC = os.path.join(outWS,iso+"_water_features.shp")

        arcpy.FeatureClassToFeatureClass_conversion(fcPath,outWS,iso+"_water_features.shp","BOUNDARY_CONTEXT = 7")

        if int(arcpy.GetCount_management(outFC)[0])==0:
            arcpy.Delete_management(outFC)



