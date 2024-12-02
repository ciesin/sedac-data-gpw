# Author:      Erin Doxsey-Whitfield
# Date:        Oct. 3, 2014

# List the CIESIN estimate fields (E_*) and the UN estimate fields (UNE_*)

#-------------------------------------------------------------------------------

# Import libraries
import arcpy, os, csv
import datetime
startTime = datetime.datetime.now()

# Import workspace
workspace = r'\\Dataserver0\gpw\GPW4\Gridding\global\inputs\gridding_boundaries_working\gridding_gubid.gdb'
##workspace = r'C:\Users\edwhitfi\Desktop\scratch\gubid_test\gridding_gubid.gdb'
arcpy.env.workspace = workspace


# Overwrite pre-existing files
arcpy.env.overwriteOutput = True

# define csv file
##output =r'C:\Users\edwhitfi\Desktop\scratch\gubid_test\gridding_field_names_test.csv'
output =r'\\DATASERVER0\gpw\GPW4\Gridding\validation\gridding_field_names_v2.csv'

# open csv file and write header
csvFile = csv.writer(open(output,'wb'))
csvFile.writerow(("COUNTRYISO","FIELDNAME"))


# List the feature classes in the null_features.gdb
fcList = arcpy.ListFeatureClasses("*com*")
fcList.sort()

for fc in fcList:

# Parse ISO from the feature class name
    isoName = os.path.basename(fc)[0:3]
    iso = isoName.lower()
    print iso

    # Skip VAT - doesn't conform to dataset
##    if iso.startswith(('vat'))== False:
    if iso.startswith(('vat'))== False:

###  List the ISO_GPW4 field
##        fieldList = arcpy.ListFields(fc,"*ISO_GPW4*")
##
##        for field in fieldList:
##            print "\t" + field.name
##            fieldName = field.name
##            
##     # Write CIESIN estimate fields to csv
##            csvFile.writerow((iso,fieldName))
##
###  List the GUBID field
##        fieldList = arcpy.ListFields(fc,"*GUBID*")
##
##        for field in fieldList:
##            print "\t" + field.name
##            fieldName = field.name
##            
##     # Write CIESIN estimate fields to csv
##            csvFile.writerow((iso,fieldName))
##
###  List the ADMINAREA fields
##        fieldList = arcpy.ListFields(fc,"*AREAKM*")
##
##        for field in fieldList:
##            print "\t" + field.name
##            fieldName = field.name
##            
##     # Write CIESIN estimate fields to csv
##            csvFile.writerow((iso,fieldName))
       

    # List all CIESIN estimate fields (E_*)
        fieldList = arcpy.ListFields(fc,"E_*")

        for field in fieldList:
            print "\t" + field.name
            fieldName = field.name
            
     # Write CIESIN estimate fields to csv
            csvFile.writerow((iso,fieldName))    
        
    # List all UN estimate fields (UNE_*)
        fieldList = arcpy.ListFields(fc,"UNE_*")

        for field in fieldList:
            print "\t" + field.name
            fieldName = field.name
            
     # Write CIESIN estimate fields to csv
            csvFile.writerow((iso,fieldName))    

    else:
        print iso + " skipped"

print "Done"


