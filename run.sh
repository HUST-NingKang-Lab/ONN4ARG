#!/bin/bash

mkdir -p onn4argtmp/work
ifn=$1
ibn=`basename ${ifn} .fasta`
split -a6 -l 2 -d $1 onn4argtmp/work/${ibn}
for query in onn4argtmp/work/* ; do
  mv $query $query.fasta
  predict.sh ${query}
  result=`cat ${query}.out`
  echo ${result} >> ${ibn}.out
done
rm -rf onn4argtmp
