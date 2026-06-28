from playwright.sync_api import sync_playwright
import os
import time

def verify():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        # Test Mobile View
        mobile_page = browser.new_page(viewport={'width': 375, 'height': 812}, is_mobile=True)
        file_path = f"file://{os.getcwd()}/money-maker-ui/index.html"
        mobile_page.goto(file_path)
        time.sleep(2)

        # Check .input-container-mobile position
        input_container = mobile_page.query_selector(".input-container-mobile")
        if input_container:
            box = input_container.bounding_box()
            style = input_container.evaluate("el => getComputedStyle(el).position")
            bottom = input_container.evaluate("el => getComputedStyle(el).bottom")
            print(f"Input Container Mobile: position={style}, bottom={bottom}, box={box}")

        # Check .mobile-nav position
        mobile_nav = mobile_page.query_selector(".mobile-nav")
        if mobile_nav:
            box = mobile_nav.bounding_box()
            style = mobile_nav.evaluate("el => getComputedStyle(el).position")
            bottom = mobile_nav.evaluate("el => getComputedStyle(el).bottom")
            print(f"Mobile Nav: position={style}, bottom={bottom}, box={box}")

        mobile_page.screenshot(path="ui_mobile_verification.png")
        print("Mobile verification screenshot captured.")

        browser.close()

if __name__ == "__main__":
    verify()
