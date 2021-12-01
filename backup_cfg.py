### Backup Klipper Config files for git checkin ###
from pathlib import Path
import os
from shutil import copyfile
import json
import subprocess
os.chdir('/home/pi/klipper_cfg_backup/')

klipperCfgPath = '/home/pi/klipper_config/'
gitRepoPath = '/home/pi/klipper_cfg_backup/Voron_v2.4_Config/'
gitBackupPath = gitRepoPath + 'klipper_config/'


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
os.chdir(gitRepoPath)
subprocess.call(["git", "add","*"])
subprocess.call(["git", "commit", "-m", "Scripted Backup"])
subprocess.call(["git", "push"])