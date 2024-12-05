# SkinPort Discount Checker

## Overview
The SkinPort Discount Checker is a tool designed to track and analyze discounts for items on the Skinport marketplace, specifically for CS:GO items. It provides both a terminal and GUI interface for users to interact with the data.

## Features
- **API Interaction**: Connects with the Skinport API to fetch real-time data.
- **Discount Checking**: Analyzes and displays discounts for CS:GO items.
- **Multiple Interfaces**: Offers both terminal and GUI options for user interaction.
- **Data Management**: Supports both live data fetching and local data storage.
- **Filtering Options**: Allows filtering by minimum discount percentage and item price.

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/SkinPort-Discount-Check.git
   ```
2. Navigate to the project directory:
   ```bash
   cd SkinPort-Discount-Check
   ```
3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Setup
1. Create a `.env` file in the root directory and add your Skinport credentials:
   ```env
   SKINPORT_CLIENT_ID=your_client_id
   SKINPORT_CLIENT_SECRET=your_client_secret
   ```

## Usage
### Terminal Interface
Run the following command to start the terminal interface:
```bash
python main.py
```

### GUI Interface
Run the following command to start the GUI interface:
```bash
python gui.py
```

## Contributing
Contributions are welcome! Please create a pull request or submit an issue for any improvements or bug fixes.

## License
This project is licensed under the MIT License.

## Acknowledgments
- [Skinport API Documentation](https://docs.skinport.com/)

---

Feel free to customize this README further to suit your project's needs.
