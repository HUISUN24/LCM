#Libraries
import sys
import os

#Find DOI
def find():
    foundFile = ''
    foundCount = 0

    doi = sys.argv[1]
    suffixDOI = doi[8:]
    print('\nDOI:  '+doi)
    path = "."
    allFiles = []
    for root, d_names, f_names in os.walk(path):
        for f in f_names:
            name = os.path.join(f)
            if os.path.splitext(name)[1]=='.pdf':
                allFiles.append(name)
    print('Matching with '+str(allFiles.__len__())+' PDFs')
    for f in allFiles:
        if suffixDOI in f:
            foundCount = foundCount+1
            foundFile = f

    if foundCount>0:
        print('\nDOI found in the reference repository.\nFound PDF:'+foundFile)
        if foundCount>1:
            print('Warning! Multiple PDFs matching DOI found.')
        else:
            print('Only one matching PDF found.\n')
    else:
        print('\nDOI not found in the reference respository!\n')

if __name__ == "__main__":
   find()