from urllib.parse import urlparse
import json
from collections import defaultdict

# Store unique URLs and subdomain counts
unique_urls = set()
subdomain_counts = defaultdict(int)

def process_url(url):
    # Normalize: remove fragment
    parsed = urlparse(url)
    url_no_fragment = parsed._replace(fragment="").geturl()
    
    # Add to unique URLs
    unique_urls.add(url_no_fragment)

    # Extract subdomain (e.g., 'vision.ics.uci.edu')
    netloc = parsed.netloc.lower()
    if netloc.endswith(".ics.uci.edu"):
        subdomain_counts[netloc] += 1

# Call this inside your crawl loop:
# for url in extracted_links:
#     process_url(url)

# After crawling, prepare JSON object
output = {
    "unique_pages": list(unique_urls),
    "subdomain_counts": dict(subdomain_counts)
}

# Save to JSON file (optional)
with open("results.json", "w") as f:
    json.dump(output, f, indent=2)
