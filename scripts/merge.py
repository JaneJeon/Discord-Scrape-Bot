# script to merge two or more log files of same format
import os, sys

if len(sys.argv) < 3:
	exit(-1)
sys.argv.pop(0)

def shell(command):
	os.popen(command).read()

shell('echo > temp.txt')
for log in sys.argv:
	shell(f'echo "$(cat {log})" >> temp.txt')
shell('echo "$(cat temp.txt | sort -u)" > result.txt; rm temp.txt')