# Kytt MacManus
# 9-30-16

# this script takes a gdb, lists its tables
# then outputs descriptive information about
# each country. eg What variables are present?
# what types are used?

# additionally, a table of variable information is generated
# and joined to a shapefile

# import libraries globally 
import arcpy,os,multiprocessing,datetime,csv
scriptTime = datetime.datetime.now()
# define global variables
rootPath = r'D:\gpw\release_4_1\loading'
gdbRoot = r'D:\gpw\release_4_1\loading\loading_table.gdb'
outCen = 'census_summary_12_16_16'
outVar = 'variable_summary_12_16_16'
templateFC = gdbRoot + os.sep + 'gpw4_admin0_variables'
# rename as needed
variablesFC = gdbRoot + os.sep + 'gpw4_variables_12_16_2016'
# comment as needed
if not arcpy.Exists(variablesFC):
    arcpy.CopyFeatures_management(templateFC,variablesFC)
# read templateFC fields into a dictionary
templateDict = {}
#############Uncomment to produce this summary csv file
## open templateFile and write header
##templateFile = rootPath + os.sep + "template_variables_11_30_16.csv"
##templateCSV = csv.writer(open(templateFile,'wb'))
##templateCSV.writerow(('table','variable'))
templateFields = arcpy.ListFields(templateFC,"A*")
for tmpfld in templateFields:
    templateDict[tmpfld.name.upper()]=1
##    templateCSV.writerow((templateFC,tmpfld.name.upper()))
##del templateCSV
#############Uncomment to produce this summary csv file 
# open csvFile and write header
varFile = rootPath + os.sep + "variable_summary_12_05_16.csv"
varCSV = csv.writer(open(varFile,'wb'))
varCSV.writerow(('iso','adminlevel','year','variable','type'))

# define census workspaces
hlWS = rootPath + os.sep + 'highlevel_census.gdb'
lWS = rootPath + os.sep + 'lowerlevel_census.gdb'
llWS = rootPath + os.sep + 'lowestlevel_census.gdb'
betaSex = rootPath + os.sep + 'beta_sex_tables.gdb'
# create workspace list
workspaces = [hlWS,lWS,llWS,betaSex]
variableList = []
missingList = []
for workspace in workspaces:
    arcpy.env.workspace = workspace
    # list tables
    tbls = arcpy.ListTables("*")
    tbls.sort()
    for tbl in tbls:
        print tbl
        # grab values
        tblSplit = tbl.split("_")
        iso = tblSplit[0]
        adminLevel = tblSplit[1]
        year = tblSplit[2]
        # list fields
        flds = arcpy.ListFields(tbl,"A*")
        for fld in flds:
            # grab values
            variable = fld.name.upper()
            variableList.append(variable)
            fldType = fld.type
            # check to see if the variable is in the list of legal variables
            if variable not in templateDict.keys():
                missingList.append((tbl,variable))
            # add to the variable summary csv
            varCSV.writerow((iso,adminLevel,year,variable,fldType))
            # create update cursor
            whereClause = 'iso = ' + "'" + iso + "'"
##            try:
##                rows = arcpy.UpdateCursor(variablesFC,whereClause)
##                for row in rows:
####                print row.getValue("iso")
####                    print row.getValue(variable)
####                    break
##                    row.setValue(variable,1)
##                    rows.updateRow(row)
##                del row
##                del rows
####                break
##            except:
##                print iso,variable
##                print arcpy.GetMessages()
        
        

        
            
             
###########Uncomment to produce this summary csv file
## open csvFile and write header
missingFile = rootPath + os.sep + "misnamed_variables_12_16_16.csv"
missingCSV = csv.writer(open(missingFile,'wb'))
missingCSV.writerow(('table','variable'))
for missing in missingList:
    missingCSV.writerow(missing)
del missingCSV

del varCSV  
print "Script Complete in " + str(datetime.datetime.now()-scriptTime)

 




