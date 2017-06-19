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
sed -e 's//\n/g' -e  's/"",""/;/g' -e 's/""//g' $1
# echo $1

