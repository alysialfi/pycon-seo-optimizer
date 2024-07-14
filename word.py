import requests
from bs4 import BeautifulSoup
from collections import defaultdict
import re
import pandas as pd
from nlp_id.postag import PosTag
import nltk
from itertools import combinations
import json

nltk.download('punkt')
postagger = PosTag() 

# Specify the URL of the website to scrape
url = "http://www.domainesia.com/hosting/"  # Replace with the target URL
valid_categories = {"FW", "NN", "NP", "NNP", "DP"}

# Fetch the webpage
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract text from the body tag
    body_text = soup.body.get_text(separator=' ', strip=True)

    # Tokenize the text into words using regex to handle different delimiters
    words = re.findall(r'\b\w+\b', body_text.lower())

    res = postagger.get_phrase_tag(body_text)
    
    # Grouping phrases with common words
    def group_phrases(data, valid_categories):
        # Filter the phrases by valid categories
        filtered_data = [(phrase[0], phrase[1]) for phrase in data if phrase[1] in valid_categories]

        # Dictionary to store groups of phrases
        grouped_phrases = defaultdict(list)

        # Check for common words and group phrases
        for phrase1, phrase2 in combinations(filtered_data, 2):
            words1 = set(phrase1[0].split())
            words2 = set(phrase2[0].split())
            if words1 & words2:  # Check for intersection of words
                key = " ".join(sorted(words1 & words2))
                grouped_phrases[key].append((phrase1[0], phrase1[1]))
                grouped_phrases[key].append((phrase2[0], phrase2[1]))

        # Remove duplicates within groups
        for key in grouped_phrases:
            grouped_phrases[key] = list(set(grouped_phrases[key]))

        # Remove groups with only one result
        grouped_phrases = {key: value for key, value in grouped_phrases.items() if len(value) > 1}

        return grouped_phrases

    # Group the phrases# Group the phrases
    grouped_phrases = group_phrases(res, valid_categories)
    filtered_grouped_phrases = {key: value for key, value in grouped_phrases.items() if len(value) > 2}
    json_data = json.dumps(filtered_grouped_phrases, indent=2)

    print(json_data)

    # # Print the results
    # for common_words, phrases in grouped_phrases.items():
    #     if len(phrases) > 1:
    #         print(f"Common words: {common_words}")
    #         for phrase, category in phrases:
    #             print(f"  {phrase} ({category})")
    #         print()

    # print(res)

    # # Use defaultdict to count the frequency of each word
    # word_counts = defaultdict(int)
    # for word in words:
    #     word_counts[word] += 1

    # # Convert the word counts to a pandas DataFrame
    # word_counts_df = pd.DataFrame(word_counts.items(), columns=['Word', 'Total'])

    # # Sort the DataFrame by the Total column in descending order
    # word_counts_df = word_counts_df.sort_values(by='Total', ascending=False).reset_index(drop=True)

    # top_20_words = word_counts_df.head(20)

    # # Print the DataFrame
    # # print(top_20_words)
else:
    print(f"Failed to retrieve the webpage. Status code: {response.status_code}")