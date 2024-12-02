import os, csv, zipfile

zipF = r'F:\gpwv411\zips'
fList = os.listdir(zipF)

outCSV = os.path.join(r'\\Dataserver1\gpw\GPW4\Release_411\documentation',"file_sizes.csv")
csvFile = csv.writer(open(outCSV,"w"))
csvFile.writerow(["zip","size","uncompressed"])

zipList = []

for f in fList:
    zips = os.listdir(os.path.join(zipF,f))
    for z in zips:
        zipList.append(z)
        
        zipPath = os.path.join(zipF,f,z)
        cSize = 0
        uSize = 0
        with zipfile.ZipFile(zipPath,'r') as zOpen:
            for info in zOpen.infolist():
                uSize += info.file_size
                cSize += zOpen.getinfo(info.filename).compress_size
                
        uSize /= 1024
        cSize /= 1024
        csvFile.writerow([z,round(cSize,0),round(uSize,0)])



repo = r'\\Winserver1\Repo\gpw-v4'
repoList = []
folderList = [f for f in os.listdir(repo) if 'rev11' in f]

for f in folderList:
    zips = os.listdir(os.path.join(repo,f,"data"))
    
    for z in zips:
        repoList.append(z)
        
#        zipPath = os.path.join(repo,f,"data",z)
#        cSize = os.path.getsize(zipPath)/1024
#        csvFile.writerow([z,int(cSize),0])

for z in zipList:
    #if z.replace("rev11","rev10") not in repoList:
    if z not in repoList:
        print(z)
        
for z in repoList:
    #if z.replace("rev10","rev11") not in zipList:
    if z not in zipList:
        print(z)
        




