import os
from mcp.server.fastmcp import FastMCP
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from html2text import html2text
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select


mcp = FastMCP("chromedriver")

CHROME_PROFILE_PATH = os.environ.get("CHROME_PROFILE_PATH", os.path.join(os.getcwd(), "chrome_profile"))
DEFAULT_DOWNLOAD_PATH = os.environ.get("DEFAULT_DOWNLOAD_PATH", os.getcwd())
CHROMIUM_PATH = "/usr/bin/chromium-browser"

driver = None  # Global variable to store the WebDriver instance

def _find_element(driver, by: str, locator: str):
    """
    Finds an element on the page using the specified locator and 'by' method.

    Args:
        driver: The webdriver instance
        locator (str): The locator string (e.g., an ID, class name, XPath).
        by (str): The method to use for locating the element (e.g., 'id', 'xpath', 'class_name', 'tag_name').

    Returns:
        The element if found, otherwise raises a NoSuchElementException.
    """
    if by == "id":
        return driver.find_element(By.ID, locator)
    elif by == "xpath":
        return driver.find_element(By.XPATH, locator)
    elif by == "class_name":
        return driver.find_element(By.CLASS_NAME, locator)
    elif by == "tag_name":
        return driver.find_element(By.TAG_NAME, locator)
    elif by == "name":
        return driver.find_element(By.NAME, locator)
    elif by == "css_selector":
        return driver.find_element(By.CSS_SELECTOR, locator)
    elif by == "link_text":
        return driver.find_element(By.LINK_TEXT, locator)
    elif by == "partial_link_text":
        return driver.find_element(By.PARTIAL_LINK_TEXT, locator)
    else:
        raise ValueError(f"Invalid 'by' method: {by}. Supported methods are: id, xpath, class_name, tag_name, name, css_selector, link_text, partial_link_text")


@mcp.tool()
def launch_browser(url: str, headless: bool = False) -> str:
    """
    Launches a Chrome browser instance with the given URL.

    Args:
        url (str): The URL to open in the browser.
        headless (bool, optional): Whether to launch the browser in headless mode. Defaults to False.

    Returns:
        str: A success message if the browser is launched successfully, or an error message if the operation fails.
    """
    global driver  # Use the global driver variable
    try:
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}")
        chrome_options.binary_location = CHROMIUM_PATH

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.get(url)
        # Do NOT quit the driver, so the browser stays open
        return f"Successfully launched browser with URL: {url} in {'headless' if headless else 'GUI'} mode."
    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to launch browser: {str(e)}"

@mcp.tool()
def goto_page(url: str) -> str:
    """
    Navigates the existing browser instance to the given URL.

    Args:
        url (str): The URL to navigate to.

    Returns:
        str: A success message if the navigation is successful, or an error message if the operation fails.
    """
    global driver  # Use the global driver variable
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."
    try:
        driver.get(url)
        return f"Successfully navigated to URL: {url}"
    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to navigate to URL: {str(e)}"

@mcp.tool()
def close_browser() -> str:
    """
    Closes the current browser instance.

    Returns:
        str: A success message if the browser is closed successfully, or an error message if the operation fails.
    """
    global driver
    if driver:
        try:
            driver.quit()
            driver = None  # Reset the driver to None after closing
            return "Browser closed successfully."
        except WebDriverException as e:
            return f"ChromeDriver error: {str(e)}"
        except Exception as e:
            return f"Failed to close browser: {str(e)}"
    else:
        return "Error: Browser not launched. No browser to close."

@mcp.tool()
def get_page_source(clean_with_html2text: bool = False) -> str:
    """
    Retrieves the source code of the current page in the browser.

    Args:
        clean_with_html2text (bool, optional): Whether to clean the source code using html2text. Defaults to False.

    Returns:
        str: The page source code, or an error message if the operation fails.
    """
    global driver
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."
    try:
        source = driver.page_source
        if clean_with_html2text:
            source = html2text(source)
        return source
    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to retrieve page source: {str(e)}"

@mcp.tool()
def execute_javascript(script: str) -> str:
    """
    Executes JavaScript code in the current browser instance.

    Args:
        script (str): The JavaScript code to execute.

    Returns:
        str: The result of the JavaScript execution, or an error message if the operation fails.
    """
    global driver
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."
    try:
        result = driver.execute_script(script)
        return str(result)  # Convert result to string for MCP compatibility
    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to execute JavaScript: {str(e)}"

