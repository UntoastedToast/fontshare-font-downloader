import os
import zipfile
import shutil
from playwright.sync_api import sync_playwright, TimeoutError
from tqdm import tqdm  # Fortschrittsanzeige

def download_fonts(max_fonts=None):
    """
    Lädt Schriftarten von Fontshare herunter und speichert sie im Ordner "fonts".
    
    :param max_fonts: Maximale Anzahl der Schriftarten, die heruntergeladen werden sollen. 
                      Wenn None, werden alle verfügbaren Schriftarten heruntergeladen.
    """
    # Erstelle einen Ordner für die heruntergeladenen Schriften
    os.makedirs("fonts", exist_ok=True)

    # Starte Playwright
    with sync_playwright() as p:
        # Setze headless=True, um den Browser im Headless-Modus auszuführen
        browser = p.chromium.launch(headless=True)  # Kein sichtbarer Browser für den produktiven Einsatz
        page = browser.new_page()

        # Gehe zur Fontshare-Startseite
        print("Navigating to Fontshare homepage...")
        page.goto("https://www.fontshare.com/")
        page.wait_for_timeout(3000)  # Warte auf das anfängliche Laden der Seite

        # Funktion zum kontinuierlichen Scrollen
        def scroll_to_load_all_fonts():
            print("Scrolling to load all fonts...")
            seen_fonts = set()
            total_fonts = 0
            pbar = tqdm(desc="Collecting font links", total=max_fonts or 100, unit="font", dynamic_ncols=True)

            while True:
                # Sammle aktuelle Links der Kacheln
                font_links = page.locator('a[href^="/fonts/"]').all()
                font_urls = [link.get_attribute("href") for link in font_links if link.get_attribute("href")]

                # Füge neue Links hinzu
                new_fonts = set(font_urls) - seen_fonts
                seen_fonts.update(new_fonts)

                # Begrenze auf neue Links maximal 6, die pro Scrollvorgang geladen werden
                total_fonts += len(new_fonts)
                pbar.update(len(new_fonts))

                # Scrolle zur letzten Kachel, um den Ladevorgang zu erzwingen
                if font_links:
                    last_font = font_links[-1]
                    last_font.scroll_into_view_if_needed()
                    page.wait_for_timeout(500)  # Warte, damit Inhalte geladen werden können

                # Beende den Scrollvorgang, wenn die maximale Anzahl erreicht wurde
                if max_fonts is not None and total_fonts >= max_fonts:
                    print(f"Reached the maximum limit of {max_fonts} fonts.")
                    break

                # Wenn keine neuen Schriften mehr geladen werden, breche die Schleife
                if not new_fonts:
                    print("No new fonts loaded. Breaking scroll loop.")
                    break

            pbar.close()
            print("Finished scrolling. All fonts are loaded.")
            return list(seen_fonts)

        # Lade alle Schriftarten durch Scrollen und sammle die Links
        font_urls = scroll_to_load_all_fonts()

        # Entferne doppelte Links und begrenze auf max_fonts
        if max_fonts is not None:
            font_urls = list(set(font_urls))[:max_fonts]
        else:
            font_urls = list(set(font_urls))
        
        print(f"Found {len(font_urls)} font families.")

        # Fortschrittsanzeige für das Herunterladen
        pbar_download = tqdm(font_urls, desc="Downloading fonts", unit="font", dynamic_ncols=True)

        # Besuche jede Schriftfamilien-Seite und lade die Schriftfamilie herunter
        for font_url in pbar_download:
            font_page_url = f"https://www.fontshare.com{font_url}"
            page.goto(font_page_url)
            page.wait_for_timeout(2000)  # Warte auf das Laden der Seite

            # Klicke auf den "Download Family"-Button
            download_button = page.locator("text='Download Family'")
            if download_button.count() > 0:
                download_button.first.click()

                # Warte auf das Erscheinen des Download-Links und lade die Schrift herunter
                try:
                    with page.expect_download() as download_info:
                        page.locator('a[href*="download"]').click()
                    download = download_info.value
                    font_name = font_url.split('/')[-1]  # Verwende den Schriftartnamen für den Dateinamen
                    download.save_as(f"fonts/{font_name}.zip")
                except TimeoutError:
                    print(f"Failed to download font: {font_name}. Skipping.")

        pbar_download.close()

        # Browser schließen
        browser.close()
        print("Browser closed.")

    # Entpacke die heruntergeladenen ZIP-Dateien und extrahiere die TTF-Schriften
    extract_and_save_ttf_fonts()

