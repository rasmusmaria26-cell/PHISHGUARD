from app.heuristic import score_url

# Test the URL analyzer with clarovirtual.life
test_urls = [
    "http://clarovirtual.life/",
    "https://clarovirtual.life/",
    "http://consultanetpro.biz/?utm_source=organic",
    "https://www.google.com",
]

print("Testing URL Analyzer:\n")
for url in test_urls:
    result = score_url(url)
    print(f"URL: {url}")
    print(f"  Score: {result['score']}")
    print(f"  Reasons: {result['reasons']}")
    print()
