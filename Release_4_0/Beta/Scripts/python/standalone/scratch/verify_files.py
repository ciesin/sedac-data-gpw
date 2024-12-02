import arcpy, imp, sys, os
# import the checkForField, checkFieldType, and validateSchema functions to a module called custom
custom = imp.load_source('custom',r'\\Dataserver0\gpw\GPW4\Beta\Scripts\python\functions\validateSchema.py')
 
workspace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs'
arcpy.env.workspace = workspace
gdbs = arcpy.ListWorkspaces('*')
gdbs.sort()

for gdb in gdbs:
    print "Processing " + gdb
    arcpy.env.workspace = gdb
    if os.path.basename(gdb)=="vcs.gdb":
        pass
    else:
        sexProportionTest = arcpy.ListTables("*_proportions")
        if len(sexProportionTest)== 0:
            print gdb + " is missing the table"
        else:
            # validate sex proportions
            sexProportions = sexProportionTest[0]
            #print sexProportions            
            # check for any ratios that <> 1
            # first create in memory table to check
            inMem = "in_memory" + os.sep + os.path.basename(sexProportions) + "_lyr"
            arcpy.CopyRows_management(sexProportions,inMem)
            #print "Created " + inMem
            # add a field
            arcpy.AddField_management(inMem,"PROPCHECK","DOUBLE")
            arcpy.CalculateField_management(inMem,"PROPCHECK","float(!ATOTPOPFTPROP!)+float(!ATOTPOPMTPROP!)","PYTHON")
            #print "Calculated PROPCHECK"
            # check out the field values, are any null?
            nullCondition = '"PROPCHECK"<>0 AND ("PROPCHECK"<0.95 OR "PROPCHECK">1.05)'
            nullView = os.path.basename(inMem) + "_view"
            if int(arcpy.GetCount_management(arcpy.MakeTableView_management(inMem,nullView,nullCondition))[0])>0:
                print gdb + " has proportions that do not add up to 1"
                outTable = gdb + os.sep + "bad_proportions"
                arcpy.CopyRows_management(inMem,outTable)
            else:
                print "Pass"          
            arcpy.Delete_management(inMem)
            arcpy.Delete_management(nullView)


            
##            # check for prop fields
##            propFieldTest = arcpy.ListFields(sexProportions,"*PROP")
##            if not len(propFieldTest) == 2:
##                print "The proportion fields are missing: " + str(propFieldTest)
##            else:
##                for field in propFieldTest:
##                    fldName = field.name
##                    # check out the field values, are any null?
##                    nullCondition = '"' + fldName  + '"' + ' IS NULL'
##                    nullView = sexProportions + fldName + "_null"
##                    if int(arcpy.GetCount_management(arcpy.MakeTableView_management(sexProportions,nullView,nullCondition))[0])>0:
##                        print fldName + " has null values"
##                    arcpy.Delete_management(nullView)
##                        arcpy.Delete_management(sexProportions)
                
