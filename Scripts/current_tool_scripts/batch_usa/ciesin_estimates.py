# population-estimates.py
# produce population estimates
# Kytt MacManus
# 2-11-13

# import libraries
import os, arcpy
import datetime
import multiprocessing

def growthRate(outWS):
    rootName = os.path.basename(outWS)[:-4]
    print rootName
    # define input table
    inTable = outWS + os.sep + rootName + "_estimates"
    # define growth rate table
    grTable = outWS + os.sep + rootName + "_growth_rate_final"
    # define join field
    joinField = "UCID2"
    # define outTable
    outTable = outWS + os.sep + rootName + "_estimates_backup"
    # define transfer attributes
    attributes = ["YEARTO2000","YEARTO2005","YEARTO2010",
                  "YEARTO2015","YEARTO2020","AGR","ATOTPOPBT_ADMIN2"]
    # copy new table
    try:
        arcpy.Copy_management(inTable,outTable)
        arcpy.AddMessage("Created " + outTable)
    except:
        arcpy.GetMessages()
    # join fields
    outTable = inTable
    try:
        arcpy.JoinField_management(outTable,joinField,grTable,joinField,attributes)
    except:
        arcpy.GetMessages()
    # define target years
    targetYears = ["2000","2005","2010","2015","2020"]

    # iterate again
    for year in targetYears:
        arcpy.AddMessage("considering " + year)
        # perform estimates. first project the total population to the reference year
        # add field to outTable
        try:
            eField = "E_ATOTPOPBT_" + year
            arcpy.AddField_management(outTable,eField,"DOUBLE")
        except:
            arcpy.GetMessages()
        # construct calcExpression
        calcExpression = "!ATOTPOPBT! * math.exp( !AGR! * !YEARTO" + year + "! )"
        # perform calculation
        try:
            arcpy.CalculateField_management(outTable,eField,calcExpression,"PYTHON_9.3")
            arcpy.AddMessage("calculated " + eField)
        except:
            arcpy.GetMessages()
##        # if year is 2010, then perform age estimates by applying proportions
##        if year == "2010":
##            # list fields
##            fieldList = arcpy.ListFields(outTable,"*PROP")
##            # iterate fields
##            for fld in fieldList:
##                field = fld.name
##                # define newField
##                newField = "E_" + field.replace("PROP",year)
##                # add newField
##                try:
##                    arcpy.AddField_management(outTable,newField,"DOUBLE")
##                except:
##                    arcpy.GetMessages()
##                # define calculation expression
##                propCalc = "!" + eField + "! * !" + field + "!"
##                # perform calculation
##                try:
##                    arcpy.CalculateField_management(outTable,newField,propCalc,"PYTHON_9.3")
##                    arcpy.AddMessage("calculated " + newField)
##                except:
##                    arcpy.GetMessages()
        ##        # delete proportion field
        ##        try:
        ##            arcpy.DeleteField_management(outTable,field)
        ##        except:
        ##            arcpy.GetMessages()
        arcpy.AddMessage("completed calculations")

def main():
    # set counter
    startTime = datetime.datetime.now()
    # define workspace
    workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\usa_state\states'
    arcpy.env.workspace = workspace
    # list gdbs
    gdbs = arcpy.ListWorkspaces("*","FILEGDB")
    pool = multiprocessing.Pool()
    pool.map(growthRate, gdbs) 
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()

##    for gdb in gdbs:
##        print gdb
##        # define output workspace
##        outWS = gdb
##        growthRate(outWS)            
            
    print datetime.datetime.now() - startTime
if __name__ == '__main__':
    main()


### The number of jobs is equal to the number of files
##    workspace = r'E:\gpw\country\ids'
##    arcpy.env.workspace = workspace
##    rasters = arcpy.ListRasters('mwi*.tif*')
##    raster_list = [os.path.join(workspace, raster) for raster in rasters]
##    print "processing"
##    # End main
##    print "complete"

        
        
