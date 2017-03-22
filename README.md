# alertlogic
scripts for working with alertlogic

# AL_TM
* Connect to Threat Manager, 
* Identify my customer ID and all my child accounts
* Collect metrics about # of appliances, protected hosts, hosts, policies, etc
* If prompted, output the resulting data as CSV
* This is designed to run nightly and insert the data into a tracking database table for long-term trending

$ python al_tm.py -u cloud_defender_username -p password -o 
