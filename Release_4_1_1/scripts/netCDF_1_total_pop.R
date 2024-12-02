library(raster)
library(rgdal)
library('sp')
library(ncdf4)

outFolder <- "F:/gpw/v411/netcdf"
root <- "//Dataserver1/gpw/GPW4/Release_411/data/rasters_lowres"
extras <- "//Dataserver1/gpw/GPW4/Release_411/data/netCDF/quality_tifs"

resolutions <- c("1_deg","30_min","15_min","2pt5_min")
rNames <- c("1 degree","30 arc-minutes","15 arc-minutes","2.5 arc-minutes")
types <- c("population_count","population_density")
tNames <- c("Count","Density")
tUnits <- c("Persons","Persons per square kilometer")
pops <- c("_adjusted","_rev")
pNames <- c("UN WPP-Adjusted ","")

for (i in 1:length(resolutions)){
	res <- resolutions[i]
	rName <- rNames[i]

	for (j in 1:length(types)){
		type <- types[j]
		tName <- tNames[j]
		tUnit <- tUnits[j]

		for (k in 1:length(pops)){
			pop <- pops[k]
			pName <- pNames[k]
			
			fileName <- ifelse(k==1, paste("gpw_v4_",type,pop,"_rev11","_",res,".nc",sep = ""),
			                   paste("gpw_v4_",type,"_rev11","_",res,".nc",sep = ""))
			print(fileName)
			
			resKey <- paste(res,".tif$",sep = "")
			fileList <- list.files(root,resKey,full.names = TRUE)
			extraList <- list.files(extras,resKey,full.names = TRUE)
			
			subList <- fileList[grep(paste(type,pop,sep = ""),fileList)]
			subList <- subList[grep("rev11_2",subList)]

			finalList <- c(subList,extraList)
			if (length(finalList) != 20) {print("did not find enough rasters")}

		 	outFile <- file.path(outFolder,fileName)
		 	
		 	cdfName <- paste(pName,"Population ",tName,", v4.11 (2000, 2005, 2010, 2015, 2020): ",rName,sep = "")

		  s <- raster::stack(finalList)
			writeRaster(s, outFile, overwrite=TRUE, format="CDF",varname=cdfName,
			            varunit=tUnit,longname=cdfName,xname="longitude",
			            yname="latitude",zname="raster")

			print("finished creating NetCDF")
		}
	}
}



