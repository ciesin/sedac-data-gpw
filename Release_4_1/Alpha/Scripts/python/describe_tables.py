# Kytt MacManus
# 9-30-16

# this script takes a gdb, lists its tables
# then outputs descriptive information about
# each country. eg What variables are present?
# what types are used?

# additionally, a table of variable information is generated
# and joined to a shapefile

# import libraries globally 
import arcpy,os,datetime,csv
scriptTime = datetime.datetime.now()


# define variables
rootPath = r'Q:\gpw\release_4_1\loading'
gdbRoot = r'Q:\gpw\release_4_1\loading\loading_table.gdb'
outCen = 'census_summary_9_30_16'
outVar = 'variable_summary_9_30_16'
templateFC = gdbRoot + os.sep + 'gpw4_admin0_variables'
# rename as needed
variablesFC = gdbRoot + os.sep + 'gpw4_variables_10_7_2016'
# comment as needed
##arcpy.CopyFeatures_management(templateFC,variablesFC)

# define input workspaces
hlWS = rootPath + os.sep + 'highlevel_census.gdb'
lWS = rootPath + os.sep + 'lowerlevel_census.gdb'
llWS = rootPath + os.sep + 'lowestlevel_census.gdb'
# create workspace list
##workspaces = [lWS]
workspaces = [hlWS,lWS,llWS]
# uncomment to produce CSV
### open csvFile and write header
##varFile = rootPath + os.sep + "variable_summary_10_05_16.csv"
##varCSV = csv.writer(open(varFile,'wb'))
##varCSV.writerow(('iso','adminlevel','year','variable','type'))


for workspace in workspaces:
    arcpy.env.workspace = workspace
    # list tables
    tbls = arcpy.ListTables("*")
    for tbl in tbls:
        # grab values
        tblSplit = tbl.split("_")
        iso = tblSplit[0]
        adminLevel = tblSplit[1]
        year = tblSplit[2]
        # list fields
        flds = arcpy.ListFields(tbl,"A*")
        for fld in flds:
            # grab values
            variable = fld.name
            fldType = fld.type
##            print variable
            # check to see if the variable is in the list of legal variables
            flds = arcpy.ListFields(variablesFC,variable)
            if len(flds)==1:
                pass
            else:
                print "Missing Variable:"
                print iso, variable
                continue
            
            # create update cursor
            whereClause = 'iso = ' + "'" + iso + "'"
            try:
                rows = arcpy.UpdateCursor(variablesFC,whereClause)
                for row in rows:
    ##                print row.getValue("iso")
##                    print row.getValue(variable)
##                    break
                    row.setValue(variable,1)
                    rows.updateRow(row)
                del row
                del rows
##                break
            except:
                print iso,variable
                print arcpy.GetMessages()
                
                

            ## uncomment these 2 line as needed to produce CSV
##            varCSV.writerow((iso,adminLevel,year,variable,fldType))
##del varCSV             


print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
