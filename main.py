import fun
from time import sleep

def main():
    driver = fun.initialize_webdriver("https://mangadex.org/")
    fun.find_searchbar(driver)
    manga_name = fun.choose_manga(driver)
    chosen_chapters = fun.choose_chapters(driver)
    for chapter_name in chosen_chapters.keys():
        driver.get(chosen_chapters[chapter_name])
        fun.download_chapter(driver, manga_name, chapter_name)
    sleep(10)
main()



"""
Stuff learned: 
- If modules don't appear as downloaded maybe try changing your python interpreter
- Think logically step by step, repeat the thought process that lead you to successfully finding an element before
- Sometimes class names have argument like words attached to them, erase them
"""