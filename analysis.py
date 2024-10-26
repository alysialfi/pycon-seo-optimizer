import requests
import random
from bs4 import BeautifulSoup
from collections import defaultdict
import re
import pandas as pd
from nlp_id.postag import PosTag
from itertools import combinations
import json

postagger = PosTag()

def analysis_result(data):
    # Specify the URL of the website to scrape
    sitename = data.get('sitename')
    # url = "http://www.domainesia.com/hosting/"  # Replace with the target URL
    valid_categories = {"FW", "NN", "NP", "NNP", "DP"}
    category_labels = {
        "FW": "Foreign Word",
        "NN": "Noun",
        "NP": "Noun Phrase",
        "NNP": "Proper Noun",
        "DP": "Data Phrase"
    }

    # Fetch the webpage
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': sitename
    }
    response = requests.get(sitename, headers=headers)
    keywords_list = []

    # return response

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        
        if meta_keywords:
            keywords_content = meta_keywords.get('content')
            keywords_list = [keyword.strip() for keyword in keywords_content.split(',')]
        else:
            match = re.search(r'/([^/]+)$', sitename)
            if match:
                route = match.group(1).replace("-", " ")
                keywords_list = [route]

        body_text = soup.body.get_text(separator=' ', strip=True)
        res = postagger.get_phrase_tag(body_text)
        # return res
        result_json = []

        category_count = defaultdict(lambda: defaultdict(int))

        for phrase, category in res:
            if category in valid_categories:
                category_count[category][phrase] += 1

        def contains_keywords(phrase, keywords):
            phrase_lower = phrase.lower()
            for keyword in keywords:
                if keyword.lower() in phrase_lower:
                    return True
            return False

        matching_results = defaultdict(lambda: defaultdict(int))

        for category, phrases in category_count.items():
            if category == "NP":
                for phrase, count in phrases.items():
                    if contains_keywords(phrase, keywords_list):
                        matching_results[category][phrase] = count

        for category, phrases in matching_results.items():
            category_string = category_labels.get(category, "Unknown Category")
            result_json.append({
                "category": category_string,
                "phrases": [{"phrase": phrase, "count": count} for phrase, count in phrases.items()]
            })
        
        for category, phrases in category_count.items():
            if category != "NP":
                filtered_phrases = {phrase: count for phrase, count in phrases.items() if count > 5}
                if filtered_phrases:
                    category_string = category_labels.get(category, "Unknown Category")
                    result_json.append({
                        "category": category_string,
                        "phrases": [{"phrase": phrase, "count": count} for phrase, count in phrases.items() if count > 5]
                    })

        final_json = json.dumps(result_json, indent=4)
        return final_json
    else:
        result = {
            "status": "failed",
            "content": 'cannot request to targeted URL',  # This could be further processed text or data
            "status_code": response.status_code
        }
        return result
        # print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
