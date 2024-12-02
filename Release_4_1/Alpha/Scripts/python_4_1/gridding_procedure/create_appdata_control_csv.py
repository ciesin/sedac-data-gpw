import arcpy, os, csv, zipfile, datetime
scriptTime = datetime.datetime.now()
# write header to csv
templateFile = r"\\dataserver0\gpw\GPW4\Release_4_1\Alpha\Gridding\deliverables_in_repo\gpw41_file_sizes.csv"
templateCSV = csv.writer(open(templateFile,'wb'))
templateCSV.writerow(('shuid','format','resolution','variable','size','uncompressed','filename'))
# define workspaces
root = r'\\winserver0\Repo\gpw-v4'
arcpy.env.workspace = root
dirs = arcpy.ListWorkspaces("*rev10*","Folder")
for dir in dirs:
    dirTime = datetime.datetime.now()
    # get shuid
    shuid = os.path.basename(dir)
    filedir = dir + os.sep + 'data'
    files = os.listdir(filedir)
    for f in files:
        # get format
        format = f.split("_")[-1][:-4]
        # get resolution
        resolution = f.split("_")[-3] + "-" + f.split(".")[0].split("_")[-2]
        # get variable
        if shuid == "gpw-v4-basic-demographic-characteristics-rev10":
            if len(f.split("_"))==7:
                variable = f.split("_")[1] + "_" + f.split("_")[2]
            else:
                if f.split("_")[1][4:]=='plus':
                    variable = f.split("_")[1]
                else:
                    variable = f.split("_")[1] + "_" + f.split("_")[2]
        elif shuid == "gpw-v4-data-quality-indicators-rev10":
            if f.split("_")[2] == 'mean':
                variable = "meanadmin"
            elif f.split("_")[2] == 'watermask':
                variable = "watermask"
            else:
                variable = "context"
        elif shuid == "gpw-v4-land-water-area-rev10":
            if f.split("_")[1] == 'landareakm':
                variable = "landareakm"
            elif f.split("_")[1] == 'waterareakm':
                variable = "waterareakm"
        elif shuid == "gpw-v4-national-identifier-grid-rev10":
            variable = "nid"
        elif shuid == "gpw-v4-admin-unit-center-points-population-estimates-rev10":
            resolution = ""
            variable = f.split("_")[1].split(".")[0].upper()
        else:
            if f.split("_")[1]=='totpop':
                variable = "totpop"
            else:
                variable = f.split("_")[1]
        # get size
        filesize = int(os.path.getsize(filedir + os.sep + f)/1000)
        # get uncompressed size
        zf = zipfile.ZipFile(str(filedir + os.sep + f), 'r')
        infos = zf.infolist()
        uncompressed = 0
        for i in infos:
            uncompressed += int(i.file_size)
        zf.close()
        uncompressed = uncompressed/1000
        # create csvData tuple
        filePath = r'/downloads/data/gpw-v4/' + shuid + r'/' + f
        csvData = (shuid,format,resolution,variable,filesize,uncompressed,filePath)
        # write to csv
        templateCSV.writerow(csvData)
    print "Completed " + dir + " in: " + str(datetime.datetime.now() - dirTime)
del templateCSV
print "Completed script in: " + str(datetime.datetime.now()-scriptTime)
        
