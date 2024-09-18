#########################################################################################################################
#  Python Version: 3.7.3                                                                                                #
#                                                                                                                       #
#  Description:                                                                                                         #
#  This script takes data from Kopano using the 'kopano-admin' command to extract group lists and their members         #
#  (names and emails). Then saves this data in XWiki 2.1 format to the 'xwiki_table.txt' file. The script organizes     #
#  the data into alphabetically sorted tables and finally runs an additional script, 'xwiki-upload-email-tables.py',    #
#  which uploads the generated tables to an XWiki page.                                                                 #
#                                                                                                                       #
#  Functions:                                                                                                           #
#  - extract_group_list(): Returns the list of available groups from the Kopano infrastructure.                         #
#  - extract_personal_data(): Returns names and emails for each group member.                                           #
#  - extract_all_data(): Aggregates data from all groups and their members.                                             #
#  - save_to_xwiki(): Creates and writes the 'xwiki_table.txt' file in XWiki 2.1 format with tables of members.         #
#  - Error logging is written to the 'errors.log' file.                                                                 #
#                                                                                                                       #
#  Dependencies:                                                                                                        #
#  - Python 3.7.3                                                                                                       #
#  - subprocess                                                                                                         #
#  - re (regular expressions)                                                                                           #
#  - logging                                                                                                            #
#                                                                                                                       #
#                                                                                       Author: Jakub Krzyżanowski      #
#                                                                                       Date: 17.09.2024                #
#########################################################################################################################
import re
import subprocess
import logging

