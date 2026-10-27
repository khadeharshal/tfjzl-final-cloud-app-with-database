import time
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()

        # 1. Admin site screenshot
        print("1. Capturing 03-admin-site.png...")
        page.goto("http://127.0.0.1:8000/admin/")
        page.fill('input[name="username"]', 'admin')
        page.fill('input[name="password"]', 'p@ssword123')
        page.click('input[type="submit"]')
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        page.screenshot(path="ss/03-admin-site.png")
        print("Saved ss/03-admin-site.png")

        # 2. Course details screenshot (optional extra for Task 3/4)
        print("2. Capturing 04-course-details.png...")
        page.goto("http://127.0.0.1:8000/onlinecourse/2/")
        page.wait_for_load_state("networkidle")
        time.sleep(1)
        page.locator('button:has-text("Start Exam")').click()
        time.sleep(1)
        page.screenshot(path="ss/04-course-details.png")
        print("Saved ss/04-course-details.png")

        # 3. Exam submission & Result screenshot
        print("3. Selecting answer and submitting exam...")
        yes_checkbox = page.locator('label:has-text("Yes") input[type="checkbox"]').first
        yes_checkbox.check()
        time.sleep(1)

        page.locator('input[type="submit"][value="Submit"]').click()
        page.wait_for_load_state("networkidle")
        time.sleep(2)

        page.screenshot(path="ss/07-final.png")
        print("Saved ss/07-final.png")

        browser.close()
        print("All screenshots generated successfully in ss/ folder!")

if __name__ == "__main__":
    main()
