#########################################################################################################################
#  Python Version: 3.7.3                                                                                                #
#                                                                                                                       #
#  Description:                                                                                                         #
#  This script uploads the content of 'xwiki_table.txt' to a XWiki page using the XWiki REST API. It takes login        #
#  credentials from environment variables, retrieves the returns page content to check the connection,                  #
#  and updates the page with new email list data from the 'xwiki_table.txt' file.                                       #
#                                                                                                                       #
#  Dependencies:                                                                                                        #
#  - Python 3.7.3                                                                                                       #
#  - requests                                                                                                           #
#  - os                                                                                                                 #
#  - logging                                                                                                            #
#                                                                                                                       #
#                                                                                       Author: Jakub Krzyżanowski      #
#                                                                                       Date: 17.09.2024                #
#########################################################################################################################
import requests
import os
import logging

logging.basicConfig(filename='/root/xwiki-script/logs/errors.log',    # configure logging to log errors to errors.log
                    level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

username = os.getenv('XWIKI_USERNAME')
password = os.getenv('XWIKI_PASSWORD')

url = 'https://intranet.ed-chemnitz.de/xwiki/rest/wikis/xwiki/spaces/Main/spaces/Contact%20information/pages/WebHome'   # an URL of API of E-mail-listen page

with open('/root/xwiki-script/data/xwiki_table.txt', 'r') as file:    # saves data from xwiki_table to a variable new_content
    new_content = file.read()

headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
}

data = {
    'content': new_content  # sets the content of site to new content that includes tables from xwiki_table.txt
}

response = requests.get(url, auth=(username, password)) # checks connection through API

if response.status_code == 200 or response.status_code == 202:  # if connection is correctly established, updates content on the site
    requests.put(url, auth=(username, password), headers=headers, data=data)
    print("The email list has been updated.")   # prints an information that page content got updated (debugging purpose)
else:
    logging.error(f"XWiki upload error: {response.status_code}")  # logs an error of communication thorugh API in an error log file ./errors.log
