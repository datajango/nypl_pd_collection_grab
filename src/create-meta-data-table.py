import csv
import json
import catalog

# open config to get the API token and other parameters
with open('config.json', 'r') as f:
    config = json.load(f)

my_cat = catalog.Catalog(config)
my_cat.load_pd_collections()

print('| Key | Value |')
print('| ----- | ----- |')

for index, key in enumerate(my_cat.keys):
    print("|{} | {} |".format(key, my_cat.data[61][key]))
