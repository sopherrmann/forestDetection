#!/bin/bash

inputFolder="/shares/mfue1/teaching/stu_scratch/Microwave_Remote_Sensing/Group1/data/input/sig0_monthly_mean"
outputFolder="miniref/input/sig0_monthly_mean"
resultFolder="miniref/result"

mkdir -p ${outputFolder}
mkdir -p ${resultFolder}

for ref in `find ${inputFolder} -name '*.tiff'`
do
  convert "${ref}" -crop 1x1+1+1 "${outputFolder}/$(basename -- "$ref")"
done
