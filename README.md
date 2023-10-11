# Python robot

A simple web scraper robot implemented in Python instead of Robot Framework syntax, using the `rpaframework` set of libraries.

It is possible to implement robots using pure Python, without using Robot Framework. These robots are first-class citizens in Robocorp: they can be developed iteratively with our developer tools, and run and orchestrated in [Control Room](/development-guide/control-room/configuring-robots), like any other robot. [RPA Framework](/automation-libraries/rpa-framework-overview), our set of open-source libraries, provides APIs for both Robot Framework and Python.

This simple robot opens a web page, searches for a term, and takes a screenshot of the web page using the [`RPA.Browser.Selenium`](/libraries/rpa-framework/rpa-browser-selenium) library.

## Robot script (Python)

```python
from RPA.Browser.Selenium import Selenium

browser_lib = Selenium()


def open_the_website(url):
    browser_lib.open_available_browser(url)


def search_for(term):
    input_field = "css:input"
    browser_lib.input_text(input_field, term)
    browser_lib.press_keys(input_field, "ENTER")


def store_screenshot(filename):
    browser_lib.screenshot(filename=filename)


# Define a main() function that calls the other functions in order:
def main():
    try:
        open_the_website("https://robocorp.com/docs/")
        search_for("python")
        store_screenshot("output/screenshot.png")
    finally:
        browser_lib.close_all_browsers()


# Call the main() function, checking that we are running as a stand-alone script:
if __name__ == "__main__":
    main()
```

- Import the `Selenium` library from the `RPA.Browser.Selenium` package.
- Initialize the browser library.
- Define the functions that implement the operations the robot is supposed to do.
- Define the `main` function.
- Call the `main` function.

> **Important:** Always use `try` and `finally` to ensure that resources such as open browsers are closed even if some of the functions fail. This is similar to using `[Teardown]` in Robot Framework scripts. Read the [Errors and Exceptions](https://docs.python.org/3.7/tutorial/errors.html) document on python.org for more information.

## `robot.yaml`

The `robot.yaml` file for the Python robot looks like this:

```yaml
tasks:
  Run Python:
    shell: python tasks.py

condaConfigFile: conda.yaml
artifactsDir: output
PATH:
  - .
PYTHONPATH:
  - .
ignoreFiles:
  - .gitignore
```

Note the `shell` section:

```yaml
shell: python tasks.py
```

> In this case, we tell Python to run the `tasks.py` file. You can customize the command for your needs.

For comparison, the typical Robot Framework command looks like this:

```yaml
shell: python -m robot --report NONE --outputdir output --logtitle "Task log" tasks.robot
```

> In this case, we tell Python to run the `robot` module (`python -m robot`) with arguments.
