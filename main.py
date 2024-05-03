#Loading Packages
import streamlit as st
import langchain 
from langchain_community.chat_models import ChatOpenAI
import pandas as pd
import numpy as np



#Lets create a dummy class for storing the coupon information for the different brands (i am assuming the Resal API already includes these info)
class Brand:
    def __init__(self, name, code, website):
        self.name = name
        self.code = code
        self.website = website

# List of Brands
brand_list = [
    Brand(name="Noon", code="RSL10", website='https://www.noon.com/?sskey=faf368464a154de192157ec07244c763'),
    Brand(name="Namshi", code="NM295", website="https://www.namshi.com/saudi-ar/"),
    Brand(name="Ounass", code="OP52", website="https://en-saudi.ounass.com/"),
    Brand(name="Styli", code="SOM54", website="https://stylishop.com/sa/en?sskey=cfaead66393141a986ca173f860ffa9e"),
    Brand(name="Lego", code="MM128", website="https://lego.saudiblocks.com/saudi-en/"),
    Brand(name="GAP", code="RSL", website=""),
    Brand(name="Victoria Secret", code="PFJYR", website=""),
    Brand(name="Sun & Sand", code="EP26", website=""),
    Brand(name="Foot Locker", code="PFYWR", website=""),
    Brand(name="H&M", code="PFUYV", website=""),
    Brand(name="American Eagle", code="PFXPB", website=""),
    Brand(name="Mumzworld", code="OP93", website=""),
    Brand(name="ToYou", code="RSL", website=""),
    Brand(name="REDTAG", code="P91", website=""),
    Brand(name="The Bodyshop", code="PFGZS", website=""),
    Brand(name="CitrussTv", code="RSL", website=""),
    Brand(name="UnderArmour", code="CR67", website=""),
    Brand(name="fordeal", code="OM36", website=""),
    Brand(name="Brands For Less", code="PF98", website=""),
    Brand(name="Mikyajy", code="RA", website=""),
    Brand(name="R&B", code="BB37", website=""),
    Brand(name="Forever21", code="BB58", website=""),
    Brand(name="The Luxury Closet", code="LC5", website=""),
    Brand(name="Homes R us", code="ASM9", website=""),
    Brand(name="Mothercare", code="PFQDC", website=""),
    Brand(name="COS", code="PFDJD", website=""),
    Brand(name="Eyewa", code="RSL", website=""),
    Brand(name="New Balance", code="PFEXH", website=""),
    Brand(name="Pottery Barn", code="PFNMT", website=""),
    Brand(name="West Elm", code="PFNHW", website=""),
    Brand(name="AlDakheel Oud", code="PL59", website=""),
    Brand(name="Bloomingdale's", code="RSL", website=""),
    Brand(name="Boots", code="PFIPC", website=""),
    Brand(name="Mamas & Papas", code="RSL", website=""),
    Brand(name="Metro Brazil", code="PF45", website=""),
    Brand(name="Toys R Us", code="PTAH", website=""),
    Brand(name="Ted Baker", code="G63", website=""),
    Brand(name="Lyle & Scott", code="OM605", website=""),
    Brand(name="Sivvi", code="RSL30", website="")
]


#Setting the brand names as a table the user can see:
brand_data = [{"Name": brand.name, "Code": brand.code} for brand in brand_list]
brand_df = pd.DataFrame(brand_data)


#Using the llm to retrieve the string that contains the name of the product from the prompt question:
def get_product(prompt_question, llm):
    """Function to extract the product from the prompt question"""

    messages = [
    ("system", "Do not answer the prompt, just output 1 string from the prompt that is the product the prompt user is asking a coupon for."),
    ("human", prompt_question),
    ]

    return llm.invoke(messages)



#Function for creating a string with all brand names:
def get_brand_names(brands):
    """Tool that returns a string of all the brand names separated by commas."""
    return ', '.join(brand.name for brand in brands)


#Function for retrieving relevent brands using llm:
def get_relevent_brands(prompt_product, brand_names, llm):
    """Function to find a list of relevent brands based on the product"""

    messages = [
    ("system", "The prompt provides a product and a list of brand names. Search through the brand names and return a list of ones that might sell the product (maximum of 3 brands).If you don't think any of the brands might have the product, then return a empty list"),
    ("human", f"Product:{prompt_product}, List of brand names: {brand_names}"),
    ]

    return llm.invoke(messages)


# #Function for retrieving brand coupon codes from the brand name:
# def get_coupons(relevent_brands, brands):
#   # Split the string into individual brand names
#   brand_names = [name.strip() for name in relevent_brands.split(',')]

#   # Iterate over the brand names and check if they match any of the brands in the list
#   for name in brand_names:
#       for brand in brands:
#           if name == brand.name:
#               st.write("Use Coupon Code:", brand.code,  "to get a discout from", brand.name)

def get_coupons(relevant_brands, brand_list, Brand):
    # Split the string into individual brand names
    #brand_names = [name.strip() for name in relevant_brands.split(',')]

    # Filter the list of brands based on the relevant brand names
    
    final_list = [brand for brand in brand_list if brand.name in relevant_brands]
    for brand in final_list:
        st.write("Use coupon code:", brand.code,  "to get a discount from", brand.name)




#Calling all the functions:
def all_comp(llm_retrieve_product, llm_find_brands, brand_list, uq, Brand):

    product_all = get_product(uq, llm_retrieve_product)
            
    product = product_all.content

    brands = get_brand_names(brand_list)

    relevent_brands = get_relevent_brands(product, brands, llm_find_brands)



    get_coupons(relevent_brands.content, brand_list, Brand)

    with st.expander("Token Usage"):
        st.write("Tokens used for retriving product (0.2 temp)", product_all.response_metadata['token_usage'])
        st.write("Tokens used for finding brands (0.8 temp):", relevent_brands.response_metadata['token_usage'])

#-----------------------------------------------------------------------------------------------------------------------------------

#STREAMLIT UI

#The title of the UI:
st.header('Resal Coupon Finder (Using ChatGPT)')
st.write("A PoC for utilizing AI Agents for Resal's Save More coupon store.")
st.divider()

st.subheader('Brand names and their coupon codes:')
st.dataframe(brand_df, hide_index=True, width=700)

st.divider()

#Chatting:
st.subheader("What are you looking for")

#Api key:
api_key = st.text_input("Enter your OpenAI key to get started", type="password")


#LLM initializations:

#1. For retrieving product from promt question. (not creative = 0.2 temperature)
#2. For finding relevent brands. (Creative = 0.8 tempreture)


if api_key:
    llm_retrieve_product = ChatOpenAI(model_name="gpt-4",temperature=0.2, openai_api_key=api_key)
    llm_find_brands = ChatOpenAI(model_name="gpt-4",temperature=0.8, openai_api_key=api_key)
    st.write("Example: I want coupons to buy a new TV")
    user_question = st.text_input(" What are you looking for: ")

    if user_question != "":
        all_comp(llm_retrieve_product, llm_find_brands, brand_list, user_question, Brand)
