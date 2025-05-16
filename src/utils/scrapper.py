from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import re
from bs4 import BeautifulSoup
from math import ceil

class Scrapper:

    def selenium_scrape(self, urls, output_file=None):
        """
        Downloads one or more webpages' HTML content using Selenium to bypass basic scraping protections.

        Args:
            urls (str or list): The URL or list of URLs to download
            output_file (str, optional): Path to save the HTML content(s). If multiple URLs, saves as numbered files.

        Returns:
            List[str]: List of HTML content strings
        """
        raise NotImplementedError("This method should be implemented in subclasses.")

    def parse_apartment_listings(self, html_content):
        """
        Extract a list of appartments from the HTML.
        
        Args:
            html_content (str): The HTML content to parse
            class_name (str): The class name to search for
            
        Returns:
            list: A list of elements (as strings) that have the specified class
        """
        raise NotImplementedError("This method should be implemented in subclasses.")
    
    def generate_pagination_urls(self, base_url, num_pages):
        """
        Generate paginated URLs based on a base URL.
        
        Args:
            base_url (str): The base URL (with or without pagination)
            num_pages (int): The number of pages to generate
        
        Returns:
            list: A list of paginated URLs, or None if URL already contains pagination
        """
        raise NotImplementedError("This method should be implemented in subclasses.")


