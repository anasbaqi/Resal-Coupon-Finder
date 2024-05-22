#Loading Packages
import streamlit as st
from langchain_community.chat_models import ChatOpenAI
import pandas as pd
import numpy as np
from deep_translator import GoogleTranslator


#Class for coupon information, contains: name in en, arabic, coupon code, category it belongs to, description and id for later
class Coupons:
    def __init__(self, name_en, name_ar, code, description="", category=None,  api_id=0):
        self.name_en = name_en
        self.name_ar = name_ar
        self.code = code
        self.description = description
        self.category = category if category is not None else []
        self.api_id = api_id

    def __str__(self):
        return f"Partner(name_en={self.name_en}, name_ar={self.name_ar}, code = {self.code}, category = {self.category})"

# List of Coupons
coupon_data = [
    {"code": "RSL10", "partner": {"name_en": "noon", "name_ar": "نون"}},
    {"code": "RSL0", "partner": {"name_en": "namshi", "name_ar": "نمشي"}},
    {"code": "EP26", "partner": {"name_en": "SSSports", "name_ar": "الشمس والرمال للرياضة"}},
    {"code": "SOM54", "partner": {"name_en": "Styli", "name_ar": "ستايلي"}},
    {"code": "PF4", "partner": {"name_en": "Basharacare", "name_ar": "بشرة كير"}},
    {"code": "G63", "partner": {"name_en": "Ted Baker", "name_ar": "تيد بيكر"}},
    {"code": "PJZ", "partner": {"name_en": "Nabataty", "name_ar": "متجر نباتاتي"}},
    {"code": "PTAH", "partner": {"name_en": "Toys R Us", "name_ar": "تويز آر اس"}},
    {"code": "CR67", "partner": {"name_en": "UnderArmour", "name_ar": "اندرارمر"}},
    {"code": "PF45", "partner": {"name_en": "Metro Brazil", "name_ar": "مترو برازيل"}},
    {"code": "BB37", "partner": {"name_en": "R&B", "name_ar": "آر اند بي"}},
    {"code": "LC5", "partner": {"name_en": "The Luxury Closet", "name_ar": "ذا لاكجري كلوزيت"}},
    {"code": "OM36", "partner": {"name_en": "fordeal", "name_ar": "فورديل"}},
    {"code": "RSL", "partner": {"name_en": "Level Shoes", "name_ar": "ليڤيل شوز"}},
    {"code": "RSL", "partner": {"name_en": "Mamas & Papas", "name_ar": "ماماز اند باباز"}},
    {"code": "PF98", "partner": {"name_en": "Brands For Less", "name_ar": "براندز فور ليس"}},
    {"code": "RSL30", "partner": {"name_en": "Sivvi", "name_ar": "سيفي"}},
    {"code": "P56", "partner": {"name_en": "Ya Hala", "name_ar": "يا هلا"}},
    {"code": "PFIPC", "partner": {"name_en": "Boots", "name_ar": "بوتس"}},
    {"code": "PFEXH", "partner": {"name_en": "New Balance", "name_ar": "نيو بالنس"}},
    {"code": "PFDJD", "partner": {"name_en": "COS", "name_ar": "كوس"}},
    {"code": "PFQDC", "partner": {"name_en": "Mothercare", "name_ar": "مذركير"}},
    {"code": "RSL", "partner": {"name_en": "GAP", "name_ar": "جاب"}},
    {"code": "PFXPB", "partner": {"name_en": "American Eagle", "name_ar": "أميركان ايجل"}},
    {"code": "RSL", "partner": {"name_en": "Mumzworld", "name_ar": "ممزورلد"}},
    {"code": "RSL", "partner": {"name_en": "CitrussTv", "name_ar": "سيتروس"}},
    {"code": "RA", "partner": {"name_en": "Mikyajy", "name_ar": "مكياجي"}},
    {"code": "BB58", "partner": {"name_en": "Forever21", "name_ar": "فوريفير 21"}},
    {"code": "PF32", "partner": {"name_en": "Barakat", "name_ar": "بركات"}},
    {"code": "PF53", "partner": {"name_en": "Store Us", "name_ar": "ستور اص"}},
    {"code": "MM128", "partner": {"name_en": "Lego", "name_ar": "ليقو"}},
    {"code": "OM605", "partner": {"name_en": "Lyle & Scott", "name_ar": "لايل اند سكوت"}},
    {"code": "PL59", "partner": {"name_en": "AlDakheel Oud", "name_ar": "الدخيل للعود"}},
    {"code": "PFGZS", "partner": {"name_en": "The Bodyshop", "name_ar": "ذي بودي شوب"}},
    {"code": "RSL", "partner": {"name_en": "Eyewa", "name_ar": "ايوا"}},
    {"code": "ASM9", "partner": {"name_en": "Homes R us", "name_ar": "هومز ار اس"}},
    {"code": "PFNMT", "partner": {"name_en": "Pottery Barn", "name_ar": "بوتري بارن"}},
    {"code": "RSL", "partner": {"name_en": "Bloomingdale's", "name_ar": "بلومينغديلز"}}
]


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

