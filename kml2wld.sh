#Found at this URL http://libreavous.teledetection.fr/telechargements/file/18-script-de-conversion-kmz-vers-worldfile

#!/bin/bash
# Purpose : Create GIS usable raster images (worldfiles) from KMZ.
# Author : Nicolas Moyroud - http://libreavous.teledetection.fr
# License : GNU/GPL v3 - Free use, distribution and modification
# Date : 2011-03-24
# Version : 2.0
# Usage : kml2wld.sh <kmzdirectory>
# Parameter <kmzdirectory> : directory containing kmz files to convert

# Modified : Chris Guest 2013-06-01
# Ignore root img files, remove French locale transforms.

if [[ $# != 1 || ! ( -d $1 ) ]]
then echo "Vous devez fournir 1 paramètre : le répertoire contenant les fichiers kmz à traiter" >&2
     exit 1
fi

path="$1/img"
mkdir "$path"
for kml in $(ls -1 $1/*.kml)
do
  bn=$(basename $kml .kml)
  #unzip -C -d "$path" "$kmz" "doc.kml"
  #mv "$path/doc.kml" "$path/$bn.kml"
  cp "$kml" "$path/$bn.kml"
  for imgname in $(grep href "$path/$bn.kml" | sed 's/^.*>\([^<]*\)<.*/\1/' | grep -v '^root' | grep -v ppm)
  do
    # unzip -C -d "$path" "$kmz" "$imgname"
    cp -a $imgname $path/$imgname
    extimg=$(echo ${imgname#*.})
    bnimg=$(basename $imgname .$extimg)
  echo "moving $path/$imgname  to $path/${bn}_${bnimg}.$extimg "
    mv "$path/$imgname" "$path/${bn}_${bnimg}.$extimg"

    width=$(identify -format "%w" "$path/${bn}_${bnimg}.$extimg")
    height=$(identify -format "%h" "$path/${bn}_${bnimg}.$extimg")

    imgcoord=$(grep -A 10 "$imgname" "$path/$bn.kml")
    north=$(echo $imgcoord | sed 's/^.*<north>\([0-9-][0-9\.]*\)<\/north>.*/\1/')
    south=$(echo $imgcoord | sed 's/^.*<south>\([0-9-][0-9\.]*\)<\/south>.*/\1/')
    east=$(echo $imgcoord | sed 's/^.*<east>\([0-9-][0-9\.]*\)<\/east>.*/\1/')
    west=$(echo $imgcoord | sed 's/^.*<west>\([0-9-][0-9\.]*\)<\/west>.*/\1/')

	echo "EWNS: " $east $west $north $south
    dimX=$(echo "($east-($west))/$width" | bc -l)
    #A=$(printf "%e" $(echo $dimX | tr . ,))
    #A=$(echo $A | tr , .)
	A=$(printf "%e" $(echo $dimX))

    dimY=$(echo "($south-($north))/$height" | bc -l)
    #E=$(printf "%e" $(echo $dimY | tr . ,))
    #E=$(echo $E | tr , .)
    E=$(printf "%e" $(echo $dimY))

    C=$(echo "$west+($dimX/2)" | bc -l)

    F=$(echo "$north+($dimY/2)" | bc -l)

    extwld="none"
    if [[ $extimg == "jpg" || $extimg == "JPG" ]]
    then extwld="jgw"
    fi
    if [[ $extimg == "tif" || $extimg == "TIF" || $extimg == "tif" || $extimg == "TIFF" ]]
    then extwld="tfw"
    fi
    if [[ $extimg == "png" || $extimg == "PNG" ]]
    then extwld="pgw"
    fi
    if [[ $extimg == "gif" || $extimg == "GIF" ]]
    then extwld="gfw"
    fi

    if [[ $extwld != "none" ]]
    then
      echo $A > "$path/${bn}_${bnimg}.$extwld"
      echo 0 >> "$path/${bn}_${bnimg}.$extwld"
      echo 0 >> "$path/${bn}_${bnimg}.$extwld"
      echo $E >> "$path/${bn}_${bnimg}.$extwld"
      echo $C >> "$path/${bn}_${bnimg}.$extwld"
      echo $F >> "$path/${bn}_${bnimg}.$extwld"

      auxpath="$path/${bn}_${bnimg}.$extimg.aux.xml"
      echo "<PAMDataset>" > "$auxpath"
      echo "  <SRS>GEOGCS[&quot;GCS_WGS_1984&quot;,DATUM[&quot;WGS_1984&quot;,SPHEROID[&quot;WGS_1984&quot;,6378137.0,298.257223563]],PRIMEM[&quot;Greenwich&quot;,0.0],UNIT[&quot;Degree&quot;,0.0174532925199433]]</SRS>" >> "$auxpath"
      echo "  <Metadata domain="IMAGE_STRUCTURE">" >> "$auxpath"
      echo "    <MDI key="SOURCE_COLOR_SPACE">YCbCr</MDI>" >> "$auxpath"
      echo "  </Metadata>" >> "$auxpath"
      echo "  <Metadata>" >> "$auxpath"
      echo "    <MDI key="PyramidResamplingType">NEAREST</MDI>" >> "$auxpath"
      echo "  </Metadata>" >> "$auxpath"
      echo "</PAMDataset>" >> "$auxpath"

    else
      echo "Le format du fichier $path/${bn}_${bnimg}.$extimg n'est pas supporté, aucun fichier de géolocalisation n'a pu être généré"
    fi

  done

done
rm "$path"/*.kml
#rmdir "$path"/files
