# Fontshare Font Downloader

## Overview

Fontshare Font Downloader is a script designed to automate the process of downloading fonts from the [Fontshare website](https://www.fontshare.com/). It uses the Playwright library to interact with the website, collect all available font links, and download them to your local machine. The script can run in a headless browser mode, making it efficient for automated workflows.

## Features

- **Automated Font Download**: Automatically downloads fonts from Fontshare.
- **Headless Browsing**: Supports headless browsing using Playwright for seamless automation.
- **Customizable Download Limits**: Allows specifying the maximum number of fonts to download.
- **Progress Display**: Utilizes TQDM to show a progress bar for font collection and download.

## Installation

1. **Clone the repository**:
  
  ```bash
  git clone https://github.com/UntoastedToast/fontshare-font-downloader.git
  cd fontshare-font-downloader
  ```
  
2. **Activate the Virtual Environment**:
  
  The project comes with a pre-configured virtual environment. Activate it using the following commands based on your operating system:
  
  ### Windows
  
  ```bash
  .\env\Scripts\activate
  ```
  
  ### macOS/Linux
  
  ```bash
  source env/bin/activate
  ```
  
3. **Install Playwright Browsers**:
  
  After activating the environment, install the necessary browsers for Playwright if they aren't already installed:
  
  ```bash
  playwright install
  ```
  

## Usage

Run the script using Python:

```bash
python fontshare_downloader.py
```

By default, it will download all available fonts. You can specify the maximum number of fonts to download:

```bash
python fontshare_downloader.py --max-fonts 50
```

This command will limit the download to 50 fonts, but you can adjust this number as needed.

## Dependencies

The following dependencies are included in the virtual environment:

- **pydantic**: Data validation and settings management using Python type annotations.
- **pandas**: Data manipulation and analysis library.
- **playwright**: Enables browser automation and web scraping capabilities.
- **tqdm**: Provides a progress bar for loops.

## Additional Notes

- **Ensure the Virtual Environment is Complete**: If you encounter any issues with the virtual environment, you may need to recreate it using the following steps:
  
  ```bash
  python -m venv env
  source env/bin/activate  # For Windows: .\env\Scripts\activate
  pip install -r requirements.txt
  ```
  
- **Playwright Browser Installation**: Ensure that you run the `playwright install` command after activating the virtual environment to install the necessary browser binaries.
  

---

### Instructions for Recreating the Virtual Environment

If you want users to set up the environment from scratch instead of using the pre-configured one, you can add the following section to guide them:

### Setup from Scratch

1. **Create a Virtual Environment**:
  
  ```bash
  python -m venv env
  ```
  
2. **Activate the Virtual Environment**:
  
  ```bash
  source env/bin/activate  # For Windows: .\env\Scripts\activate
  ```
  
3. **Install Dependencies**:
  
  ```bash
  pip install -r requirements.txt
  ```
  
4. **Install Playwright Browsers**:
  
  ```bash
  playwright install
  ```