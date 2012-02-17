#!/bin/bash

DATA_DIR=$1

if [ $# -ne 1 ]
then
    echo "Usage: `basename $0` {arg}"
    exit 65
fi

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $SCRIPT_DIR
rm fetched_users.txt
touch fetched_users.txt

for userfile in $DATA_DIR/*.txt
do
    linecount=`head $userfile | wc -l`
    if [ $linecount -gt 3 ]
    then
        userid=`echo $(basename $userfile) | sed 's/.txt//'`
        echo $userid >> fetched_users.txt
    fi
done
