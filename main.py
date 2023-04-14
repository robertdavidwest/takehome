import time 

import pandas as pd 
import requests
import ijson

from config import INDEX_FILEPATH, OUTPUT_FILEPATH, STATE, PLANTYPE


def getMRFDataFromEin(ein):
    # I found this API by looking at the Network traffic on the page
    # https://www.anthem.com/machine-readable-file/search/
    # when you search by EIN 
    url = f'https://antm-pt-prod-dataz-nogbd-nophi-us-east1.s3.amazonaws.com/anthem/{ein}.json'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception('Failed to get schema')


def getUrlsFromMRFData(data, selectedState, selectedPlanType, urls):
    for item in data["In-Network Negotiated Rates Files"]:
        fields = item['displayname'].split('_')
        state = fields[0]
        planType = fields[1]
        condition = state == selectedState and planType == selectedPlanType
        if (condition):
            urls.add(item['url'])
    return urls


def getUrlsFromEin(ein, urls, state, planType):
    mrfData = getMRFDataFromEin(ein)
    urls = getUrlsFromMRFData(mrfData, state, planType, urls)
    return urls


def getPlanEinsFromIndexFile(filepath, state, planType):
    with open(filepath, 'rb') as f:
        json_iterator = ijson.items(f, 'reporting_structure.item')
        einsSet = set()
        print('Getting eins')
        for i, item in enumerate(json_iterator):
            print('gettin eins', i)
            for p in item['reporting_plans']:
                condition = state in p['plan_name'] 
                condition &= planType in p['plan_name']
                condition &= p['plan_id_type'] == 'EIN' 
                if condition:
                    einsSet.add(p['plan_id'])

        return list(einsSet)                 


def getAllUrls(indexFilepath, state, planType):
    # using sets since they should be cheap to dedup
    # they use hash tables under the hood
    # so should be avg O(1) to add and check if an item is in the set
    urls = set()

    # get all eins before look up to avoid duplication
    eins = getPlanEinsFromIndexFile(indexFilepath, state, planType)
    for i, ein in enumerate(eins):
        print('getting urls for ein', i+1, ' of ', len(eins))
        urls = getUrlsFromEin(ein, urls, state, planType)

    df = pd.DataFrame({'url': list(urls)})
    return df


def main(state, planType, indexFilepath, outpath):
    start = time.time()
    df = getAllUrls(indexFilepath, state, planType)
    df.to_csv(outpath, index=False)
    df = df.url.sort_values()
    end = time.time()
    seconds = end - start
    minutes = seconds/60
    print('Finished in %.2f' % minutes, ' minutes')


if __name__ == '__main__':
    # GOAL : 
    # Answer this: what is the list of file URLs that represent the Anthem PPO network in New York state?

    # Thought Process for solution:

    # From the hints it looks like I'm being encouraged to use the EIN lookup service

    # if you pass an EIN to the EIN lookup service you can get a list of URLs for "In-Network Negotiated Rates Files"
    # subset down these urls to those containing "NY" and "PPO" in the filename and I have the results, iff I have all needed EINs
    # The service appears to have an open API
    # the fn above getMRFDataFromEin(ein) uses this service

    # This solution avoids having to traverse all of the confusing filepaths that are written in the index file

    # NOTE: With more time I would also explore the filepath defined in the index file too
    # I am heavily influenced by the hints and time constraints in finding a quick to code solution

    # One major assumption I am making with this approach is that the set of EINs obtainable from the plan id would yield everything I need
    # Not all plans have EINs.

    main(STATE, PLANTYPE, INDEX_FILEPATH, OUTPUT_FILEPATH)
 


