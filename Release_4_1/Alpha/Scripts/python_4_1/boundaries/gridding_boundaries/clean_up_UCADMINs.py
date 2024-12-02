#Jane Mills
#5/18/2017
#Clean up UCADMIN codes

# Import Libraries
import arcpy, os

gridding = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\boundaries\gridding_boundaries_4_1.gdb'

arcpy.env.workspace = gridding
fcList = arcpy.ListFeatureClasses()
fcList.sort()

for fc in fcList:
    print fc

    for i in range(1,7):
        with arcpy.da.UpdateCursor(fc,["UBID","UCADMIN"+str(i),"NAME"+str(i)]) as cursor:
            for row in cursor:
                if row[1] is None:
                    if row[2] == "NA":
                        row[1] = "NA"
                        cursor.updateRow(row)
                    else:
                        print row[0], "missing UCADMIN", i


print 'done'

