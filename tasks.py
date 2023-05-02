from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems import WorkItems
from RPA.Robocorp.Vault import Vault

import default_variables
from helpers import date_helper

from datetime import datetime
import time, re

browser_lib = Selenium()

def get_work_variables():

    website = default_variables.WEBSITE
    website_query = default_variables.WEBSITE_QUERY

    try:

        _secret = Vault().get_secret("credentials")

        USER_NAME = _secret["username"]
        PASSWORD = _secret["password"]

        work_items = WorkItems()
        work_items.get_input_work_item()

        search_phrase = work_items.get_work_item_variable(default_variables.SEARCH_PHRASE)
        if search_phrase == None: search_phrase = default_variables.SEARCH_PHRASE

        news_category_or_section = work_items.get_work_item_variable(default_variables.NEWS_CATEGORY_OR_SECTION)
        if not type(news_category_or_section) == list or len(news_category_or_section) == 0:
            news_category_or_section = default_variables.NEWS_CATEGORY_OR_SECTION

        months = work_items.get_work_item_variable(default_variables.MONTHS)
        if not type(months) == int: months = default_variables.MONTHS

    except Exception as ex:
        search_phrase = default_variables.SEARCH_PHRASE
        news_category_or_section = default_variables.NEWS_CATEGORY_OR_SECTION
        months = default_variables.MONTHS

    finally:
        return {
            "website": website,
            "website_query": website_query,
            "search_phrase": search_phrase,
            "news_category_or_section": news_category_or_section,
            "months": months
        }

def open_the_website(url):
    # open_headless_chrome_browser
    browser_lib.open_available_browser(url)


# The test says to navigate to website, fill a term in the search field, and click it
# That's why I've done this way
# But in real life, I would probably do a direct access to search URL. Example:
# browser_lib.go_to(https://www.nytimes.com/search?query=economy&sections=Opinion%7Cnyt%3A%2F%2Fsection%2Fd7a71185-aa60-5635-bce0-5fab76c7c297&sort=newest&startDate=20230401&endDate=20230502)
def access_search_page(query, website_query):
    try:
        # assert_page_contains
        browser_lib.click_button("xpath://button[@data-testid='nav-button']")
        browser_lib.input_text("xpath://input[@data-testid='search-input']", query)
        browser_lib.click_button("xpath://button[@data-test-id='search-submit']")
    except Exception as ex:
        website_query_url = website_query.format(query = query)
        browser_lib.go_to(website_query_url)

def close_cookies_windows():
    try:
        browser_lib.click_button("xpath://button[@data-testid='expanded-dock-btn-selector']")
    except:
        printing_message("Error when closing cookies window")


def apply_date_range_filter(months):
    try:
        # Applying months filter

        # Fixing months if something happens
        months = date_helper.fixing_months_variable(months)
        start_date_string, end_date_string = date_helper.calculate_start_and_end_date(months)

        date_range_selector = browser_lib.find_element("xpath://button[@data-testid='search-date-dropdown-a']")
        date_range_selector.click()
        
        # Unfortunately there's no id for this button or any parent element
        # So we had to go after child button via "value" property
        browser_lib.click_button("xpath://div[@aria-label='Date Range']//button[@value='Specific Dates']")
        
        browser_lib.input_text("startDate", start_date_string)
        browser_lib.input_text("endDate", end_date_string)

        # Clicking again to dismiss the dialog
        date_range_selector.click()
    except Exception as ex:
        printing_message("Error when applying date range filter")

def apply_section_filter(news_category_list):
    try:
        # If there's no category to select, we can let the filter as it is
        # Which is the "Any" category
        if len(news_category_list) == 0:
            pass

        section_selector = browser_lib.find_element("xpath://button[@data-testid='search-multiselect-button']")
        section_selector.click()

        for news_category in news_category_list:
            try:
                section_search_count = browser_lib.get_element_count(f"//span[text()='{news_category}']")

                if section_search_count == 1:
                    browser_lib.click_element(f"//span[text()='{news_category}']")
                else:
                    printing_message(f"Section '{news_category}' not found")
            except Exception as ex:
                printing_message(f"Error when trying to select '{news_category}' filter section")

        # Clicking again to dismiss the dialog
        section_selector.click()
        #a = 5 / 0
    except Exception as ex:
        printing_message("Error when applying section filter")

        # If any major error happens
        # we will go back to selecting "Any" section
        select_section_any()


