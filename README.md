# LGAMA-G

LGAMA-G is a desktop application designed to automate the process of scraping Google search results and generating lead data using Gemini AI. The application is built using Python, and it provides a user-friendly interface for entering search queries, scraping data, and saving the results in CSV and Excel formats.

## Features

- **Google Search Scraping**: Automatically scrape Google search results based on user-defined queries.
- **Lead Data Extraction**: Extract lead data such as name, email, social link, and profession from the scraped content.
- **Data Storage**: Save extracted lead data in CSV and Excel formats.
- **Retry Mechanism**: Automatically retry operations in case of failures to enhance reliability.
- **User-friendly Interface**: Simple and intuitive GUI built with customtkinter.

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/LGAMA-G.git
   cd LGAMA-AI
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Gemini API Key**
   - Open the application.
   - Navigate to the "Config" tab.
   - Enter your Gemini API key and save the settings.

## Usage

1. **Start the Application**
   ```bash
   python main.py
   ```

2. **Enter Query**
   - In the "Dom" tab, enter the search query you want to scrape Google for.

3. **Scrape Data**
   - Click the "Scrape" button to start the scraping process.
   - The application will scrape the Google search results and display progress in the output box.

4. **Stop Scraping**
   - Click the "Stop" button to halt the scraping process at any time.

5. **View Results**
   - The scraped data will be displayed in the output box.
   - The results will also be saved in CSV and Excel files in the application's directory.

## Components

- **main.py**: The main script that runs the application.
- **LeadDataProcessor**: A class for processing lead data, including saving to CSV and Excel formats.
- **EmailScraper**: A class for scraping Google search results and extracting lead data.
- **UI Components**: Built using customtkinter for a modern and intuitive user interface.

## Customization

- **Retry Mechanism**: Adjust the number of retry attempts in the `retry` decorator as needed.
- **Google Scraper**: Modify the `run_google_scraper` function to customize the scraping behavior (e.g., number of scrolls).
- **Generative AI Configuration**: Adjust the configuration of the Gemini AI model in the `LeadDataProcessor` class.

## Troubleshooting

- **Scraping Issues**: Ensure you have a stable internet connection and that Google is accessible.
- **API Key Errors**: Verify that your Gemini API key is correct and has the necessary permissions.
- **Dependencies**: Ensure all required dependencies are installed correctly. Use the provided `requirements.txt` file for installation.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [customtkinter](https://github.com/TomSchimansky/CustomTkinter) for the modern GUI elements.
- [plyer](https://github.com/kivy/plyer) for the notification functionality.
- [playwright](https://github.com/microsoft/playwright-python) for the web scraping capabilities.
- [pandas](https://pandas.pydata.org/) for data manipulation and storage.

## Contact

For any inquiries or support, please contact [kushwaha@codestam.com](mailto:kushwaha@codestam.com).

---

Thank you for using LGAMA-G!
