#!/bin/bash - 
#===============================================================================
#
#          FILE: db_backup.sh
# 
#         USAGE: ./db_backup.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Vikrant (), vikrant@cse.iitb.ac.in
#  ORGANIZATION: 
#       CREATED: Thursday 09 February 2017 11:53
#      REVISION:  ---
#===============================================================================

./pg_backup_rotated.sh
echo "copying media"
bash copy_media.sh


