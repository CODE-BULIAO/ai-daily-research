#!/usr/bin/env python3
"""
AI Daily News Collector v4
Collects news + downloads paper PDFs + extracts full text → outputs structured JSON.
LLM handles: summarization, translation, formatting.
"""

import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import re
import sys
import time
import os
import tempfile
from datetime import datetime, timedelta, timezone
from html import unescape
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

TIMEOUT = 15

# ── RSS sources ──
RSS_FEEDS = {
    "雷峰网": "https://www.leiphone.com/feed",
    "量子位": "https://www.qbitai.com/feed",
    "极客公园": "https://www.geekpark.net/rss",
    "钛媒体": "https://www.tmtpost.com/rss",
    "IT之家": "https://www.ithome.com/rss/",
    
}

# Top Tech Blogs (Karpathy recommended)
TOP_TECH_BLOGS = {
    "simonwillison.net": "https://simonwillison.net/atom/everything/",
    "antirez.com": "http://antirez.com/rss",
    "gwern.net": "https://gwern.substack.com/feed",
    "paulgraham.com": "http://www.aaronsw.com/2002/feeds/pgessays.rss",
    "mitchellh.com": "https://mitchellh.com/feed.xml",
    "overreacted.io": "https://overreacted.io/rss.xml",
    "matklad.github.io": "https://matklad.github.io/feed.xml",
    "minimalir.com": "https://minimaxir.com/index.xml",
    "geohot.github.io": "https://geohot.github.io/blog/feed.xml",
    "danluu.com": "https://danluu.com/atom.xml",
    "jvns.ca": "https://jvns.ca/atom.xml",
}

GOOGLE_NEWS_URLS = [
    "https://news.google.com/rss/search?q=AI+artificial+intelligence+when:1d&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=OpenAI+OR+Google+AI+OR+Anthropic+OR+DeepSeek+when:1d&hl=en-US&gl=US&ceid=US:en",
]

HN_API = "https://hn.algolia.com/api/v1/search_by_date?query=AI+LLM+GPT+OpenAI+agent&tags=story&hitsPerPage=30&numericFilters=points>30"

# ==============================
# 重点跟踪公司列表（论文优先级筛选）
# ==============================
FOCUS_COMPANIES_INTL = [
    "openai", "google deepmind", "google", "anthropic", "meta ai", "meta fair",
    "microsoft research", "microsoft", "apple ai", "apple", "amazon ai", "aws",
    "nvidia", "xai", "cohere", "stability ai", "mistral ai", "inflection ai",
]

FOCUS_COMPANIES_CN = [
    "百度", "baidu", "阿里巴巴", "alibaba", "阿里云", "腾讯", "tencent",
    "字节跳动", "bytedance", "豆包", "华为", "huawei", "美团", "meituan",
    "小米", "xiaomi", "商汤", "sensetime", "月之暗面", "moonshot ai", "kimi",
    "智谱ai", "zhipu ai", "glm", "百川智能", "baichuan", "零一万物", "01.ai",
    "minimax", "深度求索", "deepseek", "蚂蚁集团", "ant group", "京东", "jd.com",
    "网易", "netease", "快手", "kuaishou", "科大讯飞", "iflytek", "昆仑万维",
]

ALL_FOCUS_COMPANIES = FOCUS_COMPANIES_INTL + FOCUS_COMPANIES_CN


def is_focus_company_paper(paper):
    """Check if a paper is from any focus company."""
    text = ' '.join([
        paper.get('title', ''),
        ' '.join([a.get('affiliation', '') for a in paper.get('authors', [])]),
        ' '.join(paper.get('affiliations', [])),
    ]).lower()
    return any(company.lower() in text for company in ALL_FOCUS_COMPANIES)


def fetch_url(url, timeout=TIMEOUT):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except:
        return None


def clean_html(text):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', '', text)
    text = unescape(text)
    return re.sub(r'\s+', ' ', text).strip()


def truncate(text, max_len=400):
    if not text or len(text) <= max_len:
        return text
    return text[:max_len].rsplit(' ', 1)[0] + "..."


