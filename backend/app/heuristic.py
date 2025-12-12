from urllib.parse import urlparse
import ipaddress
import re
import logging

logger = logging.getLogger(__name__)

# Constants
IP_ADDRESS_PENALTY = 60
SUSPICIOUS_URL_LENGTH = 75
URL_LENGTH_PENALTY = 10
KEYWORD_PENALTY = 10
NO_HTTPS_PENALTY = 15
SUSPICIOUS_TLD_PENALTY = 85

SUSPICIOUS_KEYWORDS = ['login', 'verify', 'update', 'account', 'banking', 'secure', 'signin', 'password']
SUSPICIOUS_TLDS = [
    '.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.work', '.click',
    '.ink', '.site', '.info', '.club', '.live', '.buzz', '.online', '.vip',
    '.bid', '.win', '.pro', '.loan', '.men', '.review', '.party', '.trade'
]

def score_url(url: str) -> dict:
    score = 0
    reasons = []
    
    try:
        parsed = urlparse(url)
        domain = parsed.netloc
    except (ValueError, AttributeError) as e:
        logger.warning(f"URL parsing failed for {url}: {e}")
        return {"score": 50, "reasons": ["Malformed URL - potentially suspicious"]}

    if not domain:
        return {"score": 50, "reasons": ["Missing domain in URL"]}

    # 1. IP Address Check (IPv4 and IPv6)
    # Remove port if present
    hostname = domain.split(':')[0]
    
    if hostname == 'localhost':
        return {"score": 0, "reasons": ["Local development"]}

    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_private or ip.is_loopback:
             return {"score": 0, "reasons": ["Local/Private IP Address"]}

        score += IP_ADDRESS_PENALTY
        reasons.append("IP address used as domain")
    except ValueError:
        pass  # Not an IP, which is normal

    # 2. HTTPS Check
    if parsed.scheme == 'http':
        score += NO_HTTPS_PENALTY
        reasons.append("No HTTPS encryption")

    # 3. Length Check
    if len(url) > SUSPICIOUS_URL_LENGTH:
        score += URL_LENGTH_PENALTY
        reasons.append("URL suspiciously long")

    # 4. Suspicious TLD Check
    domain_lower = domain.lower()
    for tld in SUSPICIOUS_TLDS:
        if domain_lower.endswith(tld):
            score += SUSPICIOUS_TLD_PENALTY
            reasons.append(f"Suspicious top-level domain ({tld})")
            break

    # 5. Keyword Check
    # Check if keywords appear in the path (not the domain itself usually)
    path = parsed.path + parsed.query
    found_keywords = [kw for kw in SUSPICIOUS_KEYWORDS if kw in path.lower()]
    if found_keywords:
        score += KEYWORD_PENALTY
        reasons.append(f"Suspicious keywords in URL path: {', '.join(found_keywords[:3])}")

    # 6. Subdomain Count (many subdomains can be suspicious)
    subdomain_count = domain.count('.')
    if subdomain_count > 3:
        score += 15
        reasons.append(f"Excessive subdomains ({subdomain_count})")

    # 7. Domain Structure Check (Hyphens and Numbers)
    # Extract SLD (Second Level Domain) e.g., 'google' from 'google.com'
    parts = domain_lower.split('.')
    if len(parts) >= 2:
        sld = parts[-2]
        
        # Check for excessive hyphens
        if sld.count('-') > 1:
            score += 20
            reasons.append("Suspicious usage of hyphens in domain")
            
        # Check for numeric suffix (e.g. 'paypal123') - Penalize ONLY if SLD is long (avoid false positives like 'news24')
        if re.search(r'\d+$', sld):
            if len(sld) > 10:
                score += 55
                reasons.append("Long domain ending with numbers (mimic pattern)")
            else:
                score += 10 # Minor penalty for short domains ending in numbers

    return {
        "score": min(100, score),
        "reasons": reasons
    }