import asyncio
import json
from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

async def fetch_partner_codes():
    # transport with a defined url endpoint
    transport = AIOHTTPTransport(url="https://store-ms.resal.me/graphql")

    # GraphQL client using the defined transport
    client = Client(transport=transport, fetch_schema_from_transport=True)

    # GraphQL query
    query = gql(
        """
        query {
        getPartnerCodePage(input: {
            acceptLanguage: "en",
            limit: 50,
        }) {
            ... on PartnerPageResult {
            partnerCodes {
                code
                partner {
                name_en
                name_ar
                url
                }
            }
            }
        }
        }
        """
    )

    # Execute the query on the transport
    try:
        result = await client.execute_async(query)
        return result
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Run the async function and process the result
result = asyncio.run(fetch_partner_codes())

if result:
    print('got here :)')
    # Extract the relevant data
    partner_codes = result.get('getPartnerCodePage', {}).get('partnerCodes', [])
    
    # Create a dictionary with 'name_en' as keys and brand information as values
    brands_dict = {pc['partner']['name_en'].strip(): {
        'name_en': pc['partner']['name_en'].strip(),
        'name_ar': pc['partner']['name_ar'],
        'code': pc['code'],
        'url': pc['partner']['url'].replace('/ar', '/en').replace('ar/', 'en/').replace('=ar', '=en'),
        'category': []

    } for pc in partner_codes}


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

    for category, brands in categories.items():
        for brand in brands:
            if brand in brands_dict:
                # Add the category information to the brand's dictionary
                brands_dict[brand]['category'].append(category)

    for brand, details in brands_dict.items():
        print(details['url'])

    # Save the dictionary to a JSON file
    with open('brands_dict.json', 'w') as f:
        json.dump(brands_dict, f)

