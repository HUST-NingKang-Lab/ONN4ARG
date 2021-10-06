#!/bin/bash

query=$1
nproc=`nproc`

./fa2lst.pl $query.fasta >$query.lst
time diamond blastp -q $query.fasta -d model -o $query-seq.aln --id 30 --max-target-seqs 0 -p $nproc
./aln2txt.pl $query.lst model.lst $query-seq.aln >$query-seq.txt
time hhblits -i $query.fasta -d model_uniclust30 -blasttab $query-prof.aln -o /dev/null -cpu $nproc
./aln2txt.pl $query.lst model.lst $query-prof.aln >$query-prof.txt
time ./predict.py -m model-small.sav -i $query -o $query.out

