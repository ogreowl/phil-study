import os
import requests

def sanitize_filename(filename, max_length=100):
    """Sanitize the filename to avoid illegal characters and limit the filename length."""
    sanitized = "".join(c for c in filename if c.isalnum() or c in (' ', '_')).rstrip()
    return sanitized[:max_length]  # Truncate to a maximum length

def fetch_books_from_gutendex(url, params=None):
    """Fetch books from the Gutendex API with the given parameters."""
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch books. Status code: {response.status_code}")
        return None

def download_books_from_gutendex(books, download_folder="gutenberg_books"):
    """Download books in text/plain format only, skipping already downloaded files."""
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    for book in books:
        title = book.get("title")
        formats = book.get("formats", {})

        # Only download if the book has a text/plain format
        download_url = formats.get("text/plain; charset=us-ascii")

        if download_url:
            sanitized_title = sanitize_filename(title)
            file_name = f"{download_folder}/{sanitized_title}.txt"

            # Check if the file already exists before downloading
            if os.path.exists(file_name):
                print(f"Skipping {title} - Already downloaded.")
                continue

            # Download the file
            try:
                response = requests.get(download_url)
                if response.status_code == 200:
                    with open(file_name, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded: {title}")
                else:
                    print(f"Failed to download {title}.")
            except OSError as e:
                print(f"Error downloading {title}: {e}")
        else:
            print(f"No text/plain format available for {title}.")

def main():
    # Parameters for fetching philosophy books in English before 1950
    params = {
        'topic': 'philosophy',
        'languages': 'en',
        'author_year_end': 1950,
        'mime_type': 'text/plain',
    }
    
    base_url = "https://gutendex.com/books/"
    next_url = base_url
    downloaded_books = 0
    total_books_to_download = 200  # Set this to the desired number of books to download

    while next_url and downloaded_books < total_books_to_download:
        result = fetch_books_from_gutendex(next_url, params)

        if result and result.get('results'):
            books = result['results']
            print(f"Found {len(books)} books.")
            download_books_from_gutendex(books)
            downloaded_books += len(books)

            # Follow pagination link
            next_url = result.get('next')
            if next_url:
                print(f"Fetching more books from: {next_url}")
        else:
            print("No more books found.")
            break

    print(f"Downloaded {downloaded_books} books.")

if __name__ == "__main__":
    main()