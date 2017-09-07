#------------------------------------------------------------------------------
# Written by Anthony L. Leotta 9/6/2017
#------------------------------------------------------------------------------
import json
import catalog

# open config to get the API token and other parameters
with open('config.json', 'r') as f:
    config = json.load(f)

my_cat = catalog.Catalog(config)
my_cat.load_pd_collections()

searchs = ['Aegypten']

for keyword in searchs:
    results = my_cat.search(keyword)
    for result in results:
        #my_cat.download_collection(result, {'tif', 'g', 'b', 'f', 'r', 't', 'v', 'w'})
        #my_cat.download_collection(result, {'tif', 'g', 'r', 'w'})
        #my_cat.download_collection(result, {'tif', 'g', 'r', 'w'})
        my_cat.download_collection(result, {'g', 'r', 'w'})

print('Run Stats:')
print('Remote API Calls:',my_cat.remote_calls)
print('Image Downloads:',my_cat.downloads)