"""
Automated Telegram API credentials fetcher using Playwright.
Author: Your Name
Description: Automates the process of obtaining api_id and api_hash from my.telegram.org.
"""
import asyncio
from playwright.async_api import async_playwright, TimeoutError
import logging
import time
import os
import random

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def get_telegram_api_credentials_automated(
    app_title: str = "ZeniApp",
    short_name: str = "zeni",
    platform_value: str = "desktop",
    description: str = "Test app created via automation."
):
    """
    Automates the process of obtaining api_id and api_hash from my.telegram.org.
    Requires interactive input of phone number and confirmation code.
    Args:
        app_title (str): Application title for Telegram app creation.
        short_name (str): Short name for the app.
        platform_value (str): Platform type (desktop, web, etc.).
        description (str): Description for the app.
    Returns:
        Tuple[str, str]: api_id and api_hash if successful, otherwise (None, None).
    """
    ERROR_SCREENSHOTS_DIR = "error_screenshots"
    os.makedirs(ERROR_SCREENSHOTS_DIR, exist_ok=True)
    browser = None
    page = None
    try:
        async with async_playwright() as p:
            logging.info("Launching Chromium browser in visible mode...")
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context(
                user_agent=random.choice([
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0"
                ])
            )
            page = await context.new_page()
            page.set_default_timeout(60000)
            phone_number = input("Введите номер телефона (в формате +1234567890): ").strip()
            if not phone_number.startswith('+') or not phone_number[1:].isdigit():
                raise ValueError("Номер телефона должен начинаться с '+' и содержать только цифры.")
            logging.info(f"Navigating to https://my.telegram.org")
            await page.goto("https://my.telegram.org", wait_until='domcontentloaded')
            await asyncio.sleep(random.uniform(1, 2))
            phone_input_selector = "#my_login_phone"
            try:
                await page.wait_for_selector(phone_input_selector, state='visible', timeout=15000)
                logging.info(f"Phone input selector found: '{phone_input_selector}'")
            except TimeoutError:
                raise TimeoutError("Phone input field not found.")
            await page.fill(phone_input_selector, phone_number)
            await asyncio.sleep(random.uniform(1, 2))
            submit_button_selector = "button[type='submit']"
            try:
                await page.click(submit_button_selector, timeout=10000)
            except TimeoutError:
                await page.click("button:has-text('Next') || button:has-text('Continue')", timeout=10000)
            logging.info("Phone number submitted. Waiting for code field.")
            await asyncio.sleep(random.uniform(2, 5))
            code_input_selector = "#my_password"
            try:
                await page.wait_for_selector(code_input_selector, state='visible', timeout=20000)
                logging.info(f"Code input selector found: '{code_input_selector}'")
            except TimeoutError:
                raise TimeoutError("Code input field not found after phone submission.")
            code = input("❗ Введите код подтверждения из Telegram: ").strip()
            logging.info("Code received. Submitting...")
            await page.fill(code_input_selector, code)
            await asyncio.sleep(random.uniform(1, 2))
            sign_in_button_selector = "button[type='submit']:has-text('Sign In')"
            try:
                await page.click(sign_in_button_selector, timeout=10000)
            except TimeoutError:
                raise TimeoutError("Could not click 'Sign In' after code input.")
            logging.info("Code submitted. Waiting for API development tools page.")
            api_tools_link_selector = "a[href='/apps']:has-text('API development tools')"
            try:
                await page.wait_for_selector(api_tools_link_selector, state='visible', timeout=20000)
                await page.click(api_tools_link_selector)
                logging.info("Clicked 'API development tools' link.")
                await page.wait_for_selector(
                    'text="API development tools" || button:has-text("Create new application") || input[name="app_id"] || h2:has-text("Create new application")',
                    timeout=30
                )
                await asyncio.sleep(random.uniform(0.15, 0.4))
            except TimeoutError:
                logging.warning("'API development tools' link not found. Trying to continue.")
                pass
            api_id = None
            api_hash = None
            if await page.is_visible('h2:has-text("Create new application")', timeout=5000) or \
                    await page.is_visible('#app_title', timeout=5000):
                logging.info("On new app creation page. Filling form.")
                logging.info(f"Filling new app form: App title='{app_title}', Short name='{short_name}', Platform='{platform_value}'")
                await page.fill("#app_title", app_title)
                await page.fill("#app_shortname", short_name)
                await page.click(f"input[type='radio'][name='app_platform'][value='{platform_value}']")
                await page.fill("#app_desc", description)
                await asyncio.sleep(random.uniform(1, 2.5))
                create_submit_button_selector = "#app_save_btn"
                await page.click(create_submit_button_selector)
                logging.info("App creation form submitted.")
                await asyncio.sleep(random.uniform(3, 5))
                try:
                    await page.wait_for_selector('button:has-text("подтвердить") || button:has-text("ok")', timeout=5000)
                    await page.click('button:has-text("подтвердить") || button:has-text("ok")')
                    logging.info("Confirmation button clicked.")
                except TimeoutError:
                    logging.info("Confirmation dialog not found. Continuing.")
                logging.info("Waiting for API ID and API Hash...")
                await page.wait_for_selector("input[name='app_id']", state='visible', timeout=20000)
                api_id = await page.locator("input[name='app_id']").input_value()
                api_hash = await page.locator("input[name='app_hash']").input_value()
                logging.info(f"New app created. API ID: {api_id}, API Hash: {api_hash}")
            else:
                logging.info("On 'API development tools' page. Looking for existing keys.")
                api_id_element = await page.query_selector("input[name='app_id']")
                api_hash_element = await page.query_selector("input[name='app_hash']")
                if api_id_element and await api_id_element.is_visible() and \
                        api_hash_element and await api_hash_element.is_visible():
                    api_id = await api_id_element.input_value()
                    api_hash = await api_hash_element.input_value()
                    logging.info(f"Existing API keys found: api_id='{api_id}', api_hash='{api_hash}'")
                else:
                    logging.info("No existing app found. Clicking 'Create new application'.")
                    create_app_button_selector = 'button:has-text("Create new application")'
                    await page.wait_for_selector(create_app_button_selector, state='visible', timeout=10000)
                    await page.click(create_app_button_selector)
                    logging.info("Clicked 'Create new application'.")
                    logging.info("Waiting for new app creation form...")
                    await page.wait_for_selector("#app_title", state='visible', timeout=20000)
                    await asyncio.sleep(random.uniform(1.5, 3))
                    logging.info(f"Filling new app form: App title='{app_title}', Short name='{short_name}', Platform='{platform_value}'")
                    await page.fill("#app_title", app_title)
                    await page.fill("#app_shortname", short_name)
                    await page.click(f"input[type='radio'][name='app_platform'][value='{platform_value}']")
                    await page.fill("#app_desc", description)
                    await asyncio.sleep(random.uniform(1, 2.5))
                    create_submit_button_selector = "#app_save_btn"
                    await page.click(create_submit_button_selector)
                    logging.info("App creation form submitted.")
                    await asyncio.sleep(random.uniform(3, 5))
                    try:
                        await page.wait_for_selector('button:has-text("подтвердить") || button:has-text("ok")', timeout=5000)
                        await page.click('button:has-text("подтвердить") || button:has-text("ok")')
                        logging.info("Confirmation button clicked.")
                    except TimeoutError:
                        logging.info("Confirmation dialog not found. Continuing.")
                    logging.info("Waiting for API ID and API Hash...")
                    await page.wait_for_selector("input[name='app_id']", state='visible', timeout=20000)
                    api_id = await page.locator("input[name='app_id']").input_value()
                    api_hash = await page.locator("input[name='app_hash']").input_value()
                    logging.info(f"New app created. API ID: {api_id}, API Hash: {api_hash}")
            print(f"\n--- Results for your account ---")
            print(f"API ID: {api_id}")
            print(f"API Hash: {api_hash}")
            print(f"--------------------------------------")
            return api_id, api_hash
    except TimeoutError as e:
        logging.error(f"Timeout error: {e}")
        if page:
            screenshot_path = os.path.join(ERROR_SCREENSHOTS_DIR, f"timeout_error_{int(time.time())}.png")
            await page.screenshot(path=screenshot_path)
            logging.error(f"Error screenshot saved: {screenshot_path}")
        return None, None
    except ValueError as e:
        logging.error(f"Input error: {e}")
        return None, None
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        if page:
            screenshot_path = os.path.join(ERROR_SCREENSHOTS_DIR, f"general_error_{int(time.time())}.png")
            await page.screenshot(path=screenshot_path)
            logging.error(f"Error screenshot saved: {screenshot_path}")
        return None, None
    finally:
        if browser:
            logging.info("Closing browser.")
            await browser.close()

if __name__ == "__main__":
    asyncio.run(get_telegram_api_credentials_automated())
