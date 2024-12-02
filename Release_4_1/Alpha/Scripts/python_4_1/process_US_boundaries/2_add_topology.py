import arcpy, os
from arcpy import env

inGDB = r'F:\GPW\us_boundaries_working\usa_boundaries_load.gdb'

env.workspace = inGDB

fdList = arcpy.ListDatasets()
fdList.sort()

for fd in fdList:
    fdPath = os.path.join(inGDB,fd)
    iso = os.path.basename(fd)
    print iso
    env.workspace = fdPath
    fc = arcpy.ListFeatureClasses()[0]

    topo = os.path.join(fdPath,iso+'_Topology')
    arcpy.CreateTopology_management(fdPath,iso+'_Topology')
    
    arcpy.AddFeatureClassToTopology_management(topo,fc)
    arcpy.AddRuleToTopology_management(topo,'Must Not Overlap (Area)',fc)
    arcpy.ValidateTopology_management(topo)

    print "set up topology"

    
