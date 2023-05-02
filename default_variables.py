WEBSITE = "https://www.nytimes.com/"
WEBSITE_QUERY = "https://www.nytimes.com/search?query={query}"

SEARCH_PHRASE = "Economy"
NEWS_CATEGORY_OR_SECTION = ["Test A", "Business", "Test B", "Opinion", "U.S.", "Week in Review", "World"]
MONTHS = 1

CURRENCY_REGEX_LIST = [
    "\$\d{1,3}\.\d{1,2}",           # $11.1
    "\$\d{1,3}\,\d{3}\.\d{1,2}",    # $111,111.11
    "\d{1,3} dollars",              # 11 dollars
    "\d{1,3} usd"                   # 11 USD
]

CURRENCY_REGEX_LIST_JOINED = '(?:%s)' % '|'.join(CURRENCY_REGEX_LIST)