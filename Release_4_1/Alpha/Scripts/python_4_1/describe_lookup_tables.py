# interrogate lookup tables
# Kytt MacManus
# 1-9-2017

# need to also know which tables do not have fields so use the full set for evaluation
import arcpy, os, csv

## open templateFile and write header
rootPath = r'D:\gpw\release_4_1\loading'
varFile = rootPath + os.sep + "lookup_tables_01_09_17_v3.csv"
varCSV = csv.writer(open(varFile,'wb'))
varCSV.writerow(('iso','adminlevel','year','variable','type'))

arcpy.env.workspace = r'D:\gpw\release_4_1\loading\processed'
gdbs = arcpy.ListWorkspaces("*","FILEGDB")
isos = [os.path.basename(gdb)[:3] for gdb in gdbs]
isos.sort()

for iso in isos:
    arcpy.env.workspace = r'D:\gpw\release_4_1\loading\lookup_tables.gdb'
    if len(arcpy.ListTables(iso+"*"))==0:
        arcpy.env.workspace = r'D:\gpw\release_4_1\loading\processed' + os.sep + iso + ".gdb"
        tbls = arcpy.ListTables("*raw")
    else:
        tbls = arcpy.ListTables(iso+"*")
    # iterate and describe the tables
    for tbl in tbls:
        tblSplit = tbl.split("_")
        if len(tblSplit)==2:
            adminLevel = "TBD"
            year = "TBD"
        else:
            adminLevel = tblSplit[1]
            year = tblSplit[2]
        flds = arcpy.ListFields(tbl,"*")
        for fld in flds:
            variable = fld.name.upper()
            fldType = fld.type
            varCSV.writerow((iso,adminLevel,year,variable,fldType))
del varCSV
