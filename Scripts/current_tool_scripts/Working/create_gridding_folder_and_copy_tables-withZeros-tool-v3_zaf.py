# create_gridding_folder_and_copy_tables.py
# Set up gridding geodatabase, and copy the 6 tables/feature classes needed for gridding
# Erin Doxsey-Whitfield
# 12-Aug-13


# import libraries
import os, arcpy, sys
from arcpy import env
import datetime


# set counter
startTime = datetime.datetime.now()

# define input ISO
isoText = "zaf"
##isoText = arcpy.GetParameterAsText(0)
iso = isoText.lower()

print iso

# define gridding folder workspace
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'
arcpy.env.workspace = workspace
scratch = arcpy.env.scratchFolder
if scratch == None:
    scratch = r"C:\Scratch"
    if not arcpy.Exists(scratch):
        os.mkdir(scratch)


# check if geodatabase already exists.  If it does exist:
newDir = workspace + os.sep + iso + ".gdb" + os.sep + iso + "_fishnet"
if arcpy.Exists(newDir):
    sys.exit("Geodatabase already exists")
    
# if it doesn't exist:
else:
    
    # create file geodatabase in scratch
    isoGDB = scratch + os.sep + iso + ".gdb"
    if arcpy.Exists(isoGDB):
        arcpy.Delete_management(isoGDB)
    else:
        pass
    arcpy.CreateFileGDB_management(scratch,iso)
    print "Created gridding file GDB in scratch"
    arcpy.AddMessage("Created gridding file GDB in scratch")

##    # copy Fishnet and Water_mask feature classes to the scratch gdb
##    fishnets = r'\\Dataserver0\gpw\GPW4\InputData\fishnets'
##    if arcpy.Exists(fishnets + os.sep + iso + ".gdb" + os.sep + iso + "_fishnet"):
##        arcpy.CopyFeatures_management(fishnets + os.sep + iso + ".gdb" + os.sep + iso + "_fishnet",isoGDB + os.sep +iso + "_fishnet")
##        print "Fishnet copied"
##        arcpy.AddMessage("Fishnet copied")
##    else:
##        print iso + " fishnet does not exist"
##        arcpy.AddMessage(iso + " fishnet does not exist")
##        pass
##    if arcpy.Exists(fishnets + os.sep + iso + ".gdb" + os.sep + iso + "_water_mask"):
##        arcpy.CopyFeatures_management(fishnets + os.sep + iso + ".gdb" + os.sep + iso + "_water_mask",isoGDB + os.sep +iso + "_water_mask")
##        print "Water_mask copied"
##        arcpy.AddMessage("Water_mask copied")
##    else:
##        print iso + " water_mask does not exist"
##        arcpy.AddMessage(iso + " water_mask does not exist")
##        pass

    # Input parameters
##    censusTable = arcpy.GetParameterAsText(1)
##    lookupTableExist = arcpy.GetParameterAsText(2)
##    lookupTable = arcpy.GetParameterAsText(3)
##    growthRateTableExist = arcpy.GetParameterAsText(4)
##    growthRateTable = arcpy.GetParameterAsText(5)    
##    boundaryFC = arcpy.GetParameterAsText(6)
##    levelNumber = arcpy.GetParameterAsText(7)

    censusTable = r'\\Dataserver0\gpw\GPW4\Preprocessing\Country\ZAF\Ingest\Census\ZAF_ingest.mdb\zaf_admin6_census_2011'
##    lookupTable = r'\\Dataserver0\gpw\GPW4\Preprocessing\Country\FJI\Match\FJI_match_access.mdb\fji_lookup_level2'
##    growthRateTable = r'\\Dataserver0\gpw\GPW4\GrowthRate\GLP\GLP_growth_rates.mdb\GLP_growth_rate'    
##    boundaryFC = r'\\Dataserver0\gpw\GPW4\Preprocessing\Country\FJI\Ingest\Boundary\gadm2.gdb\FJI_admin2'
    levelNumber = "6"

    # copy tables and feature class to scratch geodatabase
    arcpy.Copy_management(censusTable,isoGDB + os.sep + os.path.basename(censusTable))
    print "Census table copied"
    arcpy.AddMessage("Census table copied")
    
