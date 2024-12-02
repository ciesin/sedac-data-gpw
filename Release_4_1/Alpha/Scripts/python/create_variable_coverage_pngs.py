# Kytt MacManus
# 10-7-16

import arcpy, os, textwrap

# script to create and export png files representing
# variable data coverage

# it is a prerequisite for this script that the file to base
# the visualizations on has been defined here:
varFile = r'Q:\gpw\release_4_1\loading\loading_table.gdb\gpw4_variables_10_7_2016'
# grab the date for the title
varDate = os.path.basename(varFile).split("_variables_")[1].replace("_","-")

# define the template document
templateMXD = r'Q:\gpw\release_4_1\loading\variable_coverage_template.mxd'
# define output location
outImageDir = r'Q:\gpw\release_4_1\loading\variable_images'

# open the template MXD
mxd = arcpy.mapping.MapDocument(templateMXD)

# grab the protoLyr
protoLyr = arcpy.mapping.ListLayers(mxd,"*proto")[0]
# set the date source of protoLyr
protoLyr.replaceDataSource(os.path.dirname(varFile),"FILEGDB_WORKSPACE",os.path.basename(varFile))

# list the fields in varFile
fields = arcpy.ListFields(varFile,"A*")
for fld in fields:
    variable = fld.name
    print variable
    # set definition query
    protoLyr.definitionQuery = variable + "= '1'"
    # parse a string of ISO's which contain this variable
    isoString = ""
    with arcpy.da.SearchCursor(varFile,["iso",variable]) as rows:
        for row in rows:
            iso = row[0]
            var = row[1]
            if var == '1':
                isoString = isoString  + iso + ","
            else:
                continue

    isoString = textwrap.fill(isoString,184)
    if isoString == "":
        isoString = "No Countries Included"
    elm = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "isoString")[0]
    elm.text=isoString
    elm2 = arcpy.mapping.ListLayoutElements(mxd, "TEXT_ELEMENT", "countryCount")[0]
    elm2.text=str(len(isoString.split(","))) + " out of 241"
    # set the map title
    mxd.title = variable + " AS OF: " + varDate
    # export the png
    png = outImageDir + os.sep + variable + "_" + varDate
    arcpy.mapping.ExportToPNG(mxd,png,resolution=156)
    
    
