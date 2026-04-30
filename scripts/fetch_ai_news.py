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
    "36氪": "https://36kr.com/feed",
}

GOOGLE_NEWS_URLS = [
    "https://news.google.com/rss/search?q=AI+artificial+intelligence+when:1d&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=OpenAI+OR+Google+AI+OR+Anthropic+OR+DeepSeek+when:1d&hl=en-US&gl=US&ceid=US:en",
]

HN_API = "https://hn.algolia.com/api/v1/search_by_date?query=AI+LLM+GPT+OpenAI+agent&tags=story&hitsPerPage=30&numericFilters=points>30"


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
            for a in work.get('authorships', [])[:5]:
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
            authors = [{'name': a.get('text', str(a)) if isinstance(a, dict) else str(a), 'affiliation': ''} for a in authors_info[:5]]
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

    print("  📄 arXiv (with PDF extraction)...", file=sys.stderr)
    arxiv_raw = fetch_arxiv_papers_with_fulltext(max_results=5)
    print(f"    ✓ {len(arxiv_raw)} papers with full text", file=sys.stderr)

    print("  📍 OpenAlex...", file=sys.stderr)
    openalex_raw = fetch_openalex_papers()
    print(f"    ✓ {len(openalex_raw)} papers", file=sys.stderr)

    print("  📍 DBLP...", file=sys.stderr)
    dblp_raw = fetch_dblp_papers()
    print(f"    ✓ {len(dblp_raw)} papers", file=sys.stderr)

    # Merge all news into one pool
    all_news = cn_raw + en_raw + hn_raw
    papers = arxiv_raw + openalex_raw + dblp_raw

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
        print(f"⚠️ Save failed: {e}", file=sys.stderr)

    print("✅ Done!", file=sys.stderr)


if __name__ == '__main__':
    main()
