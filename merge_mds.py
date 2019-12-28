"""
Python script to merge all file in  folder with .md
and merge them in a target file
"""


OUTPUT = 'README.md'
MD_FOLDER = 'docs'


from os import listdir
from os.path import isfile, join


target_file = open(OUTPUT, 'w')
for file_name in sorted(listdir(MD_FOLDER+'/')):
    if file_name.endswith('.md'):
        file = open(MD_FOLDER+'/'+file_name, 'r')

        target_file.write(file.read())
        target_file.write('\n\n---\n\n')

        file.close()
target_file.close()