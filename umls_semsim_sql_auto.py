import numpy as np
import mysql.connector
from mysql.connector import Error
import sys
#%%
terms_dir = 'umls/'

name = sys.argv[1] # 'types_list_1' or 'concepts_list'

# Load task list:
querying_list = np.load(terms_dir+name+'.npy')
#%%
# Framework for retrieving related concepts in an automatic way:

# Dictionary to store relationships:
inverse_isa_dict = {}

# Log file location:
f_out = open(terms_dir+'inverse_isa_'+name+'.log','w')

count = 1
# While querying list is not empty:
while len(querying_list) != 0:
    print 'Round: ',count,' dictionary: ',len(inverse_isa_dict.keys()),' querring list: ',len(querying_list)
    f_out.write('Round: '+str(count)+' dictionary: '+str(len(inverse_isa_dict.keys()))+' querring list: '+str(len(querying_list))+'\n')
    new_concepts_list = []
    # For every concept in the list:
    for concept_id in querying_list:
        # If concept is not in the dictionary yet:
        if concept_id not in inverse_isa_dict.keys():
            # Query its relations:
            try:
                connection = mysql.connector.connect(host='x-mysql-greyc.unicaen.fr',
                                                     database='umls',
                                                     user='umls',
                                                     password='*************') # put your password here
            
                sql_select_Query = "SELECT * FROM MRREL a, MRCONSO b WHERE b.cui = '"+concept_id+"' AND a.aui1 = b.aui AND a.stype1 = 'AUI' AND a.rela = 'inverse_isa' AND b.lat = 'ENG'"
                cursor = connection.cursor()
                cursor.execute(sql_select_Query)
                records = cursor.fetchall()
        
                tmp_list = []
                for row in records:
                    if row[4] != concept_id:
                        tmp_list.append(row[4])
                        new_concepts_list.append(row[4])
                    
                inverse_isa_dict[concept_id] = np.unique(tmp_list).tolist()
            
            except Error as e:
                print("Error reading data from MySQL table", e)
                f_out.write('Error reading data from MySQL table'+str(e)+'\n')
            finally:
                if (connection.is_connected()):
                    connection.close()
                    cursor.close()
                    #print("MySQL connection is closed")
                    
    # Add new distinct concepts for querying:
    querying_list = np.unique(new_concepts_list).tolist()
    
    # Update round number:
    count += 1

f_out.close()

# Save dictionary to a separate file:
np.save(terms_dir+'inverse_isa_dict_'+name+'.npy',inverse_isa_dict)
#%%
