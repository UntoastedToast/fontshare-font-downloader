# Fontshare Font Downloader

## Overview

**Fontshare Font Downloader** is a script designed to automate the process of downloading fonts from the [Fontshare website](https://www.fontshare.com/). It uses the Playwright library to interact with the website, collect all available font links, and download them to your local machine. The script supports running in headless mode, making it efficient for automated workflows.

## Features

- **Automated Font Download**: Automatically downloads fonts from Fontshare.
- **Headless Browsing**: Supports headless browsing using Playwright for seamless automation.
- **Customizable Download Limits**: Allows specifying the maximum number of fonts to download.
- **Progress Display**: Utilizes TQDM to show a progress bar for font collection and download.

## Installation

### Step-by-Step Setup Guide

1. **Clone the Repository**:
  
  bash
  
  Code kopieren
  
  `git clone https://github.com/UntoastedToast/fontshare-font-downloader.git cd fontshare-font-downloader`
  
2. **Create a Virtual Environment**:
  
  Create a virtual environment to install all necessary packages in isolation.
  
  bash
  
  Code kopieren
  
  `python -m venv env`
  
3. **Activate the Virtual Environment**:
  
  Activate the virtual environment using the following command based on your operating system:
  
  #### Windows
  
  bash
  
  Code kopieren
  
  `.\env\Scripts\activate`
  
  #### macOS/Linux
  
  bash
  
  Code kopieren
  
  `source env/bin/activate`
  
4. **Install Dependencies**:
  
  Install all required packages from the `requirements.txt` file:
  
  bash
  
  Code kopieren
  
  `pip install -r requirements.txt`
  
5. **Install Playwright Browsers**:
  
  After activating the virtual environment and installing the dependencies, install the necessary browsers for Playwright:
  
  bash
  
  Code kopieren
  
  `playwright install`
  

## Usage

Run the script using Python:

bash

Code kopieren

`python fontshare_downloader.py`

By default, it will download all available fonts. You can specify the maximum number of fonts to download:

bash

Code kopieren

`python fontshare_downloader.py --max-fonts 50`

This command will limit the download to 50 fonts, but you can adjust this number as needed.

## Dependencies

The following dependencies are listed in the `requirements.txt` file:

- **pydantic**: Data validation and settings management using Python type annotations.
- **pandas**: Data manipulation and analysis library.
- **playwright**: Enables browser automation and web scraping capabilities.
- **tqdm**: Provides a progress bar for loops.

## Additional Notes

- **Ensure the Virtual Environment is Set Up Correctly**: If you encounter any issues with the virtual environment, ensure you have followed the above steps correctly.
  
- **Playwright Browser Installation**: Ensure that you run the `playwright install` command after activating the virtual environment to install the necessary browser binaries.