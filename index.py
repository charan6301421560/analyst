import requests
from bs4 import BeautifulSoup
import csv

def scrape_product_listing_page(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    products = []

    # Extract product information from the page
    for product in soup.find_all("div", class_="s-result-item"):
        product_info = {}

        try:
            product_info["Product URL"] = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_1" + \
                product.find("a", class_="a-link-normal")["href"]
        except:
            product_info["Product URL"] = None

        try:
            product_info["Product Name"] = product.find(
                "span", class_="a-text-normal").text.strip()
        except:
            product_info["Product Name"] = None

        try:
            product_info["Product Price"] = product.find(
                "span", class_="a-offscreen").text.strip()
        except:
            product_info["Product Price"] = None

        try:
            rating = product.find("span", class_="a-icon-alt").text
            product_info["Rating"] = float(rating.split()[0])
        except:
            product_info["Rating"] = None

        try:
            product_info["Number of Reviews"] = int(product.find(
                "span", class_="a-size-base").text.replace(",", ""))
        except:
            product_info["Number of Reviews"] = None

        products.append(product_info)

    return products

base_url = "https://www.amazon.in/s?k=bags&crid=2M096C61O4MLT&qid=1653308124&sprefix=ba%2Caps%2C283&ref=sr_pg_{}"

all_products = []

# Scrape 20 pages of product listing
for page_number in range(1, 21):
    url = base_url.format(page_number)
    products_on_page = scrape_product_listing_page(url)
    all_products.extend(products_on_page)

print("Scraping of product listing pages completed.")

def scrape_product_page(product_url):
    if not product_url:
        return None

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"}

    response = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    product_info = {}

    try:
        product_info["Description"] = soup.find(
            "meta", {"name": "description"})["content"]
    except:
        product_info["Description"] = None

    try:
        product_info["ASIN"] = soup.find(
            "th", string="ASIN").find_next_sibling("td").text.strip()
    except:
        product_info["ASIN"] = None

    try:
        product_info["Product Description"] = soup.find(
            "div", id="productDescription").text.strip()
    except:
        product_info["Product Description"] = None

    try:
        product_info["Manufacturer"] = soup.find(
            "a", {"id": "bylineInfo"}).text.strip()
    except:
        product_info["Manufacturer"] = None

    return product_info

# Fetch additional information for each product URL
for product in all_products:
    product_url = product["Product URL"]
    additional_info = scrape_product_page(product_url)
    if additional_info is not None:
        product.update(additional_info)
print("Scraping of product pages completed.")

# Export data to a CSV file
csv_filename = "amazon_products.csv"

with open(csv_filename, mode='w', newline='', encoding='utf-8') as csv_file:
    fieldnames = ["Product URL", "Product Name", "Product Price", "Rating", "Number of Reviews", "Description", "ASIN", "Product Description", "Manufacturer"]
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

    for product in all_products:
        writer.writerow(product)

print("Data exported to CSV file:", csv_filename)
