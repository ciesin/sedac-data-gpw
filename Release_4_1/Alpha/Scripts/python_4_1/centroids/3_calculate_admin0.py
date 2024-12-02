#Jane Mills
#3/23/2017
#Calculate admin 0 things

# Import Libraries
import arcpy

inGDB = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\country_data.gdb'
names = r'\\Dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\global\centroids\template.gdb\admin0_names_codes'

arcpy.env.workspace = inGDB

fcs = arcpy.ListFeatureClasses()
fcs.sort()

nameDict = {}
with arcpy.da.SearchCursor(names,['ISO','Country']) as rows:
    for row in rows:
        nameDict[row[0]] = row[1]

for fc in fcs:
    iso = fc[:3].upper()
    country = nameDict[iso]
    
    if iso == 'VCS':
        iso = "VAT"
    if fc[:3] == 'ANR':
        iso = "AND"

    print iso
    
    with arcpy.da.UpdateCursor(fc,['ISOALPHA','COUNTRYNM']) as rows:
        for row in rows:
            row[0] = iso
            row[1] = country
            rows.updateRow(row)

print 'done'


