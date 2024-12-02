#identify which countries have type double for the pop count fields in the raw table
#    - these have been wrongly converted to type long in the input tables.

# Does NOT look at USA

import os,csv
import arcpy

output = r'C:\Users\edwhitfi\Desktop\countries_with_double_fields.csv'

# open csv file and write header
csvFile = csv.writer(open(output,'wb'))
csvFile.writerow(("ISO",'Tot: ATOTPOPBT Double',"Tot: Number of A fields of type DOUBLE","Sex: ATOPOPBT Double",'Sex: ATOTPOPFT Double', 'Sex: ATOTPOPMT Double', 'Sex: Number of A fields of type DOUBLE' ))


# List workspaces
workspace = r'\\Dataserver0\gpw\GPW4\Release_4_0\Beta\Gridding\country\pop_tables'
arcpy.env.workspace = workspace

# List gdb in workspace
gdbs = arcpy.ListWorkspaces("*","FileGDB")
gdbs.sort()

for gdb in gdbs:
    iso = os.path.basename(gdb)[:-4]
    print iso
    arcpy.env.workspace = gdb

# Select Total Pop raw table
    total_pop_raw_list = arcpy.ListTables("*total_pop_raw")
    if len(total_pop_raw_list) != 1:
        print "\tHas more than one total pop raw table"
    else:
        total_pop_raw = total_pop_raw_list[0]


        # Is ATOTPOPBT double?
        total_ATOTPOPBT_double = arcpy.ListFields(total_pop_raw,"ATOTPOPBT",'Double')
        if len(total_ATOTPOPBT_double) == 1:
            total_ATOTPOPBT = 'Y'
            print "\tTotal: ATOTPOPBT IS type Double"
        else:
            total_ATOTPOPBT = 'N'
            print "\tTotal: ATOTPOPBT is NOT double"

        # Count how many A fields are double
        A_fields_double = arcpy.ListFields(total_pop_raw,"A*","Double")
        total_num_double = len(A_fields_double)
        print "\t" + "Number of 'A' fields of type Double: " + str(total_num_double)



# Select Sex raw table
    if iso == 'vcs':
        pass
    else:

        sex_pop_raw_list = arcpy.ListTables("*sex_variables_raw")
        if len(sex_pop_raw_list) != 1:
            print "\tHas more than one sex raw table"
        else:
            sex_pop_raw = sex_pop_raw_list[0]


            # Is ATOTPOPBT double?
            sex_ATOTPOPBT_double = arcpy.ListFields(sex_pop_raw,"ATOTPOPBT",'Double')
            if len(sex_ATOTPOPBT_double) == 1:
                sex_ATOTPOPBT = 'Y'
                print "\tSex: ATOTPOPBT IS type Double"
            else:
                sex_ATOTPOPBT = 'N'
                print "\tSex: ATOTPOPBT is NOT double"


            # Is ATOTPOPFT double?
            sex_ATOTPOPFT_double = arcpy.ListFields(sex_pop_raw,"ATOTPOPFT",'Double')
            if len(sex_ATOTPOPFT_double) == 1:
                sex_ATOTPOPFT = 'Y'
                print "\tSex: ATOTPOPFT IS type Double"
            else:
                sex_ATOTPOPFT = 'N'
                print "\tSex: ATOTPOPFT is NOT double"

            # Is ATOTPOPMT double?
            sex_ATOTPOPMT_double = arcpy.ListFields(sex_pop_raw,"ATOTPOPMT",'Double')
            if len(sex_ATOTPOPMT_double) == 1:
                sex_ATOTPOPMT = 'Y'
                print "\tSex: ATOTPOPMT IS type Double"
            else:
                sex_ATOTPOPMT = 'N'
                print "\tSex: ATOTPOPMT is NOT double"

            # Count how many A fields are double
            A_fields_double = arcpy.ListFields(sex_pop_raw,"A*","Double")
            sex_num_double = len(A_fields_double)
            print "\t" + "Number of 'A' fields of type Double: " + str(sex_num_double)


            csvFile.writerow((iso, total_ATOTPOPBT,total_num_double,sex_ATOTPOPBT,sex_ATOTPOPFT,sex_ATOTPOPMT, sex_num_double))


print "Done"