def select_section_any():
    try:
        section_button = browser_lib.find_element(f"xpath://button[@data-testid='search-multiselect-button']")

        section_button_class = section_button.get_attribute("class")

        # This means that the Section dialog is not open
        if not "popup-visible" in section_button_class:
            section_button.click()

        browser_lib.click_element(f"//span[text()='Any']")

        # Clicking again to dismiss the dialog
        section_button.click()

    except:
        printing_message("Error when applying 'Any' section filter")

def select_sort_by_newest():
    try:
        sort_selector = browser_lib.find_element("xpath://select[@data-testid='SearchForm-sortBy']")

        sort_selector.click()
        browser_lib.click_element("xpath://select[@data-testid='SearchForm-sortBy']/option[@value='newest']")
        
        # Clicking again to dismiss the dialog
        sort_selector.click()
    except:
        printing_message("Error when sorting by newest")

# In best case scenario, isn't needed to press this button
# since the sort update will already update the query result
# But if anything wrong happens, this click will ensure that the search will happen anyway
def press_search_page_button():
    browser_lib.click_button("xpath://button[@data-testid='search-page-submit']")

def extract_articles(query):
    scroll_all_articles()
    article_info_list = get_articles_info(query)

    return article_info_list

def scroll_all_articles():
    show_more_button_xpath = "xpath://button[@data-testid='search-show-more-button']"
    articles_xpath = "xpath://ol[@data-testid='search-results']//li[@data-testid='search-bodega-result']"
    articles_count = 0
    
    while browser_lib.get_element_count(show_more_button_xpath) == 1:
        try:
            # Sometimes, it takes some time for new articles to load
            # if that happens, it's better to wait them to load
            # instead of clicking the "show more" button again
            # Also, during the last batch of articles
            # the button is still visible until the articles are loaded
            # and only after that the button disappear
            # Because of that, it is needed to check if the article list changed
            # before trying to get the "show more" button again
            if articles_count > 0 and browser_lib.get_element_count(articles_xpath) == articles_count:
                #time.sleep(3)
                continue

            articles_count = browser_lib.get_element_count(articles_xpath)

            browser_lib.scroll_element_into_view(show_more_button_xpath)
            browser_lib.click_button_when_visible(show_more_button_xpath)
        except Exception as ex:
            break
        

def get_articles_info(query):
    article_info_list = []

    articles_xpath = "xpath://ol[@data-testid='search-results']//li[@data-testid='search-bodega-result']"
    articles_count = browser_lib.get_element_count(articles_xpath)

    query_lower = query.lower()

    # Using full chained xpath
    # because using element.find_elements to find children
    # only throws exception
    for i in range(1, articles_count + 1):
        try:
            article_children_div_xpath = f"{articles_xpath}[{i}]/div/"

            title = get_attribute_inner_html            (f"{article_children_div_xpath}div/div/a/h4")
            date = get_attribute_inner_html             (f"{article_children_div_xpath}span")
            description = get_attribute_inner_html      (f"{article_children_div_xpath}div/div/a/p[1]")
            picture_filename = browser_lib.find_element (f"{article_children_div_xpath}div/figure/div/img").get_attribute("src")
            
            title_lower = title.lower()
            description_lower = description.lower()

            search_phrases_count = title_lower.count(query_lower) + description_lower.count(query_lower)
            contains_any_amount_of_money = (
                len(re.findall(default_variables.CURRENCY_REGEX_LIST_JOINED, title_lower)) > 0
                or
                len(re.findall(default_variables.CURRENCY_REGEX_LIST_JOINED, description_lower)) > 0
            )

            article_dict = {
                "title": title,
                "date": date,
                "description": description,
                "picture_filename": picture_filename,
                "search_phrases_count": search_phrases_count,
                "contains_any_amount_of_money": contains_any_amount_of_money
            }

            article_info_list.append(article_dict)

        except Exception as ex:
            printing_message(ex)

    return article_info_list

def store_screenshot(filename):
    browser_lib.screenshot(filename=filename)

def printing_message(message):
    print(f"{str(datetime.now())} - {message}")

def get_attribute_inner_html(element_path):
    return browser_lib.find_element(element_path).get_attribute("innerHTML")


# Define a main() function that calls the other functions in order:
def main():
    try:
        variables = get_work_variables()
        open_the_website(variables["website"])
        access_search_page(variables["search_phrase"], variables["website_query"])
        close_cookies_windows()
        apply_date_range_filter(variables["months"])
        apply_section_filter(variables["news_category_or_section"])
        select_sort_by_newest()
        press_search_page_button()
        article_info_list = extract_articles(variables["search_phrase"])
    except Exception as ex:
        printing_message(ex)
    finally:
        browser_lib.close_all_browsers()


# Call the main() function, checking that we are running as a stand-alone script:
if __name__ == "__main__":
    main()
