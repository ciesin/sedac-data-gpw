library(raster)
library(rgdal)
library('sp')
library(ncdf4)

outFolder = "F:/gpw/netCDF"
root = "F:/gpw/netCDF/tifs_fixed_extents"
extras = file.path(outFolder,"quality_tifs")

resolutions = c("1_deg","30_min","15_min","2pt5_min")
rNames = c("1 degree","30 arc-minutes","15 arc-minutes","2.5 arc-minutes")
types = c("cntm","dens")
tNames = c("Count","Density")
tUnits = c("Persons","Persons per square kilometer")
sexes = c("bt","mt","ft")
sNames = c("Both","Male","Female")

for (i in 1:length(resolutions)){
	res = resolutions[[i]]
	rName = rNames[[i]]

	for (j in 1:length(types)){
		type = types[[j]]
		tName = tNames[[j]]
		tUnit = tUnits[[j]]

		for (k in 1:length(sexes)){
			sex = sexes[[k]]
			sName = sNames[[k]]

			key = paste(sex,"_2010_",type,"_",res,".tif$",sep = "")
			extrakey = paste(res,".tif$",sep = "")

			fileList = list.files(root,key,full.names = TRUE)
			sexList = fileList[grep("_e_atotpop",fileList)]
			subList = fileList[grep("_e_a0",fileList)]
			ageList = subList[c(1,3,4,5,8,9,10,11,12,13,14,15,16,18)]
			extraList = list.files(extras,extrakey,full.names = TRUE)

			finalList = c(sexList,ageList,extraList)

			outFile = file.path(outFolder,paste("gpw_v4_age_",sex,"_",type,"_",res,".nc",sep = ""))
			cdfName = paste("Basic Demographic Characteristics, v4.10 (2010): ",sName,", ",tName,", ",rName,sep = "")

			s = raster::stack(finalList)
			writeRaster(s, outFile, overwrite=TRUE, format="CDF",varname=cdfName,
					varunit=tUnit,longname=cdfName,xname="longitude",
					yname="latitude",zname="raster")

			print(paste("gpw_v4_age_",sex,"_",type,"_",res,".nc",sep = ""))
			print(finalList)}}}
