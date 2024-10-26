import requests
import random
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import time

def trends_result(data):
    # Process the data as needed

    # need
    # keyword''
    # mineUrl''
    # competitorUrls[]
    # keyword=hosting murah&sitename=www.domainesia.com&competitor=niagahoster.co.id
    # keyword = data.args.get('keyword')
    # sitename = data.args.get('sitename')

    keyword = data.get('keyword')
    sitename = data.get('sitename')
    competitors = data.get('competitors')

    # print(keyword, sitename, cek)
    # return [keyword, sitename, cek]
    return get_data(keyword, sitename, competitors)

# begin logic

def clean_url(url):
    start = url.find('https://')
    if start == -1:
        return None

    end = url.find('&ved', start)
    if end == -1:
        return url[start:]
    else:
        return url[start:end]

def rank_check(sitename,serp_df,keyword,type):
    counter = 0
    #here is where we count and find our url
    d=[]
    for i in serp_df['URLs']:
        counter += 1
        if sitename in str(i):
            rank = counter
            url = i 
            now = datetime.date.today().strftime("%d-%m-%Y")
            d.append([keyword,rank,url,now,type])
            
    df = pd.DataFrame(d)

    if d:
        df = pd.DataFrame(d)

        df.columns = ['Keyword', 'Rank', 'URLs', 'Date', 'Type']
    else:
        df = pd.DataFrame(columns=['Keyword', 'Rank', 'URLs', 'Date', 'Type'])

    return df
                

def get_data(keyword,sitename,competitors):
    google_url = 'https://www.google.com/search?num=20&q='

    desktop_agent = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:15.0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
    ]

    useragent = random.choice(desktop_agent)    
    headers = {'User-Agent': useragent}

    response = requests.get(google_url + keyword, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the content
        soup = BeautifulSoup(response.text, 'html.parser')

        urls = soup.find_all('div', class_="yuRUbf")
    
        data= []
        for div in urls:
            soup = BeautifulSoup(str(div), 'html.parser')
           
            # Extracting the URL
            url_anchor = soup.find('a')
            if url_anchor:
                url = url_anchor.get('href', "No URL")
            else:
                url = "No URL"
            
            url = clean_url(url)
        
            data.append(url)
            
        serp_df = pd.DataFrame(data,columns =['URLs'])
        serp_df = serp_df.dropna(subset=['URLs'])
        
        results = rank_check(sitename,serp_df,keyword,"My Site")
    
        #competiors
        for competitor in competitors:
            c = rank_check(competitor,serp_df,keyword, "Competitor")
            results = pd.concat([results, c])

        df = pd.DataFrame(results)
        
        df = df.sort_values(by='Rank')
            
    elif response.status_code == 429:
        print('Rate limit hit, status code 429. You are Blocked From Google')
        error_message = 'Rate limit hit, status code 429. You are Blocked From Google'
        df = pd.DataFrame({'status': [error_message]})
    else:
        print(f'Failed to retrieve data, status code: {response.status_code}')
        error_message = f'Failed to retrieve data, status code: {response.status_code}'
        df = pd.DataFrame({'status': [error_message]})

    return df.to_json(orient='records')
                
# desktop = get_data('hosting murah','www.domainesia.com','www.niagahoster.co.id')  
# get_data('hosting','www.domainesia.com',['www.niagahoster.co.id'])
# trends_result()