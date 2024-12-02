import arcpy, os, csv

arcpy.env.workspace = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\inputs'
attributes = r'\\dataserver0\GPW\GPW4\Beta\Gridding\country\validate\table_boundary_validation_8_26_15_2.csv'
# open csv file and write header
csvFile = csv.writer(open(attributes,'wb'))
csvFile.writerow(("ISO","POPTABLEROWS","BOUNDARYROWS","POPTOBOUNDARYROWS",
                  "BOUNDARYTOPOPROWS","POPCONTEXTROWS","BOUNDARYCONTEXTROWS"))

gdbs = arcpy.ListWorkspaces("*","FILEGDB")
gdbs.sort()
for gdb in gdbs:
    iso = os.path.basename(gdb)[:-4]
    print iso
    # get popFile
    arcpy.env.workspace = gdb
    popFile = gdb + os.sep + str(arcpy.ListTables("*pop_input")[0])
    POPTABLEROWS = str(arcpy.GetCount_management(popFile)[0])
##    print popFile
##    print POPTABLEROWS
    arcpy.env.workspace = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\global\country_boundaries_hi_res.gdb'
    boundaryFile = arcpy.ListFeatureClasses(iso + "*")[0]
    BOUNDARYROWS = str(arcpy.GetCount_management(boundaryFile)[0])
##    print boundaryFile
##    print BOUNDARYROWS
    # add join boundary to file
    # Make Feature Layers
    layer1 = os.path.basename(popFile) + "_lyr"
    layer2 = os.path.basename(boundaryFile) + "_lyr"
    try:
        joinFeature = boundaryFile
        if not arcpy.Exists(layer1):
            try:
                arcpy.MakeFeatureLayer_management(popFile,layer1)
            except:
                arcpy.MakeTableView_management(popFile,layer1)
        if not arcpy.Exists(layer2):
            try:
                arcpy.MakeFeatureLayer_management(joinFeature,layer2)
            except:
                arcpy.MakeTableView_management(joinFeature,layer2)
##        print "Made Feature Layers"
        
    except:
        arcpy.GetMessages()
    try:
        joinField = "UBID"
        POPTOBOUNDARYROWS = str(arcpy.GetCount_management(arcpy.AddJoin_management(layer1,joinField,layer2,joinField,"KEEP_COMMON"))[0])
##        print "Added Join"
##        print POPTOBOUNDARYROWS
        arcpy.RemoveJoin_management(layer1,os.path.basename(joinFeature))
        BOUNDARYTOPOPROWS = str(arcpy.GetCount_management(arcpy.AddJoin_management(layer2,joinField,layer1,joinField,"KEEP_COMMON"))[0])
##        print "Added Join"
##        print BOUNDARYTOPOPROWS
        arcpy.RemoveJoin_management(layer2,os.path.basename(popFile))   
    except:
        print arcpy.GetMessages()

    popExpression = '"POP_CONTEXT" IS NOT NULL'
    boundaryExpression = '"BOUNDARY_CONTEXT" IS NOT NULL'
    POPCONTEXTROWS = str(arcpy.GetCount_management(arcpy.MakeTableView_management(popFile,iso+"_pop",popExpression))[0])
    BOUNDARYCONTEXTROWS = str(arcpy.GetCount_management(arcpy.MakeFeatureLayer_management(boundaryFile,iso+"_boundary",boundaryExpression))[0])
##    print POPCONTEXTROWS
##    print BOUNDARYCONTEXTROWS
    print iso,POPTABLEROWS,BOUNDARYROWS,POPTOBOUNDARYROWS,BOUNDARYTOPOPROWS,POPCONTEXTROWS,BOUNDARYCONTEXTROWS
    csvFile.writerow((iso,POPTABLEROWS,BOUNDARYROWS,POPTOBOUNDARYROWS,
                  BOUNDARYTOPOPROWS,POPCONTEXTROWS,BOUNDARYCONTEXTROWS))

del csvFile
