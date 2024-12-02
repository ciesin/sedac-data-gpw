#Jane Mills
#GPW
#Change text of service mxds

import arcpy, os

inFolder = r'F:\arcgisserver\serverdata\gpw\gpw-v4-basic-demographic-characteristics-rev11'
mxdPath = os.path.join(inFolder,'map-services','gpw_v4_basic_demographic_characteristics_rev11.mxd')

dataFolder = os.path.join(inFolder,'data')
arcpy.env.workspace = dataFolder
rasterList = arcpy.ListRasters()
rasterList.sort()

mxd = arcpy.mapping.MapDocument(mxdPath)
df = arcpy.mapping.ListDataFrames(mxd,"*")[0]

for raster in rasterList:
    if "a000_004bt" in raster or "atotpopbt" in raster:
        pass
    else:
        print(raster)

        if "a0" in raster:
            origLyr = arcpy.mapping.ListLayers(mxd,"*a000_004bt*")[0]
            arcpy.mapping.AddLayer(df,origLyr)
            arcpy.RefreshTOC()
            arcpy.RefreshActiveView()
            lyrs = arcpy.mapping.ListLayers(mxd,"*a000_004bt*")
            
        elif "atot" in raster:
            origLyr = arcpy.mapping.ListLayers(mxd,"*atot*")[0]
            arcpy.mapping.AddLayer(df,origLyr)
            arcpy.RefreshTOC()
            arcpy.RefreshActiveView()
            lyrs = arcpy.mapping.ListLayers(mxd,"*atot*")

        if len(lyrs) > 1:
            lyr = lyrs[0]

            lyr.name = lyr.name[:47]+raster[47:-11]

            if "plus" in raster:
                age0 = str(int(raster[48:51]))
                newText = lyr.description
                newText = newText.replace("Ages 0 to 4 map","Ages "+age0+" and Older map")
                newText = newText.replace("ages 0 to 4 con","ages "+age0+" and older con")
                lyr.description = newText
            elif "a0" in raster:
                age0 = str(int(raster[48:51]))
                age1 = str(int(raster[52:55]))
                newText = lyr.description
                newText = newText.replace("ges 0 to 4","ges "+age0+" to "+age1)
                lyr.description = newText
                
            if "ft_" in raster:
                newText = lyr.description
                newText = newText.replace("2010 Total Population","2010 Female Population")
                newText = newText.replace("displays male and female","displays female")
                lyr.description = newText
            elif "mt_" in raster:
                newText = lyr.description
                newText = newText.replace("2010 Total Population","2010 Male Population")
                newText = newText.replace("displays male and female","displays male")
                lyr.description = newText

        else:
            print("failed")

mxd.save()

