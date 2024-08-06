import os
import zipfile
import shutil
from playwright.sync_api import sync_playwright, TimeoutError
from tqdm import tqdm  # Progress bar

def download_fonts(max_fonts=None):
    """
    Downloads fonts from Fontshare and saves them in the "fonts" directory.
    
    :param max_fonts: Maximum number of fonts to download. 
                      If None, all available fonts will be downloaded.
    """
    # Create a directory for the downloaded fonts
    os.makedirs("fonts", exist_ok=True)

    # Start Playwright
    with sync_playwright() as p:
        # Set headless=True to run the browser in headless mode
        browser = p.chromium.launch(headless=True)  # No visible browser for production use
        page = browser.new_page()

        # Navigate to the Fontshare homepage
        print("Navigating to Fontshare homepage...")
        page.goto("https://www.fontshare.com/")
        page.wait_for_timeout(3000)  # Wait for the initial page load

        # Function for continuous scrolling
        def scroll_to_load_all_fonts():
            print("Scrolling to load all fonts...")
            seen_fonts = set()
            total_fonts = 0
            pbar = tqdm(desc="Collecting font links", total=max_fonts or 100, unit="font", dynamic_ncols=True)

            while True:
                # Collect current tile links
                font_links = page.locator('a[href^="/fonts/"]').all()
                font_urls = [link.get_attribute("href") for link in font_links if link.get_attribute("href")]

                # Add new links
                new_fonts = set(font_urls) - seen_fonts
                seen_fonts.update(new_fonts)

                # Limit to new links, max 6 per scroll
                total_fonts += len(new_fonts)
                pbar.update(len(new_fonts))

                # Scroll to the last tile to trigger loading
                if font_links:
                    last_font = font_links[-1]
                    last_font.scroll_into_view_if_needed()
                    page.wait_for_timeout(500)  # Wait for content to load

                # Break if the maximum number is reached
                if max_fonts is not None and total_fonts >= max_fonts:
                    print(f"Reached the maximum limit of {max_fonts} fonts.")
                    break

                # Break if no new fonts are loaded
                if not new_fonts:
                    print("No new fonts loaded. Breaking scroll loop.")
                    break

            pbar.close()
            print("Finished scrolling. All fonts are loaded.")
            return list(seen_fonts)

        # Load all fonts by scrolling and collect links
        font_urls = scroll_to_load_all_fonts()

        # Remove duplicate links and limit to max_fonts
        if max_fonts is not None:
            font_urls = list(set(font_urls))[:max_fonts]
        else:
            font_urls = list(set(font_urls))
        
        print(f"Found {len(font_urls)} font families.")

        # Progress bar for downloading
        pbar_download = tqdm(font_urls, desc="Downloading fonts", unit="font", dynamic_ncols=True)

        # Visit each font family page and download the font family
        for font_url in pbar_download:
            font_page_url = f"https://www.fontshare.com{font_url}"
            page.goto(font_page_url)
            page.wait_for_timeout(2000)  # Wait for the page to load

            # Click on the "Download Family" button
            download_button = page.locator("text='Download Family'")
            if download_button.count() > 0:
                download_button.first.click()

                # Wait for the download link to appear and download the font
                try:
                    with page.expect_download() as download_info:
                        page.locator('a[href*="download"]').click()
                    download = download_info.value
                    font_name = font_url.split('/')[-1]  # Use font name for the file name
                    download.save_as(f"fonts/{font_name}.zip")
                except TimeoutError:
                    print(f"Failed to download font: {font_name}. Skipping.")

        pbar_download.close()

        # Close the browser
        browser.close()
        print("Browser closed.")

    # Unpack the downloaded ZIP files and extract the TTF fonts
    extract_and_save_ttf_fonts()

def extract_and_save_ttf_fonts():
    fonts_dir = "fonts"
    all_fonts_dir = os.path.join(fonts_dir, "all_fonts")
    os.makedirs(all_fonts_dir, exist_ok=True)

    font_zip_files = [f for f in os.listdir(fonts_dir) if f.endswith(".zip")]
    
    # Progress bar for extracting and copying
    pbar_extract = tqdm(font_zip_files, desc="Extracting fonts", unit="font", dynamic_ncols=True)

    for font_zip in pbar_extract:
        font_name = font_zip.split(".zip")[0]
        font_zip_path = os.path.join(fonts_dir, font_zip)
        font_extracted_path = os.path.join(fonts_dir, font_name)

        # Unpack the ZIP file
        with zipfile.ZipFile(font_zip_path, "r") as zip_ref:
            zip_ref.extractall(font_extracted_path)

        # Move the TTF files to the top level directory
        move_ttf_files_to_top_level(font_extracted_path)

        # Copy all TTF files to the central folder
        copy_ttf_files_to_all_fonts(font_extracted_path, all_fonts_dir)

        # Delete the original ZIP file
        os.remove(font_zip_path)

    pbar_extract.close()

def move_ttf_files_to_top_level(directory):
    ttf_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".ttf"):
                ttf_files.append(os.path.join(root, file))

    # Move TTF files to the top level directory
    for ttf_file in ttf_files:
        file_name = os.path.basename(ttf_file)
        top_level_path = os.path.join(directory, file_name)

        # Move the file only if it does not already exist at the top level
        if not os.path.exists(top_level_path):
            shutil.move(ttf_file, top_level_path)

    # Delete all other files and directories
    for root, dirs, files in os.walk(directory, topdown=False):
        for name in files:
            file_path = os.path.join(root, name)
            if not file_path.endswith(".ttf"):
                os.remove(file_path)
        for name in dirs:
            dir_path = os.path.join(root, name)
            shutil.rmtree(dir_path)

def copy_ttf_files_to_all_fonts(source_dir, target_dir):
    """
    Copies all TTF files from the source directory to the target directory.
    
    :param source_dir: The source directory from which TTF files are copied.
    :param target_dir: The target directory to which TTF files are copied.
    """
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".ttf"):
                source_path = os.path.join(root, file)
                destination_path = os.path.join(target_dir, file)

                # Copy the file only if it does not already exist in the target directory
                if not os.path.exists(destination_path):
                    shutil.copy2(source_path, destination_path)

if __name__ == "__main__":
    # User input for the number of fonts to download
    user_input = input("Enter the maximum number of fonts to download (or '0' for all): ")

    # Check if the input is a number
    try:
        max_fonts = int(user_input)
        if max_fonts < 0:
            raise ValueError("The number of fonts must be 0 or greater.")

        # If input is 0, set max_fonts to None for all fonts
        if max_fonts == 0:
            max_fonts = None  # No limit

    except ValueError as e:
        print(f"Invalid input: {e}. Defaulting to 6.")
        max_fonts = 6  # Fallback value

    download_fonts(max_fonts)
