# multiprocess template
import os, datetime
import multiprocessing
import arcpy
scriptTime = datetime.datetime.now()
def process():
    processTime = datetime.datetime.now()
    iso = ###### please specify
    try:
        return "Processed "+ iso + " " + str(datetime.datetime.now()-processTime)
    except:
        return "Error while processing " + iso + " " + str(datetime.datetime.now()-processTime)
    
 

def main():
    workspace = ###### define
    arcpy.env.workspace = workspace
    print "processing"
    ##### must create procList - this routine differs by dataset
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
