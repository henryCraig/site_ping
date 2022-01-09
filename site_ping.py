import json
import sys
import time
from datetime import datetime
from subprocess import Popen, PIPE
import subprocess
import re

class SitePing():

    def __init__(self):
        pass

    def ping_sites(self, site_list):
        start_time = datetime.now()
        current_time = datetime.now()
        site_dict = {}

        #We find the difference between the start time and current time,
        #convert to minutes, then check if that difference is less than 5 mins,
        #if its not break out of the loop
        while (current_time - start_time).total_seconds()/60 < 1:
            for site in site_list:
                stdout = Popen(['ping', '-n', '1', site],
                               stdout=PIPE,
                               stderr=subprocess.STDOUT,
                               universal_newlines=True).communicate()[0]

                if "Ping request could not find host" in stdout:
                    site_dict[site] = [stdout.replace("\n", " ")]
                    site_list.remove(site)
                elif site not in site_dict:
                    site_dict[site] = [stdout.replace("\n", " ")]
                else:
                    site_dict[site].append(stdout.replace("\n", " "))

            time.sleep(30)
            current_time = datetime.now()

        #sorts each list
        for site_key in site_dict:
            site_dict[site_key].sort(key=self.sort_site_dict, reverse=True)

        return site_dict

    def sort_site_dict(self, return_string):
        if "Approximate round trip" in return_string:
            avg_rtt_reg = re.compile(r'Average = \d+')
            rtt_num = avg_rtt_reg.search(return_string).group()
            return int(rtt_num[10:])
        else:
            return 0

    def write_to_json(self, ping_dict, file_name="siteList"):
        try:
            json_object = json.dumps(ping_dict, indent=4)
            with open((file_name+".json"), "w") as outfile:
                outfile.write(json_object)
            return True
        except:
            return False

#for command line usage
if __name__ == "__main__":
    PING_INST = SitePing()
    SITE_DICT = PING_INST.ping_sites(sys.argv[1:])
    PING_INST.write_to_json(SITE_DICT)
