# multiprocess template
import os, datetime
import multiprocessing
import arcpy,socket
scriptTime = datetime.datetime.now()
def process(gdb):
    processTime = datetime.datetime.now()
    arcpy.env.workspace=gdb
    delFiles = arcpy.ListTables("*")+arcpy.ListFeatureClasses("*")
    try:
        for delFile in delFiles:
            if delFile.split("_")[-1]=='fishnet':
                continue
            else:
                arcpy.Delete_management(delFile)
        arcpy.Compact_management(gdb)
        return "Processed "+ gdb + " " + str(datetime.datetime.now()-processTime)
    except:
        return "Error while processing " + gdb + " " + str(datetime.datetime.now()-processTime)
    
 

def main():
    host = socket.gethostname()
    if host == 'Devsedarc3':
        workspace = r'F:\gpw\release_4_1\process'
    elif host == 'Devsedarc4':
        workspace = r'D:\gpw\release_4_1\process'
    arcpy.env.workspace = workspace
    print "processing"
    procList = arcpy.ListWorkspaces("deu.gdb")
    # must create procList
    print len(procList)
    pool = multiprocessing.Pool(processes=1,maxtasksperchild=1)
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
