import pandas as pd
import requests
from bs4 import BeautifulSoup
import os

# URL of the HTML file
element_url = "https://janaf.nist.gov/tables/C-index.html"

# Make an HTTP request and retrieve the HTML content
response = requests.get(element_url)
html_content = response.content

# Create the BeautifulSoup object to parse the HTML
soup = BeautifulSoup(html_content, 'html.parser')

# Find all <tr> elements after the first one
trs = soup.find_all('tr')[1:]

# List to store the links
links = []

# Iterate over each <tr> element
for tr in trs:
    # Find the fifth <td> element within the <tr>
    td = tr.find_all('td')[4]
    
    # Find the <a> element within the <td>
    a = td.find('a')
    
    # Extract the link from the href attribute
    link = a['href']
    
    # Add the link to the list
    links.append(link)

# Iterate over each link
for link in links:
    # Construct the full URL for the link
    component_url = f"https://janaf.nist.gov/tables/{link}"

    # Make an HTTP request and retrieve the HTML content
    response = requests.get(component_url)
    html_content = response.content

    # Create the BeautifulSoup object to parse the HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the table
    table = soup.find('table')

    if len(table) > 0:

        # Extract the first four <tr> or <th> elements
        header_rows = []
        for tr in table.find_all(['tr'])[:4]:
            tds = tr.find_all(['td', 'th'])
            for td in tds:
                if td.get_text(strip=True):
                    row_data = [td.get_text(strip=True)]
                    header_rows.append(row_data)

        # Add an empty row
        header_rows.append([])

        # Combine the header rows into a single string
        header_text = '\n'.join([' '.join(row) for row in header_rows])

        # Read the table from the HTML page
        df = pd.read_html(component_url)[0]

        # Remove the first four rows
        df = df.iloc[4:]

        # Find the index of the rows containing the word "PREVIOUS" (footer)
        previous_rows = df[df.apply(lambda row: 'PREVIOUS' in str(row), axis=1)].index

        # Remove the found rows and all subsequent rows
        df = df.loc[:previous_rows.min() - 1] if len(previous_rows) > 0 else df

        # Remove rows with empty values
        df = df.dropna(how='all')

        # Reset the index of the DataFrame
        df = df.reset_index(drop=True)

        # Extract the file name
        file_name = component_url.split("/")[-1].split(".")[0]
        file_name_suffix = header_rows[0][0].split('(', 1)[1].split(')')[0]
        file_name = f"{file_name}_({file_name_suffix}).txt"

        # Define the folder path
        folder_name = file_name.split('-')[0]
        folder_path = f'output/{folder_name}'

        # Full file path
        file_path = os.path.join(folder_path, file_name)

        # Create the folder (if it doesn't exist)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Save the header text and the DataFrame as a tab-separated text file
        with open(file_path, 'w', encoding='UTF-8') as file:
            file.write(header_text + '\n')
            df.to_csv(file, sep="\t", index=False, header=False, mode='a')

        print(f"File saved successfully: .../{folder_path}/{file_name}")
    else:
        print("No table found on the page:", component_url)