def parse_rss(xml_text, source_name, max_items=15):
    items = []
    try:
        root = ET.fromstring(xml_text)
        entries = root.findall('.//item')
        for entry in entries[:max_items]:
            t = entry.find('title')
            title = t.text.strip() if t is not None and t.text else ""
            l = entry.find('link')
            link = (l.text or l.get('href', '')).strip() if l is not None else ""
            d = entry.find('description')
            desc = clean_html(d.text)[:600] if d is not None and d.text else ""
            p = entry.find('pubDate')
            pub_date = p.text.strip() if p is not None and p.text else ""
            if title:
                items.append({
                    'title': clean_html(title),
                    'link': link,
                    'description': desc,
                    'source': source_name,
                    'date': pub_date,
                })
    except ET.ParseError:
        pass
    return items


def fetch_all_chinese_news():
    all_items = []
    for name, url in RSS_FEEDS.items():
        xml = fetch_url(url)
        if xml:
            items = parse_rss(xml, name, max_items=12)
            all_items.extend(items)
    return all_items


def fetch_top_tech_blogs():
    all_items = []
    for name, url in TOP_TECH_BLOGS.items():
        xml = fetch_url(url, timeout=10)
        if xml:
            items = parse_rss(xml, f"Blog:{name}", max_items=3)
            all_items.extend(items)
        time.sleep(0.2)
    return all_items


def fetch_all_english_news():
    all_items = []
    seen_titles = set()
    for url in GOOGLE_NEWS_URLS:
        for attempt in range(2):
            xml = fetch_url(url, timeout=20)
            if xml and '<item>' in xml:
                items = parse_rss(xml, "Google News", max_items=10)
                for item in items:
                    key = re.sub(r'[^\w]', '', item['title'].lower())[:40]
                    if key not in seen_titles:
                        seen_titles.add(key)
                        all_items.append(item)
                break
            time.sleep(1)
    return all_items


def fetch_hacker_news():
    items = []
    try:
        data = fetch_url(HN_API, timeout=20)
        if data:
            result = json.loads(data)
            for hit in result.get('hits', [])[:10]:
                if hit.get('points', 0) >= 30:
                    items.append({
                        'title': hit.get('title', ''),
                        'link': hit.get('url') or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
                        'description': f"{hit.get('points', 0)} points, {hit.get('num_comments', 0)} comments on HN",
                        'source': 'Hacker News',
                        'date': hit.get('created_at', ''),
                    })
    except:
        pass
    return items


def extract_arxiv_authors_and_affiliations(xml_text):
    """Extract detailed author info from arXiv XML."""
    authors_info = []
    try:
        ns = {'a': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
        root = ET.fromstring(xml_text)
        entry = root.find('a:entry', ns)
        if entry is None:
            return [], ""

        for author in entry.findall('a:author', ns):
            name_el = author.find('a:name', ns)
            name = name_el.text if name_el is not None else ""
            aff_el = author.find('arxiv:affiliation', ns)
            affiliation = aff_el.text if aff_el is not None else ""
            authors_info.append({'name': name, 'affiliation': affiliation})

        # Get comment (often contains conference info)
        comment_el = entry.find('arxiv:comment', ns)
        comment = comment_el.text.strip() if comment_el is not None and comment_el.text else ""

        # Get primary category
        primary_cat = entry.find('arxiv:primary_category', ns)
        primary = primary_cat.get('term', '') if primary_cat is not None else ""

        # Get journal ref if available
        journal_el = entry.find('arxiv:journal_ref', ns)
        journal_ref = journal_el.text.strip() if journal_el is not None and journal_el.text else ""

        return authors_info, comment, primary, journal_ref
    except:
        return [], "", "", ""


def download_and_extract_pdf(arxiv_id, max_pages=5):
    """Download arXiv PDF and extract text."""
    try:
        import fitz  # pymupdf
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}"
        req = urllib.request.Request(pdf_url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30, context=ctx) as resp:
            pdf_bytes = resp.read()

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            tmp.write(pdf_bytes)
            tmp_path = tmp.name

        doc = fitz.open(tmp_path)
        text_parts = []
        pages_to_read = min(max_pages, len(doc))
        for i in range(pages_to_read):
            page = doc[i]
            text_parts.append(page.get_text())
        doc.close()
        os.unlink(tmp_path)

        full_text = '\n'.join(text_parts)
        # Clean up
        full_text = re.sub(r'\s+', ' ', full_text)
        return full_text[:8000]  # Limit to ~8K chars for LLM context
    except Exception as e:
        return f"[PDF extraction failed: {e}]"


