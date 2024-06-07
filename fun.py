from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from re import compile
from time import sleep
from os import makedirs, getcwd
from os.path import exists


# Initialize selenium webdriver and wait until it loads
def initialize_webdriver(url):
    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(3)
    return driver


# Finds the search bar, asks for the manga you want so the driver can look at all the search results
def find_searchbar(driver):
    search_box = driver.find_element(By.CLASS_NAME, "nav-bar-search")
    search_box.click()
    search_box = driver.find_element(By.ID, "header-search-input")
    manga_name = input("Which manga do you want? ")
    search_box.send_keys(manga_name)
    search_box.send_keys(Keys.RETURN)


# Returns the most relevant search results, asks you to choose one and then follows its url
def choose_manga(driver):
    index_and_links = {}
    titles_and_links = {}
    # Here I use the trick of finding a more simple children tag to then find the parent of all the other children tags
    manga_tags = driver.find_element(By.CLASS_NAME, "manga-card").find_element(By.XPATH, '..').find_element(By.XPATH, '..').find_elements(By.XPATH, "./a[@class='manga-card-dense']")
    for counter, individual_manga_tag in enumerate(manga_tags):
        link = individual_manga_tag.find_element(By.TAG_NAME, 'a').get_attribute("href")
        title = individual_manga_tag.find_element(By.TAG_NAME, "span").text
        index_and_links[str(counter)] = link
        titles_and_links[link] = title
        print(f"{counter}.- {title}")
    selected_index = input("Choose the index(only the number) of the manga you want: ")
    driver.get(index_and_links[selected_index])
    return titles_and_links[index_and_links[selected_index]]


# Collect all of the titles(chapters) and all available languagues and urls for each title
def title_collecter(driver, titles_and_urls):
    titles_raw =  driver.find_elements(By.XPATH, ".//div[@class='bg-accent rounded-sm']")
    for title_raw in titles_raw:
        languagues_and_links = {}
        title = title_raw.find_element(By.TAG_NAME, "span").text.strip().lower()
        # Collect all the languague tags for a specific chapter
        languagues_raw = title_raw.find_elements(By.XPATH, ".//div[@class='flex chapter relative read']")
        # Collect every languague(name) and link there is for the chapter and store it in a dictionary
        for languague_raw in languagues_raw:
            lang = languague_raw.find_element(By.TAG_NAME, "img").get_attribute("title").strip()
            link = languague_raw.find_element(By.XPATH, ".//a/a").get_attribute("href").strip()
            languagues_and_links[lang] = link
        titles_and_urls[title] = languagues_and_links
    return titles_and_urls

                                
# Goes from the first page up to the last collecting all the titles 
def iterate_over_pages(driver):
    counter = 1
    all_titles_and_urls = {}
    next_page_exists = True
    while next_page_exists:
        all_titles_and_urls.update(title_collecter(driver, all_titles_and_urls))
        next_page_exists = False
        try:
            box_of_pages = driver.find_element(By.XPATH, ".//div[@class='flex justify-center flex-wrap gap-2 mt-6']")
            buttons_unfiltered = box_of_pages.find_elements(By.XPATH, "./button[span]")
            buttons = buttons_unfiltered[1:-1]
            for x, button in enumerate(buttons):
                if button.text == str(counter + 1):
                    buttons[x].click()
                    next_page_exists = True
                    break
            counter += 1
        except NoSuchElementException:
            return all_titles_and_urls
    return all_titles_and_urls


# Collects the titles from all pages and presents them using iterate_over_pages() and title_collecter(), presents them in chunks of 10
# (press enter to see next 10 titles), copy and paste the title you choose to download.
def choose_chapters(driver):
    chosen_chapters = {}
    chosen_title = ""
    while chosen_title != "finished":
        all_titles_and_urls = iterate_over_pages(driver)
        for x, title in enumerate(all_titles_and_urls.keys()):
            print(f"{title}")
            if x % 10 == 0 and x != 0 or (len(all_titles_and_urls) < 10 and x == len(all_titles_and_urls) - 1):
                chosen_title = "FOO"
                while chosen_title != "" and chosen_title != "finished":
                    chosen_title = input("Title to download or press enter to see next ones, FINISHED to stop there: ").lower()
                    if chosen_title != "finished" and chosen_title != "":
                        for languague in all_titles_and_urls[chosen_title].keys():
                            print(f"{languague}")
                        chosen_lang = input("Write the languague you want to download your manga on: ")
                        while all_titles_and_urls[chosen_title][chosen_lang] == None:
                            chosen_lang = input("Write the languague you want to download your manga on: ")
                        title_url = all_titles_and_urls[chosen_title][chosen_lang]
                        chosen_chapters[chosen_title] = title_url
            if chosen_title == "finished":
                break     
    return chosen_chapters


def attribute_starts_with(whole_expression, attribute):
    pattern = compile(f'^{attribute}')
    if pattern.match(whole_expression):
         return True
    else:
        return False


def go_next_page(driver):
    elem = driver.switch_to.active_element
    elem.send_keys(Keys.RIGHT)


def is_correct_chapter(driver, correct_chapter):
    if get_current_chapter(driver) == correct_chapter:
        return True
    else:
        return False

def get_current_chapter(driver):
    return driver.find_element(By.XPATH, ".//div[@class='reader--meta chapter']").text

def download_chapter(driver, manga_name, chapter_name):
    chapter_to_scrape = get_current_chapter(driver)
    counter = 1
    while is_correct_chapter(driver, chapter_to_scrape):
        driver.implicitly_wait(10)
        possible_url_tags = driver.find_elements(By.XPATH, ".//img[@class='img sp limit-width limit-height mx-auto']")
        for possible_url_tag in possible_url_tags:
            page_num = possible_url_tag.get_attribute("alt")
            print(page_num)
            coincidence = attribute_starts_with(page_num, str(counter))
            print(coincidence)
            if coincidence:
                folder = getcwd() + f"\\mangas\\{manga_name}\\{chapter_name}"
                print(folder)
                if not exists(folder):
                    makedirs(folder)
                    print("FOLDER CREATED")
                screenshot = possible_url_tag.screenshot_as_png
                with open(f'{folder}\\{counter}.png', 'wb') as f:
                    f.write(screenshot)
        counter += 1
        sleep(4)
        go_next_page(driver)



"""
Problems with the code -> 
. Inefficient to wait for all the chaptrs to load in order to go to one
. Doesn't allow to directly select a chapter
. Doesn't handle mispelled values or non-available mangas with any explanation
. The terminal is not user friendly
. Doesn't handle a range or list of values
"""
        

                
