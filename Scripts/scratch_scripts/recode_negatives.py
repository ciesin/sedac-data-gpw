# recode_negatives.py
# the initial gridding algorithm had a slight error which lead to some
# pop count calculations being Negative. this script postprocesses the
# countries which were affected to correct for this.  the gridding algorithm
# has been updated such that this should not be a continued problem
# Kytt MacManus
# September 27, 2013

# import libraries
import arcpy, os, sys
import datetime

root =r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs'

# Set workspace
arcpy.env.workspace = root

# List file GDBS
gdbs = arcpy.ListWorkspaces("PER*","FILEGDB")
#iterate
for gdb in gdbs:
    # parse iso code
    iso = os.path.basename(gdb)[:-4]
    # define fishnet and check for existance
    fishnet = gdb + os.sep + iso + "_fishnet"
    if not arcpy.Exists(fishnet):
        print fishnet + " does not exist"
    else:
        # Make feature layer of negative values, if the number of features with l
        # less than 0 values is greater than 0, then fix the file
        expression = '"' + "SUM_AREAKMMASKED" + '" < 0'
        fishnetLyr = iso + "_fishnetLyr"
        try:
            arcpy.MakeFeatureLayer_management(fishnet,fishnetLyr,expression)
        except:
            print "SUM_AREAKMMASKED is not in the fishnet"
            pass
        if not int(arcpy.GetCount_management(fishnetLyr)[0])>0:
            print iso + " is a-ok"
        else:
            print "processing " + iso
            # first fix the "SUM_AREAKMMASKED" field
            try:
                arcpy.CalculateField_management(fishnetLyr,"SUM_AREAKMMASKED",0,"PYTHON")
                print "Recoded SUM_AREAKMMASKED"
            except:
                print "Failed"
                print arcpy.GetMessages()
            # Next create a list of the CNTM fields
            fields = arcpy.ListFields(fishnet,"*CNTM")
            # iterate the fields
            for field in fields:
                fieldName = field.name
                expression = '"' + fieldName + '" < 0'
                fieldLyr = iso + fieldName + "_Lyr"
                arcpy.MakeFeatureLayer_management(fishnet,fieldLyr,expression)
                try:
                    time = datetime.datetime.now()
                    arcpy.CalculateField_management(fieldLyr,fieldName,0,"PYTHON")
                    print "Recoded " + fieldName
                    print str(datetime.datetime.now()-time)
                except:
                    print arcpy.GetMessages()
                                                                       
