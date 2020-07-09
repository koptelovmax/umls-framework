import numpy as np
import sys

name = sys.argv[1] # 'newermine','spectral_part','louvain' etc.

measure = sys.argv[2] # 'path','lin' or 'sem_vec'

k = 20 # Precision at top k

terms_dir = 'umls/'
work_dir = 'umls/methods/'+name+'/'
#%%
# Get vector representation of given concept in hierarchy:
def hierarchy_to_vector(norm_dict,vector,concept,level):

    vector.append((level,str(concept)))
    
    for rel_concept in norm_dict[concept]:
        if (rel_concept != concept) and (level < 100):
            vector+=hierarchy_to_vector(norm_dict,[],rel_concept,level+1)
    
    return vector

# Semantic similarity based on lenght of path:
def path_similarity(norm_dict,concept_a,concept_b):
    
    vector1 = hierarchy_to_vector(norm_dict,[],concept_a,0)
    vector2 = hierarchy_to_vector(norm_dict,[],concept_b,0)
    
    dist_list = [el1[0]+el2[0]-1 for el1 in vector1 for el2 in vector2 if el1[1] == el2[1]]
    
    if dist_list != []:
        min_dist = np.min(dist_list)
        if min_dist > 0:
            vector_sim = 1/float(np.min(min_dist))
        else:
            vector_sim = 1
    else:
        vector_sim = 0
    
    return vector_sim

# Get leaves of given concept:
def get_leaves(rev_dict,vector,concept,level):
   
    for rel_concept in rev_dict[concept]:
        if rel_concept != concept:
            if (rel_concept in rev_dict) and (level < 200):
                vector+=get_leaves(rev_dict,[],rel_concept,level+1)
            else:
                vector.append(str(rel_concept))
    
    return vector

# Get number of leaves for given concept:
def num_leaves(rev_dict,concept):
    
    if concept in rev_dict:
        n_leaves = len(np.unique(get_leaves(rev_dict,[],concept,0)))
    else:
        n_leaves = 0
        
    return n_leaves

# Get subsumers of given concept:
def get_subsumers(norm_dict,vector,concept,level):

    vector.append(str(concept))
    
    for rel_concept in norm_dict[concept]:
        if rel_concept != concept:
            if level < 200:
                vector+=get_subsumers(norm_dict,[],rel_concept,level+1)
    
    return vector

# Get number of subsumers for given concept:
def num_subsumers(norm_dict,concept):
    
    return len(np.unique(get_subsumers(norm_dict,[],concept,0)))

# Get root node of hierarchy:
def get_root(rev_dict):

    ext_rev_list = []
    for key,v_list in rev_dict.iteritems():
        ext_rev_list.append(key)
        for el_list in v_list:
            ext_rev_list.append(el_list)
            
    ext_rev_list = np.unique(ext_rev_list).tolist()
       
    num_leaves_list = []
    candidates_list = []
    for i in range(len(ext_rev_list)):

        if ext_rev_list[i] in rev_dict:
            n_leaves = num_leaves(rev_dict,ext_rev_list[i])
            num_leaves_list.append(n_leaves)
            candidates_list.append(ext_rev_list[i])
        else:
            num_leaves_list.append(0)
            candidates_list.append(ext_rev_list[i])
        
    return candidates_list[num_leaves_list.index(np.max(num_leaves_list))]

# Get reversed dictionary:
def reverse_dict(norm_dict):
    
    rev_dict = {}
    
    for key,l_value in norm_dict.iteritems():
        for el_value in l_value:
            if el_value not in rev_dict:
                rev_dict[str(el_value)] = []
            rev_dict[str(el_value)].append(str(key))
            
    return rev_dict

# Get least common subsumer:
def get_lcs(norm_dict,concept_a,concept_b):
    
    vector1 = hierarchy_to_vector(norm_dict,[],concept_a,0)
    vector2 = hierarchy_to_vector(norm_dict,[],concept_b,0)
    
    dist_list = [el1[0]+el2[0]-1 for el1 in vector1 for el2 in vector2 if el1[1] == el2[1]]
    cs_list = [el1[1] for el1 in vector1 for el2 in vector2 if el1[1] == el2[1]]
    
    if dist_list != []:
        min_dist = np.min(dist_list)
        lcs = cs_list[dist_list.index(min_dist)]
    else:
        lcs = ''
    
    return lcs

# Semantic similarity by Resnik et al.:
def resnik_similarity(norm_dict,rev_dict,concept_a,concept_b,max_leaves):
    
    # determine least common subsumer:
    lcs = get_lcs(norm_dict,concept_a,concept_b)
    
    if lcs != '':
        resnik_sim = -np.log(((num_leaves(rev_dict,lcs)/float(num_subsumers(norm_dict,lcs)))+1)/float(max_leaves+1))
    else:
        resnik_sim = 0
        
    return resnik_sim

