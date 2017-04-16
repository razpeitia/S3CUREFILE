# April 16th 2017, this source code is public domain.
# Augusto Vera, Monterrey, NL, México.
# @augustweet, averaguilar@outlook.com.

import sys              # This script's command line interface
import csv              # CSV manipulation
import subprocess       # Calling external executables with command line
import configparser     # Module to read from ini files ver. < 3.0
import glob             # Module to read the folder and filenames
import hashlib          # MD5 hash library
import time             # Date and Time module
import os.path          # Pathnames funcions module
from xml.etree import ElementTree as elTree


def mainGenerateHashes(pathToRead):
    countFiles = 0
    xmlDBFile = 's3curefiledb.xml'
    logFileName = 's3curefilelog.csv'
    writeToLog(logFileName, '>>> HASH DB CREATION STARTED: '+ pathToRead)
    #Read the folder structure and save in XML Database
    root = elTree.Element('AllItems')     # create the element Allitems for XML root
    tree = elTree.ElementTree(root)       # and pass it to the created tree
    BLOCKSIZE = 65536 # Block size to read in case of a large file.
    for fileName in glob.iglob(pathToRead + '**\*.*', recursive=True): 
        hasher = hashlib.sha256()
        with open(fileName, 'rb') as afile:
            buf = afile.read(BLOCKSIZE)
            while len(buf) > 0:  # as long as a block was read
                hasher.update(buf)
                buf = afile.read(BLOCKSIZE)
        afile.close()        
        print(hasher.hexdigest())
        root.append(dict_to_elem({'filename':fileName, 'SHA256hash': hasher.hexdigest()}))
        countFiles += 1
    # use last row of XML to store the base path and total number of files hashed
    root.append(dict_to_elem({'basepath':pathToRead, 'totalfiles': str(countFiles)}))
    # Write the XML Database with all the filenames and hashes extracted
    with open(xmlDBFile, 'w', encoding='utf-8') as file:
        tree.write(file, encoding='unicode')
    writeToLog(logFileName, '>>> HASHDB CREATION FINISHED total files hashed: ' + str(countFiles))


def mainVerify():
    logFileName = 's3curefilelog.csv'
    xmlFileName = 's3curefiledb.xml'
    # Generate the tree of XML in memory
    dom = elTree.parse(xmlFileName)
    # pulls all the FILEITEMs under the root along with all the subelements: filename and SHA256hash
    fileItems = dom.findall('FILEITEM')
    totalFilesInDB = dom.findtext("FILEITEM/totalfiles")
    totalFilesVerified = 0
    filesMissing = 0
    verifyPath = dom.findtext("FILEITEM/basepath")                             #<<<--- Extract the entire path and filename
    writeToLog(logFileName, '>>> HASH VERIFICATION STARTED ' + verifyPath)
    print(">>>> ", verifyPath)     
    BLOCKSIZE = 65536 # Block size to read in case of a large file.
    # Next for block: traverse 1 by 1 all the FILEITEMs until len -1
    # because the last FILEITEM is the base path, and file counter.
    for fileItemsIndex in range(0,len(fileItems)-1):                                           
        # then for every FILEITEM in turn, extract the filename frpm XML DB and the paired SHA256hash
        evalList = []
        for chld in fileItems[fileItemsIndex]: 
            evalList.append(chld.text)
        # print('File: ' + files[fil].text, ' Hash: ', hashes[fil].text)
        print('evalList: ', evalList)
        hasher = hashlib.sha256()
        if os.path.isfile(evalList[0]):
            with open(evalList[0], 'rb') as afile: # open the file in the database FILEITEM/filename for binary read
                buf = afile.read(BLOCKSIZE)
                while len(buf) > 0:  # as long as a block was read
                    hasher.update(buf)
                    buf = afile.read(BLOCKSIZE)
            afile.close()
            hashFromFile = hasher.hexdigest()       # Generate the SHA256 file's value
            if hashFromFile != evalList[1]:
                logmsg = "* WARNING 01 * " + evalList[0] + ' hash: ' + hashFromFile + ' db hash: ' + evalList[1]
            else:
                logmsg = 'file OK ' + evalList[0]
            totalFilesVerified += 1
        else:
            logmsg = '* WARNING 02 * the file < ' + evalList[0] + ' > in database is not present'
            filesMissing += 1
        writeToLog(logFileName, logmsg)
    writeToLog(logFileName, '>>> HASH VERIFICATION ENDED: files verified: '\
                            + str(totalFilesVerified) + ' files missing in dir: '\
                            + str(filesMissing))

def logExists(logName):
    return os.path.isfile(logName)


def initLog(logName):
    with open(logName, 'w') as logFile:
        logFileWriter = csv.writer(logFile)
        logFileWriter.writerow([time.strftime('%d/%m/%Y ') + time.strftime('%H:%M:%S'), '[>>> LOG FILE CREATED] > '])
    logFile.close()


def writeToLog(logName, message):
    with open(logName, 'a') as logFile:
        logFileWriter = csv.writer(logFile)
        logFileWriter.writerow([time.strftime('%d/%m/%Y ') + time.strftime('%H:%M:%S'), '[' + message + '] > '])
    logFile.close()
    

def dict_to_elem(dictionary):
    item = elTree.Element('FILEITEM') # Item names cannot contain spaces for proper XML read in XML editors.
    for key in dictionary:
        field = elTree.Element(key.replace(' ',''))
        field.text = dictionary[key]
        item.append(field)
    return item


if __name__ == "__main__":
    # the following two lines are kept in case of debugging without the cmd line
    # mainVerify()
    # mainGenerateHashes('D:\\PASAR A USB\\')
    logFile = 's3curefilelog.csv'
    if not logExists(logFile):
        initLog(logFile)
    # Check the command line arguments
    if len(sys.argv) == 2:
        writeToLog(logFile, 'cmd line received: ' + sys.argv[1])
        if sys.argv[1] == '-v':  # <<<--- if the command passed was -v, then verify files in the path against the XML database
            mainVerify()
        else:
            dirArgument = sys.argv[1] + '\\' # it works if the path is ended in \ or not
            if not os.path.exists(dirArgument):
                writeToLog(logFile, 'Path does not exist: ' + sys.argv[1])
            elif not os.path.isdir(dirArgument):
                writeToLog(logFile, 'Path is not a directory: ' + sys.argv[1])
            else:
                print(dirArgument)
                mainGenerateHashes(dirArgument) # <<<--- If the command passed was a path, generate the hashes
        exit(0)
    else:
        writeToLog(logFile, '* WARNING 03 * incorrect cmd line USAGE: s3curefile (PATH or -v)')
        exit(1)