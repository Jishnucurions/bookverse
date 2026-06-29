import requests
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://openlibrary.org"

def clean_work_key(key):
    """Convert /works/OL1234W to OL1234W"""
    if key and key.startswith('/works/'):
        return key.replace('/works/', '')
    return key

def search_books(query, limit=20):
    """
    Search books via Open Library Search API.
    """
    url = f"{BASE_URL}/search.json"
    params = {
        'q': query,
        'limit': limit
    }
    try:
        response = requests.get(url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results = []
            for doc in data.get('docs', []):
                key = doc.get('key', '')
                clean_key = clean_work_key(key)
                
                # Author list
                authors = doc.get('author_name', [])
                author_name = authors[0] if authors else "Unknown Author"
                
                results.append({
                    'key': clean_key,
                    'title': doc.get('title', 'Untitled'),
                    'author': author_name,
                    'year': doc.get('first_publish_year', 'N/A'),
                    'cover_id': doc.get('cover_i', None),
                })
            return results
    except Exception as e:
        logger.error(f"Error searching books for query '{query}': {e}")
    return []

def get_book_details(work_key):
    """
    Get detailed information for a specific work key (e.g. OL82586W).
    """
    url = f"{BASE_URL}/works/{work_key}.json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            
            # Extract description
            desc_data = data.get('description', '')
            description = ""
            if isinstance(desc_data, dict):
                description = desc_data.get('value', '')
            else:
                description = desc_data

            # Extract cover
            covers = data.get('covers', [])
            cover_id = covers[0] if covers else None

            # Extract authors and fetch their names
            authors = []
            for author_entry in data.get('authors', []):
                author_ref = author_entry.get('author', {})
                author_key = author_ref.get('key', '')
                if author_key:
                    author_id = author_key.replace('/authors/', '')
                    author_name = get_author_name(author_id)
                    authors.append({
                        'id': author_id,
                        'name': author_name
                    })

            subjects = data.get('subjects', [])[:8] # Limit to 8 subjects
            
            return {
                'key': work_key,
                'title': data.get('title', 'Untitled'),
                'description': description or "No description available.",
                'cover_id': cover_id,
                'authors': authors,
                'subjects': subjects,
                'first_publish_date': data.get('first_publish_date', 'N/A'),
            }
    except Exception as e:
        logger.error(f"Error fetching work details for key '{work_key}': {e}")
    return None

def get_author_name(author_id):
    """
    Fetch author name from author key.
    """
    url = f"{BASE_URL}/authors/{author_id}.json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('name', 'Unknown Author')
    except Exception as e:
        logger.error(f"Error fetching author name for '{author_id}': {e}")
    return "Unknown Author"

def get_books_by_subject(subject, limit=12):
    """
    Get works under a specific subject (e.g. 'science_fiction', 'fantasy').
    """
    url = f"{BASE_URL}/subjects/{subject.lower().replace(' ', '_')}.json"
    params = {
        'limit': limit
    }
    try:
        response = requests.get(url, params=params, timeout=3)
        if response.status_code == 200:
            data = response.json()
            results = []
            for work in data.get('works', []):
                key = work.get('key', '')
                clean_key = clean_work_key(key)
                
                authors = work.get('authors', [])
                author_name = authors[0].get('name') if authors else "Unknown Author"
                
                results.append({
                    'key': clean_key,
                    'title': work.get('title', 'Untitled'),
                    'author': author_name,
                    'year': work.get('first_publish_year', 'N/A'),
                    'cover_id': work.get('cover_id', None),
                })
            return results
    except Exception as e:
        logger.error(f"Error fetching subject '{subject}': {e}")
    return []
