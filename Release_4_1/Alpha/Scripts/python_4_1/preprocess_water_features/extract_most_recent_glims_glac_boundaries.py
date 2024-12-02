# Kytt MacManus
# 10-25-16

# identify and remove glaciers older than
# the most recently collected for each glac_id
# this script was run on the machine DEVSEDARC4
# prerequisite
# inputFC created from glims_polygons by extracting where line_type = glac_bound
# and dissolving by glac_id_src_year
import arcpy, os
inputFC = r'D:\gpw\release_4_1\water\water_inputs\global_input_files.gdb\glims_glac_bound_with_multiple_entries_dissolve'

# create dictionary to hold values
values = {}
try:
    # read the values
    with arcpy.da.SearchCursor(inputFC,["glac_id","src_year"]) as rows:
        for row in rows:
            key = row[0]
            # if the key has already been added to the values dictionary
            # then store the minimum value and a counter of the number of time
            # the id has appeared along with the max year
            # values[glac_id] = (min year, max year, id count)
            if key in values:
                values[key] = (min(values[key][0],row[1]),max(values[key][1],row[1]),values[key][2]+1)
            else:
                values[key] = (row[1],row[1],1)
            
except:
    print "Error in creating value dictionary"

# iterate the output values and print those rows which have variation in min year and max year
expCount = 0

for key,value in values.iteritems():
    minYear = value[0]
    maxYear = value[1]
    if minYear<>maxYear:
        expCount+=1
        if expCount == 1:
            expressionString = "glac_id_src_year = '" + key +"_" + str(maxYear) + "'"
        else:
            expressionString = expressionString + " OR glac_id_src_year = '" + key +"_" + str(maxYear)+ "'"
# produce the output selection
outputFC = r'D:\gpw\release_4_1\water\water_inputs\global_input_files.gdb\glims_glac_bound_selected_from_multiple_entries'
arcpy.Select_analysis(inputFC,outputFC,expressionString)

# merge outputFC with glacFC
glacFC = r'D:\gpw\release_4_1\water\water_inputs\global_input_files.gdb\glims_glac_bound_with_one_entry'
mergeFC = r'D:\gpw\release_4_1\water\water_inputs\global_input_files.gdb\glims_glac_bound_final'
arcpy.Merge_management([outputFC,glacFC],mergeFC)


