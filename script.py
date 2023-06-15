import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

# URL of the HTML file
url = "https://janaf.nist.gov/tables/C-095.html"

# Make an HTTP request and retrieve the HTML content
response = requests.get(url)
html_content = response.content

# Create the BeautifulSoup object to parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Find the first <tr> of the table
first_tr = soup.find('tr')

# Find the first <td> within the first <tr>
first_td = first_tr.find('td')

# Extract the text from the first <td>
first_td_text = first_td.get_text(strip=True)

# Find the text between parentheses in the first <td>
file_name_suffix = first_td_text.split('(', 1)[1].split(')')[0]

# Read the table from the HTML page
table = pd.read_html(url)

# Check if any table was found
if len(table) > 0:
    # Extract the file name
    file_name = url.split("/")[-1].split(".")[0]
    file_name = f"{file_name}_({file_name_suffix}).txt"
    folder_name = file_name.split('-')[0]
    folder_path = f'output/{folder_name}'

    # Convert the table to a pandas DataFrame
    df = table[0]

    # Ignore the first four rows
    df = df.iloc[4:]

    # Find the index of the rows containing the word "PREVIOUS" (footer)
    previous_rows = df[df.apply(lambda row: 'PREVIOUS' in str(row), axis=1)].index

    # Remove the found rows and all subsequent rows
    df = df.loc[:previous_rows.min() - 1] if len(previous_rows) > 0 else df

    # Full file path
    file_path = os.path.join(folder_path, file_name)

    # Create the folder (if it doesn't exist)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    # Save the DataFrame as a tab-separated text file
    df.to_csv(file_path, sep="\t", index=False, header=False)

    print(f"File saved successfully: .../{folder_path}/{file_name}")
else:
    print("No table found on the page:", url)
