# multiprocess template
import os, datetime
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
def process():
    processTime = datetime.datetime.now()
    returnList = []
    try:
        returnList.append("Processed "+ iso + " " + str(datetime.datetime.now()-processTime))
    except:
        returnList.append("Error while processing " + iso + " " + str(datetime.datetime.now()-processTime))
    
 return returnList

def main():
    workspace = r'D:\gpw\release_4_1\input_data\country_boundaries_hi_res.gdb'
    arcpy.env.workspace = workspace
    print "processing"
    # must create procList
    pool = multiprocessing.Pool(processes=20,maxtasksperchild=1)
    results = pool.map(process, procList)
    for result in results:
        print result
    # Synchronize the main process with the job processes to
    # ensure proper cleanup.
    pool.close()
    pool.join()
    print "Script Complete in " + str(datetime.datetime.now()-scriptTime)
 
if __name__ == '__main__':
    main()
