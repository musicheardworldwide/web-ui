import pdb
import pyperclip
import json
from typing import Optional, Type
from pydantic import BaseModel
from browser_use.agent.views import ActionResult
from browser_use.browser.context import BrowserContext
from browser_use.controller.service import Controller, DoneAction
from main_content_extractor import MainContentExtractor
from browser_use.controller.views import (
    ClickElementAction,
    DoneAction,
    ExtractPageContentAction,
    GoToUrlAction,
    InputTextAction,
    OpenTabAction,
    ScrollAction,
    SearchGoogleAction,
    SendKeysAction,
    SwitchTabAction,
)
import logging

logger = logging.getLogger(__name__)


class CustomController(Controller):
    def __init__(self, exclude_actions: list[str] = [], output_model: Optional[Type[BaseModel]] = None):
        super().__init__(exclude_actions=exclude_actions, output_model=output_model)
        self._register_custom_actions()

    def _register_custom_actions(self):
        """Register all custom browser actions"""

        # Existing actions
        @self.registry.action("Copy text to clipboard")
        def copy_to_clipboard(text: str):
            pyperclip.copy(text)
            return ActionResult(extracted_content=text)

        @self.registry.action("Paste text from clipboard")
        async def paste_from_clipboard(browser: BrowserContext):
            text = pyperclip.paste()
            page = await browser.get_current_page()
            await page.keyboard.type(text)
            return ActionResult(extracted_content=text)

        @self.registry.action("Take Screenshot")
        async def take_screenshot(browser: BrowserContext):
            page = await browser.get_current_page()
            screenshot = await page.screenshot()  # gets screenshot as bytes
            import base64
            screenshot_base64 = base64.b64encode(screenshot).decode("utf-8")
            return ActionResult(extracted_content="data:image/png;base64," + screenshot_base64)

        @self.registry.action("Extract Main Content")
        async def extract_main_content(browser: BrowserContext):
            page = await browser.get_current_page()
            html = await page.content()
            extractor = MainContentExtractor()
            main_content = extractor.extract(html)
            return ActionResult(extracted_content=main_content)

        @self.registry.action("Wait for Element")
        async def wait_for_element(browser: BrowserContext, selector: str, timeout: int = 5000):
            page = await browser.get_current_page()
            try:
                await page.wait_for_selector(selector, timeout=timeout)
                return ActionResult(extracted_content=f"Element '{selector}' found")
            except Exception as e:
                return ActionResult(error=str(e))

        @self.registry.action("Execute JavaScript")
        async def execute_js(browser: BrowserContext, script: str):
            page = await browser.get_current_page()
            result = await page.evaluate(script)
            return ActionResult(extracted_content=str(result))

        @self.registry.action("Scroll to Element")
        async def scroll_to_element(browser: BrowserContext, selector: str):
            page = await browser.get_current_page()
            try:
                await page.evaluate(f'document.querySelector("{selector}").scrollIntoView()')
                return ActionResult(extracted_content=f"Scrolled to element '{selector}'")
            except Exception as e:
                return ActionResult(error=str(e))

        @self.registry.action("Close Tab")
        async def close_tab(browser: BrowserContext):
            page = await browser.get_current_page()
            await page.close()
            return ActionResult(extracted_content="Tab closed")

        @self.registry.action("Log Page URL")
        async def log_page_url(browser: BrowserContext):
            page = await browser.get_current_page()
            url = page.url
            logger.info(f"Current page URL: {url}")
            return ActionResult(extracted_content=f"Logged URL: {url}")

        @self.registry.action("Open New Tab")
        async def open_new_tab(browser: BrowserContext, url: str):
            new_page = await browser.browser.new_page()
            await new_page.goto(url)
            return ActionResult(extracted_content=f"Opened new tab with URL: {url}")

        @self.registry.action("Click Element")
        async def click_element(browser: BrowserContext, selector: str):
            page = await browser.get_current_page()
            try:
                await page.click(selector)
                return ActionResult(extracted_content=f"Clicked element with selector: {selector}")
            except Exception as e:
                return ActionResult(error=str(e))

        @self.registry.action("Input Text")
        async def input_text(browser: BrowserContext, selector: str, text: str):
            page = await browser.get_current_page()
            try:
                await page.fill(selector, text)
                return ActionResult(extracted_content=f"Input text into element {selector}")
            except Exception as e:
                return ActionResult(error=str(e))

        @self.registry.action("Refresh Page")
        async def refresh_page(browser: BrowserContext):
            page = await browser.get_current_page()
            try:
                await page.reload()
                return ActionResult(extracted_content="Page refreshed")
            except Exception as e:
                return ActionResult(error=str(e))

        @self.registry.action("Hover Over Element")
        async def hover_over_element(browser: BrowserContext, selector: str):
            page = await browser.get_current_page()
            try:
                await page.hover(selector)
                return ActionResult(extracted_content=f"Hovered over element: {selector}")
            except Exception as e:
                return ActionResult(error=str(e))

        @self.registry.action("Get Cookies")
        async def get_cookies(browser: BrowserContext):
            page = await browser.get_current_page()
            try:
                cookies = await page.context.cookies()
                return ActionResult(extracted_content=str(cookies))
            except Exception as e:
                return ActionResult(error=str(e))

        @self.registry.action("Set Cookies")
        async def set_cookies(browser: BrowserContext, cookies: str):
            page = await browser.get_current_page()
            try:
                cookies_list = json.loads(cookies)
                await page.context.add_cookies(cookies_list)
                return ActionResult(extracted_content="Cookies set")
            except Exception as e:
                return ActionResult(error=str(e))

        @self.registry.action("Download File")
        async def download_file(browser: BrowserContext, url: str, download_path: Optional[str] = None):
            page = await browser.get_current_page()
            try:
                async with page.expect_download() as download_info:
                    await page.goto(url)
                download = await download_info.value
                if download_path:
                    await download.save_as(download_path)
                    return ActionResult(extracted_content=f"Downloaded file saved to {download_path}")
                return ActionResult(extracted_content="File downloaded")
            except Exception as e:
                return ActionResult(error=str(e))

        @self.registry.action("Wait for Navigation")
        async def wait_for_navigation(browser: BrowserContext, timeout: int = 10000):
            page = await browser.get_current_page()
            try:
                await page.wait_for_navigation(timeout=timeout)
                return ActionResult(extracted_content="Navigation completed")
            except Exception as e:
                return ActionResult(error=str(e))

        # --- Advanced Navigation and Interaction ---
        @self.registry.action("Scroll to Bottom of Page")
        async def scroll_to_bottom(browser: BrowserContext):
            page = await browser.get_current_page()
            try:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                return ActionResult(extracted_content="Scrolled to the bottom of the page")
            except Exception as e:
                return ActionResult(error=str(e))

        @self.registry.action("Scroll to Top of Page")
        async def scroll_to_top(browser: BrowserContext):
            page = await browser.get_current_page()
            try:
                await page.evaluate("window.scrollTo(0, 0)")
                return ActionResult(extracted_content="Scrolled to the top of the page")
            except Exception as e:
                return ActionResult(error=str(e))

        @self.registry.action("Simulate Mouse Movement")
        async def simulate_mouse_movement(browser: BrowserContext, x: int, y: int):
            page = await browser.get_current_page()
            try:
                await page.mouse.move(x, y)
                return ActionResult(extracted_content=f"Mouse moved to coordinates ({x}, {y})")
            except Exception as e:
                return ActionResult(error=str(e))

        # --- Data Extraction and Analysis ---
        @self.registry.action("Extract All Links")
        async def extract_all_links(browser: BrowserContext):
            page = await browser.get_current_page()
            try:
                links = await page.evaluate(
                    '''() => {
                        return Array.from(document.querySelectorAll('a')).map(a => a.href);
                    }'''
                )
                return ActionResult(extracted_content=json.dumps(links))
            except Exception as e:
                return ActionResult(error=str(e))

        @self.registry.action("Extract All Images")
        async def extract_all_images(browser: BrowserContext):
            page = await browser.get_current_page()
            try:
                images = await page.evaluate(
                    '''() => {
                        return Array.from(document.querySelectorAll('img')).map(img => img.src);
                    }'''
                )
                return ActionResult(extracted_content=json.dumps(images))
            except Exception as e:
                return ActionResult(error=str(e))

        @self.registry.action("Extract Table Data")
        async def extract_table_data(browser: BrowserContext, selector: str):
            page = await browser.get_current_page()
            try:
                table_data = await page.evaluate(
                    f'''() => {{
                        const rows = Array.from(document.querySelectorAll('{selector} tr'));
                        return rows.map(row => {{
                            const cells = Array.from(row.querySelectorAll('th, td'));
                            return cells.map(cell => cell.innerText);
                        }});
                    }}'''
                )
                return ActionResult(extracted_content=json.dumps(table_data))
            except Exception as e:
                return ActionResult(error=str(e))

        # --- Advanced Automation ---
        @self.registry.action("Fill and Submit Form")
        async def fill_and_submit_form(browser: BrowserContext, form_selector: str, data: str):
            page = await browser.get_current_page()
            try:
                data_dict = json.loads(data)
                for field, value in data_dict.items():
                    await page.fill(f'{form_selector} [name="{field}"]', value)
                await page.click(f'{form_selector} [type="submit"]')
                return ActionResult(extracted_content="Form filled and submitted")
            except Exception as e:
                return ActionResult(error=str(e))

        @self.registry.action("Handle Popup")
        async def handle_popup(browser: BrowserContext, action: str = "accept"):
            page = await browser.get_current_page()
            try:
                if action == "accept":
                    page.on("dialog", lambda dialog: dialog.accept())
                elif action == "dismiss":
                    page.on("dialog", lambda dialog: dialog.dismiss())
                return ActionResult(extracted_content=f"Popup handled: {action}")
            except Exception as e:
                return ActionResult(error=str(e))

        @self.registry.action("Switch to Iframe")
        async def switch_to_iframe(browser: BrowserContext, iframe_selector: str):
            page = await browser.get_current_page()
            try:
                iframe = await page.query_selector(iframe_selector)
                if iframe:
                    await iframe.content_frame()
                    return ActionResult(extracted_content=f"Switched to iframe: {iframe_selector}")
                else:
                    return ActionResult(error="Iframe not found")
            except Exception as e:
                return ActionResult(error=str(e))

        # --- Debugging and Monitoring ---
        @self.registry.action("Log Console Output")
        async def log_console_output(browser: BrowserContext):
            page = await browser.get_current_page()
            try:
                page.on("console", lambda msg: logger.info(f"Console: {msg.text}"))
                return ActionResult(extracted_content="Console logging enabled")
            except Exception as e:
                return ActionResult(error=str(e))

        @self.registry.action("Capture Network Requests")
        async def capture_network_requests(browser: BrowserContext):
            page = await browser.get_current_page()
            try:
                requests = []
                page.on("request", lambda req: requests.append(req.url))
                return ActionResult(extracted_content=json.dumps(requests))
            except Exception as e:
                return ActionResult(error=str(e))

        # --- Utility Actions ---
        @self.registry.action("Clear Browser Cache")
        async def clear_browser_cache(browser: BrowserContext):
            page = await browser.get_current_page()
            try:
                await page.context.clear_cache()
                return ActionResult(extracted_content="Browser cache cleared")
            except Exception as e:
                return ActionResult(error=str(e))

        @self.registry.action("Take Full-Page Screenshot")
        async def take_full_page_screenshot(browser: BrowserContext):
            page = await browser.get_current_page()
            try:
                screenshot = await page.screenshot(full_page=True)
                import base64
                screenshot_base64 = base64.b64encode(screenshot).decode("utf-8")
                return ActionResult(extracted_content="data:image/png;base64," + screenshot_base64)
            except Exception as e:
                return ActionResult(error=str(e))

        # --- Integration with External APIs ---
        @self.registry.action("Call External API")
        async def call_external_api(browser: BrowserContext, url: str, method: str = "GET", data: Optional[str] = None):
            try:
                import aiohttp
                async with aiohttp.ClientSession() as session:
                    if method == "GET":
                        async with session.get(url) as response:
                            result = await response.text()
                    elif method == "POST":
                        async with session.post(url, json=json.loads(data)) as response:
                            result = await response.text()
                    return ActionResult(extracted_content=result)
            except Exception as e:
                return ActionResult(error=str(e))

        # --- Error Handling and Recovery ---
        @self.registry.action("Retry Failed Action")
        async def retry_failed_action(browser: BrowserContext, action_name: str, max_retries: int = 3):
            for _ in range(max_retries):
                try:
                    result = await self.registry.execute_action(action_name, browser)
                    return result
                except Exception as e:
                    logger.warning(f"Retry {_ + 1} failed: {e}")
            return ActionResult(error=f"Action '{action_name}' failed after {max_retries} retries")
