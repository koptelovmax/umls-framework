# The framework for validation of predicted drug-target interactions founded on the UMLS

## This folder includes:
1) **umls_semsim_prep.py** - knowledge base preprocessing using the UMLS and the IUPHAR database (IUPHAR needs to be dowloaded and extracted to *'data/IUPHAR/'* and the MetaMap tool from the UMLS is installed to *'metamap/'*)
2) **umls_semsim_sql_auto.py** - semantic relation retrieval from the sql instance of the UMLS
3) **umls_semsim_verif_auto.py** - verification of predicted interactions using the UMLS and the confidence scores based on semantic similarity measures (using preprocessed knowledge base)

## To reconstruct the experiments (using preprocessed knowledge base):
1) Put the predicted interactions in *umls/methods/'name'/pred_result.txt*, where 'name' is the name of the method ('newermine' etc'.)
2) Run **umls_semsim_verif_auto.py** with 2 parameters: 'name' -- name of the method, 'measure' -- semantic measure ('path', 'lin' or 'sem_vec')
3) Collect the detailed results in *umls/methods/'name'/pred_res_verified_UMLS-'measure'.txt* and the summary in *umls/methods/'name'/pred_res_verified_UMLS-'measure'_stat.txt*

## Links to dowload:
- The IUPHAR database: https://www.guidetopharmacology.org/download.jsp
- The MetaMap tool: https://metamap.nlm.nih.gov

Environment requirements: Python 2.7, numpy, mysql, metamap
