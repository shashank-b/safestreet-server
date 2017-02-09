#!/bin/bash - 
#===============================================================================
#
#          FILE: copy_media.sh
# 
#         USAGE: ./copy_media.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Vikrant (), vikrant@cse.iitb.ac.in
#  ORGANIZATION: 
#       CREATED: Thursday 09 February 2017 11:38
#      REVISION:  ---
#===============================================================================

PROJECT_DIR="/home/vikrant/PycharmProjects/serverPothole"
cd ${PROJECT_DIR}
rsync -arvu media/uploads ${PROJECT_DIR}/backup/
