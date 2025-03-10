from ebay_integration import EbayIntegration
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_ebay_search():
    try:
        ebay = EbayIntegration()
        
        # Test case 1: Basic search
        logger.info("Test case 1 - Basic search:")
        results = ebay.search_gifts(['watch'], '10', '100', 5)
        logger.info(f"Number of results: {len(results)}")
        for item in results:
            logger.info(f"Title: {item['title']}, Price: {item['price']} {item['currency_code']}")
        logger.info("\n")

        # Test case 2: Multiple keywords
        logger.info("Test case 2 - Multiple keywords:")
        results = ebay.search_gifts(['vintage', 'camera'], '50', '200', 3)
        logger.info(f"Number of results: {len(results)}")
        for item in results:
            logger.info(f"Title: {item['title']}, Price: {item['price']} {item['currency_code']}")
        logger.info("\n")

        # Test case 3: Higher price range
        logger.info("Test case 3 - Higher price range:")
        results = ebay.search_gifts(['laptop'], '500', '1000', 4)
        logger.info(f"Number of results: {len(results)}")
        for item in results:
            logger.info(f"Title: {item['title']}, Price: {item['price']} {item['currency_code']}")

    except ValueError as ve:
        logger.error(f"Configuration Error: {str(ve)}")
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    test_ebay_search()
