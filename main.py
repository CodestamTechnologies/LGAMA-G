import os
import time
import threading
from tkinter import Tk, filedialog
from plyer import notification
import customtkinter as ctk
import pandas as pd
from playwright.sync_api import sync_playwright
from google.generativeai import configure, GenerativeModel
import webbrowser

def retry(func):
    def wrapper(*args, **kwargs):
        retry_count = 0
        while retry_count < 3:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                custom_print(f"Error: {e}. Retrying...")
                time.sleep(2)
                retry_count += 1
        custom_print(f"Failed to execute {func.__name__} after multiple retries.")
        return None
    return wrapper

class LeadDataProcessor:
    def __init__(self, api_key):
        self.api_key = api_key
        self.model = None
        self.configure_generative_ai()

    def configure_generative_ai(self):
        configure(api_key=self.api_key)
        generation_config = {"candidate_count": 1, "temperature": 1.0, "top_p": 0.7}
        safety_settings = [
            {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
        self.model = GenerativeModel(
            "gemini-pro", generation_config=generation_config, safety_settings=safety_settings
        )

    @retry
    def generate_content(self, prompt):
        response = self.model.generate_content(prompt)
        return response.text

    def dataframe(self, lead_data):
        return pd.DataFrame([lead.split(',') for lead in lead_data.split('\n')])

    def save_to_excel(self, lead_data, filename):
        data = self.dataframe(lead_data)
        file_path = f"{filename}.xlsx"
        if os.path.exists(file_path):
            existing_data = pd.read_excel(file_path)
            updated_data = pd.concat([existing_data, data], ignore_index=True)
            updated_data.to_excel(file_path, index=False)
        else:
            data.to_excel(file_path, index=False)
        return file_path

    def save_to_csv(self, lead_data, filename):
        data = self.dataframe(lead_data)
        file_path = f"{filename}.csv"
        if os.path.exists(file_path):
            existing_data = pd.read_csv(file_path)
            new_rows = data[~data.isin(existing_data)].dropna()
            if not new_rows.empty:
                updated_data = pd.concat([existing_data, new_rows], ignore_index=True)
                updated_data.to_csv(file_path, index=False)
        else:
            data.to_csv(file_path, index=False)
        return file_path
    
def process_lead_data(api_key, file_location, prompt):
    with open(file_location, 'r', encoding='utf-8') as file:
        data = file.read()

    processor = LeadDataProcessor(api_key)
    prompt_with_data = f"{prompt} {data}"
    lead_data = processor.generate_content(prompt=prompt_with_data)
    lead_data = lead_data.replace("`", "")
    lead_data = lead_data.replace("name,emailid,social link, profession", "")
    csv_file = processor.save_to_csv(lead_data, f"lead_data_{prompt}")
    excel_file = processor.save_to_excel(lead_data, f"lead_data_{prompt}")
    return csv_file, excel_file

def run_google_scraper(query, max_scrolls=10):
    filename = None
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        custom_print("Launching Chromium browser...")
        
        page.goto("https://www.google.com/", timeout=60000)
        page.get_by_label("Search", exact=True).click()
        
        custom_print("Navigating to Google search page...")
        
        page.get_by_label("Search", exact=True).fill(query)
        page.keyboard.press("Enter")
        
        custom_print("Performing Google search...")
        
        page.wait_for_load_state("networkidle")
        
        try:
            prev_scroll_height = 0
            scroll_count = 0
            
            while scroll_count < max_scrolls:
                scroll_height = page.evaluate("document.documentElement.scrollHeight")
                page.evaluate("window.scrollTo(0, document.documentElement.scrollHeight)")
                
                custom_print(f"Scrolling... {scroll_count}/{max_scrolls}")
                
                page.wait_for_timeout(1000)
                
                if scroll_height > prev_scroll_height:
                    prev_scroll_height = scroll_height
                else:
                    break
                
                scroll_count += 1
        
        except Exception as e:
            if "Target page, context or browser has been closed" in str(e):
                custom_print("Target page, context, or browser has been closed. Exiting loop.")
            else:
                custom_print(f"Error occurred: {str(e)}")
        
        finally:
            page_text = page.inner_text("body")
            filename = f"scraped_content_{query.replace(' ', '_')}.txt"
            with open(filename, "w", encoding="utf-8") as file:
                file.write(page_text)
            
            custom_print("Scraping complete. Content saved to file.")
            
            page.wait_for_timeout(3000)
    
    return filename

API_KEY = ""
stop_all_operations = False

class LGAMA(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.stop_flag = threading.Event()
        self.setup_ui()

    def setup_ui(self):
        self.geometry("500x500")
        self.title("LGAMA-AI")
        ctk.set_appearance_mode("system")
        self.configure(fg_color=('#d1dadb', '#262833'))
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.protocol("WM_DELETE_WINDOW", self.on_window_close)

        self.tab = ctk.CTkTabview(master=self, fg_color=('#84b898', '#4b4c56'), width=400, height=600)
        self.tab.pack(padx=20, pady=20)

        self.tab.add("Dom")
        self.tab.add("Config")

        dom_tab = self.tab.tab("Dom")
        config_tab = self.tab.tab("Config")

        self.setup_dom_tab(dom_tab)
        self.setup_config_tab(config_tab)

    def check_input_fields(self):
        keyword = self.keyword_box.get()
        if not keyword:
            notification.notify(
                title="Error",
                message="Please enter a query.",
                app_icon=None,
                timeout=5
            )
            return False

        api_key = self.gemini_api.get()
        if not api_key:
            notification.notify(
                title="Error",
                message="Please enter the Gemini API key.",
                app_icon=None,
                timeout=5
            )
            return False

        return True

    def setup_dom_tab(self, tab):
        self.help_button = self.query_btn(tab, "?", ("#e5ede8", "#e5ede8"), ("#84b898", "#84b898"),
                                              ("#1d1f2b"), 0.95, 0.05, "center", command=self.open_help_link)
        self.keyword_box = self.create_entry(tab, "Enter Query", 300, "transparent", ("#3a3d46", "#a6a7ac"),
                                             ("#3a3d46", "#a6a7ac"), 0.5, 0.15, "center")
        self.scrape_btn = self.create_button(tab, "Scrape", ("#e5ede8", "#e5ede8"), ("#84b898", "#84b898"),
                                              ("#1d1f2b"), 0.305, 0.25, "center", command=self.start_scraping)
        
        self.stop_scrape_btn = self.create_button(tab, "Stop", ("#e5ede8", "#e5ede8"), ("#84b898", "#84b898"),
                                                   ("#1d1f2b"), 0.685, 0.25, "center", command=self.stop_scraping)
        self.scraper_output = self.create_textbox(tab, 350, 200, ("#d1dadb", "#262833"), 0.5, 0.72, "center")

    def setup_config_tab(self, tab):
        self.gemini_api = self.create_entry(tab, "Gemini API Key", 300, "transparent", ("#3a3d46", "#a6a7ac"),
                                           ("#3a3d46", "#a6a7ac"), 0.5, 0.16, "center")
        self.save_btn = self.create_button(tab, "Save", ("#e5ede8", "#e5ede8"), ("#84b898", "#84b898"),
                                            ("#1d1f2b"), 0.5, 0.53, "center", command=self.save_config_settings)
        
    def load_file_dialog(self):
        file_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select file",
                                                filetypes=(("Text files", "*.txt"), ("CSV files", "*.csv"),
                                                           ("Excel files", "*.xlsx;*.xls")))
        if file_path:
            _, extension = os.path.splitext(file_path)
            try:
                if extension == ".txt":
                    with open(file_path, "r") as file:
                        content = file.read()
                elif extension in [".csv", ".xlsx", ".xls"]:
                    df = pd.read_excel(file_path) if extension == ".xlsx" else pd.read_csv(file_path)
                    content = df.to_string(index=False)
                else:
                    content = "Unsupported file format."
            except Exception as e:
                content = f"Error: {str(e)}"
            self.scraped_data_textbox.delete(1.0, "end")
            self.scraped_data_textbox.insert("end", content)

    def open_help_link(self):
        webbrowser.open("https://store.codestam.com/LGAMA-G")

    def save_config_settings(self):
        global API_KEY
        API_KEY = self.gemini_api.get()
        notification.notify(
            title="Config Settings Saved",
            message="Your Config settings have been successfully saved.",
            app_icon=None,
            timeout=5
        )

    def create_entry(self, master, placeholder_text, width, fg_color, text_color, placeholder_text_color, relx, rely,
                     anchor):
        entry = ctk.CTkEntry(master=master, placeholder_text=placeholder_text, width=width,
                             fg_color=fg_color, text_color=text_color,
                             placeholder_text_color=placeholder_text_color)
        entry.place(relx=relx, rely=rely, anchor=anchor)
        return entry

    def create_textbox(self, master, width, height, fg_color, relx, rely, anchor):
        textbox = ctk.CTkTextbox(master=master, width=width, height=height, fg_color=fg_color)
        textbox.place(relx=relx, rely=rely, anchor=anchor)
        return textbox

    def create_button(self, master, text, fg_color, hover_color, text_color, relx, rely, anchor, command=None):
        button = ctk.CTkButton(master=master, text=text, fg_color=fg_color, hover_color=hover_color,
                               text_color=text_color, command=command)
        button.place(relx=relx, rely=rely, anchor=anchor)
        return button
    
    def query_btn(self, master, text, fg_color, hover_color, text_color, relx, rely, anchor, command=None):
        button = ctk.CTkButton(master=master, text=text, fg_color=fg_color, hover_color=hover_color,
                               text_color=text_color, command=command, width=20, height=20)
        button.place(relx=relx, rely=rely, anchor=anchor)
        return button

    def on_window_close(self):
        self.stop_flag.set()
        self.destroy()

    def update_progress(self, message):
        self.scraper_output.insert("end", message + "\n")
        self.scraper_output.see("end")

    def start_scraping(self):
        if not self.check_input_fields():
            return

        global stop_all_operations
        stop_all_operations = False

        try:
            self.scrape_btn.configure(state="disabled")
            self.stop_flag.clear()
            self.update_progress("Started Scraping")
            threading.Thread(target=lambda: main(self.keyword_box.get(), API_KEY=API_KEY)).start()

        except Exception as e:
            self.display_error(f"Error while starting scraping: {e}")

    def stop_scraping(self):
        global stop_all_operations
        stop_all_operations = True
        self.scraper_output.insert("end", "Stopping all operations...\n")
        self.stop_scrape_btn.configure(state="disabled")

def custom_print(message):
    app.update_progress(message)

class EmailScraper:
    def __init__(self, query, max_scrolls=5):
        self.query = query
        self.max_scrolls = max_scrolls
    
    def scrape_and_extract_emails(self, API_KEY):
        custom_print("Scraping...")  
        FILE_LOCATION = run_google_scraper(self.query, self.max_scrolls)
        
        custom_print("Extracting lead data...") 
        
        result = process_lead_data(API_KEY, FILE_LOCATION, self.query)
        if result is None:
            custom_print("Error: process_lead_data returned None")
            return
        csv_file, excel_file = result
        return csv_file, excel_file

def main(QUERY, API_KEY):
    query = QUERY
    max_scrolls = 5
    scraper = EmailScraper(query, max_scrolls)
    
    csv_file, excel_file = scraper.scrape_and_extract_emails(API_KEY)

    custom_print(f"CSV file is saved as {csv_file}")
    custom_print(f"Excel file is saved as {excel_file}")

    while not stop_all_operations:
        time.sleep(1)
        if stop_all_operations:
            custom_print("Scraping stopped by user.")
            break

if __name__ == "__main__":
    app = LGAMA()
    app.mainloop()