@mcp.tool()
def take_screenshot(filename: str = "screenshot.png") -> str:
    """
    Takes a screenshot of the current page and saves it to the downloads directory.

    Args:
        filename (str, optional): The filename to use for the screenshot. Defaults to "screenshot.png".

    Returns:
        str: A success message if the screenshot is saved successfully, or an error message if the operation fails.
    """
    global driver
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."
    try:
        # Create the download directory if it doesn't exist
        if not os.path.exists(DEFAULT_DOWNLOAD_PATH):
            os.makedirs(DEFAULT_DOWNLOAD_PATH)

        filepath = os.path.join(DEFAULT_DOWNLOAD_PATH, filename)
        driver.save_screenshot(filepath)
        return f"Screenshot saved successfully to: {filepath}"
    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to take screenshot: {str(e)}"

@mcp.tool()
def find_element(locator: str, by: str) -> str:
    """
    Finds an element on the page using the specified locator and 'by' method.

    Args:
        locator (str): The locator string (e.g., an ID, class name, XPath).
        by (str): The method to use for locating the element (e.g., 'id', 'xpath', 'class_name', 'tag_name').

    Returns:
        str: The text content of the found element, or an error message if the element is not found or the browser is not launched.
    """
    global driver
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."

    try:
        element = _find_element(driver, by, locator)

        if element.text:
            return element.text
        else:
            return f"Tool call is done. Element with locator '{locator}' found using method '{by}', but it contains no text."

    except NoSuchElementException:
        return f"Error: Element with locator '{locator}' not found using method '{by}'."
    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to find element: {str(e)}"

@mcp.tool()
def get_element_text(locator: str, by: str) -> str:
    """
    Retrieves the text content of a specific element on a webpage.

    Args:
        locator (str): The locator string to identify the element (e.g., an ID, class name, XPath).
        by (str): The method used to locate the element (e.g., 'id', 'xpath', 'class_name', 'tag_name').

    Returns:
        str: The text content of the element, or an error message if the element is not found or if there's an issue.
    """
    global driver
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."

    try:
        element = _find_element(driver, by, locator)

        if element.text:
            return element.text
        else:
            return f"Tool call is done. Element with locator '{locator}' found using method '{by}', but it contains no text."

    except NoSuchElementException:
        return f"Error: Element with locator '{locator}' not found using method '{by}'."
    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to find element: {str(e)}"

@mcp.tool()
def click_element(locator: str, by: str) -> str:
    """
    Clicks a specific element on a webpage.

    Args:
        locator (str): The locator string to identify the element (e.g., an ID, class name, XPath).
        by (str): The method used to locate the element (e.g., 'id', 'xpath', 'class_name', 'tag_name').

    Returns:
        str: A success message if the element is clicked successfully, or an error message if the element is not found or if there's an issue.
    """
    global driver
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."

    try:
        element = _find_element(driver, by, locator)

        element.click()
        return f"Successfully clicked element with locator '{locator}' using method '{by}'."
    except NoSuchElementException:
        return f"Error: Element with locator '{locator}' not found using method '{by}'."
    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to click element: {str(e)}"

@mcp.tool()
def type_into_element(locator: str, by: str, text: str) -> str:
    """
    Types text into a specific element on a webpage, such as a form field.

    Args:
        locator (str): The locator string to identify the element (e.g., an ID, class name, XPath).
        by (str): The method used to locate the element (e.g., 'id', 'xpath', 'class_name', 'tag_name').
        text (str): The text to type into the element.

    Returns:
        str: A success message if the text is typed successfully, or an error message if the element is not found or if there's an issue.
    """
    global driver
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."

    try:
        element = _find_element(driver, by, locator)

        element.send_keys(text)
        return f"Successfully typed text into element with locator '{locator}' using method '{by}'."
    except NoSuchElementException:
        return f"Error: Element with locator '{locator}' not found using method '{by}'."
    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to type into element: {str(e)}"

@mcp.tool()
def clear_element_text(locator: str, by: str) -> str:
    """
    Clears the text from a specific element on a webpage, such as a form field.

    Args:
        locator (str): The locator string to identify the element (e.g., an ID, class name, XPath).
        by (str): The method used to locate the element (e.g., 'id', 'xpath', 'class_name', 'tag_name').

    Returns:
        str: A success message if the text is cleared successfully, or an error message if the element is not found or if there's an issue.
    """
    global driver
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."

    try:
        element = _find_element(driver, by, locator)

        element.clear()
        return f"Successfully cleared text from element with locator '{locator}' using method '{by}'."
    except NoSuchElementException:
        return f"Error: Element with locator '{locator}' not found using method '{by}'."
    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to clear text from element: {str(e)}"

