import arcpy, os, csv
arcpy.env.workspace = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\inputs\usa\tiles'

attributes = r'\\Dataserver0\gpw\GPW4\Beta\Gridding\country\validate\usa_table_validation9_1_15.csv'

# open csv file and write header
csvFile = csv.writer(open(attributes,'wb'))
csvFile.writerow(("ISO","RAWPOPTABLEROWS","INPUTPOPTABLEROWS", "BOUNDARYROWS","ORIGPOPROWS"))

gdbs = arcpy.ListWorkspaces("*")

for gdb in gdbs:
    iso = os.path.basename(gdb)[:-4]
    rawFile = gdb + os.sep + iso + "_admin5_2010_total_pop_raw"
    inputFile = rawFile.replace("raw","input")
    boundaryFile = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\usa_state\states_variables' + os.sep + os.path.basename(gdb) + os.sep + iso
    origPop = r'\\Dataserver0\gpw\GPW4\Gridding\country\inputs\usa_state\states_variables' + os.sep + os.path.basename(gdb) + os.sep + iso + "_admin5_2010_input_population"
##    checkFiles = [rawFile,inputFile,boundaryFile]
##    for check in checkFiles:
##        if not arcpy.Exists(check):
##            print check
##    if arcpy.GetCount_management(rawFile)[0]<>arcpy.GetCount_management(inputFile):
##            print "problem with " + gdb

    rawCount = arcpy.GetCount_management(rawFile)[0]
    inputCount = arcpy.GetCount_management(inputFile)[0]
    boundaryCount = arcpy.GetCount_management(boundaryFile)[0]
    origCount = arcpy.GetCount_management(origPop)[0]
    csvFile.writerow((iso,rawCount,inputCount,boundaryCount,origCount))
##    print "Added " + iso
del csvFile
print "Script Complete"
