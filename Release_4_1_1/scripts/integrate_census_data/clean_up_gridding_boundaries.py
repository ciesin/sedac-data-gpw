#Jane Mills
#8/5/2019
#Create census boundaries with data
#CLean up gridding boundaries (delete attributes)

import arcpy, os

inFolder = r'\\Dataserver1\gpw\GPW4\Release_411\data\boundaries\adjusted_boundaries_with_census_data'

boundaryGDBs = [os.path.join(inFolder,b) for b in os.listdir(inFolder) if b[-4:] == '.gdb']
boundaryGDBs.sort()

fieldList = ['UBID','GUBID','ISOALPHA','CONTEXT','CONTEXT_NM',
                 'WATER_CODE','AREAKM','WATERAREAKM','MASKEDAREAKM']
fieldList = fieldList + ['UCADMIN'+str(i) for i in range(7)]
fieldList = fieldList + ['NAME'+str(i) for i in range(7)]

inGDB = boundaryGDBs[0]
for inGDB in boundaryGDBs:
    print(os.path.basename(inGDB))
    arcpy.env.workspace = inGDB
    fcList = arcpy.ListFeatureClasses()
    fcList.sort()
    
    if len(fcList) > 1:
        for fc in fcList[:-1]:
            arcpy.Delete_management(fc)
    
    fc = fcList[-1]
    
    fList = [f.name for f in arcpy.ListFields(fc) if f.name not in fieldList and not f.required]
    if len(fList) > 0:
        arcpy.DeleteField_management(fc,fList)