@mcp.tool()
def scroll(delta_x: int = 0, delta_y: int = 0) -> str:
    """
    Scrolls the page by a specified amount in the x and y directions.

    Args:
        delta_x (int, optional): The amount to scroll in the x direction. Positive values scroll right, negative values scroll left. Defaults to 0.
        delta_y (int, optional): The amount to scroll in the y direction.  Positive values scroll down, negative values scroll up. Defaults to 0.

    Returns:
        str: A success message if the page is scrolled successfully, or an error message if the browser is not launched or if there's an issue.
    """
    global driver
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."

    try:
        driver.execute_script(f"window.scrollBy({delta_x}, {delta_y});")
        return f"Successfully scrolled the page by {delta_x} pixels in the x direction and {delta_y} pixels in the y direction."
    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to scroll the page: {str(e)}"

@mcp.tool()
def get_browser_stats() -> str:
    """
    Retrieves statistics about the current browser state, including scroll position, title, URL, and cookies.

    Returns:
        str: A JSON-formatted string containing the browser statistics,
             or an error message if the browser is not launched or if there's an issue.
    """
    global driver
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."

    try:
        # Execute JavaScript to get scroll position
        scroll_x = driver.execute_script("return window.pageXOffset;")
        scroll_y = driver.execute_script("return window.pageYOffset;")

        # Get window size
        window_width = driver.execute_script("return window.innerWidth;")
        window_height = driver.execute_script("return window.innerHeight;")

        # Get document size
        document_width = driver.execute_script("return document.documentElement.scrollWidth;")
        document_height = driver.execute_script("return document.documentElement.scrollHeight;")

        # Get title and URL
        title = driver.title
        current_url = driver.current_url

        # Get cookies
        cookies = driver.get_cookies()

        # Get local storage
        local_storage = driver.execute_script("""
            var items = {};
            for (var i = 0, len = localStorage.length; i < len; i++) {
                var key = localStorage.key(i);
                items[key] = localStorage.getItem(key);
            }
            return items;
        """)

        # Get session storage
        session_storage = driver.execute_script("""
            var items = {};
            for (var i = 0, len = sessionStorage.length; i < len; i++) {
                var key = sessionStorage.key(i);
                items[key] = sessionStorage.getItem(key);
            }
            return items;
        """)

       # Get number of frames
        number_of_frames = len(driver.find_elements(By.TAG_NAME, "iframe"))

        # Get device pixel ratio
        device_pixel_ratio = driver.execute_script("return window.devicePixelRatio;")

        # Get user agent
        user_agent = driver.execute_script("return navigator.userAgent;")

        # Create a dictionary to store the stats
        stats = {
            "scroll_x": scroll_x,
            "scroll_y": scroll_y,
            "window_width": window_width,
            "window_height": window_height,
            "document_width": document_width,
            "document_height": document_height,
            "title": title,
            "url": current_url,
            "cookies": cookies,
            "local_storage": local_storage,
            "session_storage": session_storage,
            "number_of_frames": number_of_frames,
            "device_pixel_ratio": device_pixel_ratio,
            "user_agent": user_agent,
        }

        import json
        return json.dumps(stats, indent=4, default=str)  # Convert the dictionary to a JSON string

    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to retrieve browser stats: {str(e)}"

@mcp.tool()
def get_element_attribute(locator: str, by: str, attribute: str) -> str:
    """
    Retrieves the value of a specific attribute of an element on a webpage.

    Args:
        locator (str): The locator string to identify the element (e.g., an ID, class name, XPath).
        by (str): The method used to locate the element (e.g., 'id', 'xpath', 'class_name', 'tag_name').
        attribute (str): The name of the attribute to retrieve (e.g., 'href', 'src', 'class').

    Returns:
        str: The value of the attribute, or an error message if the element is not found, 
             the attribute is not present, or if there's an issue.
    """
    global driver
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."

    try:
        element = _find_element(driver, by, locator)

        attribute_value = element.get_attribute(attribute)
        if attribute_value is not None:
            return attribute_value
        else:
            return f"Error: Attribute '{attribute}' not found on element with locator '{locator}' using method '{by}'."

    except NoSuchElementException:
        return f"Error: Element with locator '{locator}' not found using method '{by}'."
    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to get element attribute: {str(e)}"