##    if lookupTableExist == "true":
##        arcpy.Copy_management(lookupTable,isoGDB + os.sep + os.path.basename(lookupTable))
##        print "Lookup table copied"
##        arcpy.AddMessage("Lookup table copied")
##    else:
##        print "No lookup table"
##        arcpy.AddMessage("No lookup table")
##        pass
##    
##    if growthRateTableExist == "true":
##        arcpy.Copy_management(growthRateTable,isoGDB + os.sep + os.path.basename(growthRateTable))
##        print "Growth Rate table copied"
##        arcpy.AddMessage("Growth Rate table copied")
##    else:
##        print "No growth rate table"
##        arcpy.AddMessage("No growth rate table")
##        pass
    
##    arcpy.CopyFeatures_management(boundaryFC,isoGDB + os.sep + iso + "_admin" + levelNumber + "_boundaries_2010")
##    print "Boundaries copied"
##    arcpy.AddMessage("Boundaries copied")


# Create UCIDs (add zeros to UCADMINs)
    # Create list of fields
    scratchCensusTable = isoGDB + os.sep + os.path.basename(censusTable)
    fields=arcpy.ListFields(scratchCensusTable,"UCADMIN*")

    #Add new fields
    if levelNumber == "0":
        newFields =["UTCID0", "UCID0"]
        textFields = ["UTCID0"]
    elif levelNumber == "1":
        newFields =["UTCID0","UTCID1","UCID0","UCID1"]
        textFields = ["UTCID0","UTCID1"]
    elif levelNumber == "2":
        newFields =["UTCID0","UTCID1","UTCID2","UCID0","UCID1","UCID2"]
        textFields = ["UTCID0","UTCID1","UTCID2"]
    elif levelNumber == "3":
        newFields =["UTCID0","UTCID1","UTCID2","UTCID3","UCID0","UCID1","UCID2","UCID3"]
        textFields = ["UTCID0","UTCID1","UTCID2","UTCID3"]
    elif levelNumber == "4":
        newFields =["UTCID0","UTCID1","UTCID2","UTCID3","UTCID4","UCID0","UCID1","UCID2","UCID3","UCID4"]
        textFields = ["UTCID0","UTCID1","UTCID2","UTCID3","UTCID4"]
    elif levelNumber == "5":
        newFields =["UTCID0","UTCID1","UTCID2","UTCID3","UTCID4","UTCID5","UCID0","UCID1","UCID2","UCID3","UCID4","UCID5"]
        textFields = ["UTCID0","UTCID1","UTCID2","UTCID3","UTCID4","UTCID5"]
    elif levelNumber == "6":
        newFields =["UTCID0","UTCID1","UTCID2","UTCID3","UTCID4","UTCID5","UTCID6","UCID0","UCID1","UCID2","UCID3","UCID4","UCID5","UCID6"]
        textFields = ["UTCID0","UTCID1","UTCID2","UTCID3","UTCID4","UTCID5","UTCID6"]
    else:
        pass
    
    for newField in newFields:
        # Create condition to check if field already exists, if it does move on, if not add it
        fieldExistList = arcpy.ListFields(scratchCensusTable, newField)
        if len(fieldExistList) == 1:
            print newField + " already exists in " + scratchCensusTable
            arcpy.AddMessage(newField + " already exists in " + scratchCensusTable)
        else:            
            try:
                arcpy.AddField_management(scratchCensusTable,newField,"STRING")
                print "Added " + newField
                arcpy.AddMessage("Added " + newField)
            except:
                print arcpy.GetMessages()
            

    # Iterate the list of fields
    for field in fields:
        print field.name
        arcpy.AddMessage(field.name)
        
        #Create condition to define the correct number of characters
        if field.name=="UCADMIN0":
            fieldLength=3
            newField = "UTCID0"
            calculationField = "UCID0"
            calculationExpression = "[UTCID0]"
        elif field.name=="UCADMIN1":
            fieldLength=5
            newField = "UTCID1"
            calculationField = "UCID1"
            calculationExpression = "[UTCID0] & [UTCID1]"
        elif field.name=="UCADMIN2":
            fieldLength=7
            newField = "UTCID2"
            calculationField = "UCID2"
            calculationExpression = "[UTCID0] & [UTCID1] & [UTCID2]"
        elif field.name=="UCADMIN3":
            fieldLength=8
            newField = "UTCID3"
            calculationField = "UCID3"
            calculationExpression = "[UTCID0] & [UTCID1] & [UTCID2]& [UTCID3]"
        elif field.name=="UCADMIN4":
            fieldLength=10
            newField = "UTCID4"
            calculationField = "UCID4"
            calculationExpression = "[UTCID0] & [UTCID1] & [UTCID2]& [UTCID3] & [UTCID4]"
        elif field.name=="UCADMIN5":
            fieldLength=7
            newField = "UTCID5"
            calculationField = "UCID5"
            calculationExpression = "[UTCID0] & [UTCID1] & [UTCID2]& [UTCID3] & [UTCID4]& [UTCID5]"
        elif field.name=="UCADMIN6":
            fieldLength=6
            newField = "UTCID6"
            calculationField = "UCID6"
            calculationExpression = "[UTCID0] & [UTCID1] & [UTCID2]& [UTCID3] & [UTCID4]& [UTCID5] &[UTCID6]"
        else:
            print "It's not any of those fields"
            arcpy.GetMessages("It's not any of those fields")
        print "Field length = " + str(fieldLength)
        arcpy.AddMessage("Field length = " + str(fieldLength))
       
        # Create search cursor
        search=arcpy.UpdateCursor(scratchCensusTable)
        for row in search:
            value=row.getValue(field.name)
            stringValue=str(int(value))
            print stringValue
            arcpy.AddMessage(stringValue)
            # Create condition to test length of values in row
            if len(stringValue)==fieldLength:
                extraDigits=0
                newValue=stringValue
                print "field length matches max"
                arcpy.AddMessage("field length matches max")
            else:
                extraDigits=fieldLength-len(stringValue)
                print "Add " + str(extraDigits)+ " zeros to start of row to make the total length " + str(fieldLength)
                arcpy.AddMessage("Add " + str(extraDigits)+ " zeros to start of row to make the total length " + str(fieldLength))
            # Append zeroes to front of value
            while extraDigits>0:
                newValue="0"+stringValue
                stringValue=newValue
                extraDigits=extraDigits-1
            print newValue + " is the new value"
            arcpy.AddMessage(newValue + " is the new value")
            row.setValue(newField,newValue)
            search.updateRow(row)

        # Calculate hierarchical ids
        try:
            arcpy.CalculateField_management(scratchCensusTable,calculationField,calculationExpression,"VB","#")
            print "Calculated " + calculationField
            arcpy.AddMessage("Calculated " + calculationField)
        except:
            print arcpy.GetMessages()


    # Join UBID from lookup table to census table, if needed
    censusJoinField = "USCID"
    boundaryJoinField = "UBID"
    scratchLookupTable = isoGDB + os.sep + os.path.basename(lookupTable)

    if lookupTableExist == "true":
        arcpy.AddMessage("Join is needed")
        try:
           arcpy.JoinField_management(scratchCensusTable,censusJoinField,scratchLookupTable,censusJoinField,boundaryJoinField)
           arcpy.AddMessage("UBID joined to census table")
        except:
           arcpy.AddMessage("Join was not successful.  Does UBID exist in your lookup table?")
           sys.exit("Join was not successful.  Does UBID exist in your lookup table?")
    else:
        print "No join needed"
        arcpy.AddMessage("No join needed")
        pass

    # Delete UTCID fields (no longer needed after UCID fields are calculated)
    for textField in textFields:
        arcpy.DeleteField_management(scratchCensusTable,textFields)
        print textField + " field deleted"
        arcpy.AddMessage(textField + " field deleted")
    
    # Copy gdb from scratch to gridding workspace
    arcpy.Copy_management(isoGDB,workspace + os.sep + iso + ".gdb")

    # Delete gdb from scratch workspace
##    arcpy.RefreshCatalog(scratch)
##    arcpy.Delete_management(isoGDB)
    print "Done"
    arcpy.AddMessage("Done")
    print datetime.datetime.now() - startTime  
