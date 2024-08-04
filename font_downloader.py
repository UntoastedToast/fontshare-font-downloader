import os
from playwright.sync_api import sync_playwright, TimeoutError

def download_fonts():
    # Erstelle einen Ordner für die heruntergeladenen Schriften
    os.makedirs("fonts", exist_ok=True)

    # Starte Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=50)  # Sichtbarer Browser für Debugging
        page = browser.new_page()

        # Gehe zur Fontshare-Startseite
        print("Navigating to Fontshare homepage...")
        page.goto("https://www.fontshare.com/")
        page.wait_for_timeout(3000)  # Warte auf das anfängliche Laden der Seite

        # Funktion zum kontinuierlichen Scrollen
        def scroll_to_load_all_fonts():
            print("Scrolling to load all fonts...")
            seen_fonts = set()

            while True:
                # Sammle aktuelle Links der Kacheln
                font_links = page.locator('a[href^="/fonts/"]').all()
                font_urls = [link.get_attribute("href") for link in font_links if link.get_attribute("href")]

                # Füge neue Links hinzu
                new_fonts = set(font_urls) - seen_fonts
                if not new_fonts:
                    print("No new fonts loaded. Breaking scroll loop.")
                    break
                
                seen_fonts.update(font_urls)

                # Scrolle zur letzten Kachel, um den Ladevorgang zu erzwingen
                if font_links:
                    last_font = font_links[-1]
                    last_font.scroll_into_view_if_needed()
                    page.wait_for_timeout(1000)  # Warte, damit Inhalte geladen werden können

                print(f"Collected {len(seen_fonts)} font links so far.")

            print("Finished scrolling. All fonts are loaded.")
            return list(seen_fonts)

        # Lade alle Schriftarten durch Scrollen und sammle die Links
        font_urls = scroll_to_load_all_fonts()

        # Entferne doppelte Links
        font_urls = list(set(font_urls))
        print(f"Found {len(font_urls)} font families.")

        # Besuche jede Schriftfamilien-Seite und lade die Schriftfamilie herunter
        for font_url in font_urls:
            font_page_url = f"https://www.fontshare.com{font_url}"
            print(f"Visiting font page: {font_page_url}")
            page.goto(font_page_url)
            page.wait_for_timeout(2000)  # Warte auf das Laden der Seite

            # Klicke auf den "Download Family"-Button
            download_button = page.locator("text='Download Family'")
            if download_button.count() > 0:
                print("Download button found. Attempting to download...")
                download_button.first.click()

                # Warte auf das Erscheinen des Download-Links und lade die Schrift herunter
                try:
                    with page.expect_download() as download_info:
                        page.locator('a[href*="download"]').click()
                    download = download_info.value
                    font_name = font_url.split('/')[-1]  # Verwende den Schriftartnamen für den Dateinamen
                    download.save_as(f"fonts/{font_name}.zip")
                    print(f"Font {font_name} downloaded successfully.")
                except TimeoutError:
                    print(f"Failed to download font: {font_name}. Skipping.")

            else:
                print("Download button not found.")

        # Browser schließen
        browser.close()
        print("Browser closed.")

if __name__ == "__main__":
    download_fonts()