@mcp.tool()
def get_elements(locator: str, by: str) -> str:
    """
    Retrieves a list of elements matching the given locator and 'by' method.

    Args:
        locator (str): The locator string (e.g., an ID, class name, XPath).
        by (str): The method to use for locating the element (e.g., 'id', 'xpath', 'class_name', 'tag_name').

    Returns:
        str: A JSON-formatted string containing a list of dictionaries, where each dictionary
             represents an element and contains its 'text' and 'attributes'.
             Returns an error message if the browser is not launched or if there's an issue.
    """
    global driver
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."

    try:
        if by == "id":
            elements = driver.find_elements(By.ID, locator)
        elif by == "xpath":
            elements = driver.find_elements(By.XPATH, locator)
        elif by == "class_name":
            elements = driver.find_elements(By.CLASS_NAME, locator)
        elif by == "tag_name":
            elements = driver.find_elements(By.TAG_NAME, locator)
        elif by == "name":
            elements = driver.find_elements(By.NAME, locator)
        elif by == "css_selector":
            elements = driver.find_elements(By.CSS_SELECTOR, locator)
        elif by == "link_text":
            elements = driver.find_elements(By.LINK_TEXT, locator)
        elif by == "partial_link_text":
            elements = driver.find_elements(By.PARTIAL_LINK_TEXT, locator)
        else:
            return f"Error: Invalid 'by' method: {by}. Supported methods are: id, xpath, class_name, tag_name, name, css_selector, link_text, partial_link_text"

        element_list = []
        for element in elements:
            element_data = {
                "text": element.text,
                "attributes": driver.execute_script(
                    """
                    var items = {};
                    var attrs = arguments[0].attributes;
                    for (var i = 0; i < attrs.length; i++) {
                        items[attrs[i].name] = attrs[i].value;
                    }
                    return items;
                    """,
                    element,
                ),
            }
            element_list.append(element_data)

        import json
        return json.dumps(element_list, indent=4, default=str)

    except NoSuchElementException:
        return f"Error: Element with locator '{locator}' not found using method '{by}'."
    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to find elements: {str(e)}"

@mcp.tool()
def submit_form(locator: str, by: str) -> str:
    """Submits a form element.

    Args:
        locator (str): The locator string to identify the form element (e.g., an ID, class name, XPath).
        by (str): The method used to locate the element (e.g., 'id', 'xpath', 'class_name', 'tag_name').

    Returns:
        str: A success message if the form is submitted successfully, or an error message if the form is not found or if there's an issue.
    """
    global driver
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."

    try:
        form_element = _find_element(driver, by, locator)

        form_element.submit()
        return f"Successfully submitted form with locator '{locator}' using method '{by}'."

    except NoSuchElementException:
        return f"Error: Form element with locator '{locator}' not found using method '{by}'."
    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to submit form: {str(e)}"

@mcp.tool()
def wait_for_element(by: str, locator: str, timeout: int) -> str:
    """Waits for an element to be present on the page.

    Args:
        by (str): The method to use for locating the element (e.g., 'id', 'xpath', 'class_name', 'tag_name').
        locator (str): The locator string (e.g., an ID, class name, XPath).
        timeout (int): The maximum time to wait, in seconds.

    Returns:
        str: A success message if the element is found within the timeout, or an error message if the timeout is reached or if there's an issue.
    """
    global driver
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."

    try:
        if by == "id":
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.ID, locator))
            )
        elif by == "xpath":
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, locator))
            )
        elif by == "class_name":
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CLASS_NAME, locator))
            )
        elif by == "tag_name":
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, locator))
            )
        elif by == "name":
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.NAME, locator))
            )
        elif by == "css_selector":
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, locator))
            )
        elif by == "link_text":
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.LINK_TEXT, locator))
            )
        elif by == "partial_link_text":
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.PARTIAL_LINK_TEXT, locator))
            )
        else:
            return f"Error: Invalid 'by' method: {by}. Supported methods are: id, xpath, class_name, tag_name, name, css_selector, link_text, partial_link_text"

        return f"Successfully waited for element with locator '{locator}' using method '{by}' to be present within {timeout} seconds."

    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Timeout: Element with locator '{locator}' did not appear within {timeout} seconds."

