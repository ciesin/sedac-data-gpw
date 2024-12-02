# Author:      Erin Doxsey-Whitfield
# Date:        Oct. 3, 2014

# Merge the centroid files together
# GUBID = ISO_ubid

#-------------------------------------------------------------------------------

# Import libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()

# Import workspace
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\gridding_boundaries_working\gridding_centroids.gdb'
##workspace = r'C:\Users\edwhitfi\Desktop\scratch\gubid_test\gridding_gubid_centroids.gdb'
arcpy.env.workspace = workspace


# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# List the feature classes in the null_features.gdb
fcList = arcpy.ListFeatureClasses("*")
fcList.sort()

# Create FieldMappings object to manage merge output fields
fieldMappings = arcpy.FieldMappings()


for fc in fcList:

# Parse ISO from the feature class name
    isoName = os.path.basename(fc)[0:3]
    iso = isoName.lower()
    

### Skip VAT - doesn't conform to dataset
##    if iso.startswith(('vat'))== False:

       
# Add all fields from feature classes to field Mapping
    fieldMappings.addTable(fc)
    print iso + " added to field Mappings"

##    else:
##        print iso + " skipped"

# Field list includes ISO_GPW4, GUBID, the 3 Area fields, and the 30 E_ATOTPOP*_2010/DS/DSM fields
fieldList = ["ISO_GPW4","GUBID", "ADMINAREAKM", "ADMINWATERAREAKM", "ADMINAREAKMMASKED","E_ATOTPOPBR_2010","E_ATOTPOPBR_2010_DS","E_ATOTPOPBR_2010_DSM","E_ATOTPOPBT_2010","E_ATOTPOPBT_2010_DS","E_ATOTPOPBT_2010_DSM","E_ATOTPOPBU_2010","E_ATOTPOPBU_2010_DS","E_ATOTPOPBU_2010_DSM","E_ATOTPOPFR_2010","E_ATOTPOPFR_2010_DS","E_ATOTPOPFR_2010_DSM","E_ATOTPOPFT_2010","E_ATOTPOPFT_2010_DS","E_ATOTPOPFT_2010_DSM","E_ATOTPOPFU_2010","E_ATOTPOPFU_2010_DS","E_ATOTPOPFU_2010_DSM","E_ATOTPOPMR_2010","E_ATOTPOPMR_2010_DS","E_ATOTPOPMR_2010_DSM","E_ATOTPOPMT_2010","E_ATOTPOPMT_2010_DS","E_ATOTPOPMT_2010_DSM","E_ATOTPOPMU_2010","E_ATOTPOPMU_2010_DS","E_ATOTPOPMU_2010_DSM","E_ATOTPOPUT_2010","E_ATOTPOPUT_2010_DS","E_ATOTPOPUT_2010_DSM"]


# Remove all output fields from the field mappings, except fields in the fieldList
for field in fieldMappings.fields:
    print field.name
    
    if field.name not in fieldList:
        fieldMappings.removeFieldMap(fieldMappings.findFieldMapIndex(field.name))
        print "\tRemoved: " + field.name

# Use Merge tool to move features into single dataset
mergeFC = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\gridding_boundaries_working\gridding_centroids_merge.gdb\gridding_centroids_merge'
##mergeFC = r'C:\Users\edwhitfi\Desktop\scratch\gubid_test\gridding_centroids_merge.gdb\gridding_centroids_merge'
try:
    arcpy.Merge_management(fcList,mergeFC,fieldMappings)
##    arcpy.Merge_management(fcList,mergeFC)
except:
    arcpy.GetMessages()
print "Merged centroids together together"

print "Done"







##for fc in fcList:
##    
### Parse ISO from the feature class name
##        isoName = os.path.basename(fc)[0:3]
##        iso = isoName.lower()
##        print iso
