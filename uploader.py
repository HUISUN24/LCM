#%%

import pandas as pd
import sys
import json
import pymatgen.core as mg
import time
from datetime import datetime
from pymongo import MongoClient

def upload():
    excelFile = sys.argv[1]

    print('Starting the upload process!\nLoading credentials...')

    cred = json.load(open('credentials.json'))
    if cred['name']=='test':
        print('Loaded test credentials. Aborting!')
        return
    print('Loaded credentials for: '+cred['name'])

    # Connect to the MongoDB using the credentails
    client_string = 'mongodb+srv://' + cred['name'] + ':' + cred[
        'dbKey'] + '@testcluster.g3kud.mongodb.net/ULTREA_materials?retryWrites=true&w=majority'
    database_name = 'ULTREA_materials'
    collection_name = cred['name']

    client = MongoClient(client_string)
    collection = client[database_name][collection_name]
    print('Connected to the database.')

    if excelFile=='-PurgeMyCollection':
        print('Warning. All data from your collection will be removed in 5s.\nPress Ctrl+C to abort.')
        time.sleep(5)
        collection.remove({})
        print('Collection purged.')
        return

    #Import metadata
    print('Reading the metadata.')
    metaDF = pd.read_excel(excelFile,
                           usecols="A:F", nrows=4)
    meta = metaDF.to_json(orient="split")
    metaParsed = json.loads(meta)['data']
    # get timestamp
    now = datetime.now()
    dateString = now.strftime('%Y-%d-%b-%H-%M')
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

    # Logging progress into a CSV table
    dataFileName = excelFile.replace('.xls', '').replace('.xlsx', '')
    logger = open(dataFileName+'_REPORT_'+dateString+'.csv', "w")
    logger.write('Composition, Result\n')

    # Import data
    print('Importing data.')
    df2 = pd.read_excel(excelFile,
                       usecols="A:N",nrows=500,skiprows=8)
    result = df2.to_json(orient="records")
    parsed = json.loads(result)
    print('Imported '+str(parsed.__len__())+' datapoints.\n')

    # Convert metadata and data into database datapoints and upload
    for datapoint in parsed:
        comp = datapoint['Composition'].replace(' ','')
        print('Processing: '+comp)
        try:
            uploadEntry = datapoint2entry(metaData, datapoint)
            collection.insert_one(uploadEntry)
            logger.write(comp+',Success!\n')
            print('Succesfully uploaded the datapoint!\n')
        except ValueError as e:
            exceptionMessage = str(e)
            print(exceptionMessage)
            logger.write(comp + ',Fail!,<-------,'+exceptionMessage+'\n')
            print('Upload failed!\n')
            pass
    logger.close()


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
        raise ValueError("Warning! Can't parse composition!: "+s)
        #return ['', [], '', '', '', 0]
    print([compObj.iupac_formula, compObj.as_dict(), compObj.anonymized_formula,
                compObj.reduced_formula, compObj.chemical_system, compObj.__len__()])

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
    print([ls, ls.__len__()])

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
        #print('Warning. Parsing an entry with an empty composition field.')
        raise ValueError("Could not parse the composition! Required for upload. Aborting upload!")
    print('comp',compList)
    entry['material'].update({
            'formula' : compList[0],
            'compositionDictionary' : compList[1],
            'anonymizedFormula' : compList[2],
            'reducedFormula' : compList[3],
            'system' : compList[4],
            'nComponents' : compList[5]})

    # structure
    try:
        if dataP['Structure'] is not None:
            structList = structStr2list(dataP['Structure'])
            entry['material'].update({
                'structure': structList[0],
                'nPhases': structList[1]})
        else:
            print('No structure data!')
    except:
        pass
    print('Structure',structList)
    # processing
    try:
        if dataP['Processing'] is not None:
            processingList = processStr2list(dataP['Processing'])
            entry['material'].update({
                    'processes' : processingList[0],
                    'nProcessSteps' : processingList[1]})
        else:
            print('No process data!')
    except:
        pass

    # comment
    try:
        if dataP['Material Comment'] is not None:
            entry['material'].update({
                    'comment' : dataP['Material Comment']})
    except:
        pass

    try:
        if dataP['Name'] is not None:
            entry['property'].update({
                'name' : dataP['Name'],
                'source' : dataP['Source'],
                'temperature' : dataP['Temperature [K]'],
                'value' : dataP['Value [SI]'],
                #'unitName' : dataP['Unit [SI]']
                })
        else:
            print('No property data!')
            del entry['property']
    except:
        pass

    try:
        if dataP['DOI'] is not None:
            entry['reference'].update({
                    'pointer' : dataP['Pointer'],
                    'doi' : dataP['DOI']})
        else:
            print('No reference data!')
            del entry['reference']
    except:
        pass

    return entry


if __name__ == "__main__":
   upload()