error_occurred = False  # A flag to control presence of errors
logging.basicConfig(filename='/root/xwiki-script/logs/errors.log',    # Logging configuration that saves erros of script methods in ./errors.log
                    level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s') # defines a format of logged erors

###                        EXTRACTING DATA from KOPANO                       ###
def extract_group_list():   # core method that takes list of available groups and convert it to a list "groups"
    global error_occurred
    try:
        groups = []
        output = subprocess.run(['/usr/sbin/kopano-admin', '-L'], text=True, check=True, capture_output=True) # saves output of kopano-admin -L
        lines = output.stdout.splitlines()  # splits the output into lines that can be iterated and saved as items of a "groups" list
        for line in lines[4:-1]:
            groups.append(line.strip())
        return sorted(groups)   # returns alphabetically sorted list that will be forwarded further to next methods
    except subprocess.CalledProcessError as e:  # catches kopano-admin -L execution errors
        logging.error(f"An error with processing a kopano-admin -L command in extract_group_list method: {e}")  # logs an error in error.log file
        error_occurred = True   # turns on the error flag
        return []   # returns empty list in case of an error presence
    except Exception as e:  # catches other errors, but mainly turns on the error flag
        logging.error(f"An unknown error in extract_group_list method: {e}")
        error_occurred = True
        return []

def extract_personal_data(group):   # core method that extract emails and fullnames from every available group in Kopano
    global error_occurred
    try:
        personal_data = []
        output = subprocess.run(['/usr/sbin/kopano-admin', '--type', 'group', '--details', group], text=True, check=True, capture_output=True)  # saves output of kopano-admin --typ group --details that returns detailed info (emails, fullnames) of given group
        lines = output.stdout.splitlines() # splits the output info into lines that can be iterated and saved as items of "personal_data" list
        email_pattern = '^\s*([a-z0-9]+(?:-[a-z0-9]+)?\.[a-z0-9]+(?:-[a-z0-9]+)?)'  # regex pattern that looks for emails in the output of kopano-admin --type group --details command
        fullname_pattern = r'\s+([A-Za-zÀ-ÖØ-öø-ÿ\s-]+)\s*$'    # regex pattern that looks for fullnames in the output of kopano-admin --type group --details command
        for line in lines[11:-1]:
            line = line.strip()
            email_match = re.search(email_pattern, line)    # saves every email match to a variable email_match
            fullname_match = re.search(fullname_pattern, line)  # saves every fullname match to a variable fullname_match
            if email_match and fullname_match:  # if statement that checks if matches exists
                email = email_match.group().strip() + '@ed-chemnitz.de' # saves data that matched to email_pattern to a variable email adding "@ed-chemnitz.de" (emails arent provided with this ending in kopano-admin output)
                fullname = fullname_match.group().strip()   # saves data that matched to fullname_pattern to a variable "fullname"
                personal_data.append([fullname, email]) # appends each personal data (email and fullname) to a personal_data list
        return sorted(personal_data)    # sorts alphabetically the list
    except subprocess.CalledProcessError as e:  # catches kopano-admin --type group --details execution errors
        logging.error(f"An error with processing the kopano-admin command on a {group} in extract_personal_data method: {e}")   # logs an error in error.log file
        error_occurred = True # turns on the error flag
        return []   # returns empty list in case of an error presence
    except Exception as e:  # catches other errors, but mainly turns on the error flag
        logging.error(f"An unknown error with processing the details of {group} in extract_personal_data method: {e}")
        error_occurred = True
        return []

def extract_all_data(): # method that returns "all_data" list, each item contains a group name and every memeber of this group
    global error_ocurred
    try:
        all_data = []
        groups = extract_group_list() # saves the output group names list into a variable "group"
        for group in groups:    # for loop that iterates through every element in a "group" list
            people = extract_personal_data(group)   # saves the output personal info list into a variable "group"
            if people:  # if there is a personal info in a group, appends final all_data list
                all_data.append([group, people])
        return all_data
    except Exception as e:  # catches errors, but mainly turns on the error flag
        logging.error(f"An error in extract_all_data method: {e}")  # logs an error in error.log file
        error_ocurred = True    # turns on the error flag
        return []

###                     CONVERTING DATA to xwiki_table.txt in XWiki 2.1 syntax                         ###
def save_to_xwiki(all_data, filename='/root/xwiki-script/data/xwiki_table.txt'):  # method that updates/creates a xwiki_table.txt file that's exported to XWiki server
    global error_occurred
    if not error_occurred:  # if statement to avoid saving corrupted data into xwiki_table.txt. If there is at least one error, xwiki_table.txt would not be saved
        try:
            with open(filename, 'w') as file:   # opens xwiki_table.txt in writing mode
                for data in all_data:   # iterates through every group info, creating tables in xwiki_table.txt file
                    group_name = data[0]
                    people_data = data[1]
                    file.write(f"==== {group_name} ====\n\n")   # creates a table title
                    file.write("(% class=\"wikitable\" style=\"table-layout: fixed;\" %)\n")    # changes cosmetics of tables
                    file.write("|=(% style=\"background-color: #b0b0b0; color: white;\" %)Name |=(% style=\"background-color: #b0b0b0; color: white;\" %)Email |=(% style=\"background-color: #b0b0b0; color: white;\" %)Name |=(% style=\"background-color: #b0b0b0; color: white;\" %)Email\n")   # creates a header of table
                    # This part of code splits the list of people into two columns
                    middle_index = (len(people_data) + 1) // 2  # computes the middle of a list
                    left_column = people_data[:middle_index]    # each person up to the middle of list saved to a left column
                    right_column = people_data[middle_index:]   # each person from the middle of list saved to right column
                    max_length = max(len(left_column), len(right_column))   # takes max number of people that can appear a column
                    flag = True # flag that helps to stylize each row
                    # For loop that simultaneously iterates through every element in both columns
                    for i in range(max_length):
                        if i < len(left_column):
                            fullname1, email1 = left_column[i]  # splits personal info from each left_column item into fullname and email
                        else:
                            fullname1, email1 = "", ""
                        if i < len(right_column):
                            fullname2, email2 = right_column[i] # splits personal info from each right_column item into fullname and email
                        else:
                            fullname2, email2 = "", ""
                        if flag:
                            file.write(f"|(% style=\"background-color: #f9f9f9;\" %){fullname1}|(% style=\"background-color: #f9f9f9;\" %){email1}|(% style=\"background-color: #f9f9f9;\" %){fullname2}|(% style=\"background-color: #f9f9f9;\" %){email2}\n") # creates a stylized row in table with personal data
                            flag = False
                        else:
                            file.write(f"|(% style=\"background-color: #f0f0f0;\" %){fullname1}|(% style=\"background-color: #f0f0f0;\" %){email1}|(% style=\"background-color: #f0f0f0;\" %){fullname2}|(% style=\"background-color: #f0f0f0;\" %){email2}\n") # creates a stylized row in table with personal data
                            flag = True
                    file.write("\n")    # writes a new line in a file below every table to separete them
        except IOError as e:    # catches an error of processing a table_xwiki.txt
            logging.error(f"An error with processing a file {filename}: {e}")   # logs an error to a error.log file
            error_occurred = True
        except Exception as e:  # catches other errors of this method, but mainly turns on the error flag
            logging.error(f"Unknown error in save_to_xwiki method: {e}")
            error_occurred = True

###                 EXECUTIVE PART OF THE SCRIPT                ###
save_to_xwiki(extract_all_data())
if not error_occurred:  # checks if any error occurred, if not, proceeds to run the xwiki-upload-email-tables.py script that post table_xwiki.txt on https://intranet.ed-chemnitz.de/xwiki/bin/view/Main/Contact%20information/
    subprocess.run(["/usr/bin/python3", "/root/xwiki-script/scripts/xwiki-upload-email-tables.py"])
else:
    logging.error("XWiki page has not been updated due to critical error in kopano_extract_emails.py script.")  # logs an error in error.log