# Semantic similarity by Lin et al.:
def lin_similarity(norm_dict,rev_dict,concept_a,concept_b,max_leaves):
    
    # Resnik similarity:
    res_sim = resnik_similarity(norm_dict,rev_dict,concept_a,concept_b,max_leaves)
    
    # Information content of a leaf:
    ic_leaf = -np.log(1/float(max_leaves+1))
    
    #lin_similarity = 2*res_sim/(ic_leaf+ic_leaf)
    lin_similarity = res_sim/float(ic_leaf)
    
    return lin_similarity

# Get cost of the shortest path between given concept and root:
def get_cost(norm_dict,concept,root,level):
     
    if concept != root:
        cost_list = [100]
        for rel_concept in norm_dict[concept]:
            if (rel_concept != concept) and (level < 100):
                cost_list.append(get_cost(norm_dict,rel_concept,root,level+1))
        cost = np.min(cost_list)
        
    else:
        cost = level
    
    return cost

# Find shortest path between two given nodes (concept and root) with cost:
def get_shortest_path_dict(norm_dict,path_dict,concept,root,level):

    if concept != root:
        concept_list = []
        cost_list = [100]
        for rel_concept in norm_dict[concept]:
            if (rel_concept != concept) and (level < 100):
                concept_list.append(rel_concept)
                cost_list.append(get_cost(norm_dict,rel_concept,root,level+1))
        min_cost = np.min(cost_list)
        if concept_list != []:
            cost_list.remove(100)
            next_concept = concept_list[cost_list.index(min_cost)]
            path_dict[str(next_concept)] = level+1
            path_dict = get_shortest_path_dict(norm_dict,path_dict,next_concept,root,level+1)
        
    return path_dict

# Furthest common subsumer:
def get_fcs(norm_dict,concept_a,concept_b):
    
    vector1 = hierarchy_to_vector(norm_dict,[],concept_a,0)
    vector2 = hierarchy_to_vector(norm_dict,[],concept_b,0)
    
    dist_list = [el1[0]+el2[0]-1 for el1 in vector1 for el2 in vector2 if el1[1] == el2[1]]
    cs_list = [el1[1] for el1 in vector1 for el2 in vector2 if el1[1] == el2[1]]
    
    if dist_list != []:
        max_dist = np.max(dist_list)
        fcs = cs_list[dist_list.index(max_dist)]
    else:
        fcs = ''
    
    return fcs

# Semantic vectors similarity:
def sem_vec_similarity(norm_dict,concept_a,concept_b):
    
    sem_root = get_fcs(norm_dict,concept_a,concept_b)
    
    if sem_root != '':  
        sem_dict1 = get_shortest_path_dict(norm_dict,{concept_a:0},concept_a,sem_root,0)
        sem_dict2 = get_shortest_path_dict(norm_dict,{concept_b:0},concept_b,sem_root,0)
        
        concept_list = np.unique(sem_dict1.keys()+sem_dict2.keys()).tolist()
    
        numerator = 0
        denominator1 = 0
        denominator2 = 0
        for concept in concept_list:
            if (concept in sem_dict1) and (concept in sem_dict2):
                product = (1/float(1+sem_dict1[concept]))*(1/float(1+sem_dict2[concept]))
            else:
                product = 0
            numerator += product
            
            if concept in sem_dict1:
                denominator1 += (1/float(1+sem_dict1[concept]))*(1/float(1+sem_dict1[concept]))
            
            if concept in sem_dict2:
                denominator2 += (1/float(1+sem_dict2[concept]))*(1/float(1+sem_dict2[concept]))
                
        sem_vec_sim = numerator/float(np.sqrt(denominator1)*np.sqrt(denominator2))
    else:
        sem_vec_sim = 0
    
    return sem_vec_sim
#%%
# Load ligands and targets:
ligands = np.load(terms_dir+'ligands.npy',allow_pickle=True).tolist()
targets = np.load(terms_dir+'targets.npy',allow_pickle=True).tolist()

# Load dictionary of drugs and targets with corresponding lists and coulples of semantic types with scores:
drug_target_dict = np.load(terms_dir+'drug_target_dict.npy').tolist()

# Load inverse_isa_dict extended with drug/target concepts and semantic types:
inverse_isa_dict_ext = np.load(terms_dir+'inverse_isa_dict_ext.npy').tolist()

# invert inverse_isa extended dictionary:
inverse_isa_dict_ext_reverse = reverse_dict(inverse_isa_dict_ext)
        
# get maximum number of leaves (number of leaves for a root node) for resnik measure:
max_leaves_root = num_leaves(inverse_isa_dict_ext_reverse,get_root(inverse_isa_dict_ext_reverse))
#%%
# Convert prediction results:
f = open(work_dir+"pred_result.txt", 'r')
f_out = open(work_dir+"pred_res_conv.txt", 'w')
  
