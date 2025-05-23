import re
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from process_results import process_url

def scraper(url, resp):
    links = extract_next_links(url, resp)

    valid_links = []
    for link in links:
        if is_valid(link):
            valid_links.append(link)

    return valid_links

def extract_next_links(url, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    links = []
    
    if resp.status != 200:
        return links
    
    try:
        process_url(url, resp)
        content = resp.raw_response.content
        soup = BeautifulSoup(content, "html.parser")

        text = soup.get_text(separator=' ', strip=True)
        text_length = len(text)
        html_length = len(content)
        
        if text_length < 20:
            print(f"Dead page detected at {url}")
            return links
        
        if text_length / max(html_length, 1) < 0.03: 
            print(f"Low text density page detected at {url}")
            return links

        for link in soup.find_all("a", href = True):
            href = link["href"]
            url = urljoin(resp.url, href)
            url = urlparse(url)
            url = url._replace(fragment="").geturl()
            if is_valid(url):
                links.append(url)
    
    except Exception as e:
        print(f"Error while parsing {e}")
    
    
    return links

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        if 'doku.php' in parsed.path:
            return False
        if len(url) > 300:
            return False
        if re.search(r'(calendar|date|year=\d{4}|month=\d{1,2})', url.lower()):
            return False
        if "ical=" in parsed.query:
            return False
        if "format=" in parsed.query:   #too many 122b zip files look like this
            return False
        if url.count('=') > 3:
            return False
        if 'uci.zoom.us' in parsed.netloc:
            return False
        if "uploads" in parsed.path:
            return False
        if 'action=' in parsed.query:
            return False
        if 'share=' in parsed.query:
            return False
        if 'from=' in parsed.query:
            return False
        if "login" in parsed.path:
            return False
        if 'login.php' in parsed.path:
            return False
        if 'respond' in parsed.fragment:
            return False
        if 'branding' in parsed.fragment:
            return False
        if 'comments' in parsed.fragment:
            return False
        if 'comment' in parsed.fragment:
            return False
        if 'page' in parsed.fragment:
            return False
        if 'content' in parsed.fragment:   # usually a normal page with the same content 
            return False
        if '~eppstein/pix' in parsed.path:  # pictures we dont need
            return False
        if 'deldroid' in parsed.path:   # somehow program gets killed when up to this point
            return False
        if 'PmWiki' in parsed.path: # page doesnt even show
            return False
        if 'Nanda/seminar' in parsed.path:  # trap that kept adding to path like this Nanda/seminar/Nanda/seminar.. etc
            return False
        if 'seminar/Nanda' in parsed.path:
            return False
        if 'plrg' in parsed.netloc:
            return False
        if 'EMWS09' in parsed.path:
            return False
        if "zip-attachment" in parsed.path: 
            return False
        if 'ics.uci.edu' not in parsed.netloc:
            if 'cs.uci.edu' not in parsed.netloc:
                if 'informatics.uci.edu' not in parsed.netloc:
                    if 'stat.uci.edu' not in parsed.netloc:
                        if 'today.uci.edu/department/information_computer_sciences' not in parsed.netloc:
                            return False
        
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico|conf|java|lif"
            + r"|png|tiff?|mid|mp2|mp3|mp4|git|sh|apk|nb"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1|php|py|sql|war|xml|mpg"
            + r"|thmx|mso|arff|rtf|jar|csv|cp|h|git|ppsx|cs|ppt|pptx|ppsx"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise
