from urllib.parse import urlparse
import json
from collections import defaultdict, Counter
from bs4 import BeautifulSoup
import nltk
from nltk.corpus import stopwords

totalNumLinks = 0
unique_urls = set()
subdomain_counts = defaultdict(int)
longest_page_url = ""
longest_page_numWords = 0
word_counter = Counter()

nltk.download('stopwords')
stop_words = set(stopwords.words('english'))

def getWordsInUrl(url,resp):
    try:
        content = resp.raw_response.content
        soup = BeautifulSoup(content, "html.parser")
        text = soup.get_text(separator=' ', strip = True)
        words = []
        curr_word = ""
        for char in text:
            if char.isalnum() and char.isascii():
                curr_word += char
            else:
                if curr_word:
                    if len(curr_word) < 3:
                        curr_word = ""
                        continue
                    words.append(curr_word.lower())
                    curr_word = ""
        if curr_word:
            words.append(curr_word.lower())
        return words
    except Exception as e:
        #print(f"Error processing {url}: {e}")
        return []

def parseWords(words):
    for word in words:
        if word not in stop_words:
            word_counter.update([word])

        
        #word_counter = word_counter.most_common(5000)

def process_url(url, resp):    
    totalNumLinks += 1

    global longest_page_url, longest_page_numWords
    words = getWordsInUrl(url,resp)
    numWordsInUrl = len(words)

    if longest_page_numWords < numWordsInUrl:
        longest_page_url = url
        longest_page_numWords = numWordsInUrl
    
    parseWords(words)

    # remove fragment
    parsed = urlparse(url)
    url_no_fragment = parsed._replace(fragment="").geturl()
    
    # add to unique urls
    unique_urls.add(url_no_fragment)

    # get subdomain and add to count
    netloc = parsed.netloc.lower()
    if netloc.endswith("uci.edu"):
        subdomain_counts[netloc] += 1
    
    save_results()

def save_results():
    output = {
        "unique_pages": list(unique_urls),
        "number_of_unique_pages": len(unique_urls),
        "subdomain_counts": dict(sorted(subdomain_counts.items())),
        "longest_page_url": longest_page_url,
        "longest_page_numWords": longest_page_numWords,
        "top_50_words": word_counter.most_common(50)

    }

    with open("results.json", "w") as f:
        json.dump(output, f, indent=2)
