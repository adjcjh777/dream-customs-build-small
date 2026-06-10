#!/usr/bin/env python3
"""Smoke test: submit dream, answer question, verify result."""
import asyncio
from playwright.async_api import async_playwright


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1280, "height": 900})
        await page.goto("http://127.0.0.1:7863", timeout=10000)
        await asyncio.sleep(3)

        # Step 1: Type dream
        textarea = page.locator("textarea").first
        await textarea.fill("我梦到在一栋老楼里，电梯按钮融化了，按下去黏黏的。醒来有点焦虑。")
        await asyncio.sleep(0.5)
        await page.screenshot(path="dream-qa-smoke-01-record.png", full_page=False)

        # Step 2: Click Continue/Send
        send_btn = page.locator("button:has-text('发送')").first
        await send_btn.click()
        await asyncio.sleep(5)  # Wait for processing
        await page.screenshot(path="dream-qa-smoke-02-ask.png", full_page=False)

        # Step 3: Answer or skip the question
        skip_btn = page.locator("button:has-text('先跳过')")
        if await skip_btn.count() > 0:
            await skip_btn.click()
            await asyncio.sleep(5)
        await page.screenshot(path="dream-qa-smoke-03-result.png", full_page=False)

        # Step 4: Full page screenshot
        await page.screenshot(path="dream-qa-smoke-04-full.png", full_page=True)

        await browser.close()
        print("Smoke screenshots saved!")


if __name__ == "__main__":
    asyncio.run(main())