@mcp.tool()
def select_option(locator: str, by: str, value: str) -> str:
    """Selects an option from a dropdown menu.

    Args:
        locator (str): The locator string to identify the select element (e.g., an ID, class name, XPath).
        by (str): The method used to locate the element (e.g., 'id', 'xpath', 'class_name', 'tag_name').
        value (str): The value of the option to select.

    Returns:
        str: A success message if the option is selected successfully, or an error message if the select element or option is not found, or if there's an issue.
    """
    global driver
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."

    try:
        select_element = _find_element(driver, by, locator)

        select_object = Select(select_element)
        select_object.select_by_value(value)
        return f"Successfully selected option with value '{value}' in select element with locator '{locator}' using method '{by}'."

    except NoSuchElementException:
        return f"Error: Select element with locator '{locator}' not found using method '{by}'."
    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to select option: {str(e)}"

@mcp.tool()
def upload_file(locator: str, by: str, file_path: str) -> str:
    """Uploads a file to the specified file input element.

    Args:
        locator (str): The locator string to identify the file input element (e.g., an ID, class name, XPath).
        by (str): The method used to locate the element (e.g., 'id', 'xpath', 'class_name', 'tag_name').
        file_path (str): The path to the file to upload.

    Returns:
        str: A success message if the file is uploaded successfully, or an error message if the element is not found or if there's an issue.
    """
    global driver
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."

    try:
        file_input = _find_element(driver, by, locator)

        file_input.send_keys(file_path)
        return f"Successfully uploaded file '{file_path}' to element with locator '{locator}' using method '{by}'."

    except NoSuchElementException:
        return f"Error: File input element with locator '{locator}' not found using method '{by}'."
    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to upload file: {str(e)}"

@mcp.tool()
def open_new_tab(url: str) -> str:
    """Opens a new tab with the given URL.

    Args:
        url (str): The URL to open in the new tab.

    Returns:
        str: A success message if the tab is opened successfully, or an error message if the browser is not launched or if there's an issue.
    """
    global driver
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."

    try:
        # Open a new tab
        driver.execute_script("window.open('{}', '_blank');".format(url))

        # Switch to the new tab
        driver.switch_to.window(driver.window_handles[-1])

        return f"Successfully opened a new tab with URL: {url}"

    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to open a new tab: {str(e)}"

@mcp.tool()
def switch_to_tab(index: int) -> str:
    """Switches to a specific tab in the browser.

    Args:
        index (int): The index of the tab to switch to (0-based).

    Returns:
        str: A success message if the tab is switched to successfully, or an error message if the browser is not launched, the index is out of bounds, or if there's an issue.
    """
    global driver
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."

    try:
        window_handles = driver.window_handles
        if 0 <= index < len(window_handles):
            driver.switch_to.window(window_handles[index])
            return f"Successfully switched to tab with index: {index}"
        else:
            return f"Error: Tab index {index} is out of bounds. There are {len(window_handles)} tabs open (0-{len(window_handles)-1})."

    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to switch to tab: {str(e)}"


@mcp.tool()
def close_tab() -> str:
    """Closes the current tab.

    Returns:
        str: A success message if the tab is closed successfully, or an error message if the browser is not launched or if there's an issue.
    """
    global driver
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."

    try:
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return "Successfully closed current tab."

    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to close current tab: {str(e)}"

@mcp.tool()
def switch_to_frame(by: str, locator: str) -> str:
    """Switches the driver's focus to a particular iframe.

    Args:
        by (str): The method to use for locating the iframe (e.g., 'id', 'xpath', 'class_name', 'tag_name').
        locator (str): The locator string (e.g., an ID, class name, XPath).

    Returns:
        str: A success message if the switch is successful, or an error message if the iframe is not found or if there's an issue.
    """
    global driver
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."

    try:
        iframe = _find_element(driver, by, locator)

        driver.switch_to.frame(iframe)
        return f"Successfully switched to iframe with locator '{locator}' using method '{by}'."

    except NoSuchElementException:
        return f"Error: Iframe with locator '{locator}' not found using method '{by}'."
    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to switch to iframe: {str(e)}"

@mcp.tool()
def get_current_tab_index() -> str:
    """Returns the index of the currently active tab.

    Returns:
        str: The index of the current tab (0-based), or an error message if the browser is not launched.
    """
    global driver
    if driver is None:
        return "Error: Browser not launched. Please launch the browser first using the launch_browser tool."

    try:
        window_handle = driver.current_window_handle
        window_handles = driver.window_handles
        index = window_handles.index(window_handle)
        return str(index)
    except ValueError:
        return "Error: Current window handle not found in list of window handles."
    except WebDriverException as e:
        return f"ChromeDriver error: {str(e)}"
    except Exception as e:
        return f"Failed to get current tab index: {str(e)}"
