from google_shopping_integration import GoogleShoppingIntegration
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_google_shopping_search():
    try:
        google_shopping = GoogleShoppingIntegration()
        
        # Test case 1: Basic search
        logger.info("Test case 1 - Basic search:")
        results = google_shopping.search_gifts(['watch'], 50, 200, 5)
        logger.info(f"Number of results: {len(results)}")
        for item in results:
            logger.info(f"Title: {item['title']}, Price: {item['price']} {item['currency_code']}")
        logger.info("\n")

        # Test case 2: Multiple keywords
        logger.info("Test case 2 - Multiple keywords:")
        results = google_shopping.search_gifts(['handmade', 'scarf'], 20, 150, 3)
        logger.info(f"Number of results: {len(results)}")
        for item in results:
            logger.info(f"Title: {item['title']}, Price: {item['price']} {item['currency_code']}")
        logger.info("\n")

        # Test case 3: Higher price range
        logger.info("Test case 3 - Higher price range:")
        results = google_shopping.search_gifts(['laptop'], 500, 1000, 4)
        logger.info(f"Number of results: {len(results)}")
        for item in results:
            logger.info(f"Title: {item['title']}, Price: {item['price']} {item['currency_code']}")

    except Exception as e:
        logger.error(f"Unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    test_google_shopping_search()
