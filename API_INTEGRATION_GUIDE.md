# 🌐 Adding Custom APIs to Retrieval Engine

## Current Setup

The `RetrievalEngine` now uses a **priority-based fallback chain**:

1. **Local JSON Knowledge Base** (TF-IDF + Cosine Similarity)
2. **DuckDuckGo Instant Answer API** (Fast, no auth)
3. **Wikipedia API** (Detailed, reliable)

---

## 🔧 How to Add Your Own API

### Step 1: Create API Fetch Method

Add a new method to `learners/retrieval_engine.py`:

```python
def _fetch_your_api(self, query: str) -> Tuple[str, float, str]:
    """Fetch from your custom API"""
    try:
        # Example: NewsAPI
        url = f"https://newsapi.org/v2/everything"
        params = {
            'q': query,
            'apiKey': 'YOUR_API_KEY',  # Add to .env
            'pageSize': 1
        }
        
        response = requests.get(url, params=params, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract relevant data
            if data.get('articles'):
                article = data['articles'][0]
                answer = article.get('description', '')
                
                if answer:
                    return (
                        answer,
                        0.70,  # Set appropriate confidence
                        "Web Retrieval (Your API Name)"
                    )
    except Exception as e:
        logger.error(f"Your API fetch failed: {e}")
        
    return "", 0.0, "Your API retrieval failed"
```

### Step 2: Add to Priority Chain

Update `_fetch_from_web_apis` method:

```python
def _fetch_from_web_apis(self, query: str) -> Tuple[str, float, str]:
    """Try APIs in priority order"""
    
    # Priority 1: DuckDuckGo
    result = self._fetch_duckduckgo(query)
    if result[0]:
        return result
    
    # Priority 2: Your Custom API (ADD HERE)
    result = self._fetch_your_api(query)
    if result[0]:
        return result
    
    # Priority 3: Wikipedia (Fallback)
    result = self._fetch_wikipedia(query)
    if result[0]:
        return result
    
    return "", 0.0, "All APIs failed"
```

---

## 📋 **Recommended Free APIs**

### 1. **DuckDuckGo** ✅ (Already Added)
```
URL: https://api.duckduckgo.com/
Auth: None
Limit: Unlimited
Use: Quick facts, instant answers
```

### 2. **Wikipedia** ✅ (Already Added)
```
URL: https://en.wikipedia.org/api/rest_v1/page/summary/{query}
Auth: None
Limit: High (rate-limited)
Use: Detailed encyclopedic content
```

### 3. **REST Countries API**
```python
def _fetch_country_info(self, query: str) -> Tuple[str, float, str]:
    try:
        url = f"https://restcountries.com/v3.1/name/{query}"
        response = requests.get(url, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                country = data[0]
                answer = f"{country['name']['common']} is located in {country['region']}. Capital: {country.get('capital', ['N/A'])[0]}. Population: {country.get('population', 'Unknown')}."
                return answer, 0.85, "Web Retrieval (REST Countries API)"
    except Exception as e:
        logger.error(f"REST Countries failed: {e}")
    return "", 0.0, ""
```

**Test Query:** `Tell me about France`

---

### 4. **OpenLibrary API**
```python
def _fetch_book_info(self, query: str) -> Tuple[str, float, str]:
    try:
        url = f"https://openlibrary.org/search.json"
        params = {'q': query, 'limit': 1}
        response = requests.get(url, params=params, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('docs'):
                book = data['docs'][0]
                title = book.get('title', 'Unknown')
                author = ', '.join(book.get('author_name', ['Unknown']))
                year = book.get('first_publish_year', 'Unknown')
                
                answer = f"Book: '{title}' by {author} (Published: {year})"
                return answer, 0.75, "Web Retrieval (OpenLibrary API)"
    except Exception as e:
        logger.error(f"OpenLibrary failed: {e}")
    return "", 0.0, ""
```

**Test Query:** `Harry Potter book`

---