# ==============================
# Enhanced Affiliation Extraction (from hermes-arxiv-agent)
# ==============================
ORG_KEYWORDS = {
    "university", "institute", "school", "college", "department", "laboratory",
    "lab", "centre", "center", "research", "academy", "hospital", "faculty",
    "polytechnic", "technological", "technology", "technion",
    "google", "microsoft", "meta", "apple", "amazon", "ibm", "intel", "nvidia",
    "amd", "qualcomm", "samsung", "huawei", "tencent", "alibaba", "bytedance",
    "deepmind", "openai", "anthropic", "mistral", "cohere", "huggingface",
    "mit", "stanford", "harvard", "princeton", "yale", "berkeley", "cornell",
    "oxford", "cambridge", "eth", "epfl", "inria", "tum", "kaist", "postech",
    "cmu", "carnegie", "gatech", "purdue", "uiuc", "columbia", "caltech",
    "ucla", "ucsd", "toronto", "montreal", "tsinghua", "peking", "fudan",
    "zhejiang", "nanjing", "shanghai", "beihang", "sjtu", "ustc", "unist",
    "ntu", "nus", "renmin", "cas", "academy of military sciences",
    "baidu", "bytedance", "xiaomi", "meituan", "jd.com", "netease",
    "kuaishou", "iflytek", "sensetime", "moonshot", "zhipu", "minimax",
    "deepseek", "baichuan", "01.ai",
}

AFFILIATION_HINTS = {
    "engineering", "science", "computer", "mathematics", "statistics", "ai",
    "artificial intelligence", "informatics", "information", "electrical",
    "electronic", "automation", "physics", "medicine", "medical", "business",
    "data", "robotics", "systems", "communication", "software",
}

NOISE_PATTERNS_AFF = [
    r"https?://\S+",
    r"www\.\S+",
    r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}\b",
    r"\barxiv\b", r"\bcopyright\b", r"\bpreprint\b", r"\baccepted\b",
    r"\bfigure\b", r"\btable\b", r"\bappendix\b",
]

BAD_LINE_PATTERNS = [
    r"\babstract\b", r"\bintroduction\b", r"\bcontributions?\b",
    r"\brelated work\b",
    r"\bwe (?:study|show|propose|introduce|present|analyze|derive|establish)\b",
    r"\bour (?:method|analysis|results|experiments|framework)\b",
    r"\baccuracy\b", r"\bbenchmark\b", r"\bproof\b", r"\btheorem\b", r"\bresults?\b",
]

KNOWN_SUFFIXES = [
    "University", "Institute", "School", "College", "Department", "Laboratory",
    "Research", "Center", "Centre", "Hospital", "Sciences", "Technology",
    "Engineering", "Mathematics", "Physics", "Medicine",
]

SMALL_WORDS = ["of", "the", "and", "for", "in", "on", "at", "to", "by", "with", "from",
               "de", "du", "la", "le", "da", "del", "di"]


def _normalize_aff_text(text):
    text = text.replace("\u2013", "-").replace("\u2014", "-").replace("\u00a0", " ")
    return re.sub(r'\s+', ' ', text).strip(" ,;:-")


def _fix_glued_words(text):
    text = _normalize_aff_text(text)
    text = re.sub(r'(?<=\d)(?=[A-Za-z])', ' ', text)
    text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)
    for word in SMALL_WORDS:
        text = re.sub(rf"(?i)([A-Za-z])({word})([A-Z])", r"\1 \2 \3", text)
        text = re.sub(rf"(?i)([A-Za-z])({word})([a-z])", r"\1 \2 \3", text)
    for suffix in KNOWN_SUFFIXES:
        text = re.sub(rf"(?<=[A-Za-z])(?={suffix}\b)", " ", text)
    return re.sub(r'\s+', ' ', text).strip(" ,;:-")


def _has_org_signal(text):
    low = text.lower()
    return any(k in low for k in ORG_KEYWORDS) or any(k in low for k in AFFILIATION_HINTS)


def _looks_like_affiliation(text):
    if not text:
        return False
    low = text.lower()
    if any(re.search(p, low) for p in BAD_LINE_PATTERNS):
        return False
    if len(re.findall(r"[=<>±∑∫]", text)) > 0:
        return False
    if not _has_org_signal(text):
        return False
    letters = len(re.findall(r"[A-Za-z]", text))
    if letters < 6:
        return False
    return True


