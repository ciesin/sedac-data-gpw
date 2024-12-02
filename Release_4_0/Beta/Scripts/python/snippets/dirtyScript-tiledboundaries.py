# quick dirty script to copy data from alpha gdbs
# not sure if some of the code will be reusable
# retain .py just in case
# sorry for the dirtyness!

import arcpy, os

outFolder = r'G:\gpw\tiled_countries\shps'
# The number of jobs is equal to the number of shapefiles
usaSpace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\usa\tiles'
braSpace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\bra\tiles'
canSpace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\can\tiles'
grlSpace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\grl\tiles'
rusSpace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\rus\tiles'
workspaces = [braSpace,canSpace,grlSpace,rusSpace]
gdb_list = []
for ws in workspaces:
    arcpy.env.workspace = ws
    gdbs = arcpy.ListWorkspaces('*',"FILEGDB")
    gdbs.sort()
    gdb_temp = [os.path.join(ws, gdb) for gdb in gdbs]
    for gdbt in gdb_temp:
        gdb_list.append(gdbt) 
for gdbItem in gdb_list:
    fileString = os.path.basename(gdbItem)[:-4]
    iso = os.path.basename(gdbItem)[:3].upper()
    if iso == "BRA":
        isoNUM = 76
    elif iso == "CAN":
        isoNUM = 124
    elif iso == "GRL":
        isoNUM = 304
    elif iso == "RUS":
        isoNUM = 643
    else:
        sys.exit("The iso is broken" + iso)
    arcpy.env.workspace = gdbItem
    boundaryFile = arcpy.ListFeatureClasses("*boundaries*")[0]
    outFile = outFolder + os.sep + fileString + "_tile.shp"
    arcpy.Dissolve_management(boundaryFile, outFile)
    arcpy.AddField_management(outFile,"ISO","TEXT")
    arcpy.AddField_management(outFile,"ISONUM","SHORT")
    arcpy.CalculateField_management(outFile,"ISO",'"'+iso+'"',"PYTHON")
    arcpy.CalculateField_management(outFile,"ISONUM",isoNUM,"PYTHON")
    print "Created " + outFile
        
    