### 5. **NewsAPI** (Requires Free API Key)
```python
def _fetch_news(self, query: str) -> Tuple[str, float, str]:
    try:
        # Get API key from environment
        api_key = os.getenv('NEWS_API_KEY', '')
        if not api_key:
            return "", 0.0, ""
            
        url = f"https://newsapi.org/v2/everything"
        params = {
            'q': query,
            'apiKey': api_key,
            'pageSize': 1,
            'sortBy': 'relevancy'
        }
        
        response = requests.get(url, params=params, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('articles'):
                article = data['articles'][0]
                answer = f"{article['title']}. {article['description']}"
                return answer, 0.80, "Web Retrieval (NewsAPI)"
    except Exception as e:
        logger.error(f"NewsAPI failed: {e}")
    return "", 0.0, ""
```

**Setup:**
1. Get free key: https://newsapi.org/
2. Add to `.env`: `NEWS_API_KEY=your_key_here`

---

### 6. **Exchange Rate API**
```python
def _fetch_exchange_rate(self, query: str) -> Tuple[str, float, str]:
    try:
        # Extract currency codes (e.g., "USD to EUR")
        import re
        match = re.search(r'(\w{3})\s+to\s+(\w{3})', query.upper())
        if not match:
            return "", 0.0, ""
            
        from_curr, to_curr = match.groups()
        
        url = f"https://api.exchangerate-api.com/v4/latest/{from_curr}"
        response = requests.get(url, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            rate = data['rates'].get(to_curr)
            if rate:
                answer = f"1 {from_curr} = {rate} {to_curr}"
                return answer, 0.95, "Web Retrieval (Exchange Rate API)"
    except Exception as e:
        logger.error(f"Exchange Rate API failed: {e}")
    return "", 0.0, ""
```

**Test Query:** `USD to EUR exchange rate`

---

## 🎯 **Quick Implementation Example**

Let's add **REST Countries API** right now:

### Add this to `retrieval_engine.py`:

```python
def _fetch_country_info(self, query: str) -> Tuple[str, float, str]:
    """Fetch country information from REST Countries API"""
    try:
        # Extract potential country name
        country_name = query.replace("tell me about", "").replace("what is", "").strip()
        
        url = f"https://restcountries.com/v3.1/name/{country_name}"
        response = requests.get(url, timeout=3)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                country = data[0]
                capital = country.get('capital', ['N/A'])[0] if country.get('capital') else 'N/A'
                answer = f"{country['name']['common']} is located in {country['region']}. Capital: {capital}. Population: {country.get('population', 'Unknown'):,}."
                return answer, 0.85, "Web Retrieval (REST Countries API)"
    except Exception as e:
        logger.error(f"REST Countries API failed: {e}")
    return "", 0.0, ""
```

### Then update `_fetch_from_web_apis`:

```python
def _fetch_from_web_apis(self, query: str) -> Tuple[str, float, str]:
    # Priority 1: DuckDuckGo
    result = self._fetch_duckduckgo(query)
    if result[0]:
        return result
    
    # Priority 2: Country Info (for geography queries)
    if any(word in query.lower() for word in ['country', 'capital', 'population']):
        result = self._fetch_country_info(query)
        if result[0]:
            return result
    
    # Priority 3: Wikipedia (General fallback)
    result = self._fetch_wikipedia(query)
    if result[0]:
        return result
    
    return "", 0.0, "Web retrieval failed (all APIs exhausted)"
```

---

## ✅ **Test Your New API**

1. Restart backend: `uvicorn app:app --reload`
2. Ask: `Tell me about Japan`
3. Expected: Response from REST Countries API
4. Check terminal reason: `"Web Retrieval (REST Countries API)"`

---

## 🚀 **Best Practices**

1. **Always use timeouts** (e.g., `timeout=3`)
2. **Handle errors gracefully** with try/except
3. **Set appropriate confidence scores** (0.0 - 1.0)
4. **Log failures** for debugging
5. **Respect API rate limits**
6. **Use environment variables** for API keys

---

**Your Retrieval Engine is now highly extensible!** Add as many APIs as you need. 🌐
