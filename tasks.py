from RPA.Browser.Selenium import Selenium
from RPA.Robocorp.WorkItems import WorkItems
from RPA.Robocorp.Vault import Vault

import default_variables

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


def apply_filters(news_category, months):
    pass


def store_screenshot(filename):
    browser_lib.screenshot(filename=filename)


# Define a main() function that calls the other functions in order:
def main():
    try:
        variables = get_work_variables()
        open_the_website(variables["website"])
        access_search_page(variables["search_phrase"], variables["website_query"])
        apply_filters()
        store_screenshot("output/screenshot.png")
    except Exception as ex:
        print(ex)
    finally:
        browser_lib.close_all_browsers()


# Call the main() function, checking that we are running as a stand-alone script:
if __name__ == "__main__":
    main()
