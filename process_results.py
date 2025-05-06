from urllib.parse import urlparse
import json
from collections import defaultdict, Counter
from bs4 import BeautifulSoup
import urllib.request


# Store unique URLs and subdomain counts
unique_urls = set()
subdomain_counts = defaultdict(int)
longest_page_url = ""
longest_page_numWords = 0
word_counter = Counter()
stop_words = set()

def getWordsInUrl(url):
    try:
        with urllib.request.urlopen(url) as resp:
            html = resp.read()
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text()

            words = []
            curr_word = ""
            for char in text:
                if char.isalnum() and char.isascii():
                    curr_word += char
                else:
                    if curr_word:
                        words.append(curr_word.lower())
                        curr_word = ""
            if curr_word:
                words.append(curr_word.lower())

            return words
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return []

def parseWords(words):
    for word in words:
        if word not in stop_words:
            word_counter.update([word])
        #word_counter = word_counter.most_common(5000)

def process_url(url):
    # finds longest page in terms of # of words
    
    global longest_page_url, longest_page_numWords
    words = getWordsInUrl(url)
    numWordsInUrl = len(words)

    if longest_page_numWords < numWordsInUrl:
        longest_page_url = url
        longest_page_numWords = numWordsInUrl
    
    parseWords(words)

    # Normalize: remove fragment
    parsed = urlparse(url)
    url_no_fragment = parsed._replace(fragment="").geturl()
    
    # Add to unique URLs
    unique_urls.add(url_no_fragment)

    # Extract subdomain (e.g., 'vision.ics.uci.edu')
    netloc = parsed.netloc.lower()
    if netloc.endswith("uci.edu"):
        subdomain_counts[netloc] += 1


# After crawling, prepare JSON object
output = {
    "unique_pages": list(unique_urls),
    "subdomain_counts": dict(subdomain_counts),
    "longest_page_url": longest_page_url,
    "longest_page_numWords": longest_page_numWords,
    "top_50_words": word_counter.most_common(50)
}

# Save to JSON file (optional)
with open("results.json", "w") as f:
    json.dump(output, f, indent=2)

with open("stop_words.txt", "r") as f:
    stop_words = {line.strip() for line in f if line.strip()}