import numpy as np
import re
import subprocess
#%%
iuphar_dir = 'data/IUPHAR/'
metamap_dir = 'metamap/'
terms_dir = 'umls/'
#%%
# Load ligand names from IUPHAR ligand properties:
f = open(iuphar_dir+"ligands.csv", 'r')

# dictionary of drugs:
ligands = {}
    
line = f.next()
for line in f:
    try:
        data = line.split('","')
        ligands['l'+data[0].strip('"')] = re.sub('<[^<]+>', "",data[1])
    except ValueError:
        print "Invalid input:", line

f.close()

# Load target names from IUPHAR target properties:
f = open(iuphar_dir+"targets_and_families.csv", 'r')

# dictionary of targets:
targets = {}
    
line = f.next()
for line in f:
    try:
        data = line.split('","')
        targets['t'+data[3]] = re.sub('<[^<]+>', "",data[4])
    except ValueError:
        print "Invalid input:", line

f.close()

print 'Control sum:\n'
print 'Ligands:',len(ligands)
print 'Targets:',len(targets)

# Save into single files:
np.save(terms_dir+'ligands.npy',ligands)
np.save(terms_dir+'targets.npy',targets)
#%%
# Load ligands and targets from files:
ligands = np.load(terms_dir+'ligands.npy').tolist()
targets = np.load(terms_dir+'targets.npy').tolist()
#%%
# Create collection of terms:
terms = []

for drug in ligands:
    terms.append(ligands[drug].strip())

for target in targets:
    terms.append(targets[target].strip())

terms = np.unique(terms).tolist()

# Save terms into separate files:
for i in range(len(terms)):
    f_out = open(terms_dir+"terms//term_"+str(i), 'w')
    f_out.write(terms[i]+'\n')
    f_out.close()

# Save terms as a dictionary in a single file:
np.save(terms_dir+'terms.npy',terms)
#%%
# Load terms from file:
terms = np.load(terms_dir+'terms.npy').tolist()
#%%
# Retrieve semantic types for every term in predictions using MetaMap (run only once):
# Don't forget to run the server first:
# cd Documents/soft/MetaMap/public_mm
# ./bin/skrmedpostctl start
f_out = open(terms_dir+"temp.txt",'w')

# obtain concepts for every term in the collection:
for i in range(len(terms)):
    print 'term',i
    subprocess.call([metamap_dir+'public_mm/bin/metamap','-I','-s',terms_dir+'terms1/term_'+str(i)], stdout=f_out)
f_out.close()
#%%
# Dictionary of terms and corresponding concepts with scores:
concepts_dict = {}

for i in range(len(terms)):
    
    f = open(terms_dir+"terms//term_"+str(i)+".out", "r")
    concepts_dict[i] = []
    
    for line in f:
        try:
            if (' [' in line) and ('Phrase' not in line) and ('Processing' not in line):
                if '[EPC]' in line:
                    line = line.replace('[EPC]','(EPC)')
                data = line.split('  ')
                data2 = data[2].split(':')
                concepts_dict[i].append((np.int(data[1]),data2[0].strip()))
        except ValueError:
            print "Invalid input:", line
    
    f.close()
    
# Save dictionary to a separate file:
np.save(terms_dir+'concepts_dict.npy',concepts_dict)
#%%
# Load dictionary of terms from file:
concepts_dict = np.load(terms_dir+'concepts_dict.npy').tolist()
#%%
concepts_list = []
# List of unique concepts:
for i in range(len(concepts_dict.keys())):
    for concept in concepts_dict[i]:
        concepts_list.append(concept[1])
        
concepts_list = np.unique(concepts_list)

# Save to a separate file:
np.save(terms_dir+'concepts_list.npy',concepts_list)
#%%
# Load used semantic types:
sem_types_used = np.load(terms_dir+'sem_types_used.npy')
#%%
# Retrieve semantic types concept ids using MetaMap (run only once):
# Don't forget to run the server first:
# cd Documents/soft/MetaMap/public_mm
# ./bin/skrmedpostctl start
f_out = open(terms_dir+"temp.txt",'w')

