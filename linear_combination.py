
from pymongo import MongoClient
import json
import pymatgen as mg
import pandas as pd
import math
from collections import defaultdict

def structure_choose(metaIndex_dict,meta_dict,material,n_index):
    metaIndex_update1={}
    for j,k in metaIndex_dict.items():
        comb_final=0
        data={}
        comb=0
        sum_comb=0
        if k>2:
            for o in material['compositionDictionary'].keys():
                
                if n_index!=None:
                    s=n_index
                    structure=material['structure'][s].upper()
                elif n_index==None:
                    try:
                        for a in meta_dict[o].keys():
                            int(a)
                            structure=meta_dict[o][a][1]
                    except:
                        structure='BCC'
                    #print('strucutre',material['compositionDictionary'],o,structure)
                else:
                    pass;
                    #print('structure')
                try:
                    data[j]=meta_dict[o][structure][k]
                    float(data[j])
                    ##print('BCC')
                except:
                    ##print('No vaule for '+j+' of '+o+' for the phase in records, try other structures')
                    if structure=='BCC':
                        try:
                            data[j]=meta_dict[o]['FCC'][k];
                            float(data[j])
                            ##print('FCC')
                        except:
                            try:
                                data[j]=meta_dict[o]['HCP'][k];
                                float(data[j])
                                ##print('HCP')
                            except:
                                ##print('BREAk')
                                data[j]=0;
                                break;
    
                    elif structure=='FCC':
                        try:
                            data[j]=meta_dict[o]['HCP'][k];
                            float(data[j])
                        except:
                            try:
                                data[j]=meta_dict[o]['BCC'][k];
                                float(data[j])
                            except:
                                data[j]=0;
                                break;
                    elif structure=='HCP':
                        try:
                            data[j]=meta_dict[o]['FCC'][k];
                            float(data[j])
                        except:
                            try:
                                data[j]=meta_dict[o]['BCC'][k];
                                float(data[j])
                            except:
                                data[j]=0;
                                break;
                    elif structure=='Others':
                        try:
                            data[j]=meta_dict[o]['BCC'][k];
                            float(data[j])
                            #print('others','BCC')
                        except:
                            try:
                                data[j]=meta_dict[o]['FCC'][k];
                                float(data[j])
                                #print('others','FCC')
                            except:
                                try:
                                    data[j]=meta_dict[o]['HCP'][k];
                                    float(data[j])
                                    #print('others','HCP')
                                except:
                                    data[j]=0;
                                    break;
                

                ##print('data',comb,i['material']['compositionDictionary'][o])
                comb=comb+material['compositionDictionary'][o]*data[j]
                
                sum_comb=sum_comb+material['compositionDictionary'][o]
                        
            if data[j]!=0:
                comb_final=comb/sum_comb
            else:
                comb_final=0
        metaIndex_update1[j]=[comb_final]
    ##print(metaIndex_update1)
    return metaIndex_update1

def structure_calculate(metaIndex_dict,meta_dict,material):
    all_structure=['BCC','FCC','HCP']
    metaIndex_update=defaultdict(dict)
    n=0
    n_index=[]
    try:
        for i in range(len(material['structure'])):
            if material['structure'][i].upper() in all_structure:
                n=n+1;
                n_index.append(i) 
        #print('n and st',n)
    except:
        n=0
    if n>1:
        #print('n_value',material['formula'],material['structure'][n_index[0]].upper())
        for s in n_index:
            metaIndex_update[material['formula']][material['structure'][s].upper()]=structure_choose(metaIndex_dict,meta_dict,material,s)
    elif n==1:
        #print('n_value1',material['formula'],material['structure'][n_index[0]].upper())
        metaIndex_update[material['formula']][material['structure'][n_index[0]].upper()]=structure_choose(metaIndex_dict,meta_dict,material,n_index[0])
    elif n==0:
        #print('n_value0',material['formula'])
        metaIndex_update[material['formula']]['unknown_structure']=structure_choose(metaIndex_dict,meta_dict,material,None)
    ##print(metaIndex_update)
    return metaIndex_update

def linear_combination_run(data):
    print('now')
    excelFile='./JPCM_Paper/FundemantalDescriptors_PureElements.xlsx'
    metaDF = pd.read_excel(excelFile)
    meta = metaDF.to_json(orient="split")
    metaIndex = json.loads(meta)['columns']
    metaParsed = json.loads(meta)['data']
    meta_dict=defaultdict(dict)
    metaIndex_dict={}
    for k in metaParsed:
        meta_dict[k[2]][k[0]]=k
    ##print(metaIndex,meta_dict)
    for j in range(len(metaIndex)):
        metaIndex_dict[metaIndex[j]]=j
    metaIndex_update1=structure_calculate(metaIndex_dict,meta_dict,data['material'])
    return metaIndex_update1