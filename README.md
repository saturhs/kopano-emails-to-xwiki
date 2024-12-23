## Project Overview

This project automates the process of extracting user data (names, emails) from the Kopano infrastructure and updates an XWiki page with the latest data in a table format. The project consists of two Python scripts:

- **kopano_extract_emails.py**: This script extracts user data from Kopano and generates an XWiki-compatible table file (`xwiki_table.txt`) in XWiki 2.1 format.
- **xwiki-upload-email-tables.py**: This script uploads the generated `xwiki_table.txt` file to a specific XWiki page via the XWiki REST API.

## Project Structure
```md
xwiki-script
│
├── scripts                             # Contains the project scripts
│   ├── kopano_extract_emails.py        # Main script to extract data from Kopano
│   └── xwiki-upload-email-tables.py    # Script to upload data to XWiki
│
├── data                                # Contains the generated data files
│   └── xwiki_table.txt                 # XWiki-compatible table file
│
├── logs                                # Log files generated by the scripts
│   └── errors.log                      # Error log file
│
└── README.md                           # Project documentation (this file)

etc/systemd/system
├── xwiki-script.service                # Systemd service that runs the kopano-extract-emails.py
└── xwiki-script.timer                  # Systemd timer that runs the service every 12h
```
## Setup Instructions

### Prerequisites
- Python 3.7.3 or higher
- Kopano administration tool (kopano-admin)
- XWiki account with API access

1. **Set up environment variables:**

   Make sure to set the following environment variables for XWiki authentication:
   
   - export XWIKI_USERNAME='your_xwiki_username'    
   - export XWIKI_PASSWORD='your_xwiki_password'

   You can automate this by adding them to a script like /.bashrc and sourcing it:

   source /.bashrc

   Or add them into a service file (e.g. xwiki-script.service)

2. **Automation**

   The script is automated using `xwiki-script.service` and `xwiki-script.timer`.
