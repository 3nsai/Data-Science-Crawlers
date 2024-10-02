import requests
import json
import pandas as pd
import re
import csv
from bs4 import BeautifulSoup

#======================================================================================
url = "https://api.d3.app/graphql"
headers = {}
# List your query here
query_string_MPF = "query MarketplaceFeed($page: Int, $size: Int, $tld: String, $previousDays: Int, $type: MarketplaceFeedRecordType) {\n  marketplaceFeed(\n    page: $page\n    size: $size\n    tld: $tld\n    previousDays: $previousDays\n    type: $type\n  ) {\n    items {\n      sld\n      tld\n      type\n      price\n      currency {\n        symbol\n        decimals\n        icon\n      }\n      buyerName\n      sellerName\n      updatedAt\n    }\n    totalCount\n    pageSize\n    currentPage\n    totalPages\n    hasPreviousPage\n    hasNextPage\n    brandingInfo {\n      name\n      styling {\n        fontColor\n        primaryColor\n        squareLogo {\n          url\n        }\n        logo {\n          url\n        }\n        secondaryColor\n      }\n      tld\n    }\n  }\n}"
query_string_SRL = "query SearchRecentListings($page: Int, $size: Int, $tlds: [String!], $minPrice: Float, $maxPrice: Float, $minChars: Int, $maxChars: Int, $premiumNames: Boolean, $sortByDate: SortOrder, $sortByPrice: SortOrder) {\n  searchRecentListings(\n    page: $page\n    size: $size\n    tlds: $tlds\n    minPrice: $minPrice\n    maxPrice: $maxPrice\n    minChars: $minChars\n    maxChars: $maxChars\n    premiumNames: $premiumNames\n    sortByDate: $sortByDate\n    sortByPrice: $sortByPrice\n  ) {\n    items {\n      sld\n      tld\n      registrant {\n        id\n        name\n      }\n     ownerName\n      chain {\n      blockExplorerUrl\n        name\n        networkId\n  \n      }\n    \n    }\n    }\n \n}"

# Sent request
response = requests.post(url, json={'query': query_string_MPF})
response_data = response.json()

try:
    # Load data
    items = response_data.get('data', {}).get('marketplaceFeed', {}).get('items', [])
    
    # Initialize empty list
    extracted_data = []

    # Iterate over items
    for item in items:
        sld = item.get('sld')
        tld = item.get('tld')
        item_type = item.get('type')
        price = item.get('price')
        buyer = item.get('buyerName')
        seller = item.get('sellerName')
        
        # Add item to list
        extracted_data.append({
            'sld': sld,
            'tld': tld,
            'type': item_type,
            'price': price,
            'buyer': buyer,
            'seller': seller
        })

    # Print extracted data
    for data in extracted_data:
        print(data)

except Exception as e:
    print("Error processing the JSON data:", str(e))

#<><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><><>
# Modify your query string and run it again
# Add headers if needed adn Variables
print("<>" * 50)
variables = {
    'page': 1,
    'size': 60,
    'tlds': ["core", "vic", "shib"],
    'premiumNames': True,
    'sortByDate': 'DESC'
}
response = requests.post(url, json={'query': query_string_SRL, 'variables': variables})
print(response.status_code)

# if response.status_code == 200:
#     try:
#         response_data = response.json()
#         print(response_data)
#     except json.JSONDecodeError:
#         print("Failed to decode JSON from response")
# else:
#     print(f"HTTP Request Failed: Status Code {response.status_code}")
#     print("Response content:", response.text)
# response_data = response.json()
response_data = response.json()
try:
    # Load data
    items = response_data.get('data', {}).get('searchRecentListings', {}).get('items', [])
    
    # Initialize empty list
    extracted_data = []

    # Iterate over items
    for item in items:
        sld = item.get('sld')
        tld = item.get('tld')
        registrant = item.get('registrant')
        saleType = item.get('saleType')
        # owner = item.get('ownerName')
        
        # Add item to list
        extracted_data.append({
            'sld': sld,
            'tld': tld,
            'registrant': registrant,
            'saleType': saleType,
            # 'owner': ownerName
        })

    # Print extracted data
    for data in extracted_data:
        print(data)

except Exception as e:
    print("Error processing the JSON data:", str(e))