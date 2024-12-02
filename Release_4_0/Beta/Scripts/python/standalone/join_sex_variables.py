# multiprocess_template   

import os
import re
import multiprocessing
import arcpy
import imp, sys, datetime
# import the checkForField, checkFieldType, and validateSchema functions to a module called custom
custom = imp.load_source('custom',r'\\Dataserver0\gpw\GPW4\Beta\Scripts\python\functions\validateSchema.py')
 
def joinSexData(gdb):
    '''Worker function'''
    arcpy.env.workspace = gdb
    if os.path.basename(gdb)=="vcs.gdb":
        pass
    else:
        popFile = arcpy.ListTables("*pop_input")[0]
        POPTABLEROWS = str(arcpy.GetCount_management(popFile)[0])
        ## maybe add similar validation from validate agr script here
        sexProportions = arcpy.ListTables("*sex_variables_proportions")[0]
        estimatesFile = str(popFile).replace("_input","_estimates")
        # check if the sexProportions is already existing
        if arcpy.Exists(estimatesFile):
            print estimatesFile + " already exists"
        else:
            # first preprocess the sexFile
            # create output table
            arcpy.CopyRows_management(popFile,estimatesFile)
            print "Created " + estimatesFile
            # try to add ATOTPOPMT and ATOTPOPFT
            arcpy.AddField_management(estimatesFile,"ATOTPOPMT","LONG")
            arcpy.AddField_management(estimatesFile,"ATOTPOPFT","LONG")
            # need to also add and calculate VARID, and SPOPYEAR and SPOPLEVEL
            arcpy.AddField_management(estimatesFile,"VARID","TEXT","","",200)
            arcpy.AddField_management(estimatesFile,"SPOPYEAR","SHORT")
            arcpy.AddField_management(estimatesFile,"SPOPLEVEL","SHORT")
            # parse VARID_SOURCE to create expression and grab year
            with arcpy.da.SearchCursor(sexProportions,["VARID_SOURCE","RPOPYEAR"]) as rows:
                for row in rows:
                    VARIDSOURCE = str(row[0])
                    SPOPYEAR = int(row[1])
                    break
            # calculate level and year
            arcpy.CalculateField_management(estimatesFile,"SPOPYEAR",SPOPYEAR,"PYTHON")
            print "Calculated SPOPYEAR = " + str(SPOPYEAR)
            SPOPLEVEL = len(VARIDSOURCE.split("_"))-1
            arcpy.CalculateField_management(estimatesFile,"SPOPLEVEL",SPOPLEVEL,"PYTHON")
            print "Calcultat SPOPLEVEL = " + str(SPOPLEVEL)
            
            for varItem in VARIDSOURCE.split("_"):
                if varItem == VARIDSOURCE.split("_")[0]:
                    expression = "!" + varItem + "!"
                else:
                    expression = expression + '+"_"+' + "!" + varItem + "!"
            print "VARID_SOURCE = " + VARIDSOURCE
            print "Expression = " + expression
            arcpy.CalculateField_management(estimatesFile,"VARID",expression,"PYTHON")
            print "Calculated VARID"
        # Make Feature Layers
        layer1 = os.path.basename(estimatesFile) + "_lyr"
        layer2 = os.path.basename(sexProportions) + "_lyr"
        try:
            addTime = datetime.datetime.now()
            joinFeature = sexProportions
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
            print "Made Feature Layers"
            arcpy.AddMessage("Made Feature Layers")
            print datetime.datetime.now() - addTime
            arcpy.AddMessage(datetime.datetime.now() - addTime)
        except:
            arcpy.GetMessages()
        # Add Join
        try:
            joinField = "VARID"
            addTime = datetime.datetime.now()
            arcpy.AddJoin_management(layer1,joinField,layer2,joinField,"KEEP_COMMON")
            print "Added Join"
            arcpy.AddMessage("Added Join")
            print datetime.datetime.now() - addTime
            arcpy.AddMessage(datetime.datetime.now() - addTime)
        except:
            print arcpy.GetMessages()
        # define fields to join
        mProp = "ATOTPOPMTPROP"
        fProp = "ATOTPOPFTPROP"
        joinVariables = [mProp,fProp]
        for joinVariable in joinVariables:
            print joinVariable
            if joinVariable == mProp:
                sField = os.path.basename(estimatesFile) + ".ATOTPOPMT"
            elif joinVariable == fProp:
                sField = os.path.basename(estimatesFile) + ".ATOTPOPFT"
            else:
                print "There is a problem with the sField"
            try:
                addTime = datetime.datetime.now()
                expression = '!' + os.path.basename(joinFeature) + "." + joinVariable + '!*!' + os.path.basename(estimatesFile) + ".ATOTPOPBT!"
                arcpy.CalculateField_management(layer1,sField,expression,'PYTHON')
                print "Calculated " + joinVariable
                arcpy.AddMessage("Calculated " + joinVariable)
                print datetime.datetime.now() - addTime
                arcpy.AddMessage(datetime.datetime.now() - addTime)
            except:
                print arcpy.GetMessages()
        try:
            addTime = datetime.datetime.now()
            arcpy.RemoveJoin_management(layer1,os.path.basename(joinFeature))
            print "Removed temporary join"
            arcpy.Delete_management(layer1)
            arcpy.Delete_management(layer2)
            arcpy.AddMessage("Removed temporary join")
            print datetime.datetime.now() - addTime
            arcpy.AddMessage(datetime.datetime.now() - addTime)
        except:
            print arcpy.GetMessages()

#####Code to stringify UBIDs
##    if custom.checkFieldType(popFile,"UBID","String"):
##        pass
##    else:
##        validationField = "UBID"
##        tmpField = "STRING1"
##        tmpCalc = 'int(!UBID!)'
##        validationCalc = '!'+tmpField+'!' 
##        try:
##            arcpy.AddField_management(popFile,tmpField,"TEXT","","",255)
##            arcpy.CalculateField_management(popFile,tmpField,tmpCalc,"PYTHON")
##        except:
##            sys.exit("The calculation failed")
##        try:
##            arcpy.DeleteField_management(popFile,validationField)
##            arcpy.AddField_management(popFile,validationField,"TEXT","","",255)
##            arcpy.CalculateField_management(popFile,validationField,validationCalc,"PYTHON")
##            arcpy.DeleteField_management(popFile,tmpField)
##        except:
##            arcpy.GetMessages()
##        print "Corrected " + popFile
 
# End update_shapefiles
def main():
    ''' Create a pool class and run the jobs.'''
    # The number of jobs is equal to the number of shapefiles
    workspace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs'
    usaSpace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\usa\tiles'
    braSpace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\bra\tiles'
    canSpace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\can\tiles'
    grlSpace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\grl\tiles'
    rusSpace = r'\\dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\rus\tiles'
    workspaces = [workspace]#,usaSpace,braSpace,canSpace,grlSpace,rusSpace]
    gdb_list = []
    for ws in workspaces:
        arcpy.env.workspace = ws
        gdbs = arcpy.ListWorkspaces('ecu*',"FILEGDB")
        gdbs.sort()
        gdb_temp = [os.path.join(ws, gdb) for gdb in gdbs]
        for gdbt in gdb_temp:
            gdb_list.append(gdbt) 
    for gdbItem in gdb_list:
        #print gdbItem
        joinSexData(gdb)
##    pool = multiprocessing.Pool(processes=30,maxtasksperchild=1)
##    pool.map(joinSexData, gdb_list)
## 
##    # Synchronize the main process with the job processes to
##    # ensure proper cleanup.
##    pool.close()
##    pool.join()
##    # End main
 
if __name__ == '__main__':
    main()
