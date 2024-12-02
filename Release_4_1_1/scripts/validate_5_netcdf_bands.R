library(raster)
library(rgdal)
library('sp')
library(ncdf4)


inFolder <- "F:/gpw/v411/netcdf"

fileList <- list.files(inFolder,".nc$",full.names = FALSE)

for (f in fileList){
  library(raster)
  filePath <- file.path(inFolder,f)
  nc <- nc_open(filePath)
  test <- length(nc$dim$raster$vals)
  if (grepl("demographic",f)){
    if (test != 30){print(paste(f,": ",test, sep = ""))}
  }
  if (grepl("population",f)){
    if (test != 20){print(paste(f,": ",test, sep = ""))}
  }
}
