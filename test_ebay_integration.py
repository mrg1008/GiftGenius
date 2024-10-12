from ebay_integration import EbayIntegration

def test_ebay_search():
    ebay = EbayIntegration()
    
    # Test case 1: Basic search
    results = ebay.search_gifts(['watch'], '10', '100', 5)
    print("Test case 1 - Basic search:")
    print(f"Number of results: {len(results)}")
    for item in results:
        print(f"Title: {item['title']}, Price: {item['price']} {item['currency_code']}")
    print("\n")

    # Test case 2: Multiple keywords
    results = ebay.search_gifts(['vintage', 'camera'], '50', '200', 3)
    print("Test case 2 - Multiple keywords:")
    print(f"Number of results: {len(results)}")
    for item in results:
        print(f"Title: {item['title']}, Price: {item['price']} {item['currency_code']}")
    print("\n")

    # Test case 3: Higher price range
    results = ebay.search_gifts(['laptop'], '500', '1000', 4)
    print("Test case 3 - Higher price range:")
    print(f"Number of results: {len(results)}")
    for item in results:
        print(f"Title: {item['title']}, Price: {item['price']} {item['currency_code']}")

if __name__ == "__main__":
    test_ebay_search()
