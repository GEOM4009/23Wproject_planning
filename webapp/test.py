from selenium import webdriver
from selenium.webdriver.common.keys import Keys

# create a new Chrome browser instance
driver = webdriver.Chrome()

# navigate to the Google home page
driver.get("https://www.google.com")

# find the search box element by its name attribute
search_box = driver.find_element_by_id("input")

# enter some text into the search box
search_box.send_keys("Selenium WebDriver")

# submit the search by pressing the Enter key
search_box.send_keys(Keys.ENTER)

# wait for the search results to load
driver.implicitly_wait(10)

# print the title of the search results page
print(driver.title)

# close the browser
driver.quit()