def _clean_aff_candidate(text):
    text = _normalize_aff_text(text)
    text = re.sub(r"[\*†‡§¶‖#]+", " ", text)
    text = re.sub(r"(?<![A-Za-z])[\^]?\d+(?=[A-Za-z])", "", text)
    text = re.sub(r"^\s*[\^]?\d+[\)\].,:-]?\s*", "", text)
    for pattern in NOISE_PATTERNS_AFF:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE)
    text = _fix_glued_words(text)
    text = re.sub(r"\([^)]*@[^)]*\)", " ", text)
    return re.sub(r'\s+', ' ', text).strip(" ,;:-")


def extract_affiliations_from_text(pdf_text, max_affiliations=10):
    """Extract affiliations from extracted PDF text using heuristic rules.
    Inspired by hermes-arxiv-agent's reextract_affiliations.py approach.
    """
    if not pdf_text or pdf_text.startswith("[PDF extraction"):
        return []

    # Take first ~3000 chars (likely title/author/abstract area)
    header_text = pdf_text[:3000]
    lines = [l.strip() for l in re.split(r'\n+', header_text) if l.strip()]

    # Merge hyphenated cross-line words
    merged = []
    i = 0
    while i < len(lines):
        line = lines[i]
        while line.endswith("-") and i + 1 < len(lines):
            line = line[:-1] + lines[i + 1]
            i += 1
        merged.append(line)
        i += 1

    candidates = []
    for line in merged:
        cleaned = _clean_aff_candidate(line)
        if _looks_like_affiliation(cleaned):
            # Split numbered affiliations: "1 MIT 2 Stanford" → ["MIT", "Stanford"]
            parts = re.split(r'\s(?=\d+[)\].,:-]?\s*[A-Z])', cleaned)
            for part in parts:
                part = _clean_aff_candidate(part)
                if _looks_like_affiliation(part):
                    candidates.append(part)

    # Deduplicate
    seen = set()
    result = []
    for c in candidates:
        key = re.sub(r'[^a-z0-9]+', '', c.lower())
        if key and key not in seen:
            seen.add(key)
            result.append(c)
    return result[:max_affiliations]


