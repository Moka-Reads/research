import requests
import pandas as pd

def fetch_books_from_google(query, max_results=1200, api_key=None):
    url = "https://www.googleapis.com/books/v1/volumes"
    books = []
    fetched = 0
    step = 40  # max allowed per Google Books API

    while fetched < max_results:
        params = {
            "q": query,
            "startIndex": fetched,
            "maxResults": min(step, max_results - fetched),
            "printType": "books",
            "langRestrict": "en"
        }
        if api_key:
            params["key"] = api_key

        response = requests.get(url, params=params)
        if response.status_code != 200:
            print(f"Error: {response.status_code} - {response.text}")
            break

        data = response.json()
        items = data.get("items", [])
        if not items:
            break  # no more results

        for item in items:
            volume = item.get("volumeInfo", {})
            sale = item.get("saleInfo", {})

            title = volume.get("title", "N/A")
            authors = ", ".join(volume.get("authors", []))
            page_count = volume.get("pageCount", "N/A")
            publisher = volume.get("publisher", "N/A")
            format_ = volume.get("printType", "N/A")

            retail_price = sale.get("retailPrice", {}).get("amount")
            currency = sale.get("retailPrice", {}).get("currencyCode", "")
            price = f"{retail_price} {currency}" if retail_price else "N/A"
            source = sale.get("buyLink", "N/A")
            is_ebook = sale.get("isEbook", False)

            books.append({
                "Title": title,
                "Authors": authors,
                "Pages": page_count,
                "Publisher": publisher,
                "Format": format_,
                "Price": price,
                "Source": source,
                "IsEbook": is_ebook,
                "Volume": volume, 
                "Sale": sale, 
            })

        fetched += len(items)

    df = pd.DataFrame(books)

    # Extract numeric value from the 'Price' column (all assumed CAD)
    df['PriceValue'] = df['Price'].str.extract(r'([\d.]+)').astype(float)

    # Clean the dataset: drop rows with N/A in Price or Pages
    df_clean = df[
        (df["Price"] != "N/A") &
        (df["Pages"] != "N/A")
    ].copy()

    return df_clean
# Example usage
df_google = fetch_books_from_google("programming")
df_google.to_csv("dataset.csv")


# Ensure Pages column is numeric
df_google['Pages'] = df_google['Pages'].astype(float)

# Split datasets
ebooks = df_google[df_google['IsEbook'] == True]
nonebooks = df_google[df_google['IsEbook'] == False]

# eBooks stats
min_price_ebook = ebooks['PriceValue'].min()
max_price_ebook = ebooks['PriceValue'].max()
mean_price_ebook = ebooks['PriceValue'].mean()

min_page_ebook = ebooks['Pages'].min()
max_page_ebook = ebooks['Pages'].max()
mean_page_ebook = ebooks['Pages'].mean()

# Non-eBooks stats
min_price_physical = nonebooks['PriceValue'].min()
max_price_physical = nonebooks['PriceValue'].max()
mean_price_physical = nonebooks['PriceValue'].mean()

min_page_physical = nonebooks['Pages'].min()
max_page_physical = nonebooks['Pages'].max()
mean_page_physical = nonebooks['Pages'].mean()
print(f"Dataset size: {len(df_google)}")
# Output
print("📘 eBooks:")
print(f"  Minimum Price: {min_price_ebook}")
print(f"  Maximum Price: {max_price_ebook}")
print(f"  Average Price: {mean_price_ebook:.2f}")
print(f"  Minimum Pages: {min_page_ebook}")
print(f"  Maximum Pages: {max_page_ebook}")
print(f"  Average Pages: {mean_page_ebook:.2f}\n")

if nonebooks.empty:
    print("All books in the dataset are eBooks\n")
else:
    print("📗 Non-eBooks:")
    print(f"  Minimum Price: {min_price_physical}")
    print(f"  Maximum Price: {max_price_physical}")
    print(f"  Average Price: {mean_price_physical:.2f}")
    print(f"  Minimum Pages: {min_page_physical}")
    print(f"  Maximum Pages: {max_page_physical}")
    print(f"  Average Pages: {mean_page_physical:.2f}")
    
print(f"{ebooks.describe()}")

df_google['PricePerPage'] = df_google['PriceValue'] / df_google['Pages']
min_ppp = df_google['PricePerPage'].min()
max_ppp = df_google['PricePerPage'].max()
mean_ppp = df_google['PricePerPage'].mean()

print(f"Min Price/Page: ${min_ppp:.4f}")
print(f"Max Price/Page: ${max_ppp:.4f}")
print(f"Average Price/Page: ${mean_ppp:.4f}")
