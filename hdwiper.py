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
import smtplib

from time import strftime

parser = argparse.ArgumentParser()
parser.add_argument("-d", help="Please enter a valid drive path", required=True)
args = parser.parse_args()

path = args.d

script_path = os.path.dirname(os.path.abspath(__file__))
myTime = strftime("%Y-%m-%d-%H%M%S")
log_output = raw_input("Give the log file a name:  ")

email_log_subject = "HDWiper complete: %s" % log_output
email_server = "localhost"
email_for_logs = "ENTER NAME HERE"
email_port = "25"

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
        f = open(script_path + "/" + log_output,'w')
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

def email_log_files(log_text):
    log_text = bytes.decode(log_text)
    msg = "Subject: %s\n%s"% (email_log_subject,log_text)
    s = smtplib.SMTP(email_server,email_port)
    s.sendmail(email_for_logs,email_for_logs,msg)
    s.quit()

if __name__ == "__main__":
        if(ask_confirmation("You are about to wipe out '%s'.  Are you sure?  This will wipe out all data!" % path)):
            check_disk(path)
            run_smartmon(path)
            shred_disk(path)
            email_log_files("HDWiper has finished with %s" % log_output)
        else:
            print("Mission aborted!")
            sys.exit(1)

