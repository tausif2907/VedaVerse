from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
import time

# Path to the Edge WebDriver executable
edge_driver_path = "msedgedriver.exe"  # Replace with the actual path

# Setup the Edge driver service
service = Service(executable_path=edge_driver_path)

# Set up Edge options if needed
options = webdriver.EdgeOptions()
options.add_argument("start-maximized")  # Opens the browser in maximized mode
options.add_argument("disable-infobars")  # Disables the infobar that shows "Chrome is being controlled by automated test software"

# Initialize the Edge driver
driver = webdriver.Edge(service=service, options=options)

# Open a website
driver.get("https://www.youtube.com")

# Perform some actions (optional)
time.sleep(5)  # Wait for 5 seconds to see the page

# Close the browser
driver.quit()
