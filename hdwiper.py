#!/usr/bin/python

'''
Summary:
    Script will -
        ask user for the point of the drive (i.e. /dev/sda)
        run smartmontools
        output the report to it's own folder (datestamp folder?)
        then run shred on the drive
'''
import argparse
import stat
import os
import subprocess
import sys
from time import strftime

parser = argparse.ArgumentParser()
parser.add_argument("-d", help="Please enter a valid drive path", required=True)
args = parser.parse_args()

path = args.d

myTime = strftime("%Y-%m-%d-%H%M%S")
log_output = raw_input("Give the log file a name:  ")

# check if disk is really there...
def check_disk(path):
    try:
        return stat.S_ISBLK(os.stat(path).st_mode)
    except:
        return False



# run smartctl on the drive passed
# and output a log
def run_smartmon(path):
    try:
        print("Running smartmon")
        smart_result = subprocess.Popen(
            ['smartctl','-H',path],
            stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        output,err = smart_result.communicate()
        rc = smart_result.returncode
        log = (output)
        f = open(log_output,'w')
        f.write(log)
        f.close()
    except:
        print("Something went wrong while running smartctl.  Make sure the path to the disk is correct.  Also, do not add a / to the end of the line.  Only enter /dev/sdx")
        sys.exit(1)

# kill the disk
def shred_disk(path):
        print("Running shred...")
        kill_disk = subprocess.Popen(['shred','-vfz','-n 1',path],)
        output,err = kill_disk.communicate()
        kill_return = kill_disk.returncode



def ask_confirmation(question,default="yes"):
        valid = {"yes":True,"y":True,"no":False,"n":False}
        if default is None:
                prompt = " [y/n]"
        elif default == "yes":
                prompt = " [Y/N]"
        elif default == "no":
                prompt = " [y/N]"
        else:
             raise ValueError("Invalid answer!")

        while True:
             sys.stdout.write(question + prompt)
             choice = raw_input().lower()
             if default is not None and choice == '':
                     return valid[default]
             elif choice in valid:
                     return valid[choice]
             else:
                     sys.stdout.write("Please respond with yes, no, y or n")

if __name__ == "__main__":
        if(ask_confirmation("You are about to wipe out '%s'.  Are you sure?  This will wipe out all data!" % path)):
	        check_disk(path)
	        run_smartmon(path)
	        shred_disk(path)
        else:
                print("Mission aborted!")
                sys.exit(1)

