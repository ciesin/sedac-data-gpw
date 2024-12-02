# Olena Borkovska
# Add variables to national identifier polygon

# Import libraries
import arcpy, os, datetime
from arcpy import env
from datetime import datetime
arcpy.env.overwriteOutput = True
startTime = datetime.now()

# main folder
rootFolder = r'\\dataserver1\gpw\GPW4\Release_4_1\Alpha\Gridding\global\national_identifier_edits'
tables = os.path.join(rootFolder,'tables')
polyGDB = os.path.join(rootFolder,'national_identifier_polygons.gdb')
tableGDB = os.path.join(rootFolder, 'tables.gdb')

print 'starting script now..'

#list dbf tables and export to a geodatabase if needed
env.workspace = tables
dbfList = [os.path.join(tables,dbf) for dbf in arcpy.ListTables()]
print "tables listed"
for dbf in dbfList:
    outTable = os.path.basename(dbf)[:-4]
    
    if not arcpy.Exists(os.path.join(tableGDB,outTable)): 
        arcpy.TableToTable_conversion(dbf,tableGDB, outTable)
        print 'table {} created'.format(outTable)
print 'tables exist'

# list tables in the geodatabase
env.workspace = tableGDB
tableList = [os.path.join(tableGDB,t) for t in arcpy.ListTables()]
tableList.sort()

# Define workspace
env.workspace = polyGDB

# Set workspace environment
fcList = arcpy.ListFeatureClasses()
fcList.sort()
for fc in fcList:
    print 'starting ' + fc
    for table in tableList:
        #join needed tables to the feature classes
        if 'AgeData' in table:
            print "joining {} now..".format(os.path.basename(table))
            arcpy.JoinField_management(fc, "NAME0", table, "Country_or")

        elif 'SexData' in table:
            print "joining {} now..".format(os.path.basename(table))
            arcpy.JoinField_management(fc, "NAME0", table, "Country_or")


        else:
            pass

    #Delete all unecessary fields
    fieldList = [f.name for f in arcpy.ListFields(fc)]
    keepList = ['OBJECTID','AGEDATACODE','AGEDATALEVEL','AGEDATATYPE','AGEDATAYEAR','SEXDATACODE','SEXDATALEVEL','SEXDATATYPE',
                'SEXDATAYEAR','Shape','GRIDCODE','ISOCODE','UNSDCODE','NAME0','CIESINCODE','DATATYPE','DATACODE','DATAYEAR','DATALEVEL',
                'GRSTATE','GREND','GRLEVEL','LASTCENSUS','MEANUNITKM','Shape_Length','Shape_Area']
    for f in fieldList:
        if f in keepList:
            pass
        else:
            print f
            arcpy.DeleteField_management(fc,f)
            print 'field deleted'
            


print 'script complete @ {}'.format(str(datetime.now() - startTime))
            
    

    



