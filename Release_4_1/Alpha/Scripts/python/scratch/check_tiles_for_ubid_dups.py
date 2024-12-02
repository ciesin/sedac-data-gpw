import arcpy, os

wildcards = ["bra*","can*","grl*","rus*"]
for wildcard in wildcards:
    print wildcard
    arcpy.env.workspace = inWS = r'D:\gpw\stage\pop_tables'
    ubids = {}
    gdbs = arcpy.ListWorkspaces(wildcard,"FILEGDB")
    for gdb in gdbs:
        arcpy.env.workspace = gdb
        intersectedFishnet = arcpy.ListFeatureClasses("*_gridding")[0]
        with arcpy.da.SearchCursor(intersectedFishnet,["UBID"]) as rows:
            for row in rows:
                ubid = row[0]
                if ubid in ubids:
                    print "Duplicate ubid: " + ubid
                else:
                    ubids[ubid]=1

    print len(ubids)
    
