#Olena Borkovska
#1/3/2018
#remove multiple fields from attribute table

import os, arcpy

lookupGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\KOF_request\gridding_boundaries_4_1.gdb'
arcpy.env.workspace = lookupGDB
arcpy.env.overwriteOutput = True

listFeatureClasses = arcpy.ListFeatureClasses()

exclude =["UBID","NAME0","NAME1","NAME2","NAME3","NAME4","NAME5","NAME6","UCADMIN0","UCADMIN1","UCADMIN2","UCADMIN3","UCADMIN4","UCADMIN5","UCADMIN6"]

for fc in listFeatureClasses:
    fields = arcpy.ListFields(fc)
    deleteList = []
    print "fields listed"
    for field in fields:
        if not field.required:
              if not field.name in exclude:
                  deleteList.append(field.name)

    arcpy.DeleteField_management(fc,deleteList)
                 

    



