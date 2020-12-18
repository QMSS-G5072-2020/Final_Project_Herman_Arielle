def collections(*searches, api_key="ac40e6c2cb345593ed1691e0a8b601bba398e42d85f81f893c5ab709cec63c6c"):
    """
    Returns a complete list of the current collections in the British Columbia University Library with some metadata
    and whether or not specific items are in the list.
    
    By default, it uses the British Columbia Library public API key, and makes two get requests: one to access an endpoint
    with a full list of the collections and a second endpoint with metadata (full name, number of items, and brief
    description).  If the user does not enter an api key, the function returns a warning message suggesting that the user
    register for a private api key.  This function can optionally accept searches for specific collections, and returns
    whether or not they are in the
    full list.
    
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
    # 1. api_key
    if api_key=="ac40e6c2cb345593ed1691e0a8b601bba398e42d85f81f893c5ab709cec63c6c":
        print('This function utilizes the British Columbia Library public API Key by default, '
              'which limits requests to 10 per minute. '
              'Please register for a free private API Key to make up to 200 requests per minute. \n')
    
    # 2. 
    params = {'api_key':api_key}
    r = requests.get(f'https://oc2-index.library.ubc.ca/collections', params=params)
    print('The status of this request is: ', r.status_code, '. Please wait. \n')
    rseries = pd.DataFrame(r.json()).loc[:, ['data']].applymap(str) # change request into dataframe and make it str, to enable merge
    
    # 3. get metadata
    items_dict = {}
    i = 0
    for name in rseries['data'][:10]:
        ritems = requests.get(f'https://oc2-index.library.ubc.ca/collections/{str(name)}', params=params).json()['data']
        items_dict[i] = [name, ritems['title'], ritems['description'], ritems['items']]
        i += 1
     
    # 4. check
    for search in searches:
        if search in ritems['title'] or search in rseries['data'].any():
            print(f'{search} is a currently listed collection. \n')
        else:
            print(f'{search} is not a current collection in the University of British Columbia Library. \n'
                  'Please check your spelling or check the output to see available collections.')    
        
    items_df = pd.DataFrame.from_dict(items_dict, orient='index',
                                      columns=['CollectionID','CollectionName', 'description', 'items'])
    items_clean = items_df.replace(to_replace=[r'</?(p|span|title|i|a)(\s(class|style)="\w*\W*?.?")?>|\r\n|&#\d{1,5}'], value=[''], regex=True)
    
    return items_clean