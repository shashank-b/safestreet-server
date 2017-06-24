#!/bin/bash - 
#===============================================================================
#
#          FILE: parshing.sh
# 
#         USAGE: ./parshing.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Vikrant (), vikrant@cse.iitb.ac.in
#  ORGANIZATION: 
#       CREATED: Friday 09 June 2017 11:18
#      REVISION:  ---
#===============================================================================


# sed -e 's/^M/\n/g' -e 's/"\[""/\n/g' -e 's/"",""/\n/g' -e 's/]",/\n/g' $1 | sed -e '/IMEI/d'
# input_file=$1
output_dir="$PWD/parsed_data2"
mkdir -p $output_dir

for input_file in $(ls *.csv); do
    head -n1 "$input_file" | grep -q "payload"
    if [ $? -eq 1 ]; then
        # echo "payload not found in file $input_file";
        echo "id,payload">"$output_dir/$input_file"
        sed -e 's///g' -e 's/"",""/;/g' -e 's/""//g' -e '/^\s*$/d' $input_file | sort | uniq >> "$output_dir/$input_file"
    else
        # echo "payload found";
        head -n1 $input_file > "$output_dir/$input_file"
        sed -e '1d' -e 's///g' -e 's/"",""/;/g' -e 's/""//g' -e '/^\s*$/d' $input_file | sort | uniq >> "$output_dir/$input_file"
    fi
done
# echo $1

