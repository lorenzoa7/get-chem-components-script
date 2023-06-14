import requests
from bs4 import BeautifulSoup

url = "https://janaf.nist.gov/tables/C-095.html"
file_name = "C-095.txt"

# Download HTML page
response = requests.get(url)
html_content = response.content

# Check HTML content
soup = BeautifulSoup(html_content, "html.parser")

# Extract text content
text_content = soup.get_text()

# Save the content into a .txt file
with open(file_name, "w") as file:
    file.write(text_content)

print(f"File saved as '{file_name}'")