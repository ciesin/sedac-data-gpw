import arcpy
centroids = r'E:\gpw_centroids\Experiments.gdb\gpw_v4_centroids'
fields = arcpy.ListFields(centroids)
fieldDict = {}
for field in fields:
    if field.name != 'Shape':
        fieldDict[field.name] = field.type

print('Shape' in fieldDict.keys())



    
