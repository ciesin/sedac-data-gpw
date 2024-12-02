# Jane Mills
# 12/11/17
# Check that all files are in the repo

import os

root = r'F:\gpw\gpw4_rev10_fixed_extents'
repo = r'\\winserver0\Repo\gpw-v4'

# First list files in the repo
##folderList = [os.path.join(repo,f) for f in os.listdir(repo) if 'rev10' in f]
##for folderPath in folderList:
##    if 'data' in os.listdir(folderPath):
##        fileList = os.listdir(os.path.join(folderPath,'data'))
##        for f in fileList:
##            print f
##
##    else:
##        print "did not find data folder:",folderPath



# Now the zips on devsedarc1
folderList = [os.path.join(root,f) for f in os.listdir(root) if 'zipped' in f]
for folderPath in folderList:
    fileList = os.listdir(folderPath)
    for f in fileList:
        print f

