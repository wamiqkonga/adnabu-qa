#AdNabu Test Store — Automated Test
#Scenario: Search for a product and add it to the cart successfully


import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

STORE_URL    = "https://adnabu-store-assignment1.myshopify.com/"
STORE_PASS   = "AdNabuQA"
SEARCH_TERM  = "snowboard"
WAIT_TIMEOUT = 2



def build_driver(headless: bool = False) -> webdriver.Chrome:
    """Return a configured Chrome WebDriver instance."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")

    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.service import Service
    service = Service(ChromeDriverManager().install())

    return webdriver.Chrome(service=service, options=options)


# ---------------------------------------------------------------------------
# Page-level helpers
# ---------------------------------------------------------------------------

def unlock_store(driver: webdriver.Chrome, wait: WebDriverWait) -> None:
    """Enter the Shopify store password if the password gate is present."""
    driver.get(STORE_URL)
    try:
        pwd_input = wait.until(
            EC.presence_of_element_located((By.ID, "password"))
        )
        pwd_input.clear()
        pwd_input.send_keys(STORE_PASS)
        pwd_input.send_keys(Keys.RETURN)
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "body")))
    except TimeoutException:
        pass  # Store already unlocked


def open_search(driver: webdriver.Chrome, wait: WebDriverWait) -> None:
    """Click the search icon to open the search input."""
    search_trigger_selectors = [
        "[aria-label='Search']",
        "[aria-label='search']",
        "button.search-modal__open-button",
        "a[href='/search']",
        "details[id*='search']",
        ".site-nav__link--icon[href*='search']",
    ]
    for selector in search_trigger_selectors:
        try:
            trigger = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            trigger.click()
            return
        except TimeoutException:
            continue
    raise RuntimeError("Could not locate a search trigger element on the page.")


def type_search_query(driver: webdriver.Chrome, wait: WebDriverWait, query: str) -> None:
    """Type the search query and submit."""
    search_input_selectors = [
        "input[type='search']",
        "input[name='q']",
        "#Search-In-Modal",
        ".search__input",
    ]
    search_input = None
    for selector in search_input_selectors:
        try:
            search_input = wait.until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, selector))
            )
            break
        except TimeoutException:
            continue

    if search_input is None:
        raise RuntimeError("Search input field not found.")

    search_input.clear()
    search_input.send_keys(query)
    search_input.send_keys(Keys.RETURN)


def find_clickable_element(driver: webdriver.Chrome, wait: WebDriverWait, selectors: list[str]):
    """Find the first clickable element matching any selector."""
    combined_selector = ", ".join(selectors)
    return wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, combined_selector)))


def find_visible_element(driver: webdriver.Chrome, wait: WebDriverWait, selectors: list[str]):
    """Find the first visible element matching any selector."""
    combined_selector = ", ".join(selectors)
    elements = wait.until(
        EC.visibility_of_any_elements_located((By.CSS_SELECTOR, combined_selector))
    )
    return elements[0]


def wait_for_results_and_click_first(driver: webdriver.Chrome, wait: WebDriverWait) -> str:
    """Wait for search results and click the first product. Returns product title."""
    result_selectors = [
        ".product-card__name",
        ".card__heading a",
        ".product-item__title",
        "h3.h5 a",
        ".grid__item .card a",
    ]
    first_result = None
    for selector in result_selectors:
        try:
            first_result = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
            )
            break
        except TimeoutException:
            continue

    if first_result is None:
        raise AssertionError(
            f"No search results found for '{SEARCH_TERM}'. "
            "Update SEARCH_TERM to a product that exists in the store."
        )

    product_title = first_result.text.strip()
    first_result.click()
    return product_title


def add_product_to_cart(driver: webdriver.Chrome, wait: WebDriverWait) -> None:
    """Click the Add to Cart button on the product page."""
    add_btn_selectors = [
        "button[name='add']",
        "button[type='submit'].product-form__submit",
        "#ProductSubmitButton",
        ".product-form__cart-submit",
    ]
    add_btn = find_clickable_element(driver, wait, add_btn_selectors)

    if add_btn is None:
        raise RuntimeError("Add to Cart button not found on the product page.")

    btn_text = add_btn.text.strip().lower()
    assert "sold out" not in btn_text and add_btn.is_enabled(), (
        "Product is out of stock — cannot add to cart."
    )

    add_btn.click()


def verify_item_added_to_cart(driver: webdriver.Chrome, wait: WebDriverWait) -> int:
    """Confirm cart shows at least 1 item. Returns cart count."""
    cart_count_selectors = [
        ".cart-count-bubble span[aria-hidden='true']",
        "#CartCount",
        ".cart__count",
        "[data-cart-count]",
        "span.cart-count",
    ]
    count_el = find_visible_element(driver, wait, cart_count_selectors)
    raw = count_el.text.strip() or count_el.get_attribute("data-cart-count") or "0"
    try:
        return int("".join(filter(str.isdigit, raw)))
    except ValueError:
        # Fallback — check for cart notification banner
        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".cart-notification, .cart-notification-product")
                )
            )
            return 1
        except TimeoutException:
            raise AssertionError("Could not confirm item was added to cart.")


# ---------------------------------------------------------------------------
# pytest fixture
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def driver():
    """Spin up Chrome and tear it down after the test."""
    d = build_driver(headless=False)  # Set headless=True to run without a browser window
    yield d
    d.quit()


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------

def test_search_and_add_to_cart(driver: webdriver.Chrome) -> None:
    """
    E2E scenario:
        1. Unlock the password-protected store
        2. Search for a product
        3. Open the first search result
        4. Add it to the cart
        5. Assert cart count >= 1
    """
    wait = WebDriverWait(driver, WAIT_TIMEOUT)

    # Step 1 — Unlock store
    unlock_store(driver, wait)

    # Step 2 — Search
    open_search(driver, wait)
    type_search_query(driver, wait, SEARCH_TERM)

    # Step 3 — Open first result
    product_title = wait_for_results_and_click_first(driver, wait)
    print(f"\n  → Opened product: {product_title!r}")

    # Step 4 — Add to cart
    add_product_to_cart(driver, wait)

    # Step 5 — Verify
    cart_count = verify_item_added_to_cart(driver, wait)
    print(f"  → Cart count after adding: {cart_count}")

    assert cart_count >= 1, (
        f"Expected cart count >= 1 after adding '{product_title}', got {cart_count}"
    )