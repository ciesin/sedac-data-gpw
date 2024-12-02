# Kytt MacManus
# July 8, 2014

# Import Libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()
# Define Workspace Variable
workspace = r'E:\gpw\usa_state_v2\states'
outGDB = r'E:\gpw\usa_state_v2\usa_state_tiles.gdb'
# Assign workspace environment for ArcPy
arcpy.env.workspace = workspace

# List GDBs in workspace environment
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()

# iterate
for gdb in gdbs:
    arcpy.env.workspace = gdb
    COUNTRYCODE = os.path.basename(gdb)[:-4]    
    fcs = arcpy.ListFeatureClasses("*gridding")
    if len(fcs)==0:
        print gdb + " is missing the input gridding boundaries"
    else:
        for fc in fcs:
            outFC = outGDB + os.sep + os.path.basename(fc)
            try:
                copyTime = datetime.datetime.now()
                arcpy.CopyFeatures_management(fc,outFC)
                print "copied " + outFC
                print datetime.datetime.now() - copyTime
            except:
                print arcpy.GetMessages()



                

    
    
print datetime.datetime.now() - startTime
