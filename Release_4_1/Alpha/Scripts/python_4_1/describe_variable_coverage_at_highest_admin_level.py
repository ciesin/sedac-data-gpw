# multiprocess template
import os, datetime
import multiprocessing
import arcpy
import csv
scriptTime = datetime.datetime.now()
def process(gdb):
    arcpy.env.overwriteOutput=True
    returnList = []
    # must specify
    processTime = datetime.datetime.now()
    iso = os.path.basename(gdb)[:-4]
    arcpy.env.workspace=gdb
    # list the raw tables
    rawTbls = arcpy.ListTables("*raw")
    for rawTbl in rawTbls:
        tableSplit = rawTbl.split("_")
        admin = tableSplit[1]
        year = tableSplit[2]

        # set all return variables to 0
        age=0
        sex=0
        ur=0
        age_sex=0
        age_ur=0
        sex_ur=0
        age_sex_ur=0
        total = 0
        # create a list of variable tables and cycle through them
        # to determine which variables exist?
        tbls =  arcpy.ListTables("*"+admin+"*"+year+"*")
        
        for tbl in tbls:
            if tbl == rawTbl:
                continue
            elif tbl.split("_")[-1]=='lookup':
                continue
            else:
                newName = tbl.replace(iso+"_"+admin+"_"+year+"_","")
                newSplit = newName.split("_")
                
                if len(newSplit)==1:
                    if newSplit[0]=='sex':
                        sex = 1
                    elif newSplit[0]=='ur':
                        ur = 1
                    elif newSplit[0]=='total':
                        total = 1
                elif len(newSplit)==2:
                    if newSplit[0]=='age':
                        age = 1
                    elif str(newSplit[0]+"_"+newSplit[1])=='sex_ur':
                        sex_ur=1
                else:
                    if str(newSplit[0]+"_"+newSplit[1]+"_"+newSplit[2])=='age_sex_ur':
                        age_sex_ur=1
                    elif str(newSplit[0]+"_"+newSplit[1]+"_"+newSplit[2])=='age_sex_group':
                        age_sex=1
                    elif str(newSplit[0]+"_"+newSplit[1]+"_"+newSplit[2])=='age_sex_singleyear':
                        age_sex=1
                    elif str(newSplit[0]+"_"+newSplit[1])=='age_ur':
                        age_ur=1
                    
                        

        returnList.append((iso,admin,year,age,sex,ur,age_sex,age_ur,sex_ur,age_sex_ur,total))
    return returnList
 

def main():
    workspace = r'D:\gpw\release_4_1\loading\processed'
    arcpy.env.workspace = workspace
    print "processing"
    # open csvFile and write header
    varFile = os.path.join(os.path.dirname(workspace),"high_resolution_variable_coverage_01_13_17.csv")
    varCSV = csv.writer(open(varFile,'wb'))
    varCSV.writerow(('iso','admin','year','age','sex','ur','age_sex','age_ur','sex_ur','age_sex_ur','total'))
    # must create procList
    gdbs = arcpy.ListWorkspaces("*","FILEGDB")
    procList = [os.path.join(workspace,gdb) for gdb in gdbs]
##    print procList[0]
    pool = multiprocessing.Pool(processes=20,maxtasksperchild=1)
    results = pool.map(process, procList)
    for result in results:
        for result2 in result:
            varCSV.writerow(result2)
        
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    del varCSV
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
