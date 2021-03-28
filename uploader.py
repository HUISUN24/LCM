#%%

import pandas as pd
import sys
import json
import pymatgen as mg
from datetime import datetime
from pymongo import MongoClient

def upload():
    excelFile = sys.argv[1]

    print('Starting the upload process!\nLoading credentials...')

    cred = json.load(open('credentials.json'))
    if cred['name']=='test':
        return 'Loaded test credentials. Aborting!'
    print('Loaded credentials for: '+cred['name'])

    #Import metadata
    print('Reading the metadata.')
    metaDF = pd.read_excel(excelFile,
                           usecols="A:F", nrows=4)
    meta = metaDF.to_json(orient="split")
    metaParsed = json.loads(meta)['data']
    # get timestamp
    now = datetime.now()
    dateString = now.strftime('%Y-%d-%b-%H-%M-%S')
    # Format metadata into a dictionary
    metaData = {
        'name': metaParsed[0][1],
        'email': metaParsed[1][1],
        'directFetch': metaParsed[2][1],
        'handFetch': metaParsed[3][1],
        'comment': metaParsed[0][5],
        'timeStamp': dateString
    }
    print('Data credited to: '+metaParsed[0][1])
    print('Contact email: '+metaParsed[1][1])

    # Import data
    print('Importing data.')
    df2 = pd.read_excel(excelFile,
                       usecols="A:N",nrows=500,skiprows=8)
    result = df2.to_json(orient="records")
    parsed = json.loads(result)
    print('Imported '+str(parsed.__len__())+' datapoints.')

    # Connect to the MongoDB using the credentails
    client_string = 'mongodb+srv://' + cred['name'] + ':' + cred[
        'dbKey'] + '@testcluster.g3kud.mongodb.net/ULTREA_materials?retryWrites=true&w=majority'
    database_name = 'ULTREA_materials'
    collection_name = cred['name']

    client = MongoClient(client_string)
    collection = client[database_name][collection_name]

    # Convert metadata and data into database datapoints and upload
    for datapoint in parsed:
        uploadEntry = datapoint2entry(metaData, datapoint)
        comp = uploadEntry['material']['formula'].replace(' ','')
        try:
            collection.insert_one(uploadEntry)
            print('Succesfully uploaded a datapoint for '+comp)
        except:
            print('Upload of '+comp+' failed!')


#%% Modify composition string from the template into a unified
# representation of (1) IUPAC standardized formula, (2) pymatgen reduced
# composition object, (3) reduced formula, and (4) chemical system

def compStr2compList(s):
    try:
        compObj = mg.Composition(s).reduced_composition
        if not compObj.valid:
            print("Composition invalid")
        return [compObj.iupac_formula, compObj.as_dict(), compObj.anonymized_formula,
                compObj.reduced_formula, compObj.chemical_system, compObj.__len__()]
    except:
        print("Warning! Can't parse composition!: "+s)
        return ['', [], '', '', '', 0]

#%% Unifies phase names in the database
# If composition -> keep as is
# if all uppercase (e.g. BCC, FCC) -> keep as is
# otherwise -> make all lowercase

def phaseNameUnifier(s):
    exceptionToUpper = ['b0', 'b1', 'b2', 'a0', 'a1', 'a2']
    try:
        isComp = mg.Composition(s).valid
    except:
        isComp = False

    if s in exceptionToUpper:
        return s.upper()
    elif isComp:
        return s
    elif s.isupper():
        return s
    else:
        return s.lower()

#%% Transforms the structure string into a list of
# individual phases, interpreting (1) multiple phases
# of the same type, (2) composition-defined phases, and
# (3) named phases. Processes them in a unified way.

def structStr2list(s):
    ls = []
    try:
        s = s.replace(' ','')
        tempLs = list(s.split('+'))
        for phase in tempLs:
            if phase[0].isdigit():
                for i in range(int(phase[0])):
                    ls.append(phaseNameUnifier(phase[1:]))
            else:
                ls.append(phaseNameUnifier(phase))
        ls.sort()
        if ls.__len__()>0:
            return [ls, ls.__len__()]
        else:
            return []
    except:
        print('Warning! Error parsing structure list.')
        return []

#%% Process name unifier

def processNameUnifier(s):
    exception = []

    if s in exception:
        return s
    elif s.isupper():
        return s
    else:
        return s.lower()

#%% Processes processing string into a unified-form process list

def processStr2list(s):
    ls = []
    try:
        s = s.replace(' ','')
        tempLs = list(s.split('+'))
        for process in tempLs:
            if process[0].isdigit():
                for i in range(int(process[0])):
                    ls.append(processNameUnifier(process[1:]))
            else:
                ls.append(processNameUnifier(process))
        if ls.__len__()>0:
            return [ls, ls.__len__()]
        else:
            return []
    except:
        print('Warning! Error parsing process list.')
        return []

#%% Convert a pair of metadata and data into ULTERA Database datapoint
def datapoint2entry(metaD, dataP):
    # metadata
    entry = {'meta' : metaD, 'material' : {}, 'property' : {}, 'reference' : {}}

    # composition
    try:
        compList = compStr2compList(dataP['Composition'])
    except:
        print('Warning. Parsing an entry with an empty composition field.')

    try:
        entry['material'].update({
                'formula' : compList[0],
                'compositionDictionary' : compList[1],
                'anonymizedFormula' : compList[2],
                'reducedFormula' : compList[3],
                'system' : compList[4],
                'nComponents' : compList[5]})
    except:
        pass

    # structure
    try:
        structList = structStr2list(dataP['Structure'])
    except:
        print('Warning! Parsing an entry with an empty structure field.')

    try:
        entry['material'].update({
                'structure' : structList[0],
                'nPhases' : structList[1]})
    except:
        pass

    # processing
    try:
        processingList = processStr2list(dataP['Processing'])
    except:
        print('Warning! Parsing an entry with an empty structure field.')

    try:
        entry['material'].update({
                'processes' : processingList[0],
                'nProcessSteps' : processingList[1]})
    except:
        pass

    # comment
    try:
        entry['material'].update({
                'comment' : dataP['Material Comment']})
    except:
        pass

    try:
        entry['property'].update({
            'name' : dataP['Name'],
            'source' : dataP['Source'],
            'temperature' : dataP['Temperature [K]'],
            'value' : dataP['Value [SI]'],
            #'unitName' : dataP['Unit [SI]']
            })
        entry['reference'].update({
                'pointer' : dataP['Pointer'],
                'doi' : dataP['DOI']})
    except:
        pass

    return entry


if __name__ == "__main__":
   upload()
   print('Success!')