#functiion for categorizing all the coupons, API does not have this information so I did it myself
def categorize(coupon_data, categories):
    #adding the categories to the class:
    for item in coupon_data:
        brand_name = item['partner']['name_en']
        item['category'] = []
        
        for category, brands in categories.items():
            if brand_name in brands:
                item['category'].append(category)
        
        if not item['category']:
            item['category'].append('other')

    # Create a list to store Partner instances
    coupons = []

    # Create Partner instances from the data and add them to the list
    for coupon in coupon_data:
        name_en = coupon["partner"]["name_en"]
        name_ar = coupon["partner"]["name_ar"]
        code = coupon["code"]
        category = coupon["category"]
        partner = Coupons(name_en, name_ar, code, category=category)
        coupons.append(partner)
    
    return coupons




#Using the llm to retrieve the string that contains the name of the product from the prompt question:
def get_product(prompt_question, llm):
    """Function to extract the product from the prompt question"""

    messages = [
    ("system", "Do not answer the prompt, just output a single string that is the product the user is asking for."),
    ("human", prompt_question),
    ]

    return llm.invoke(messages)



#Function for creating a string with all coupon names:
def get_categories(categories):
    """Tool that returns a string of all the categories separated by commas."""
    return ', '.join(categories.keys())


#Function for retrieving category using llm:
def get_relevent_category(prompt_product, category_names, llm):
    """Function to find a list of relevent category based on the product"""

    messages = [
    ("system", "The prompt provides a product and a list of categories. Just output which category is most relevent based on the product."),
    ("human", f"Product:{prompt_product}, List of categories: {category_names}"),
    ]

    return llm.invoke(messages)



def get_coupons(relevant_category, coupons, Coupons, lang):
    # Filter the list of brands based on the relevant brand names
    relevent_coupons = [coupon for coupon in coupons if relevant_category in coupon.category]
    if lang == 0:
        for coupon in relevent_coupons:
            st.write(f"Use coupon code: **{coupon.code}** to get a discount from **{coupon.name_en}**")
    
    else:
        for coupon in relevent_coupons:
            st.write(f"استخدم رمز القسيمة: **{coupon.code}** للحصول على خصم من **{coupon.name_ar}**")


#Calling all the functions:
def all_comp(llm_retrieve_product, llm_find_brands, category_list, uq, Coupons, lang):

    coupons = categorize(coupon_data, category_list)

    product_all = get_product(uq, llm_retrieve_product)

    product = product_all.content
    #st.write(product)
    categories = get_categories(category_list)

    relevent_category = get_relevent_category(product, categories, llm_find_brands)

    #st.write(relevent_category.content)

    get_coupons(relevent_category.content, coupons, Coupons, lang)

    with st.expander("Token Usage"):
        st.write("Tokens used for retriving product (0.4 temp)", product_all.response_metadata['token_usage'])
        st.write("Tokens used for finding brands (0.8 temp):", relevent_category.response_metadata['token_usage'])

#-----------------------------------------------------------------------------------------------------------------------------------

#STREAMLIT UI

#The title of the UI:
st.header('Resal Coupon Finder (Using ChatGPT)')
st.write("A PoC for utilizing AI Agents for Resal's Save More coupon store.")

st.divider()

language = st.selectbox(
    "Select page language",
    ("English", "عربي")
)

if language == 'English':
    #Api key:
    api_key = st.text_input("Enter your OpenAI key to get started", type="password")
    #Chatting:
    st.subheader("What are you looking for?")


    #LLM initializations:

    #1. For retrieving product from promt question. (not creative = 0.4 temperature)
    #2. For finding relevent brands. (Creative = 0.8 tempreture)
    if api_key:
        llm_retrieve_product = ChatOpenAI(model_name="gpt-4",temperature=0.4, openai_api_key=api_key)
        llm_find_brands = ChatOpenAI(model_name="gpt-4",temperature=0.8, openai_api_key=api_key)
        
        user_question = st.text_input(" What are you looking for: ")

        st.write("Example: I want to buy a new TV")
        st.divider()
        if user_question != "":
            all_comp(llm_retrieve_product, llm_find_brands, categories, user_question, Coupons, lang=0)

else:
    #Api key:
    api_key = st.text_input("أدخل مفتاح OpenAI الخاص بك للبدء", type="password")
    st.subheader("ما الذي تبحث عنه؟")

    #LLM initializations:

    #1. For retrieving product from promt question. (not creative = 0.4 temperature)
    #2. For finding relevent brands. (Creative = 0.8 tempreture)
    if api_key:
        llm_retrieve_product = ChatOpenAI(model_name="gpt-4",temperature=0.4, openai_api_key=api_key)
        llm_find_brands = ChatOpenAI(model_name="gpt-4",temperature=0.8, openai_api_key=api_key)
        
        user_question = st.text_input(" ما الذي تبحث عنه ")
        st.write("مثال: أريد شراء جهاز تلفزيون جديد")
        st.divider()
        if user_question != "":
            english_question = GoogleTranslator(source='ar', target='en').translate(user_question)
            all_comp(llm_retrieve_product, llm_find_brands, categories, english_question, Coupons, lang=1)