class ZonaPropScrapper(Scrapper):

    def selenium_scrape(self, urls, output_file=None):
        """
        Downloads one or more webpages' HTML content using Selenium to bypass basic scraping protections.

        Args:
            urls (str or list): The URL or list of URLs to download
            output_file (str, optional): Path to save the HTML content(s). If multiple URLs, saves as numbered files.

        Returns:
            List[str]: List of HTML content strings
        """

        if isinstance(urls, str):
            urls = [urls]

        html_contents = []
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36")

            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            driver.set_page_load_timeout(30)

            for idx, url in enumerate(urls):
                print(f"Accessing webpage: {url}")
                driver.get(url)
                time.sleep(5)
                html_content = driver.page_source
                html_contents.append(html_content)
                if output_file:
                    if len(urls) == 1:
                        file_path = output_file
                    else:
                        file_path = f"{output_file.rsplit('.', 1)[0]}_{idx+1}.html"
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(html_content)
                    print(f"HTML content saved to {file_path} ({len(html_content)} characters)")
            driver.quit()
            return html_contents
        except Exception as e:
            print(f"Error: {e}")
            return []

    def parse_property_listings(self, html_content):
        """
        Extract all elements and their children with a specific class name from HTML content.
        
        Args:
            html_content (str): The HTML content to parse
            class_name (str): The class name to search for
            
        Returns:
            list: A list of elements (as strings) that have the specified class
        """

        if isinstance(html_content, list):
            html_content = "".join(html_content)

        # Parse the HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all elements with the specified class
        elements = soup.find_all(class_="postingCardLayout-module__posting-card-layout")
        
        # Convert the elements to strings to preserve their structure including children
        extracted_elements = [str(element) for element in elements]
        
        apartments = []
        
        for html_element in extracted_elements:
            # Parse the HTML element
            soup = BeautifulSoup(html_element, 'html.parser')
            
            # Initialize apartment data dictionary
            apartment_data = {
                "id": None,
                "price": {
                    "monthly_rent": None,
                    "maintenance_fee": None,
                    "total_price": None,
                    "price_per_sqm": None
                },
                "location": {
                    "address": None,
                    "neighborhood": None
                },
                "specifications": {},
                "features": [],
                "url": None,
                "description": None,
                "agency": None,
                "images": []
            }
            
            # Extract ID from data attribute
            if 'data-id' in soup.div.attrs:
                apartment_data["id"] = soup.div['data-id']
            
            # Extract URL from data attribute or anchor tag
            url_element = soup.select_one('a[href]')
            if url_element and 'href' in url_element.attrs:
                apartment_data["url"] = "https://www.zonaprop.com.ar" + url_element['href']
            
            # Extract price information
            price_element = soup.select_one('.postingPrices-module__price')
            if price_element:
                apartment_data["price"]["monthly_rent"] = price_element.text.strip()
            
            # Extract maintenance fee
            expenses_element = soup.select_one('.postingPrices-module__expenses')
            if expenses_element:
                apartment_data["price"]["maintenance_fee"] = expenses_element.text.strip()

            # Extract address
            address_element = soup.select_one('.postingLocations-module__location-address')
            if address_element:
                apartment_data["location"]["address"] = address_element.text.strip()
            
            # Extract neighborhood
            location_element = soup.select_one('.postingLocations-module__location-text')
            if location_element:
                apartment_data["location"]["neighborhood"] = location_element.text.strip()
            
            # Extract specifications
            features_container = soup.select_one('.postingMainFeatures-module__posting-main-features-block')
            if features_container:
                feature_spans = features_container.select('.postingMainFeatures-module__posting-main-features-span')
                for span in feature_spans:
                    text = span.text.strip()
                    if 'm²' in text:
                        # Extract only the numeric value and unit
                        area_match = re.search(r'(\d+)\s*m²', text)
                        if area_match:
                            apartment_data["specifications"]["total_area_m2"] = int(area_match.group(1))
                        else:
                            apartment_data["specifications"]["total_area"] = text
                    elif 'amb.' in text:
                        # Extract number of rooms
                        rooms_match = re.search(r'(\d+)\s*amb', text)
                        if rooms_match:
                            apartment_data["specifications"]["rooms"] = int(rooms_match.group(1))
                        else:
                            apartment_data["specifications"]["rooms_text"] = text
                    elif 'dorm.' in text:
                        # Extract number of bedrooms
                        bedrooms_match = re.search(r'(\d+)\s*dorm', text)
                        if bedrooms_match:
                            apartment_data["specifications"]["bedrooms"] = int(bedrooms_match.group(1))
                        else:
                            apartment_data["specifications"]["bedrooms_text"] = text
                    elif 'baño' in text:
                        # Extract number of bathrooms
                        bathrooms_match = re.search(r'(\d+)\s*baño', text)
                        if bathrooms_match:
                            apartment_data["specifications"]["bathrooms"] = int(bathrooms_match.group(1))
                        else:
                            apartment_data["specifications"]["bathrooms_text"] = text
                    elif 'coch.' in text:
                        # Extract number of parking spaces
                        parking_match = re.search(r'(\d+)\s*coch', text)
                        if parking_match:
                            apartment_data["specifications"]["parking_spaces"] = int(parking_match.group(1))
                        else:
                            apartment_data["specifications"]["parking_text"] = text
            
            # Extract description
            description_element = soup.select_one('.postingCard-module__posting-description a')
            if description_element:
                apartment_data["description"] = description_element.text.strip()
                
                # Extract additional details from description
                desc_text = description_element.text.lower()
                
                # Check for elevator
                if 'ascensor' in desc_text:
                    apartment_data["features"].append("elevator")
                
                # Check for floor level
                if 'piso alto' in desc_text:
                    apartment_data["specifications"]["floor_level"] = "high"
                            
                # Check for balcony
                if 'balcón' in desc_text:
                    apartment_data["features"].append("balcony")
                
                # Check for built-in closet
                if 'placard' in desc_text:
                    apartment_data["features"].append("built_in_closet")
                
                # Check for kitchen features
                if 'cocina equipada' in desc_text:
                    apartment_data["features"].append("equipped_kitchen")
                
                # Check for brightness and spaciousness
                if 'luminoso' in desc_text:
                    apartment_data["features"].append("bright")
                if 'amplio' in desc_text:
                    apartment_data["features"].append("spacious")
                        
            # Extract real estate agency
            agency_logo = soup.select_one('.postingPublisher-module__logo')
            if agency_logo and 'alt' in agency_logo.attrs:
                apartment_data["agency"] = agency_logo['alt'].replace('logo publisher', '').strip()
            
            # Extract image URLs
            #img_elements = soup.select('img[src]')
            #for img in img_elements:
            #    if 'src' in img.attrs and 'data-flickity-lazyload' not in img.attrs and 'zonaprop' in img['src']:
                    # Filter out navigation icons and other non-property images
            #        if 'avisos' in img['src']:
            #            apartment_data["images"].append(img['src'])
            
            # Check for laundry facilities
            laundry_element = soup.select_one('.pills-module__trigger-pill-item-span')
            if laundry_element and 'lavadero' in laundry_element.text.lower():
                apartment_data["features"].append("laundry")
            
            # Calculate total_price and price_per_sqm
            def parse_price(price_str):
                if not price_str:
                    return None
                price_num = re.sub(r"[^\d]", "", price_str)
                return int(price_num) if price_num else None

            monthly_rent = parse_price(apartment_data["price"].get("monthly_rent"))
            maintenance_fee = parse_price(apartment_data["price"].get("maintenance_fee"))
            area = apartment_data["specifications"].get("total_area_m2")

            if monthly_rent is not None:
                total_price = monthly_rent + (maintenance_fee if maintenance_fee else 0)
                apartment_data["price"]["total_price"] = total_price
                if area:
                    apartment_data["price"]["price_per_sqm"] = ceil(total_price / area)
            
            # Clean up empty sections and None values
            for key in list(apartment_data.keys()):
                if apartment_data[key] is None:
                    del apartment_data[key]
                elif isinstance(apartment_data[key], dict):
                    # Remove empty nested dictionaries or dictionaries with only None values
                    nested_dict = apartment_data[key]
                    for nested_key in list(nested_dict.keys()):
                        if nested_dict[nested_key] is None:
                            del nested_dict[nested_key]
                    if not nested_dict:
                        del apartment_data[key]
                elif isinstance(apartment_data[key], list) and not apartment_data[key]:
                    del apartment_data[key]
            
            apartments.append(apartment_data)
        
        return apartments

    def generate_pagination_urls(self, base_url, num_pages):
        """
        Generate paginated URLs for Zonaprop based on a base URL.
        
        Args:
            base_url (str): The base URL (with or without pagination)
            num_pages (int): The number of pages to generate
        
        Returns:
            list: A list of paginated URLs, or None if URL already contains pagination
        """
        # Check if the base URL already contains pagination
        if "-pagina-" in base_url:
            print("Error: URL already contains pagination. Please provide a base URL without pagination.")
            return None
        
        # Remove trailing .html if present
        if base_url.endswith(".html"):
            base_url = base_url[:-5]
        
        urls = [base_url + ".html"]  # First page is the original URL
        
        # Generate URLs for subsequent pages
        for page_num in range(2, num_pages + 1):
            paginated_url = f"{base_url}-pagina-{page_num}.html"
            urls.append(paginated_url)
        
        return urls
