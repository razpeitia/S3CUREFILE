import sys              # This script's command line interface
import csv              # CSV manipulation
import subprocess       # Calling external executables with command line
import configparser     # Module to read from ini files ver. < 3.0
import glob             # Module to read the folder and filenames
import hashlib          # MD5 hash library
import time             # Date and Time module
import os.path          # Pathnames funcions module
from xml.etree import ElementTree as et


def mainGenerateHashes(pathToRead):
    countFiles = 0
   
    if not logExists():
        initLog('s3curefilelog.csv')
    writeToLog('hash database creation start dir: '+ pathToRead)

    #Read the folder structure and save in XML Database
    root = et.Element('AllItems')     # create the element first for XML root
    tree = et.ElementTree(root)       # and pass it to the created tree
    BLOCKSIZE = 65536 # Block size to read in case of a large file.
    hasher = hashlib.sha256()
    for fileName in glob.iglob(pathToRead + '**\*.*', recursive=True): 
        with open(fileName, 'rb') as afile:
            buf = afile.read(BLOCKSIZE)
            while len(buf) > 0:  # as long as a block was read
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        print(hasher.hexdigest())
        root.append(dict_to_elem({'filename':fileName, 'SHA256hash': hasher.hexdigest()}))
        countFiles += 1
    # Write the XML Database with all the filenames and hashes extracted
    xmlDBFile = 's3curefiledb.xml'
    with open(xmlDBFile, 'w', encoding='utf-8') as file:
        tree.write(file, encoding='unicode')
    writeToLog('hash database finished files hashed: ' + str(countFiles))


def logExists():
    return os.path.isfile("s3curefilelog.csv")


def initLog(logName):
    with open(logName, 'w') as csvfile:
        fieldnames = ['datetime', 'message']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()


def writeToLog(message):
    with open('s3curefilelog.csv', 'a') as csvfile:
        fieldnames = ['datetime', 'message']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({'datetime': time.strftime('%d/%m/%Y|') + time.strftime('%H:%M:%S'), 'message': message})


# Create one record for XML database of file hashes
def dict_to_elem(dictionary):
    item = et.Element('FILEITEM') # Item names cannot contain spaces for proper XML read in XML editors.
    for key in dictionary:
        field = et.Element(key.replace(' ',''))
        field.text = dictionary[key]
        item.append(field)
    return item

# >>>>>>>>_________ CORREGIR LA INCONSISTENCIA DEL CMD LINE, SI PASO DIRECTORIO CON ESPACIOS Y "", NO HACE RECURSION
if __name__ == "__main__":
       # Check the command line arguments
    if len(sys.argv) == 2:
        writeToLog('[cmd line] > ' + sys.argv[1])
        if sys.argv[1] == '-v':
            #mainVerify()
            writeToLog(sys.argv[1])
            print('verify')
        else:
            dirArgument = sys.argv[1] + '\\' # it works if the path is ended in \ or not
            if not os.path.exists(dirArgument):
                writeToLog('[Path does not exist] > ' + sys.argv[1])
            elif not os.path.isdir(dirArgument):
                writeToLog('[Path is not a directory] > ' + sys.argv[1])
            else:
                print(dirArgument)
                mainGenerateHashes(dirArgument)
        exit(0)
    else:
        writeToLog('[incorrect cmd line] USAGE: s3curefile (PATH or -v)')
        exit(1) #regresa estatus 1, checar con echo $?
        #main()