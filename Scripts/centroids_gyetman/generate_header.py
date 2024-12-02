# generate_header.py
# generates the one-line header file for the global centroids .csv file
# G. Yetman 11/15
import arcpy, os
from arcpy import env

centroids = r'E:\gpw_centroids\Experiments.gdb\gpw_v4_centroids'
outPath = r'E:\gpw_centroids'

fieldInfos = arcpy.ListFields(centroids)
headerRow = ''
for f in fieldInfos:
    if f.name <> 'Shape':
        headerRow += '"' + f.name + '"' + ','
# remove trailing comma
headerRow = headerRow[:-1]

###debug
##where = "ISOALPHA = 'ABW'"
### get the fields for making the layer inside the loop
##clyr = arcpy.MakeTableView_management(centroids, 'lyr', where)
##rows = arcpy.da.SearchCursor(clyr,'*')
##cols = rows.fields
##fields = []
##for col in cols: fields.append(col)
### drop the shape field from the list
##fields.remove('Shape')
##del clyr
##print fields

print '...........................'
print 'Writing header'
with open(os.path.join(outPath,'header.csv'), 'w') as f:
    f.write(headerRow)
print '...done.'
