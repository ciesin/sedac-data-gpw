# multiprocess template
import os, datetime
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
arcpy.env.overwriteOutput=True
   
def process(gdb):
    returnList = []
    arcpy.env.workspace = gdb
    tbls = arcpy.ListTables("*age_group")
    for tbl in tbls:
        processTime = datetime.datetime.now()
        try:
            # grab the fields to calculate
            cFields = arcpy.ListFields(tbl,"A000_014*")+arcpy.ListFields(tbl,"A015_064*")
            calcFields = [cField.name for cField in cFields]
            for calcField in calcFields:
                prefix = calcField[:-2]
                suffix = calcField[-2:]
                if prefix == "A000_014":
                    exp = "!A000_004" + suffix + "! + !A005_009" + suffix + "! + !A010_014" + suffix + "!"
                else:
                    exp = "!A015_019" + suffix + "! + !A020_024" + suffix + "! + !A025_029" + suffix + "! + !A030_034" + suffix + "! + !A035_039" + suffix + "! + !A040_044" + suffix + "! + !A045_049" + suffix + "! + !A050_054" + suffix + "! + !A055_059"+ suffix + "! + !A060_064" + suffix + "!"
                # complete the calculation
                try:
                    arcpy.CalculateField_management(tbl,calcField,exp,"PYTHON")
                except:
                     returnList.append(arcpy.GetMessages())     
            returnList.append("Processed " + tbl + " " + str(datetime.datetime.now()-processTime))
        except:
            returnList.append("Failed to Process " + tbl + " " + str(datetime.datetime.now()-processTime))
    return returnList
        

def main():
    workspace = r'D:\gpw\release_4_1\loading\processed'
    arcpy.env.workspace = workspace
    print "processing"
    gdbs = arcpy.ListWorkspaces("usaaz*")
    procList = []
    # use a pool to evaluate the GDBs
    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
    results = pool.map(process, gdbs)
    for result in results:
        for result2 in result:
            print result2
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
## 
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
