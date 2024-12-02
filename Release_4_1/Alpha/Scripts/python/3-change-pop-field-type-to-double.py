# some of the raw input data was calculated and contains decimals
# in the beta release these numbers were converted to integer
# but it was found that this had a major effect on the calculation of sex ratios
# therefore, for the production release we are processing these data type double
# this script modifies the input tables to store pop data as type double

# 2-9-2016
# Kytt MacManus

# import libraries
import arcpy, os

# define input and output directories
inWS = r'F:\usa\names'

# create dictionaries for table selection
keys = ["total_pop","sex_pop"]
inputs = {"total_pop":"*total_pop_input","sex_pop":"*sex_variables_input"}
raws = {"total_pop":"*total_pop_raw","sex_pop":"*sex_variables_raw"}

# define lists of fields to modify
inputFields = ["ATOTPOPBT"]
sexFields = ["ATOTPOPBT","ATOTPOPMT","ATOTPOPFT"]

# list workspaces
arcpy.env.workspace = inWS
workspaces = arcpy.ListWorkspaces("*")
workspaces.sort(reverse=True)
for workspace in workspaces:
    print "processing " + os.path.basename(workspace)
    # describe the workspace
    workDesc = arcpy.Describe(workspace)
    # if it is "BRA, CAN, GRL, RUS, or USA" then it is nested in subfolder
    if str(workDesc.workspaceType)=="FileSystem":
        workspace = workspace + os.sep + os.path.basename(workspace)+".gdb"
    arcpy.env.workspace = workspace
    for key in keys:   
        # first grab the pop table
        try:
            popInput = arcpy.ListTables(inputs[key])[0]
        except:
            print "The total pop table is missing for " + workspace
            break
        # next grab the raw table
        try:
            popRaw = arcpy.ListTables(raws[key])[0]
        except:
            print "The raw pop table is missing for " + workspace
            break
        # add USCIDT to both the tables
        # check if USCID exist
        if len(arcpy.ListFields(popInput,"USCID"))==0:
            calcFld = "!VARID!"
            if len(arcpy.ListFields(popInput,"VARID"))==0:
                print "missing USCID and VARID"
                break
        else:
            calcFld = "!USCID!"
        arcpy.AddField_management(popInput,"USCIDT","TEXT")
        arcpy.CalculateField_management(popInput,"USCIDT",calcFld,"PYTHON")
        arcpy.AddField_management(popRaw,"USCIDT","TEXT")
        arcpy.CalculateField_management(popRaw,"USCIDT",calcFld,"PYTHON")
##        print "Added USCIDS"
        # select fieldList
        if key == "total_pop":
            fieldList = inputFields
        else:
            fieldList = sexFields                
        # iterate fields
        for field in fieldList:
              # delete the field from the input table
              arcpy.DeleteField_management(popInput,field)
              # add new field type double
              arcpy.AddField_management(popInput,field,"DOUBLE")
##              print "Deleted " + field
        # validate the join
        # create tables views
        layer1 = os.path.basename(popInput) + "_view"
        layer2 = os.path.basename(popRaw) + "_view"
        arcpy.MakeTableView_management(popInput,layer1)
        arcpy.MakeTableView_management(popRaw,layer2)
        origRows = int(arcpy.GetCount_management(popInput)[0])
        joinRows = int(arcpy.GetCount_management(arcpy.AddJoin_management
                                                 (layer1,"USCIDT",layer2,"USCIDT","KEEP_COMMON"))[0])
        if joinRows < origRows:
            print "Join Problem, Check " + os.path.basename(workspace) 
        else:            
            # iterate fields
            for field in fieldList:
                expression = '!' + os.path.basename(popRaw) + "." + field + '!'
                arcpy.CalculateField_management(layer1,os.path.basename(popInput) + "." + field,expression,'PYTHON')       
            print "Joined Fields"
            arcpy.RemoveJoin_management(layer1,os.path.basename(popRaw))
            # check for zeros and remove if needed
            vTable = os.path.basename(popInput) + "_" + field
            vExpression = '"'+field+'" <0'
            if int(arcpy.GetCount_management(arcpy.MakeTableView_management(popInput,vTable,vExpression))[0])>0:
                arcpy.CalculateField_management(vTable,field,0,"PYTHON")
                print "Updated " + field
            
            # finally clean up the "USCIDT" fields
            arcpy.DeleteField_management(popInput,"USCIDT")
            arcpy.DeleteField_management(popRaw,"USCIDT")
            
            
