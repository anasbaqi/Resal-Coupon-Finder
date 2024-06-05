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
    brands_dict = {pc['partner']['name_en'].lower(): {
        'name_en': pc['partner']['name_en'],
        'name_ar': pc['partner']['name_ar'],
        'code': pc['code'],
        'url': pc['partner']['url']
    } for pc in partner_codes}

    for brand, info in brands_dict.items():
        if 'ar' in info['url']:
            info['url'] = info['url'].replace('ar', 'en')

    # Save the dictionary to a JSON file
    with open('brands_dict.json', 'w') as f:
        json.dump(brands_dict, f)

