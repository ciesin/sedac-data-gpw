#Jane Mills
#3/23/2017
#Calculate admin 0 things

# Import Libraries
import arcpy

inGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'
usaGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data_usa.gdb'
names = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\ancillary.gdb\admin0_names_codes'

arcpy.env.workspace = inGDB
fcs = arcpy.ListFeatureClasses()
fcs.sort()

nameDict = {}
with arcpy.da.SearchCursor(names,['ISO','Country']) as rows:
    for row in rows:
        nameDict[row[0]] = row[1]

#Do all countries except USA
for fc in fcs:
    iso = fc[:3].upper()
    country = nameDict[iso]

    print iso, country
    
    with arcpy.da.UpdateCursor(fc,['COUNTRYNM']) as rows:
        for row in rows:
            row[0] = country
            rows.updateRow(row)

#Now fill in the USA
arcpy.env.workspace = usaGDB
fcs = arcpy.ListFeatureClasses()
fcs.sort()

for fc in fcs:
    iso = "USA"
    country = "United States of America"
    print fc[:6], country
    with arcpy.da.UpdateCursor(fc,['COUNTRYNM']) as rows:
        for row in rows:
            row[0] = country
            rows.updateRow(row)

print 'done'


