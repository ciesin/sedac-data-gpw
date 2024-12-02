# Join_census_and_lookup_tables.py
# Joins UBID from lookup table to census table
# Erin Doxsey-Whitfield
# 14-Aug-13

# import libraries
import os, arcpy, sys
from arcpy import env
import datetime


# set counter
startTime = datetime.datetime.now()


# define gridding folder workspace
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'
arcpy.env.workspace = workspace
scratch = arcpy.env.scratchFolder

# define paramaters
censusTable = arcpy.GetParameterAsText(0)
lookupTable = arcpy.GetParameterAsText(1)
joinField = arcpy.GetParameterAsText(2)
ubidField = "UBID"

# Join UBID from lookup table to census table
try:
    arcpy.JoinField_management(censusTable,joinField,lookupTable,joinField,ubidField)
    arcpy.AddMessage("UBID joined to census table")
    arcpy.AddMessage("Done")
except:
    arcpy.AddMessage("Join was not successful.  Does UBID exist in your lookup table?")
    sys.exit("Join was not successful.  Does UBID exist in your lookup table?")