def fetch_arxiv_papers_with_fulltext(max_results=8):
    """Fetch arXiv papers with author affiliations, venue info, and full text.
    Only fetches LLM-related papers using targeted search queries."""
    items = []
    # Focused LLM-related queries
    queries = [
        ("ti:language+model+OR+ti:LLM+OR+ti:transformer+OR+ti:GPT+OR+ti:chat", "LLM-Core"),
        ("ti:reasoning+AND+cat:cs.CL+OR+ti:fine-tuning+AND+cat:cs.CL+OR+ti:alignment+AND+cat:cs.CL", "LLM-Training"),
        ("ti:agent+AND+(cat:cs.CL+OR+cat:cs.AI)+OR+ti:RAG+OR+ti:retrieval+AND+cat:cs.CL", "LLM-Agent"),
        ("ti:benchmark+AND+cat:cs.CL+OR+ti:safety+AND+cat:cs.CL+OR+ti:evaluation+AND+cat:cs.CL", "LLM-Eval"),
    ]

    for cat_query, label in queries:
        url = f"https://export.arxiv.org/api/query?search_query={cat_query}&sortBy=submittedDate&sortOrder=descending&max_results=6"
        xml = fetch_url(url, timeout=25)
        if not xml:
            continue

        # Parse for basic info first
        try:
            ns = {'a': 'http://www.w3.org/2005/Atom'}
            root = ET.fromstring(xml)
            paper_ids = []
            for entry in root.findall('a:entry', ns):
                id_el = entry.find('a:id', ns)
                arxiv_id = id_el.text.strip().split('/abs/')[-1] if id_el is not None else ""
                if arxiv_id:
                    paper_ids.append(arxiv_id)
        except:
            continue

        # Now fetch detailed info + PDF for each paper
        for arxiv_id in paper_ids[:max_results]:
            # Fetch detailed metadata
            detail_url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}"
            detail_xml = fetch_url(detail_url, timeout=20)
            time.sleep(1)  # Rate limit

            authors_info, comment, primary_cat, journal_ref = extract_arxiv_authors_and_affiliations(detail_xml)

            # Parse basic info
            try:
                ns = {'a': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
                root = ET.fromstring(detail_xml)
                entry = root.find('a:entry', ns)
                if entry is None:
                    continue

                title = entry.find('a:title', ns).text.strip().replace('\n', ' ')
                abstract = entry.find('a:summary', ns).text.strip()
                published = entry.find('a:published', ns).text[:10]

                # Download and extract PDF
                print(f"  📥 Downloading PDF: {arxiv_id}...", file=sys.stderr)
                full_text = download_and_extract_pdf(arxiv_id, max_pages=4)

                author_names = [a['name'] for a in authors_info]
                affiliations = list(set([a['affiliation'] for a in authors_info if a['affiliation']]))
                
                # Enhanced affiliation extraction from PDF if XML has none
                if not affiliations and full_text and not full_text.startswith("[PDF extraction"):
                    pdf_affs = extract_affiliations_from_text(full_text)
                    if pdf_affs:
                        affiliations = pdf_affs
                        print(f"    🏛️  Extracted {len(pdf_affs)} affiliations from PDF", file=sys.stderr)

                items.append({
                    'title': title,
                    'link': f"https://arxiv.org/abs/{arxiv_id}",
                    'authors': [{'name': a['name'], 'affiliation': a['affiliation']} for a in authors_info],
                    'author_names': author_names,
                    'affiliations': affiliations,
                    'abstract': abstract,
                    'full_text': full_text,
                    'comment': comment,
                    'primary_category': primary_cat,
                    'journal_ref': journal_ref,
                    'source': 'arXiv',
                    'date': published,
                    'arxiv_id': arxiv_id,
                })
            except:
                continue

    return items


def fetch_openalex_papers(max_results=5):
    items = []
    params = urllib.parse.urlencode({
        'search': 'large language model OR deep learning OR AI agent OR neural network OR transformer',
        'filter': 'from_publication_date:2026-04-23,type:article',
        'sort': 'cited_by_count:desc',
        'per_page': max_results,
        'select': 'title,doi,authorships,primary_location,cited_by_count,publication_date,abstract_inverted_index'
    })
    url = f"https://api.openalex.org/works?{params}"
    data = fetch_url(url, timeout=20)
    if not data:
        return items
    try:
        result = json.loads(data)
        for work in result.get('results', []):
            title = work.get('title', '')
            if not title:
                continue
            venue = ""
            venue_type = ""
            loc = work.get('primary_location', {})
            if loc and loc.get('source'):
                venue = loc['source'].get('display_name', '')
                venue_type = loc['source'].get('type', '')
            authors_with_aff = []
            for a in work.get('authorships', []):
                name = a.get('author', {}).get('display_name', '')
                insts = [i.get('display_name', '') for i in a.get('institutions', [])]
                aff = insts[0] if insts else ''
                if name:
                    authors_with_aff.append({'name': name, 'affiliation': aff})
            cited = work.get('cited_by_count', 0)
            doi = work.get('doi', '')
            pub_date = work.get('publication_date', '')
            abstract = ""
            aii = work.get('abstract_inverted_index')
            if aii:
                try:
                    word_pos = {}
                    for word, positions in aii.items():
                        for pos in positions:
                            word_pos[pos] = word
                    abstract = ' '.join(word_pos[i] for i in sorted(word_pos.keys()))
                except:
                    pass
            items.append({
                'title': title,
                'link': doi or '',
                'authors': authors_with_aff,
                'author_names': [a['name'] for a in authors_with_aff],
                'affiliations': list(set([a['affiliation'] for a in authors_with_aff if a['affiliation']])),
                'abstract': abstract,
                'full_text': '',
                'venue': venue,
                'venue_type': venue_type,
                'cited_by': cited,
                'source': 'OpenAlex',
                'date': pub_date,
            })
    except (json.JSONDecodeError, KeyError):
        pass
    return items


def fetch_dblp_papers(max_results=5):
    items = []
    params = urllib.parse.urlencode({
        'q': 'large language model OR deep learning OR AI agent 2026',
        'format': 'json',
        'h': max_results
    })
    url = f"https://dblp.uni-trier.de/search/publ/api?{params}"
    data = fetch_url(url, timeout=20)
    if not data:
        return items
    try:
        result = json.loads(data)
        hits = result.get('result', {}).get('hits', {}).get('hit', [])
        for hit in hits:
            info = hit.get('info', {})
            title = info.get('title', '')
            if isinstance(title, dict):
                title = title.get('text', '')
            title = title.rstrip('.')
            venue = info.get('venue', '')
            year = info.get('year', '')
            pub_type = info.get('type', '')
            doi = info.get('doi', '')
            authors_info = info.get('authors', {}).get('author', [])
            if isinstance(authors_info, dict):
                authors_info = [authors_info]
            authors = [{'name': a.get('text', str(a)) if isinstance(a, dict) else str(a), 'affiliation': ''} for a in authors_info]
            link = f"https://doi.org/{doi}" if doi else info.get('ee', '')
            if title:
                items.append({
                    'title': title,
                    'link': link,
                    'authors': authors,
                    'author_names': [a['name'] for a in authors],
                    'affiliations': [],
                    'abstract': '',
                    'full_text': '',
                    'venue': venue,
                    'year': year,
                    'pub_type': pub_type,
                    'source': 'DBLP',
                    'date': str(year),
                })
    except (json.JSONDecodeError, KeyError, TypeError):
        pass
    return items


def main():
    print("🔄 Collecting from all sources...", file=sys.stderr)

    print("  📰 Chinese RSS...", file=sys.stderr)
    cn_raw = fetch_all_chinese_news()
    print(f"    ✓ {len(cn_raw)} items", file=sys.stderr)

    print("  🌍 Google News...", file=sys.stderr)
    en_raw = fetch_all_english_news()
    print(f"    ✓ {len(en_raw)} items", file=sys.stderr)

    print("  💬 Hacker News...", file=sys.stderr)
    hn_raw = fetch_hacker_news()
    print(f"    ✓ {len(hn_raw)} items", file=sys.stderr)

    print("  ✍️  Top Tech Blogs (Karpathy recommended)...", file=sys.stderr)
    blogs_raw = fetch_top_tech_blogs()
    print(f"    ✓ {len(blogs_raw)} items", file=sys.stderr)

    print("  📄 arXiv (with PDF extraction)...", file=sys.stderr)
    arxiv_raw = fetch_arxiv_papers_with_fulltext(max_results=8)
    print(f"    ✓ {len(arxiv_raw)} papers with full text", file=sys.stderr)

    print("  📍 OpenAlex...", file=sys.stderr)
    openalex_raw = fetch_openalex_papers(max_results=8)
    print(f"    ✓ {len(openalex_raw)} papers", file=sys.stderr)

    print("  📍 DBLP...", file=sys.stderr)
    dblp_raw = fetch_dblp_papers(max_results=8)
    print(f"    ✓ {len(dblp_raw)} papers", file=sys.stderr)

    # Merge all news into one pool
    all_news = cn_raw + en_raw + hn_raw + blogs_raw
    
    # Merge papers and prioritize by focus company
    all_papers = arxiv_raw + openalex_raw + dblp_raw
    
    # Mark focus company papers
    for p in all_papers:
        p['is_focus_company'] = is_focus_company_paper(p)
    
    # Sort: focus company papers first, then by date/source
    all_papers.sort(key=lambda x: (not x.get('is_focus_company', False), x.get('date', '') != datetime.now(timezone(timedelta(hours=8))).strftime('%Y-%m-%d')))
    
    # Count focus company papers
    focus_count = sum(1 for p in all_papers if p.get('is_focus_company'))
    print(f"  🏢 Focus company papers: {focus_count}/{len(all_papers)}", file=sys.stderr)
    
    papers = all_papers

    output = {
        "date": datetime.now(timezone(timedelta(hours=8))).strftime("%Y-%m-%d"),
        "stats": {
            "news_count": len(all_news),
            "papers_count": len(papers),
            "total": len(all_news) + len(papers),
        },
        "all_news": all_news,
        "papers": papers,
    }

    print(json.dumps(output, ensure_ascii=False, indent=2))

    now = datetime.now(timezone(timedelta(hours=8)))
    filename = f"/opt/data/cron/output/ai_raw_{now.strftime('%Y%m%d')}.json"
    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        print(f"💾 Saved to {filename}", file=sys.stderr)

    except Exception as e:
        print(f"⚠️  Failed to save raw file: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
