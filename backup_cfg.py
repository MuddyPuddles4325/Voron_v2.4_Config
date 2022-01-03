### Backup Klipper Config files for git checkin ###
from pathlib import Path
import os
from shutil import copyfile
import json
import subprocess
from datetime import datetime

### Path to your config folder you want to backup
klipperCfgPath = '/home/pi/klipper_config/'

### Path to your Klipper folder, by default that is '~/klipper'
klipper_folder= Path('/home/pi/klipper')

### Path to your Moonraker folder,by default that is '~/moonraker'
moonraker_folder= Path('/home/pi/moonraker')

### Path to your Mainsail folder, by default that is '~/mainsail'
mainsail_folder= Path('/home/pi/mainsail/.version')

### Path to your Fluidd folder, by default that is '~/fluidd'
fluidd_folder= Path('/home/pi/fluidd/.version')

### Path to your config backup repo folder
gitRepoPath = '/home/pi/klipper_cfg_backup/Voron_v2.4_Config/'
gitBackupPath = gitRepoPath + 'klipper_config/'

def getVersionInfo():
    versions = ""
    if(Path.exists(klipper_folder) == True):
        os.chdir(klipper_folder)
        out = subprocess.check_output(['git', 'rev-parse', '--short=7', 'HEAD']).decode("utf-8").strip()
        versions = versions +  "Klipper on commit: " + out + "\n"
    if(Path.exists(moonraker_folder) == True):
        os.chdir(moonraker_folder)
        out = subprocess.check_output(['git', 'rev-parse', '--short=7', 'HEAD']).decode("utf-8").strip()
        versions = versions +  "Moonraker on commit: " + out + "\n"
    
    if(Path.exists(mainsail_folder) == True):
        versions = versions +  "Mainsail version: "  + open(mainsail_folder).readline() + "\n"
    if(Path.exists(fluidd_folder) == True):
        versions = versions + "Fluidd version: " + open(fluidd_folder).readline() + "\n"
    
    return versions

def copyLatestFiles():
    os.chdir('/home/pi/klipper_cfg_backup/')
    ## Get list of files to back up ##
    cfgFolderList = os.listdir(klipperCfgPath)
    backupList = []
    for file in cfgFolderList:
        if not file.startswith('printer-202') and not file.startswith('.'):
            backupList.append(file)

    ## Clean up old files that are not in current config directory ##
    backupFolderList = os.listdir(gitBackupPath)
    for file in backupFolderList:
        if not file in backupList:
            os.remove(Path(gitBackupPath + file)) 
            print("Deleting removed file: " + file)

    ## Copy all other files to GIT backup folder ##
    for file in backupList:
        if(file == 'mooncord.json'):
            ## Remove tokens to avoid revealing secret keys     
            mooncord = json.load(open(Path(klipperCfgPath + file)))
            mooncord['connection']['bot_token'] = ''
            mooncord['connection']['bot_application_key'] = ''
            mooncord['connection']['bot_application_id'] = ''
            with open(Path(gitBackupPath + file), "w") as outfile:
                json.dump(mooncord, outfile, indent=4, sort_keys=False)
        else:
            copyfile(Path(klipperCfgPath + file), Path(gitBackupPath + file))
            print("Copied file to " + gitBackupPath + file)

#change directory to git repo path and commit changes
#manually run git config --global credential.helper store to avoid log in requirements
now = datetime.now()
commmitComment = "Autocommit from " + now.strftime("%Y/%m/%d, %H:%M:%S") + "\n\n" + getVersionInfo()
copyLatestFiles()
os.chdir(gitRepoPath)
subprocess.call(["git", "pull"])
subprocess.call(["git", "add","*"])
subprocess.call(["git", "commit", "-m", commmitComment])
subprocess.call(["git", "push"])
