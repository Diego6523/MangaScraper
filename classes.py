from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from time import sleep

# Initialize selenium webdriver and wait until it loads
driver = webdriver.Chrome()
driver.get("https://mangadex.org/")
driver.implicitly_wait(3)

# Find the search icon, click on it then find the newly appeared searchbox and search for the manga you choose
search_box = driver.find_element(By.CLASS_NAME, "nav-bar-search")
search_box.click()
search_box = driver.find_element(By.ID, "header-search-input")
manga_name = input("Which manga od you want? ")
search_box.send_keys(manga_name)
search_box.send_keys(Keys.RETURN)

# Return the list of coincidences and choose on of them
titles_and_links = {}
# Here I use the trick of finding a more simple children tag to then find the parent of all the other children tags
manga_tags = driver.find_element(By.CLASS_NAME, "manga-card").find_element(By.XPATH, '..').find_element(By.XPATH, '..').find_elements(By.XPATH, "./a[@class='manga-card-dense']")
for tag in manga_tags:
    print(tag.text)
print(len(manga_tags))
for counter, individual_manga_tag in enumerate(manga_tags):
    link = individual_manga_tag.find_element(By.TAG_NAME, 'a').get_attribute("href")
    print(link)
    title = individual_manga_tag.find_element(By.TAG_NAME, "span").text
    titles_and_links[str(counter)] = link
    print(f"{counter}.- {title}")
selected_index = input("Choose the index(only the number) of the manga you want: ")
driver.get(titles_and_links[selected_index])


"""
Stuff learned: 
- If modules don't appear as downloaded maybe try changing your python interpreter
- Think logically step by step, repeat the thought process that lead you to successfully finding an element before
- Sometimes class names have argument like words attached to them, erase them
"""