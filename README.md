# S3CUREFILE
Augusto Vera, April 16th 2017
My first useful Python program, hasher generator SHA256 for windows files within a path tree.

This program uses 2 command line inputs:

PATH to hash, Securefile.py generates a XML database in the same folder where it was placed named s3curefiledb.xml, and in this database it stores all the filenames and file hashes generated for all files in the folder and subfolders contained in PATH.

-v which is a flag that indicates the script to traverse all the filenames stored in s3curefile.xml, and generate again the hash value to compare against the hash value stored in the database.

XML Database:
This script creates a XML database called "s3curefiledb.xml" where it stores all the filenames and corresponding paths, and all the hash values generated. This script uses the SHA256 algorithm to generate the hasn values.

Script logging:
This script generates a log file called "s3curefilelog.csv", if it does not exist, it will generate it when a PATH is passed in as command line.
This script stores information of the activities performed by the script. The first column stores date and time of the action, and the second column the resulting action.
When the script encounters a problem it signals it beggining the log message with * WARNING XX* XX being a number:
    01 for differences encountered in a file hash against the hash stored in the database.
    02 for files missing within the folder structure of the PATH being verified.
    03 for not passing the correct cmd lines.
    04 to indicate that the database is not present, to pass -v cmd successfully first create the hash database on a PATH folde structure.

Examples:
python s3curefile.py "C:\PASAR A USB"  <<<<<---- this indicates to generate all the hash values for the files of folder indicated with subfolders it can end with a backslash or not, it will work anyway.
python s3curefile.py -v <<<<<---- This performs a verification of the hash values of all files in the folder stored in DB against the actual existig files in the folder in disk.    

    


