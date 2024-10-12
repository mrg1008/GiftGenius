from etsy_integration import EtsyIntegration
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_etsy_search():
    try:
        etsy = EtsyIntegration()
        
        # Test case 1: Basic search
        logger.info("Test case 1 - Basic search:")
        results = etsy.search_gifts(['necklace'], '10', '100', 5)
        logger.info(f"Number of results: {len(results)}")
        for item in results:
            logger.info(f"Title: {item['title']}, Price: {item['price']} {item['currency_code']}")
        logger.info("\n")

        # Test case 2: Multiple keywords
        logger.info("Test case 2 - Multiple keywords:")
        results = etsy.search_gifts(['handmade', 'scarf'], '20', '150', 3)
        logger.info(f"Number of results: {len(results)}")
        for item in results:
            logger.info(f"Title: {item['title']}, Price: {item['price']} {item['currency_code']}")
        logger.info("\n")

        # Test case 3: Higher price range
        logger.info("Test case 3 - Higher price range:")
        results = etsy.search_gifts(['artwork'], '200', '500', 4)
        logger.info(f"Number of results: {len(results)}")
        for item in results:
            logger.info(f"Title: {item['title']}, Price: {item['price']} {item['currency_code']}")

    except ValueError as ve:
        logger.error(f"Configuration Error: {str(ve)}")
    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    test_etsy_search()