# obtain concepts for every term in the collection:
for i in range(len(sem_types_used)):
    print 'semantic type',i
    subprocess.call([metamap_dir+'public_mm/bin/metamap','-I','-z',terms_dir+'sem_types/type_'+str(i)], stdout=f_out)
    
f_out.close()
#%%
# Process retrived semantic type IDs:
# Dictionary of semantic types and corresponding IDs:
types_dict = {}

for i in range(len(sem_types_used)):
    f = open(terms_dir+"sem_types//type_"+str(i)+".out", "r")
    types_dict[sem_types_used[i]] = []
    
    for line in f:
        try:
            if (' [' in line) and ('Phrase' not in line) and ('Processing' not in line):
                data = line.split('  ')
                data2 = data[2].split(':')
                types_dict[sem_types_used[i]].append(data2[0].strip())
        except ValueError:
            print "Invalid input:", line
    
    types_dict[sem_types_used[i]] = np.unique(types_dict[sem_types_used[i]]).tolist()
    
    f.close()
 
# Save dictionary to a separate file:
np.save(terms_dir+'types_dict.npy',types_dict)
#%%
# Load semantic types ids:
types_dict = np.load(terms_dir+'types_dict.npy').tolist()
#%%
# list of unique concept ids used for semantic types:
types_list = []
# List of unique concepts:
for i in range(len(types_dict.keys())):
    for c_type in types_dict.values()[i]:
        types_list.append(c_type)
        
types_list = np.unique(types_list)

# Save to a separate file:
np.save(terms_dir+'types_list_1.npy',types_list)
#%%
# Dictionary of drug/target names with corresponding concepts and probabilities creation:
drug_target_dict = {}

for i in range(len(terms)):
    f = open(terms_dir+"terms//term_"+str(i)+".out", "r")
    drug_target_dict[terms[i]] = []
    
    for line in f:
        try:                   
            if (' [' in line) and ('Phrase' not in line) and ('Processing' not in line):
                if '[EPC]' in line:
                    line = line.replace('[EPC]','(EPC)')
                data = line.split('  ')
                data2 = data[2].split(':')
                drug_target_dict[terms[i]].append((np.int(data[1]),data2[0].strip()))
        except ValueError:
            print "Invalid input:", line
    
    f.close()
    
# Save dictionary to a separate file:
np.save(terms_dir+'drug_target_dict.npy',drug_target_dict)
#%%
# Extended dictionary of 'inverse_isa' relations with drug/target concepts and semantic types creation:
inverse_isa_dict_ext = {}

semantic_types = np.load(terms_dir+'sem_types.npy').tolist()

# load output from umls_semsim_sql_auto.py:
inverse_isa_dict1 = np.load(terms_dir+'inverse_isa_dict_types_list_1.npy').tolist()

for i in range(len(terms)):
    f = open(terms_dir+"terms//term_"+str(i)+".out", "r")
    
    for line in f:
        try:
            if (' [' in line) and ('Phrase' not in line) and ('Processing' not in line):
                if '[EPC]' in line:
                    line = line.replace('[EPC]','(EPC)')
                data = line.split('  ')
                data2 = data[2].split('[')
                data3 = data2[1].split(',')
                data4 = data2[0].split(':')
                concept = data4[0].strip()
                if concept not in inverse_isa_dict_ext:
                    inverse_isa_dict_ext[concept] = []
                    for group in data3:
                        for rel_concept in types_dict[semantic_types[group.strip().strip(']')]]:
                            inverse_isa_dict_ext[concept].append(rel_concept)
        except ValueError:
            print "Invalid input:", line
    
    f.close()
    
inverse_isa_dict_ext.update(inverse_isa_dict1)
    
# Save dictionary to a separate file:
np.save(terms_dir+'inverse_isa_dict_ext.npy',inverse_isa_dict_ext)
#%%