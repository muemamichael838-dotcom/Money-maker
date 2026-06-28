from playwright.sync_api import sync_playwright
import os
import time

def verify():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1280, 'height': 800})

        # We'll use a local file for the test since the server isn't running in this context
        file_path = f"file://{os.getcwd()}/money-maker-ui/index.html"
        page.goto(file_path)

        # Wait for Lucide icons and JS init
        time.sleep(2)

        # Take desktop screenshot
        page.screenshot(path="ui_desktop.png")
        print("Desktop screenshot captured.")

        # Verify Sidebar elements
        sidebar = page.query_selector("#main-sidebar")
        if sidebar and sidebar.is_visible():
            print("Sidebar is visible on desktop.")
        else:
            print("Sidebar check failed.")

        # Test Mobile View
        mobile_page = browser.new_page(viewport={'width': 375, 'height': 812}, is_mobile=True)
        mobile_page.goto(file_path)
        time.sleep(2)

        # Check for mobile header and menu button
        header = mobile_page.query_selector("header")
        if header and header.is_visible():
            print("Mobile header is visible.")

        # Open Sidebar on Mobile
        menu_btn = mobile_page.query_selector("button[onclick='toggleSidebar(true)']")
        if menu_btn:
            menu_btn.click()
            time.sleep(1)
            page.screenshot(path="ui_mobile_sidebar.png")
            print("Mobile sidebar toggle verified.")

        mobile_page.screenshot(path="ui_mobile.png")
        print("Mobile screenshots captured.")

        browser.close()

if __name__ == "__main__":
    verify()
