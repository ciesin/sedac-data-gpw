# population-estimates.py
# produce population estimates
# Kytt MacManus
# 2-11-13

# import libraries
import os, arcpy
import datetime
import multiprocessing

def unAdjust(outWS):
    rootName = os.path.basename(outWS)[:-4]
    print rootName
    # define input table
    inTable = outWS + os.sep + rootName + "_estimates"
    # define growth rate table
    inUNTable = r"\\Dataserver0\gpw\GPW4\Gridding\country\ancillary.gdb\un_adjustment_factors"
    # select appropriate row
    try:
        unTable = outWS + os.sep + rootName + "_un_adjustment"
        arcpy.TableSelect_analysis(inUNTable,unTable,'"ISO" = ' + "'" + "USA" + "'")
        arcpy.AddMessage("Created " + unTable)
    except:
        arcpy.GetMessages()
    # create backup of inTable
    try:
        backupTable = outWS + os.sep + rootName + "_estimates_backup2"
        arcpy.Copy_management(inTable,backupTable)
        arcpy.AddMessage("Created " + backupTable)
    except:
        arcpy.GetMessages()
    
    # create list of total pop fields to summarize
    summaryFields = ["E_ATOTPOPBT_2000","E_ATOTPOPBT_2005","E_ATOTPOPBT_2010","E_ATOTPOPBT_2015","E_ATOTPOPBT_2020"]
    # create empty list of adjFields to add adjField values to
    adjFields = []
    # iterate and summarize
    for summaryField in summaryFields:
        # define outTable
        outTable = "in_memory" + os.sep + rootName + "_" + summaryField #
        # summarize the field
        try:
            arcpy.Frequency_analysis(inTable,outTable,"UCID0",summaryField)
            arcpy.AddMessage("Created " + outTable)
        except:
            arcpy.GetMessages()
        # join the summarized GPWPOP to the un adjustment table
        try:
            arcpy.JoinField_management(unTable,"UCID0",outTable,"UCID0",summaryField)
            arcpy.AddMessage("Joined Fields")
        except:
            arcpy.GetMessages()
        # add adjustment factor field
        adjField = "UNADJFAC_" + summaryField[-4:]
        numerator = "UNPOP" + summaryField[-4:]
        adjFields.append(adjField)
        try:
            arcpy.AddField_management(unTable,adjField,"DOUBLE")
            
        except:
            arcpy.GetMessages()
        # calculation adjustment factor field        
        calcExpression = "(!" + numerator + "!/!" + summaryField + "!) - 1" 
        try:
            arcpy.CalculateField_management(unTable,adjField,calcExpression,"PYTHON_9.3")
            arcpy.AddMessage("Calculated " + adjField)
        except:
            arcpy.GetMessages()
    # join adjustment factor fields to the btn_estimates table
    try:
        arcpy.JoinField_management(inTable,"UCID0",unTable,"UCID0",adjFields)
        arcpy.AddMessage("Joined Fields")
    except:
        arcpy.GetMessages()
    # iterate through adjFields
    for adjField in adjFields:        
        year = adjField[-4:]
        # Create list of fields to adjust
        eFields = arcpy.ListFields(inTable,"E_*" + year)
        #
        newFieldPrefix = "UN"            
        # iterate the eFields
        for eField in eFields:
            fieldName = eField.name
            # define newField
            newField = newFieldPrefix + fieldName
            # add newField to table
            try:            
                arcpy.AddField_management(inTable,newField,"DOUBLE")
            except:
                arcpy.GetMessages()
            # construct unAdjustment
            unAdjustment = "(!" + adjField + "! * !" + fieldName + "!) + !" + fieldName + "!"
            # perform calculation
            try:
                arcpy.CalculateField_management(inTable,newField,unAdjustment,"PYTHON_9.3")
                arcpy.AddMessage("Calculated " + newField)
            except:
                arcpy.GetMessages()    

def main():
    # set counter
    startTime = datetime.datetime.now()
    # define workspace
    workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\usa_state\states'
    arcpy.env.workspace = workspace
    # list gdbs
    gdbs = arcpy.ListWorkspaces("*","FILEGDB")
    pool = multiprocessing.Pool()
    pool.map(unAdjust, gdbs) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()

##    for gdb in gdbs:
##        print gdb
##        # define output workspace
##        outWS = gdb
##        unAdjust(outWS)            
            
    print datetime.datetime.now() - startTime
if __name__ == '__main__':
    main()


        
        