def extract_and_save_ttf_fonts():
    fonts_dir = "fonts"
    all_fonts_dir = os.path.join(fonts_dir, "all_fonts")
    os.makedirs(all_fonts_dir, exist_ok=True)

    font_zip_files = [f for f in os.listdir(fonts_dir) if f.endswith(".zip")]
    
    # Fortschrittsanzeige für das Extrahieren und Kopieren
    pbar_extract = tqdm(font_zip_files, desc="Extracting fonts", unit="font", dynamic_ncols=True)

    for font_zip in pbar_extract:
        font_name = font_zip.split(".zip")[0]
        font_zip_path = os.path.join(fonts_dir, font_zip)
        font_extracted_path = os.path.join(fonts_dir, font_name)

        # Entpacke die ZIP-Datei
        with zipfile.ZipFile(font_zip_path, "r") as zip_ref:
            zip_ref.extractall(font_extracted_path)

        # Verschiebe die TTF-Dateien ins Verzeichnis der obersten Ebene
        move_ttf_files_to_top_level(font_extracted_path)

        # Kopiere alle TTF-Dateien in den zentralen Ordner
        copy_ttf_files_to_all_fonts(font_extracted_path, all_fonts_dir)

        # Lösche die ursprüngliche ZIP-Datei
        os.remove(font_zip_path)

    pbar_extract.close()

def move_ttf_files_to_top_level(directory):
    ttf_files = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".ttf"):
                ttf_files.append(os.path.join(root, file))

    # Verschiebe die TTF-Dateien ins Verzeichnis der obersten Ebene
    for ttf_file in ttf_files:
        file_name = os.path.basename(ttf_file)
        top_level_path = os.path.join(directory, file_name)

        # Verschiebe die Datei nur, wenn sie noch nicht auf der obersten Ebene existiert
        if not os.path.exists(top_level_path):
            shutil.move(ttf_file, top_level_path)

    # Lösche alle anderen Dateien und Ordner
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
    Kopiert alle TTF-Dateien aus dem Quellverzeichnis in das Zielverzeichnis.
    
    :param source_dir: Das Quellverzeichnis, aus dem die TTF-Dateien kopiert werden.
    :param target_dir: Das Zielverzeichnis, in das die TTF-Dateien kopiert werden.
    """
    for root, _, files in os.walk(source_dir):
        for file in files:
            if file.endswith(".ttf"):
                source_path = os.path.join(root, file)
                destination_path = os.path.join(target_dir, file)

                # Kopiere die Datei nur, wenn sie nicht bereits im Zielverzeichnis existiert
                if not os.path.exists(destination_path):
                    shutil.copy2(source_path, destination_path)

if __name__ == "__main__":
    # Benutzereingabe für die Anzahl der zu ladenden Schriftarten
    user_input = input("Geben Sie die maximale Anzahl der herunterzuladenden Schriftarten ein (oder '0' für alle): ")

    # Prüfen, ob die Eingabe eine Zahl ist
    try:
        max_fonts = int(user_input)
        if max_fonts < 0:
            raise ValueError("Die Anzahl der Schriftarten muss 0 oder größer sein.")

        # Wenn die Eingabe 0 ist, setze max_fonts auf None für alle Schriftarten
        if max_fonts == 0:
            max_fonts = None  # Keine Begrenzung

    except ValueError as e:
        print(f"Ungültige Eingabe: {e}. Standardwert von 6 wird verwendet.")
        max_fonts = 6  # Fallback-Wert

    download_fonts(max_fonts)
