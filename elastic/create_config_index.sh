#!/bin/sh

if [ $# -eq 0 ]
then
<<<<<<< HEAD
    ELASTIC=http://localhost:9200
else
    ELASTIC=$1
fi

./create_index.sh config $ELASTIC
./put_mapping.sh config domains config.json $ELASTIC
python load_config.py 


