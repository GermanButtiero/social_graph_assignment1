import urllib.request
import urllib.parse
import json
import regex as re
import pandas as pd
from tqdm import tqdm
import os


# List of mainstream rock performers
# wiki_url = https://en.wikipedia.org/wiki/List_of_mainstream_rock_performers

baseurl = "https://en.wikipedia.org/w/api.php?"
action = "action=query"
title = "titles=List_of_mainstream_rock_performers"
content = "prop=revisions&rvprop=content"
dataformat ="format=json"
rvslots = "rvslots=main"


query = "{}{}&{}&{}&{}&{}".format(baseurl, action, content, title, dataformat, rvslots)

headers = {"User-Agent" : "MyWikipediaClient/1.0 (example@example.com)"} # just use this dict as-is.
wikirequest = urllib.request.Request(query,None,headers)    # Needed to pass error 403
wikiresponse = urllib.request.urlopen(wikirequest)
wikidata = wikiresponse.read()
wikitext = wikidata.decode('utf-8')

# Load JSON and extract page content
wiki_json = json.loads(wikitext)
pages = wiki_json['query']['pages']['68324070']['revisions'][0]['slots']['main']['*']

# Example of an url listed -- |url=https://www.allmusic.com/artist/10cc-mn0000502163 
# Example of a name listed -- \n* [[10cc]]
# Build regex to extract all urls

artists = re.findall(r'\n\*\s\[\[(.*?)\]\]', pages)
artists_cleaned = [artist.split('|')[0] for artist in artists]
artists_joined = [artist.replace(' ', '_') for artist in artists_cleaned]


# Initialize adjacency matrix and word count dictionary
adjacency_matrix = pd.DataFrame(0, index=artists_cleaned, columns=artists_cleaned)
word_count_dict = {}
artist_genre_dict = {}


for name in tqdm(artists_joined):

    # Properly encode the title to handle special characters like Ö, -, etc.
    # encoded_title = urllib.parse.quote(name)
    encoded_title = urllib.parse.quote(name, safe='')
    artist_title = f"titles={encoded_title}"

    query = "{}{}&{}&{}&{}&{}".format(baseurl, action, content, artist_title, dataformat, rvslots)

    try:
        artist_wikirequest = urllib.request.Request(query,None,headers)    # Needed to pass error 403
        artist_wikiresponse = urllib.request.urlopen(artist_wikirequest)
        artist_wikidata = artist_wikiresponse.read()
        artist_wikitext = artist_wikidata.decode('utf-8')

        artist_wiki_json = json.loads(artist_wikitext)

        artist_page_id = list(artist_wiki_json['query']['pages'].keys())[0]
        artist_page_content = artist_wiki_json['query']['pages'][artist_page_id]['revisions'][0]['slots']['main']['*']

        artist_page_content_valid = re.split(r'==References==', artist_page_content)[0] # split into sections
        artist_page_words = re.findall(r'\w+', artist_page_content_valid)
        artist_page_references = re.findall(r"<ref[^>]*>(.*?)<\/ref>", artist_page_content_valid)
        artist_page_word_count = len(artist_page_words)-len(artist_page_references) # exclude references from word count
        # print(artist_page_content)

        # Store word count
        clean_artist_name = name.replace('_', ' ')
        if clean_artist_name not in word_count_dict:
            word_count_dict[clean_artist_name] = artist_page_word_count
        else:
            print(f"Duplicate entry found for {clean_artist_name}")

        # Check if other artists are mentioned in the output
        for artist in artists_cleaned:
            if artist in str(artist_page_content) and clean_artist_name != artist: # avoid self loops
                adjacency_matrix.loc[clean_artist_name, artist] += 1
        
        # Extract genre information
        # Extract genre information
        genre_match = re.search(r'\|\s*genre\s*=\s*(.+?)(?=\n\s*\||$)', artist_page_content, re.DOTALL)
        if genre_match:
            genre_content = genre_match.group(1)
            
            # Remove all reference tags and their content
            genre_content_clean = re.sub(r'<ref[^>]*?>.*?</ref>', '', genre_content, flags=re.DOTALL)
            
            # Remove all template markup like {{hlist|...}} or {{flatlist|...}}
            genre_content_clean = re.sub(r'{{.*?\|', '', genre_content_clean)
            genre_content_clean = re.sub(r'}}', '', genre_content_clean)
            
            # Extract all [[...]] patterns, handling piped links
            genres = re.findall(r'\[\[([^\]|]+?)(?:\|[^\]]+?)?\]\]', genre_content_clean)
            
            # Clean up: strip whitespace and remove any entries with control characters
            genres = [re.sub(r'\s+', ' ', genre.strip()) for genre in genres]
            genres = [genre for genre in genres if genre and not re.search(r'[\x00-\x1F\x7F-\x9F]', genre)]
            
            if len(genres) != 0:
                artist_genre_dict[clean_artist_name] = genres
        
        # Save artist page
        if not os.path.exists('artist_pages'):
            os.makedirs(f'artist_pages')

        with open(f"artist_pages\{clean_artist_name}.txt", "w", encoding='utf-8') as f:
            f.write(artist_page_content_valid)
            

    except Exception as e:
        print(f"Error processing {name}: {e}")
            

# Save adjacency matrix, word counts, and genres to CSV or json files
adjacency_matrix.to_csv('rock_artists_adjacency_matrix.csv')

word_count_df = pd.DataFrame(list(word_count_dict.items()), columns=['Artist', 'Word_Count'])
word_count_df.to_csv('rock_artists_word_counts.csv', index=False)

with open('rock_artists_genres.json', 'w') as f:
    json.dump(artist_genre_dict, f)