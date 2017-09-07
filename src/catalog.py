import requests
import urllib
import pprint
import os.path
import json
import csv

class Catalog(object):

    # 'Alternative Title'
    # 'Contributor',
    # 'Database ID'
    # 'Date'
    # 'Date End'
    # 'Date Start'
    # 'Description'
    # 'Digital Collections URL'
    # 'Genre'
    # 'Identifier Accession Number'
    # 'Identifier BNumber'
    # 'Identifier Call Number'
    # 'Identifier ISBN'
    # 'Identifier ISSN'
    # 'Identifier Interview ID'
    # 'Identifier LCCN'
    # 'Identifier OCLC/RLIN''Identifier Postcard ID'
    # 'Language'
    # 'Note'
    # 'Number of Items'
    # 'Physical Description Extent'
    # 'Physical Description Form'
    # 'Place Of Publication'
    # 'Publisher'
    # 'Resource Type'
    # 'Subject Geographic'
    # 'Subject Name'
    # 'Subject Temporal'
    # 'Subject Title'
    # 'Subject Topical'
    # 'Title'
    # 'UUID'

    def __init__(self, config):

        self.token = config['token']
        self.api_url = config['api_url']
        self.img_url = config['img_url']
        self.data_path = config['data_path']
        self.pd_collections = config['pd_collections']
        self.keys = []
        self.data = []
        self.remote_calls = 0
        self.downloads = 0

    def load_pd_collections(self):
        self.data = []
        self.keys = []

        filename = self.pd_collections
        with open(filename, encoding="utf8") as csvfile:
            reader = csv.DictReader(csvfile)
            idx = 0
            for row in reader:
                self.data.append(row)
                idx += 1

        self.keys = sorted(self.data[0].keys())

    def search(self, key):
        rows = []

        for row in self.data:

            haystack = row['Title'].lower()
            needle = key.lower()

            res = haystack.find(needle)
            if res > 0:
                print('search found:', row['Title'])
                rows.append(row)

            haystack = row['UUID'].lower()
            needle = key.lower()

            res = haystack.find(needle)
            if res > 0:
                print('search found:', row['UUID'], row['Title'])
                rows.append(row)
        return rows

    def get_url(self, url, filename):
        if os.path.exists(filename):
            with open(filename) as json_data:
                response = json.load(json_data)
        else:
            response = requests.get(url, headers={'Authorization':'Token token=' + self.token})
            self.remote_calls+=1
            with open(filename, 'w') as outfile:
                json.dump(response, outfile)

        return response

    def get_captures(self, uuid, page):
        url = self.api_url + 'items/' + uuid + '?withTitles=yes&per_page=500&page=' + str(page)
        call = requests.get(url, headers={'Authorization ': 'Token token=' + self.token})
        self.remote_calls += 1
        return call.json()

    def get_item(self, uuid, page):
        url = self.api_url + 'items/mods/' + uuid + '?per_page=500&page=' + str(page)
        call = requests.get(url, headers={'Authorization': 'Token token=' + self.token})
        self.remote_calls += 1
        return call.json()

    def get_container(self, uuid, page):
        url = self.api_url + '/collections/' + uuid + '?per_page=500&page=' + str(page)
        call = requests.get(url, headers={'Authorization': 'Token token=' + self.token})
        self.remote_calls += 1
        return call.json()

    def get_verb(self, uuid, page, verb, func):

        if not os.path.exists(os.path.join(self.data_path, 'collections')):
            os.makedirs(os.path.join(self.data_path, 'collections'))

        save_filename = os.path.join(self.data_path, 'collections', uuid + "_" + verb + "_" + str(page) + ".json")
        if os.path.exists(save_filename):
            with open(save_filename) as json_data:
                response = json.load(json_data)
        else:
            response = func(uuid, page)

            with open(save_filename, 'w') as outfile:
                json.dump(response, outfile)

        pretty_filename = os.path.join(self.data_path, 'collections', uuid + "_" + verb + "_" + str(page) + ".txt")

        if not os.path.exists(pretty_filename):
            with open(pretty_filename, 'wt', encoding="utf8") as out:
                pp = pprint.PrettyPrinter(indent=4, width=256, stream=out)
                pp.pprint(response)

        return response

    def fetch(self, uuid, page):

        capture_response = self.get_verb(uuid, page, 'capture', self.get_captures)
        item_response = self.get_verb(uuid, page, 'item', self.get_item)
        container_response = self.get_verb(uuid, page, 'container', self.get_container)

        return capture_response, item_response, container_response

    def download_collection(self, collection_info, capture_types={'g'}):

        title = collection_info['Title']
        collection_url = collection_info['Digital Collections URL']
        #print(collection_url)
        uuid = collection_info['UUID']

        #image_path = os.path.join(self.data_path, 'images', (title[:50]) if len(title) > 50 else title)
        image_path = os.path.join(self.data_path, 'images', uuid)

        if not os.path.exists(image_path):
            os.makedirs(image_path)

        print('Title:',title)
        print('Path:', image_path)

        capture_response, item_response, container_response = self.fetch(uuid, page=1)

        capture_items = capture_response['nyplAPI']['response']['capture']
        num_items = int(container_response['nyplAPI']['response']['numItems'])
        num_results = int(container_response['nyplAPI']['response']['numResults'])

        print('num_items:', num_items)
        print('num_results:', num_results)
        print('number of capture_items:', len(capture_items))

        total_pages = int(capture_response['nyplAPI']['request']['totalPages'])
        print('total_pages:', total_pages)

        page = int(capture_response['nyplAPI']['request']['page'])
        #print('page:', page)

        for page_index in range(1, total_pages+1):
            print('Page:', page_index)

            if page_index > 1:
                capture_response, item_response, container_response = self.fetch(uuid, page=page_index)

                capture_items = capture_response['nyplAPI']['response']['capture']
                #num_items = int(container_response['nyplAPI']['response']['numItems'])
                #num_results = int(container_response['nyplAPI']['response']['numResults'])

            for capture_item in capture_items:
                image_title = capture_item['title']
                print('image_title:', image_title)
                image_id = capture_item['imageID']
                print('image_id:', image_id)

                try:
                    high_res_link_url = capture_item['highResLink']

                    if 'tif' in capture_types:
                        filename = image_id + ".tif"
                        full_filename = os.path.join(image_path, filename)
                        try:
                            if not os.path.exists(full_filename):
                                print('downloading:', full_filename)
                                urllib.request.urlretrieve(high_res_link_url, full_filename)
                                self.downloads += 1
                        except ConnectionResetError as e:
                            print('ConnectionResetError - Network Exception getting image', full_filename)

                        except urllib.error.HTTPError as httperr:
                            print('urllib.error.HTTPError - Network Exception getting image', full_filename)

                except KeyError as keyerr:
                    print('Exception caught KeyError', keyerr)

                #print(capture_item)

                images_to_download = []

                if 'imageLink' in capture_item:
                    imageLink = capture_item['imageLink']
                    images_to_download.append(imageLink)

                if 'imageLinks' in capture_item and capture_item['imageLinks'] is not None:
                    for imageLink in capture_item['imageLinks']['imageLink']:
                        images_to_download.append(imageLink)


                for image_link in images_to_download:
                    parsed = urllib.parse.urlparse(image_link)
                    qs = urllib.parse.parse_qs(parsed.query)
                    image_id = qs['id'][0]
                    image_type = qs['t'][0]
                    #image_suffix = qs['suffix'][0]

                    if image_type in capture_types:
                        filename = image_id + "_" + image_type + ".jpg"
                        full_filename = os.path.join(image_path, filename)

                        try:
                            if not os.path.exists(full_filename):
                                urllib.request.urlretrieve(image_link,  full_filename)
                                self.downloads += 1
                                print('downloaded', full_filename)
                            #else:
                            #    print('exists', full_filename)
                        except ConnectionResetError as e:
                            print('Network Exception getting image', full_filename)