# Disney Movies & Character Analysis

**Final Project** for the course **02805 Social Graphs and Interactions, Fall 2025**

**Contributors:**  
- German Buttiero (s243660)  
- Sree Keerthi Desu (s243933)


## Project Idea

This project aims to investigate **gender representation in Disney movie plots**. Specifically, we want to understand whether male and female characters are portrayed differently, and if common **gender stereotypes** appear in the words and interactions associated with them.  

## Project Overview

This project collects and analyzes **Disney movies and character data** from Wikipedia and the Disney Fandom Wiki. It includes:

1. **Movie Plot Extraction**  
   - Retrieves a list of Disney movies from Wikipedia.  
   - Extracts **infoboxes** and **plot summaries** for each movie.  
   - Cleans wiki markup, links, and templates.  
   - Saves each movie as a text file under `project/movies/`.

2. **Character Name Scraping**  
   - Scrapes **male and female Disney characters** from Disney Fandom Wiki.  
   - Saves names to `disney_male_characters.txt` and `disney_female_characters.txt`.

3. **Word Pair**  
   - Processes movie plot text to extract **character co-occurrences**.
     
4. **Graph Analysis and Community Detection**  
   - Computes **Positive Pointwise Mutual Information (PPMI)** between words/characters.  
   - Builds weighted graphs for each gender with node attributes like POS and gender.  
   - Detects **communities** within the graphs to identify clusters of related words or characters.  
   - Generates **word clouds** for each community to visualize the most prominent words associated with male and female characters.


