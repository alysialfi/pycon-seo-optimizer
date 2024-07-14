import requests
import random
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import time
from halo import Halo
from termcolor import colored

# Set up the spinner animation
spinner = Halo(text='', spinner='dots')
# Start the spinner
spinner.start()

# inputs
keyword = 'hosting'
sitename = "www.domainesia.com"

competitor1 = "www.niagahoster.co.id"
# competitor2 = "https://idwebhost.com/"
# competitor3 = "https://www.rumahweb.com/"

# competitors = [competitor1,competitor2,competitor3]
competitors = [competitor1]

desktop_agent = [
    # Updated Chrome 110 on Windows
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',

    # Updated Chrome 110 on MacOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',

    # Updated Firefox 105 on MacOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:105.0) Gecko/20100101 Firefox/105.0',

    # Updated Safari 15 on MacOS
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:15.0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
]

def clean_url(url):
    """
   Cleans a given URL by extracting the portion starting from 'https://'
   up to the '&ved' parameter, if present.

   Parameters:
   url (str): The URL to be cleaned.

   Returns:
   str: The cleaned URL or None if 'https://' is not found.
   """
    # Find the start of 'https://'
    start = url.find('https://')
    if start == -1:
        return None  # 'https://' not found in the URL

    # Find the end position, which is the start of '&ved'
    end = url.find('&ved', start)
    if end == -1:
        # If '&ved' is not found, return the URL from 'https://' onwards
        return url[start:]
    else:
        # Return the URL from 'https://' up to '&ved'
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
            #print(keyword,rank,url, now)
            
    df = pd.DataFrame(d)

    if d:  # Check if the list 'd' is not empty
        df = pd.DataFrame(d)
        df.columns = ['Keyword', 'Rank', 'URLs', 'Date', 'Type']
    else:
        # Create an empty DataFrame with the specified columns
        df = pd.DataFrame(columns=['Keyword', 'Rank', 'URLs', 'Date', 'Type'])

    return df
                

def get_data(keyword,sitename,device):
    # Google Search URL
    google_url = 'https://www.google.com/search?num=20&q='

    print(colored("- Checking  Desktop Rankings" ,'black',attrs=['bold']))
    useragent = random.choice(desktop_agent)
    headers = {'User-Agent': useragent}
    print(headers)

    # Make the request
    response = requests.get(google_url + keyword, headers=headers)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the content
        soup = BeautifulSoup(response.text, 'html.parser')
            
        device.lower() == 'desktop'
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
        
        print(colored(f"- Rankings results for {sitename}",'black',attrs=['bold']))
        print(results)
    
        #competiors
        for competitor in competitors:
            c = rank_check(competitor,serp_df,keyword, "Competitor")
            results = pd.concat([results, c])

        df = pd.DataFrame(results)
        
        df = df.sort_values(by='Rank')
            
    elif response.status_code == 429:
        # Handle rate limiting
        print('Rate limit hit, status code 429. You are Blocked From Google')
        error_message = 'Rate limit hit, status code 429. You are Blocked From Google'
        df = pd.DataFrame({'status': [error_message]})
    else:
        # Handle other status codes
        print(f'Failed to retrieve data, status code: {response.status_code}')
        error_message = f'Failed to retrieve data, status code: {response.status_code}'
        df = pd.DataFrame({'status': [error_message]})
        
    print(colored(f"- Competitors Ranking results",'black',attrs=['bold']))   
    print(df)   
    
    return df

desktop = get_data(keyword,sitename,'desktop')
