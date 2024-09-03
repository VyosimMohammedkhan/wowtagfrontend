from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk import pos_tag, word_tokenize
from playwright.async_api import async_playwright
import stopwords



import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
from sklearn.feature_extraction import _stop_words

# Define the FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Define the request model
class DomainRequest(BaseModel):
    domain: str

# Function to filter by POS tags
def pos_filter(text):
    tokens = word_tokenize(text)
    tagged = pos_tag(tokens)
    return [word for word, tag in tagged if tag.startswith('NN') and len(word)>2]  # Nouns

# Function to scrape page text using Puppeteer
async def scrape_homepage_text(domain):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        try:
            await page.goto(f'http://{domain}', timeout=10000)
            
            # Extract visible text content from the body of the page
            page_text = await page.text_content('body')
            
             # Extract meta description using querySelector
            meta_description_element = await page.query_selector('meta[name="description"]')
            meta_description = await meta_description_element.get_attribute('content') if meta_description_element else ''
            
            # Extract meta keywords using querySelector
            meta_keywords_element = await page.query_selector('meta[name="keywords"]')
            meta_keywords = await meta_keywords_element.get_attribute('content') if meta_keywords_element else ''
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to scrape the domain: {e}")
        finally:
            await browser.close()
        
        # Return the extracted information in a dictionary
        return {
            "page_text": page_text,
            "meta_description": meta_description,
            "meta_keywords": meta_keywords
        }
    
import re

def remove_stopwords(text, stopwords):
    # Convert the stopwords list to a set for faster lookup
    stopwords_set = set(stopwords)
    
    # Define a regular expression pattern to keep only alphanumeric characters
    alphanumeric_pattern = re.compile(r'\W+')

    # Split the text into words, clean them, and filter out the stopwords
    filtered_words = [
        alphanumeric_pattern.sub('', word).lower()  # Remove non-alphanumeric chars and convert to lowercase
        for word in text.split()
        if alphanumeric_pattern.sub('', word).lower() not in stopwords_set  # Check if the cleaned word is not in stopwords
    ]
    
    # Join the filtered words back into a string
    filtered_text = ' '.join(filtered_words)
    
    return filtered_text



# Define the API endpoint
@app.post("/extract_keywords")
async def extract_keywords(request: DomainRequest):
    domain = request.domain

    # Scrape the homepage text
    try:
        print('starting scrape for ', domain)
        scraped = await scrape_homepage_text(domain)
        description = scraped['meta_description']
        keywords = scraped['meta_keywords']
        page_text = scraped['page_text']
        print('scrape complete')
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
    custom_stopwords = stopwords.websiteterms
    default_stopwords = set(_stop_words.ENGLISH_STOP_WORDS)  # Default sklearn English stopwords
    combined_stopwords = list(default_stopwords.union(set(custom_stopwords))) if custom_stopwords else list(default_stopwords)
    clean_text = remove_stopwords(page_text, combined_stopwords)
    print('filtering')
    # Apply POS filtering
    filtered_text = " ".join(pos_filter(clean_text))

    # Initialize the TF-IDF Vectorizer to consider uni-grams, bi-grams, and tri-grams
    vectorizer_keywords = TfidfVectorizer(stop_words=combined_stopwords, token_pattern=r"\b\w{3,}\b", max_features=30, ngram_range=(1,3))
    print('vectorizing')

    X = vectorizer_keywords.fit_transform([filtered_text])
    tags = vectorizer_keywords.get_feature_names_out()
    weights = X.sum(axis=0).A1
    # Create dictionaries with feature names and their scores
    keyword_weights = dict(zip(tags, weights))
    sorted_keywords = dict(sorted(keyword_weights.items(), key=lambda x: x[1], reverse=True))
    print('all done')
    
    return [{"domain": domain, "keywords":keywords, "description":description, "tags":sorted_keywords}]

