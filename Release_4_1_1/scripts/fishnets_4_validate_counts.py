# -------------------------------------------------------------------------------
#Jane Mills
#1/18/2019
#recreate fishnets
# -------------------------------------------------------------------------------


import arcpy, os
arcpy.env.overwriteOutput = True

root = r'F:\gpwv411\processed_fishnets'
outFolder = os.path.join(root,'output_fishnets')
validGDB = os.path.join(root,'validation.gdb')
arcpy.env.scratchWorkspace = outFolder

gdbList = [os.path.join(outFolder,g) for g in os.listdir(outFolder)]
gdbList.sort()
print("Let's get going: {}".format(len(gdbList)))

for gdb in gdbList:
    countryName = os.path.basename(gdb)[:-4]
    print(countryName)
    inFish = os.path.join(gdb,countryName+"_fishnet")




