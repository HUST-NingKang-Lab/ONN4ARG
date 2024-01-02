# ONN4ARG
![](https://img.shields.io/badge/status-beta-brightgreen?style=flat-square&logo=appveyor) [![downloads](https://static.pepy.tech/badge/onn4arg)](https://pepy.tech/project/onn4arg) [![](https://img.shields.io/badge/DOI-10.1101/2021.07.30.454403-brightgreen?style=flat-square&logo=appveyor)](https://www.biorxiv.org/content/10.1101/2021.07.30.454403) ![](https://img.shields.io/github/license/HUST-NingKang-Lab/ONN4ARG?style=flat-square&logo=appveyor)

[ONN4ARG](http://onn4arg.xfcui.com/) is an Ontology-aware Neural Network model for Antibiotic Resistance Gene (ARG) annotation predictions. It employs a novel ontology-aware layer to encourage annotation predictions satisfying the ontology rules (i.e., the ontology tree structure). It requires the [Diamond](https://github.com/bbuchfink/diamond) and the [HHblits](https://github.com/soedinglab/hh-suite) alignment tools to run. Our source codes are available on [GitHub](https://github.com/HUST-NingKang-Lab/ONN4ARG), and our pre-built ARG database and our pre-trained model can be downloaded from [Zenodo](https://zenodo.org/record/4973684) or [release](https://github.com/HUST-NingKang-Lab/ONN4ARG/releases/tag/v1.0). ONN4ARG provides [web service](http://onn4arg.xfcui.com/) for fast ARG prediction.

<img src="image/Figure 1.png" width="828" height="736" align="middle">
Overview of the ONN4ARG model and its use for novel ARG discovery. (A) The antibiotic resistance gene ontology contains four levels. The root (first level) is a single node, namely, “arg”. There are 1, 2, 34, and 277 nodes from the first level to the fourth level, respectively. (B) The feature encoding procedure of ONN4ARG model. The sequence alignment features and profile HMMs features are encoded by calling Diamond and HHblits. (C) The architecture of the ontology-aware neural network could be described in four functional layers, including feature embedding layer, residual layer, compress layer and ontology-aware layer. The ontology-aware layer is a partially connected layer which encourage annotation predictions satisfying the ontology rules (i.e., the ontology tree structure). Specially, weight between nodes with relationship (e.g., parent and child) satisfying the ontology rules would be saved in the partially connected layer, and weights between irrelevant nodes would be masked. (D) Building the dataset for training and testing, and applying ONN4ARG model on metagenomic samples to discover candidate novel ARGs.

## Database
The ARGs we used in this study for model training and testing were from the Comprehensive Antibiotic Resistance Database (CARD, v3.0.3). We also used protein sequences from the UniProt (SwissProt and TrEMBL) database to expand our training dataset. First, genes with ARG annotations were collected from CARD (2,587 ARGs) and SwissProt (2,261 ARGs). Then, their close homologs (with sequence identities greater than 90%) were collected from TrEMBL (23,728 homologous genes). These annotated and homologous ARGs made up our positive dataset. The negative dataset was made from non-ARG genes that had relatively weak sequence similarities to ARG genes (with sequence identities smaller than 90% and bit-scores smaller than alignment lengths) but not annotated as ARG genes in SwissProt (17,937 genes). For evaluation and comparison of ONN4ARG, 75% of the dataset was randomly selected for training, and the remaining 25% of the dataset was selected for testing. Finally, redundant genes with identical sequences were filtered out. As a result, our ARG gene dataset, namely, ONN4ARG-DB, contained 28,396 ARGs. 

<img src="image/ONN4ARG-DB.png" width="288" height="684" align="middle">
The number of genes in ONN4ARG-DB. The horizontal axis indicates the logarithmic number of genes, and the vertical axis indicates different antibiotic resistance types.

## Ontology
The ARG ontology contains a list of types of antibiotic resistance (drug class), and was organized into a four-level tree structure (a graph contains no cycles), in which higher-level resistance types cover lower-level resistance types. There are 1, 2, 34, and 277 nodes (terms) from the first level to the fourth level, respectively. For instance, the root (first level) is a single node, namely, “arg”, there are “beta-lactam” and “non-beta-lactam” in the second level, “acridine dye” and “aminocoumarin” in the third level, and “acriflavine” and “clorobiocin” in the fourth level.

## Requirements
- Unix/Linux operating system

## Dependency
- [Pytorch 1.7.1](https://github.com/pytorch/pytorch)
- [diamond 0.9.10](https://github.com/bbuchfink/diamond/releases?page=6)
- [NumPy 1.20.3](https://numpy.org/)
- [hhblits](https://github.com/soedinglab/hh-suite)
- [h5py](https://pypi.org/project/h5py/)
- [tqdm](https://tqdm.github.io/)

## Installation
We recommend deploying ONN4ARG using `git` and `conda`.
#### Prepare the conda environment
```shell
# clone the repository
git clone https://github.com/HUST-NingKang-Lab/ONN4ARG.git
cd ONN4ARG
# create the conda environment
conda env create -f environment.yaml
# activate the conda environment
conda activate onn4arg
```
#### Installation via source codes
```shell
# download source codes
wget https://files.pythonhosted.org/packages/f6/c7/3cd9a628628b8c36aec58cc7a2b0db8b0926213c4b4f8e44887657eaa83d/onn4arg-1.0.tar.gz
tar zxf onn4arg-1.0.tar.gz
cd onn4arg-1.0
# add the PATH of onn4arg to the environment, please modify the `/path_to_anaconda` based on the actual path of conda on your machine
export PATH=./onn4arg:$PATH
# download model files
wget https://github.com/HUST-NingKang-Lab/ONN4ARG/releases/download/v1.0.1/onn4arg-v1.0-model.tar.gz
tar zxf onn4arg-v1.0-model.tar.gz
# try running the example
predict.sh model/example
# check the example result, if the result is "arg, non - beta - lactam, aminoglycoside, streptomycin", then the installation is complete
cat model/example.out
```
#### Installation via pip
```shell
# download and install the onn4arg package from pip
pip install onn4arg
# add the PATH of onn4arg to the environment, please modify the `/path_to_anaconda` based on the actual path of conda on your machine
export PATH=/path_to_anaconda/envs/onn4arg/lib/python3.7/site-packages/onn4arg:$PATH
# add executable permissions for python scripts, please also modify the `/path_to_anaconda` based on the actual path of conda on your machine
chmod +x /path_to_anaconda/envs/onn4arg/lib/python3.7/site-packages/onn4arg/*.py
# download model files
wget https://github.com/HUST-NingKang-Lab/ONN4ARG/releases/download/v1.0.1/onn4arg-v1.0-model.tar.gz
tar zxf onn4arg-v1.0-model.tar.gz
# try running the example
predict.sh model/example
# check the example result, if the result is "arg, non - beta - lactam, aminoglycoside, streptomycin", then the installation is complete
cat model/example.out
```

## Usage
#### Run all the steps in a single script
- `predict.sh Single_FASTA_fileprefix`
- `run.sh Multiple_FASTA_filename`

The program will take `FASTA_fileprefix.fasta` as input and store the predicted annotations in "FASTA_fileprefix.out". Note that only one sequence is supported in the input FASTA file. If you have multiple sequences in a single FASTA file, please use `run.sh` and ensure the file has the `.fasta` suffix.

#### Run the scripts step by step (example)
1. Get the query
 `fa2lst.pl model/example.fasta >model/example.lst`
2. Run the sequence alignment
`diamond blastp -q model/example.fasta -d model/model -o model/example-seq.aln --id 30 --max-target-seqs 0 -p 1`
3. Process the sequence alignment result
`aln2txt.pl model/example.lst model/model.lst model/example-seq.aln >model/example-seq.txt`
4. Run the profile alignment
`hhblits -i model/example.fasta -d model/model_uniclust30 -blasttab model/example-prof.aln -o /dev/null -cpu 1`
5. Process the profile alignment result
`aln2txt.pl model/example.lst model/model.lst model/example-prof.aln >model/example-prof.txt`
6. Predict the resistance categories
`predict.py -m model/model-small.sav -t model/tree.out -i model/example -o model/example.out`
## Developers

   Name   |      Email      |      Affiliation
----------|-----------------|----------------------------------------------------------------------------------------
Yuguo Zha |hugozha@hust.edu.cn| School of Life Science and Technology, Huazhong University of Science & Technology
Cheng Chen |chencheng3123@163.com| School of Computer Science, Shandong University
Qihong Jiao |qhjiao@mail.sdu.edu.cn| School of Computer Science, Shandong University
Xiaomei Zeng |xmzeng@hust.edu.cn| School of Life Science and Technology, Huazhong University of Science & Technology
Xuefeng Cui |xfcui@email.sdu.edu.cn| School of Computer Science, Shandong University
Kang Ning |ningkang@hust.edu.cn| School of Life Science and Technology, Huazhong University of Science & Technology
## Reference
Yuguo Zha, Cheng Chen, Qihong Jiao, Xiaomei Zeng, Xuefeng Cui, Kang Ning, Ontology-Aware Deep Learning Enables Novel Antibiotic Resistance Gene Discovery Towards Comprehensive Profiling of ARGs, bioRxiv 2021.07.30.454403 (2021) [(download the PDF file)](https://doi.org/10.1101/2021.07.30.454403)

