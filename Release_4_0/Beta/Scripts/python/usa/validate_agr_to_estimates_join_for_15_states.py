import arcpy, os, csv

##attributes = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\validate\agr_to_table_validation_usa_dirty_states.csv'
### open csv file and write header
##csvFile = csv.writer(open(attributes,'wb'))
##csvFile.writerow(("ISO","POPTABLEROWS","AGRROWS", "AGRTOPOPROWS"))
#"usa_nd",
isoList = ["usa_ri","usa_mt","usa_nc",
               "usa_ne","usa_nh","usa_nj",
               "usa_nm","usa_nv","usa_ny",
               "usa_oh","usa_ok","usa_og",
               "usa_pa","usa_sc","usa_akeast","usa_akwestse","usa_akwestsw","usa_akwestne","usa_akwestnw"]#"
for t in isoList:
    arcpy.env.workspace = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\usa\tiles'
    gdbs = arcpy.ListWorkspaces("*"+t+"*","FILEGDB")
    gdbs.sort()
    for gdb in gdbs:
        iso = os.path.basename(gdb)[:-4].upper()
        print iso
        # get popFile
        arcpy.env.workspace = gdb
        popFile = gdb + os.sep + str(arcpy.ListTables("*pop_input")[0])
        estimatesFile = popFile.replace("_input","_estimates")
        arcpy.CopyRows_management(popFile,estimatesFile)
        POPTABLEROWS = str(arcpy.GetCount_management(popFile)[0])
    ##    print popFile
    ##    print POPTABLEROWS
        #arcpy.env.workspace = r'\\Dataserver0\gpw\GPW4\Beta\GrowthRate\country_tables_beta.gdb'
        agrFile = r'\\Dataserver0\gpw\GPW4\Beta\GrowthRate\country_tables_beta.gdb\USA_growth_rate_admin2_2000_2010'
        AGRROWS = str(arcpy.GetCount_management(agrFile)[0])
    ##    print boundaryFile
    ##    print BOUNDARYROWS
        # add join boundary to file
        # Make Feature Layers
        layer1 = os.path.basename(estimatesFile) + "_lyr"
        layer2 = os.path.basename(agrFile) + "_lyr"
        try:
            joinFeature = agrFile
            if not arcpy.Exists(layer1):
                try:
                    arcpy.MakeFeatureLayer_management(estimatesFile,layer1)
                except:
                    arcpy.MakeTableView_management(estimatesFile,layer1)
            if not arcpy.Exists(layer2):
                try:
                    arcpy.MakeFeatureLayer_management(joinFeature,layer2)
                except:
                    arcpy.MakeTableView_management(joinFeature,layer2)
    ##        print "Made Feature Layers"
            
        except:
            arcpy.GetMessages()

        # parse AGRID
        # create search cursor in order to determine agrid_source
        searchCursor = arcpy.SearchCursor(agrFile)
        searchCount = 0
        searchRow = searchCursor.next()
        while searchCount == 0:
            agrid_source = searchRow.getValue('agrid_source')
            searchCount = 1
        del searchRow
        del searchCursor

        # parse agrid first
        # need to handle complex agrid_source (e.g. UCADMIN1_UCADMIN2_UCADMIN3)
        agridSplit = agrid_source.split('_')
        # parse agrid expression
        if len(agridSplit)==1:
            agridExp = '!' + agridSplit[0] + '!'
        else:
            agridFields = iter(agridSplit)
            next(agridFields)
            agridExp = '!' + agridSplit[0] + '!'
            for expField in agridFields:
                agridExp = agridExp + ' + ' + '"' + '_' + '" ' + '+ ' + '!' + expField + '!'
        # add and calculate agrid
        arcpy.AddField_management(estimatesFile,"AGRID","TEXT","","",200)
        arcpy.CalculateField_management(estimatesFile, "AGRID", agridExp,"PYTHON")

        try:
            joinField = "AGRID"
            AGRTOPOPROWS = str(arcpy.GetCount_management(arcpy.AddJoin_management(layer1,joinField,layer2,joinField,"KEEP_COMMON"))[0])

            arcpy.RemoveJoin_management(layer1,os.path.basename(joinFeature))
        except:
            print arcpy.GetMessages()

        
    ##    popExpression = '"POP_CONTEXT" IS NOT NULL'
    ##    boundaryExpression = '"BOUNDARY_CONTEXT" IS NOT NULL'
    ##    POPCONTEXTROWS = str(arcpy.GetCount_management(arcpy.MakeTableView_management(popFile,iso+"_pop",popExpression))[0])
    ##    BOUNDARYCONTEXTROWS = str(arcpy.GetCount_management(arcpy.MakeFeatureLayer_management(boundaryFile,iso+"_boundary",boundaryExpression))[0])
    ##    print POPCONTEXTROWS
    ##    print BOUNDARYCONTEXTROWS
##        print iso,POPTABLEROWS,AGRROWS, AGRTOPOPROWS
##        csvFile.writerow((iso,POPTABLEROWS,AGRROWS, AGRTOPOPROWS))
##
##    del csvFile