for line in f:
    try:
        data = line.split(' ')
        f_out.write(ligands[data[0]].strip()+'\t'+targets[data[1].strip()].strip()+'\n')
    except ValueError:
        print "Invalid input:", line

f.close()
f_out.close()
#%%
# Matching between drug concepts, target concepts and their relations:
f = open(work_dir+"pred_res_conv.txt", 'r')
f_out = open(work_dir+"pred_res_verified_UMLS-"+measure+".txt", 'w')

count = 0
count_verified = 0
count_verified_max = 0
measure_scores = []
for line in f:
    try:
        print count
        data = line.split('\t')
        
        drug_concepts = drug_target_dict[data[0]]
        target_concepts = drug_target_dict[data[1].strip()]
        
        f_out.write(str(count)+': '+data[0]+' --> '+data[1])
        f_out.write('Drug concepts: ')
        
        for drug_c in drug_concepts:
            f_out.write('['+drug_c[1]+']')
        f_out.write('\n')
        
        f_out.write('Target concepts: ')
        
        for target_c in target_concepts:
            f_out.write('['+target_c[1]+']')
        f_out.write('\n')
        
        # Lists of interaction concepts and scores:
        sim_list = []
        concept_list = []
        
        for drug_c in drug_concepts:
            for target_c in target_concepts:
                if measure == 'path':
                    concept_sim = (drug_c[0]/float(1000))*(target_c[0]/float(1000))*path_similarity(inverse_isa_dict_ext,drug_c[1],target_c[1])
                elif measure == 'lin':
                    concept_sim = (drug_c[0]/float(1000))*(target_c[0]/float(1000))*lin_similarity(inverse_isa_dict_ext,inverse_isa_dict_ext_reverse,drug_c[1],target_c[1],max_leaves_root)                
                elif measure == 'sem_vec':
                    concept_sim = (drug_c[0]/float(1000))*(target_c[0]/float(1000))*sem_vec_similarity(inverse_isa_dict_ext,drug_c[1],target_c[1])
                if concept_sim != 0:
                    sim_list.append(concept_sim)
                    measure_scores.append(concept_sim)
                    concept_list.append((drug_c[1],target_c[1]))
        
        if sim_list != []:
            f_out.write('Best score: '+str(round(np.max(sim_list),4))+'\n')
            f_out.write('Concepts: '+str(concept_list[sim_list.index(np.max(sim_list))][0])+' '+str(concept_list[sim_list.index(np.max(sim_list))][1])+'\n')
            f_out.write('Average score: '+str(round(np.mean(sim_list),4))+' x '+str(len(sim_list))+'\n')
            count_verified += 1
            if round(np.max(sim_list),4) >= 0.5:
                count_verified_max += 1
        else:
            f_out.write('Best score: 0\n')
            f_out.write('Average score: 0 x 0\n')
        f_out.write('\n')
        
        count += 1
    except ValueError:
        print "Invalid input:", line

f.close()
f_out.close()
#%%
# Check number of predictions:
f = open(work_dir+"pred_result.txt", 'r')
ligands_pred = []
targets_pred = []

for line in f:
    try:
        data = line.split(' ')
        ligands_pred.append(data[0])
        targets_pred.append(data[1].strip())
    except ValueError:
        print "Invalid input:", line

ligands_pred = np.unique(ligands_pred)
targets_pred = np.unique(targets_pred)

f.close()

# Get some statistics:
f_out = open(work_dir+"pred_res_verified_UMLS-"+measure+"_stat.txt", 'w')

f_out.write('Some statistics:\n\n')
f_out.write('Distinct drugs used for prediction: '+str(len(ligands_pred))+'\n')
f_out.write('Value of Precision at k used for prediction: '+str(k)+'\n')
f_out.write('Estimated number of predictions: '+str(len(ligands_pred)*k)+'\n')
f_out.write('Real number of predictions: '+str(count)+'\n')
f_out.write('Distinct targets in prediction results: '+str(len(targets_pred))+'\n\n')
f_out.write('Predictions verified with non-zero score: '+str(count_verified)+' out of '+str(count)+' ('+str(round(count_verified*100/float(count),2))+' %)\n')
f_out.write('Verified with score >= 0.5: '+str(count_verified_max)+' out of '+str(count)+' ('+str(round(count_verified_max*100/float(count),2))+' %)\n')

f_out.write('Score range (min/max/mean/median): '+str(np.min(measure_scores))+' '+str(np.max(measure_scores))+' '+str(np.mean(measure_scores))+' '+str(np.median(measure_scores))+'\n')

f_out.close()
#%%