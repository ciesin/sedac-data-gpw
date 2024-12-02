# preprocess-create-directories-tool_v2.py
# set up preprocessing folders
# Kytt MacManus, edited by Erin Doxsey-Whitfield
# 14-Aug-3

# import libraries
import os, arcpy, sys
import datetime


# define input ISO
##iso = arcpy.GetParameterAsText(0)
iso = "YEM"

# define preprocessing workspace
workspace = r'\\Dataserver0\gpw\GPW4\Preprocessing\Country\YEM\Ingest\Boundary\gadm2.gdb'
arcpy.env.workspace = workspace
suffix = 2
suffixStr = str(suffix)
##
### Add UBID field to gadm2_adminX
gadm2AdminX = workspace + os.sep + iso + "_admin" + suffixStr
arcpy.AddField_management(gadm2AdminX,"UBID","TEXT","","",50)

fields = ["ID_0", "ID_1", "ID_2", "ID_3", "ID_4", "ID_5"]

if suffix == 0:
    calculationExpression = '[ID_0]'
elif suffix == 1:
    calculationExpression = '[ID_0] & "_" & [ID_1]'
elif suffix == 2:
    calculationExpression = '[ID_0] & "_" & [ID_1] & "_" & [ID_2]'
elif suffix == 3:
    calculationExpression = '[ID_0] & "_" & [ID_1] & "_" & [ID_2] & "_" & [ID_3]'
elif suffix == 4:
    calculationExpression = '[ID_0] & "_" & [ID_1] & "_" & [ID_2] & "_" & [ID_3] & "_" & [ID_4]'
elif suffix == 5:
    calculationExpression = '[ID_0] & "_" & [ID_1] & "_" & [ID_2] & "_" & [ID_3] & "_" & [ID_4] & "_" & [ID_5]'
else:
    print "You have more than 5 admin levels in GADM.  You need to add the UBID manually."
    arcpy.AddMessage("You have more than 5 admin levels in GADM.  You need to add the UBID manually.")
    calculationExpression = "<NULL>"
arcpy.CalculateField_management(gadm2AdminX,"UBID",calculationExpression)
print "UBID added to GADMv2"
arcpy.AddMessage("UBID added to GADMv2")


print "done"


##
### check the gadm country data to determine its administrative level
##gadmAdminWS = r'\\Dataserver0\gpw\GPW4\Preprocessing\Global\AdministrativeBoundaries'
##gadmFeatures = gadmAdminWS + os.sep + "gadm2_country.gdb" + os.sep + iso
##fields = ["ID_0", "ID_1", "ID_2", "ID_3", "ID_4", "ID_5"]
##searchRows = arcpy.da.SearchCursor(gadmFeatures,fields)
##for row in searchRows:
##    if row[1] == None:
##        suffix = "0"
##        break
##    elif row[2] == None:
##        suffix = "1"
##        break
##    elif row[3] == None:
##        suffix = "2"
##        break
##    elif row[4] == None:
##        suffix = "3"
##        break
##    elif row[5] == None:
##        suffix = "4"
##        break
##    elif row[5] <> None:
##        suffix = "5"
##        break
##del row
##del searchRows
##print "The gadm country file is at admin: " + suffix
##arcpy.AddMessage("The gadm country file is at admin: " + suffix)
##    
##
### copy GADM files in the gadm2 gdb
##arcpy.CopyFeatures_management(gadmAdminWS + os.sep + "gadm2_admin0.gdb" + os.sep + iso,
##                              gadm2GDB + os.sep + iso + "_admin0")
##arcpy.CopyFeatures_management(gadmAdminWS + os.sep + "gadm2_country.gdb" + os.sep + iso,
##                              gadm2GDB + os.sep + iso + "_admin" + suffix)

