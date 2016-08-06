#!/bin/bash - 
#===============================================================================
#
#          FILE: pg_dump.sh
# 
#         USAGE: ./pg_dump.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: YOUR NAME (), 
#  ORGANIZATION: 
#       CREATED: Saturday 06 August 2016 22:32
#      REVISION:  ---
#===============================================================================
psql -h localhost -d potholedb -U potholeuser -f elearning_academy.sql
