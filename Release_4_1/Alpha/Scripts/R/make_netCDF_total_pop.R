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
pops = c("une","e")
pNames = c("UN-Adjusted ","")

for (i in 1:length(resolutions)){
	res = resolutions[[i]]
	rName = rNames[[i]]

	for (j in 1:length(types)){
		type = types[[j]]
		tName = tNames[[j]]
		tUnit = tUnits[[j]]

		for (k in 1:length(pops)){
			pop = pops[[k]]
			pName = pNames[[k]]

			print(paste("gpw_v4_",pop,"_",type,"_",res,".nc"))

			key = paste(type,"_",res,".tif$",sep = "")
			extrakey = paste(res,".tif$",sep = "")

			fileList = list.files(root,key,full.names = TRUE)

			subList = fileList[grep(paste("_",pop,"_atotpopbt_2",sep = ""),fileList)]
			extraList = list.files(extras,extrakey,full.names = TRUE)

			finalList = c(subList,extraList)

			outFile = file.path(outFolder,paste("gpw_v4_",pop,"_atotpopbt_",type,"_",res,".nc",sep = ""))
			cdfName = paste(pName,"Population ",tName,", v4.10 (2000, 2005, 2010, 2015, 2020): ",rName,sep = "")

		  s = raster::stack(finalList)
			writeRaster(s, outFile, overwrite=TRUE, format="CDF",varname=cdfName,
					varunit=tUnit,longname=cdfName,xname="longitude",
					yname="latitude",zname="raster")

			paste("gpw_v4_",pop,"_",type,"_",res,".nc",sep = "")
			print(finalList)}}}


