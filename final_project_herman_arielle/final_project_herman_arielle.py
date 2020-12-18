import requests
import os
import pandas as pd
import json
import numpy as np
import time

def collections(*searches, api_key="ac40e6c2cb345593ed1691e0a8b601bba398e42d85f81f893c5ab709cec63c6c"):
    """
    Returns a complete list of the current collections in the British Columbia University Library with some metadata
    and whether or not specific items are in the list.
    
    By default, it uses the British Columbia Library public API key, and makes two get requests: one to access an endpoint
    with a full list of the collections and a second endpoint with metadata (full name, number of items, and brief
    description).  If the user does not enter an api key, the function returns a warning message suggesting that the user
    register for a private api key.  This function can optionally accept searches for specific collections, and returns
    whether or not they are in the full list.  Finally, this function automatically cleans the descriptions of html jargon.
    
    Parameters:
    *searches (str): any character string.
    api_key (str): accepts a private api key registered through the British Columbia University Library:
        https://open.library.ubc.ca/docs#reference-search-params
        
    Returns:
    pd.DataFrame containing the full name, nickname, description, and number of items in each collection.
    
    Example:
    collections("darwin", "aaah")
    >>>
    
    """
    # 1. set up
    if api_key=="ac40e6c2cb345593ed1691e0a8b601bba398e42d85f81f893c5ab709cec63c6c":
        print('This function utilizes the British Columbia Library public API Key by default, '
              'which limits requests to 10 per minute. ')
    assert isinstance(api_key, str), "Please enter your api_key as a string."
    params = {'api_key': api_key}
    
    # 2. lists of available collections
    try:          
        r = requests.get(f'https://oc2-index.library.ubc.ca/collections', params=params)
    except Exception as err:
        print(f'Other error occured: {err}')
    else:
        print('The status of the first request is: ', r.status_code, '. Please wait. \n')
    rseries = pd.DataFrame(r.json()).loc[:, ['data']].applymap(str) # change request into dataframe and make it str, to enable merge
    
    # 3. get metadata
    items_dict = {}
    i = 0
    for name in rseries['data']:
        try:
            ritems = requests.get(f'https://oc2-index.library.ubc.ca/collections/{str(name)}', params=params)
        except Exception as err:
            print(f'Other error occured: {err}')
        else:
            if i == 0:
                print(f'The status of the second request is: {ritems.status_code}.  Please wait. \n')
        ritems_json = ritems.json()['data']
        items_dict[i] = [name, ritems_json['title'], ritems_json['description'], ritems_json['items']]
        if i == round(len(rseries['data'])/2):
            print('Halfway there! \n')
            time.sleep(10)
        i += 1
        
    items_df = pd.DataFrame.from_dict(items_dict, orient='index',
                                      columns=['CollectionID','CollectionName', 'description', 'items'])
    items_clean = items_df.replace(to_replace=[r'</?(p|span|title|i|a)(\s(class|style)="\w*\W*?.?")?>|\r\n|&#\d{1,5}'], value=[''], regex=True)
    
    # 4. check if optional argument in collections
    for search in searches:
        if isinstance(search, str):
            if (items_clean['CollectionID'] == search).any() == True or (items_clean['CollectionName'] == search).any() == True:
                print(f'{search} is a currently listed collection. \n')
            else:
                print(f'{search} is not a current collection in the University of British Columbia Library. \n'
                      'Please check your spelling or check the output to see available collections. \n' )
        else:
            print(f'Cannot parse search term: {search}.  Please enter search term as a string.')
        
    return items_clean



def structures(collection="", api_key="ac40e6c2cb345593ed1691e0a8b601bba398e42d85f81f893c5ab709cec63c6c"):
    params = {'api_key': api_key}
    if api_key == "ac40e6c2cb345593ed1691e0a8b601bba398e42d85f81f893c5ab709cec63c6c":
        print('This function utilizes the University of British Columbia public api key by default.'
              'You can register for a free private api key that will be able to perform 200 requests per minute. \n')
        
    assert isinstance(collection, str), "Please enter a character string for collection parameter."
    assert isinstance(api_key, str), "Please enter your api_key as a string."
        
    try:
        rthings = requests.get(f'https://oc-index.library.ubc.ca/collections/{str(collection)}/items', params=params)
        things = [rthings.json()['data'][thing]['_id'] for thing in range(0, len(rthings.json()['data']))]
    
    except Exception as err:
        print(f'Other error occured: {err}')
    else:
        print(f'The request to retrieve the list of items in a collection was successful, and the status code is: {rthings.status_code}.')
        print(f'Please wait while collecting field structure information on {len(things)} items. \n')
    
    structures = {}
    i = 0
    j = 0
    for thing in things:
        try:
            rfields = requests.get(f'https://oc-index.library.ubc.ca/collections/{str(collection)}/items/{str(thing)}')
            fields = rfields.json()['data'].keys()
        except Exception as err:
            print(f'Other error occured: {err}.')
        else:
            if list(fields) not in list(structures.values()):
                structures[i] = list(fields)
                i += 1
        if j == 0:
            print(f'The status code for the request to retrieve the structures in the collection is: {rfields.status_code}. \n')
        j += 1
    print(f'There are {len(list(structures.values()))} field structures in this collection.')
    return structures

def difference_two(struct1, struct2):
    assert isinstance(struct1, list), "struct1 must be a list item."
    assert isinstance(struct2, list), "struct2 must be a list item."
    
    x = list(set(struct1)-set(struct2))
    y = list(set(struct2)-set(struct1))
    differences = {}
    differences[0] = {"struct1Fields": len(struct1), "uniqueComponents": x}
    differences[1] = {"struct2Fields": len(struct2), "uniqueComponents": y}
    return differences