#Loading Packages
import streamlit as st
from langchain_openai import ChatOpenAI
import pandas as pd
import json
import requests
from bs4 import BeautifulSoup
import urllib.parse
import time
import random
import re

# Load the dictionary with coupon data from the JSON file
def load_brands_dict(json_file):
    try:
        with open(json_file, 'r') as f:
            brands_dict = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print(f"Failed to load '{json_file}'. Creating a new empty dictionary.")
        brands_dict = {}
    return brands_dict


#Created a list of categories and categorized all the coupons:
categories = {
    "fashion": ["noon", "namshi", "Styli", "Ted Baker", "Metro Brazil", "R&B", "Level Shoes", "Brands For Less", "Sivvi", "GAP", "American Eagle", "CitrussTv", "Forever21", "Lyle & Scott", "Bloomingdale's", "fordeal", "COS", "Eyewa", "Store Us"],
    "sports": ["SSSports", "UnderArmour", "New Balance", "Store Us", "noon"],
    "beauty": ["Basharacare", "Boots", "Mikyajy", "The Bodyshop", "AlDakheel Oud", "Store Us", "noon", "CitrussTv"],
    "toys": ["Toys R Us", "Lego", "Store Us", "noon"],
    "baby": ["Mamas & Papas", "Mothercare", "Toys R Us", "Mumzworld", "Store Us", "noon"],
    "home": ["Homes R us", "Pottery Barn", "Nabataty", "The Luxury Closet", "Store Us", "noon", "CitrussTv"],
    "mobile plans": ["Ya Hala"],
    "grocery":["Barakat"],
    "technology":["noon", "Store Us"]
}

category_names = list(categories.keys())

#Function for retrieving category using llm:
def get_product(uq, llm):
    """Function to find the product from the user query"""

    messages = [
    ("system", "The prompt provides a url link for a product, return a string with what the product is, just the product."),
    ("human", f"{uq}"),
    ]

    return llm.invoke(messages)

#Function for retrieving category using llm:
def get_relevent_category(prompt_product, category_names, llm):
    """Function to find a list of relevent category based on the product"""

    messages = [
    ("system", "The prompt provides a product and a list of categories. Just output which category is most relevent based on the product."),
    ("human", f"Product:{prompt_product}, List of categories: {category_names}"),
    ]

    return llm.invoke(messages)


def get_coupons(relevant_category, brands_dict):
    # Filter brands based on the relevant category
    relevant_brands = [(brand, details) for brand, details in brands_dict.items() if relevant_category in details.get('category', [])]
    return relevant_brands

# Function to search Google with retry mechanism and improved error handling
def google_search(query, site, num_results=2, retries=3):
    query = f"{query} site:{site}"
    url = f"https://www.google.com/search?q={query}&num={num_results}"
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
        # Add more user agents if needed
    ]

    for attempt in range(retries):
        try:
            headers = {
                "User-Agent": random.choice(user_agents)
            }
            response = requests.get(url, headers=headers)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")
            result = soup.find('div', class_='tF2Cxc')
            if result:
                title = result.find('h3').text if result.find('h3') else 'No title'
                link = result.find('a')['href'] if result.find('a') else 'No link'
                snippet = result.find('div', class_='IsZvec').text if result.find('div', class_='IsZvec') else 'No snippet'
                return {'title': title, 'link': link, 'snippet': snippet}
            else:
                return None
        except requests.RequestException:
            time.sleep(2 ** attempt)  # Exponential backoff

    return None
    

def search_stores_free(relevant_brands, product):

    for brand, details in relevant_brands:
        # Format the coupon information for English language
        coupon_url = details.get('url', '')
        coupon_name = details.get('name_en', '')
        coupon_code = details.get('code', '')

        search_result = google_search(f"{product}", f"{coupon_url}")
    
        if search_result:
            st.markdown(f"Visit **{coupon_name}** and use coupon code **{coupon_code}** to get a discount: [{search_result['title']}]({search_result['link']})")
        
def search_stores(relevant_brands, product, api, search_id):

    for brand, details in relevant_brands:
        # Format the coupon information for English language
        coupon_url = details.get('url', '')
        coupon_name = details.get('name_en', '')
        coupon_code = details.get('code', '')
    
        url = "https://www.googleapis.com/customsearch/v1"

        params = {
            "q": f"{product} site:{coupon_url}",
            'key': api,
            'cx': search_id
        }

        response = requests.get(url, params=params)
        results = response.json()

        if 'items' in results:
            st.markdown(f"Visit **{coupon_name}** and use coupon code **{coupon_code}** to get a discount: [{results['items'][0]['title']}]({results['items'][0]['link']})")



#Calling all the functions:
def all_comp(llm_find_brands, category_list, uq):

    brand_dict = load_brands_dict("brands_dict1.json")
    pattern = re.compile(r'.+\..+')
    is_url = 0
    if re.search(pattern, uq):
        uq_raw = get_product(uq, llm_find_brands)
        uq = uq_raw.content
        is_url = 1

    relevent_category = get_relevent_category(uq, category_list, llm_find_brands)

    #st.write(relevent_category.content)

    relevant_brands = get_coupons(relevent_category.content, brand_dict)

    search_stores_free(relevant_brands, uq)


    st.divider()
    with st.expander("Token Usage"):
        if is_url:
           st.write("Tokens used for finding product from url (0.8 temp):", uq_raw.response_metadata['token_usage']) 
           input_cost = (uq_raw.response_metadata['token_usage']['prompt_tokens'] / 1_000_000) * 5.00
           output_cost = (uq_raw.response_metadata['token_usage']['completion_tokens'] / 1_000_000) * 15.00
           st.write("Cost (USD):",  round(input_cost+output_cost, 5))
        
        st.write("Tokens used for finding brands (0.8 temp):", relevent_category.response_metadata['token_usage'])
        input_cost = (relevent_category.response_metadata['token_usage']['prompt_tokens'] / 1_000_000) * 5.00
        output_cost = (relevent_category.response_metadata['token_usage']['completion_tokens'] / 1_000_000) * 15.00
        st.write("Cost (USD):",  round(input_cost+output_cost, 5))

#-----------------------------------------------------------------------------------------------------------------------------------

#STREAMLIT UI

#The title of the UI:
st.header('Resal Coupon Finder')
st.write("A PoC for utilizing AI Agents for Resal's Save More coupon store.")


#Api key:
openAI_api = st.text_input("[Enter your OpenAI key to get started](https://openai.com/api/)", type="password")
st.divider()
#Chatting:
st.subheader("What are you looking for?")


if openAI_api:
    #LLM initializations for finding relevent brands. (Creative = 0.8 tempreture)
    llm_find_brands = ChatOpenAI(model_name="gpt-4",temperature=0.8, openai_api_key=openAI_api)

    user_question = st.text_input("Enter a product or a url link: ")
    st.write("(Example) You can enter either:")
    st.write("LG TV")
    st.write("or a link like:")
    st.write("https://www.amazon.ca/lg-oled-65/s?k=lg+oled+65")
    st.divider()
    st.subheader('Results:')
    if user_question != "":
        all_comp(llm_find_brands, category_names, user_question)

