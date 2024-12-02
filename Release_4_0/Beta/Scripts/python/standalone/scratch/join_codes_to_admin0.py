import arcpy, imp, sys, os
# import the checkForField, checkFieldType, and validateSchema functions to a module called custom
custom = imp.load_source('custom',r'\\Dataserver0\gpw\GPW4\Beta\Scripts\python\functions\validateSchema.py')
 
workspace = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\global\country_boundaries_admin0.gdb'
arcpy.env.workspace = workspace

##fcs = arcpy.ListFeatureClasses("*")

lookupTable = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\ancillary.gdb\gpw4_country_codes_subset'

dataDict = {}

admin0Shps = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\global\admin0_shps'

with arcpy.da.SearchCursor(lookupTable,"*") as rows:
    fieldNameObject = rows.fields
    for row in rows:
        isocode = row[1].lower()
        ucadmin0 = row[7]
        
        
        fc = workspace + os.sep + isocode + "_admin0"
        if not arcpy.Exists(fc):
            print "missing " + fc
        else:
            try:
                arcpy.AddField_management(fc,"UCADMIN0", "TEXT","","","10")
                arcpy.AddField_management(fc,"ISONUM", "SHORT")
            except:
                print arcpy.GetMessages()
                
            try:
                arcpy.CalculateField_management(fc,"UCADMIN0",'"' + str(ucadmin0) + '"',"PYTHON")
                arcpy.CalculateField_management(fc,"ISONUM",ucadmin0,"PYTHON")
                
                print "Calculated UCADMIN0 for " + fc
            except:
                print arcpy.GetMessages()

            try:
                arcpy.CopyFeatures_management(fc,admin0Shps + os.sep + os.path.basename(fc) + ".shp")
                print "Copied " + fc
            except:
                print arcpy.GetMessages()
                
##            if custom.checkForField(fc,"ISO")==0:
##                try:
##                    arcpy.AddField_management(fc,"ISO", "TEXT","","","15")
##                except:
##                    print arcpy.GetMessages()
##                    
##                try:
##                    arcpy.CalculateField_management(fc,"ISO",'"' + isocode.upper() + '"',"PYTHON")
##                except:
##                    print arcpy.GetMessages()
##                
##        print "processed " + isocode

##        for fieldName in fieldNameObject:
##            fieldIndex = fieldNameObject.index(fieldName)
##            dataDict[fieldName]=row[fieldIndex]
##
##    print dataDict

##for fc in fcs:
##    print fc[:3]
