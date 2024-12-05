import tkinter as tk
from tkinter import ttk, messagebox
from main import SkinportAPI
from dotenv import load_dotenv
import os
import threading
from datetime import datetime
from typing import Optional

class SkinportGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Skinport Discount Checker")
        self.root.geometry("800x600")
        
        # Initialize API
        load_dotenv()
        client_id = os.getenv('SKINPORT_CLIENT_ID')
        client_secret = os.getenv('SKINPORT_CLIENT_SECRET')
        self.api = SkinportAPI(client_id, client_secret)
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Settings frame
        self.settings_frame = ttk.LabelFrame(self.main_frame, text="Settings", padding="5")
        self.settings_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Data source frame
        self.source_frame = ttk.Frame(self.settings_frame)
        self.source_frame.grid(row=0, column=0, columnspan=7, sticky=(tk.W, tk.E), pady=5)
        
        # Data source selection
        ttk.Label(self.source_frame, text="Data Source:").grid(row=0, column=0, padx=5)
        self.data_source = tk.StringVar(value="api")
        ttk.Radiobutton(self.source_frame, text="API", variable=self.data_source, 
                       value="api", command=self._toggle_source).grid(row=0, column=1, padx=5)
        ttk.Radiobutton(self.source_frame, text="Local", variable=self.data_source,
                       value="local", command=self._toggle_source).grid(row=0, column=2, padx=5)
        
        # Saved responses dropdown
        ttk.Label(self.source_frame, text="Saved Response:").grid(row=0, column=3, padx=5)
        self.saved_response_var = tk.StringVar()
        self.saved_response_dropdown = ttk.Combobox(self.source_frame, textvariable=self.saved_response_var, width=30)
        self.saved_response_dropdown.grid(row=0, column=4, padx=5)
        
        # Refresh button for saved responses
        self.refresh_button = ttk.Button(self.source_frame, text="↻", width=3, 
                                       command=self._update_saved_responses)
        self.refresh_button.grid(row=0, column=5, padx=5)
        
        # Initialize saved responses list
        self._update_saved_responses()
        self._toggle_source()
        
        # Filter settings frame
        self.filter_frame = ttk.Frame(self.settings_frame)
        self.filter_frame.grid(row=1, column=0, columnspan=7, sticky=(tk.W, tk.E), pady=5)
        
        # Minimum discount entry
        ttk.Label(self.filter_frame, text="Minimum Discount %:").grid(row=0, column=0, padx=5)
        self.min_discount = tk.StringVar(value="10")
        self.discount_entry = ttk.Entry(self.filter_frame, textvariable=self.min_discount, width=10)
        self.discount_entry.grid(row=0, column=1, padx=5)
        
        # Minimum price entry
        ttk.Label(self.filter_frame, text="Minimum Price:").grid(row=0, column=2, padx=5)
        self.min_price = tk.StringVar(value="1.00")
        self.price_entry = ttk.Entry(self.filter_frame, textvariable=self.min_price, width=10)
        self.price_entry.grid(row=0, column=3, padx=5)
        
        # Currency dropdown
        ttk.Label(self.filter_frame, text="Currency:").grid(row=0, column=4, padx=5)
        self.currency = tk.StringVar(value="EUR")
        currencies = ["EUR", "USD", "GBP"]
        self.currency_dropdown = ttk.Combobox(self.filter_frame, textvariable=self.currency, values=currencies, width=10)
        self.currency_dropdown.grid(row=0, column=5, padx=5)
        
        # Search button
        self.search_button = ttk.Button(self.filter_frame, text="Search Discounts", command=self.search_discounts)
        self.search_button.grid(row=0, column=6, padx=10)
        
        # Results treeview
        self.create_treeview()
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_bar = ttk.Label(self.main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.rowconfigure(1, weight=1)
        
    def create_treeview(self):
        # Create treeview with scrollbar
        self.tree_frame = ttk.Frame(self.main_frame)
        self.tree_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.tree = ttk.Treeview(self.tree_frame, columns=("name", "current", "suggested", "discount"), show="headings")
        
        # Define columns
        self.tree.heading("name", text="Item Name")
        self.tree.heading("current", text="Current Price")
        self.tree.heading("suggested", text="Suggested Price")
        self.tree.heading("discount", text="Discount %")
        
        # Configure column widths
        self.tree.column("name", width=300)
        self.tree.column("current", width=100)
        self.tree.column("suggested", width=100)
        self.tree.column("discount", width=100)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Grid treeview and scrollbar
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configure tree frame grid weights
        self.tree_frame.columnconfigure(0, weight=1)
        self.tree_frame.rowconfigure(0, weight=1)
        
    def format_currency(self, amount: float, currency: str) -> str:
        currency_symbols = {
            "EUR": "€",
            "USD": "$",
            "GBP": "£"
        }
        symbol = currency_symbols.get(currency, currency)
        return f"{symbol}{amount:.2f}"
        
    def search_discounts(self):
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        try:
            min_discount = float(self.min_discount.get())
            min_price = float(self.min_price.get())
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numbers for minimum discount and price")
            return
            
        # Get data source settings
        use_local = self.data_source.get() == "local"
        local_file = None
        if use_local and self.saved_response_var.get() != "No saved responses":
            # Extract filename from the selected option
            selected = self.saved_response_var.get()
            filename = selected.split('(')[1].rstrip(')')
            local_file = os.path.join(self.api.data_dir, filename)
            
        self.search_button.configure(state='disabled')
        self.status_var.set("Searching for discounted items...")
        
        # Run search in separate thread
        thread = threading.Thread(target=lambda: self._search_thread(use_local, local_file))
        thread.daemon = True
        thread.start()
        
    def _search_thread(self, use_local: bool, local_file: Optional[str]):
        try:
            items = self.api.get_discounted_items(
                min_discount_percent=float(self.min_discount.get()),
                currency=self.currency.get(),
                min_price=float(self.min_price.get()),
                use_local=use_local,
                local_file=local_file
            )
            
            # Update UI in main thread
            self.root.after(0, self._update_results, items)
            
        except Exception as e:
            self.root.after(0, self._show_error, str(e))
            
    def _update_results(self, items):
        for item in items:
            self.tree.insert("", tk.END, values=(
                item['market_hash_name'],
                self.format_currency(item['min_price'], self.currency.get()),
                self.format_currency(item['suggested_price'], self.currency.get()),
                f"{item['discount_percent']:.1f}%"
            ))
            
        self.search_button.configure(state='normal')
        self.status_var.set(f"Found {len(items)} items with discounts. Last updated: {datetime.now().strftime('%H:%M:%S')}")
        
    def _show_error(self, error_message):
        self.search_button.configure(state='normal')
        self.status_var.set("Error occurred during search")
        messagebox.showerror("Error", f"Failed to fetch items: {error_message}")
        
    def _update_saved_responses(self):
        """Update the saved responses dropdown with available files."""
        saved = self.api.get_saved_responses()
        if saved:
            # Format the timestamps for display
            options = [f"{datetime.strptime(ts, '%Y%m%d_%H%M%S').strftime('%Y-%m-%d %H:%M:%S')} ({os.path.basename(f)})"
                      for f, ts in saved]
            self.saved_response_dropdown['values'] = options
            if not self.saved_response_var.get():
                self.saved_response_var.set(options[0])  # Select most recent by default
        else:
            self.saved_response_dropdown['values'] = ["No saved responses"]
            self.saved_response_var.set("No saved responses")
            
    def _toggle_source(self):
        """Handle toggling between API and local source."""
        is_local = self.data_source.get() == "local"
        self.saved_response_dropdown.configure(state='readonly' if is_local else 'disabled')
        self.refresh_button.configure(state='normal' if is_local else 'disabled')
        
def main():
    root = tk.Tk()
    app = SkinportGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
