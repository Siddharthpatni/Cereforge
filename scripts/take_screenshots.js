const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        viewport: { width: 1280, height: 800 },
        colorScheme: 'dark' // If the app supports dark mode
    });
    const page = await context.newPage();
    page.on('response', response => console.log('<<', response.status(), response.url()));

    console.log('Navigating to auth page...');
    await page.goto('http://localhost:5173/auth');
    await page.waitForLoadState('networkidle');
    // wait 1s for any anims
    await page.waitForTimeout(1000);

    await page.screenshot({ path: path.join(__dirname, '../docs/screenshots/auth.png') });
    console.log('Registering user via API...');
    const registerResponse = await fetch('http://localhost:8000/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            username: `user_${Date.now()}`,
            email: `user_${Date.now()}@example.com`,
            password: 'StrongPassword123!',
            skill_level: 'some_python',
            background: 'Playwright Setup'
        })
    });
    const authData = await registerResponse.json();

    console.log('Injecting auth state into localStorage...');
    await page.goto('http://localhost:5173/');
    await page.evaluate((data) => {
        localStorage.setItem('auth-storage', JSON.stringify({
            state: {
                isAuthenticated: true,
                user: data.user,
                token: data.access_token
            },
            version: 0
        }));
    }, authData);

    console.log('Navigating to dashboard...');
    await page.goto('http://localhost:5173/');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000); // let dashboard data load fully

    await page.screenshot({ path: path.join(__dirname, '../docs/screenshots/dashboard.png') });
    console.log('Saved dashboard.png');

    console.log('Navigating to tasks list...');
    await page.goto('http://localhost:5173/tasks');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000); // let tasks list render

    await page.screenshot({ path: path.join(__dirname, '../docs/screenshots/tasks.png') });
    console.log('Saved tasks.png');

    console.log('Navigating to community post...');
    await page.goto('http://localhost:5173/community');
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);

    // Click the first post in the list, assuming there is one from seed data
    // Or fallback by directly navigating if the link structure is known. But clicking is safer.
    const firstPost = await page.$('.post-card, a[href^="/community/"]');
    if (firstPost) {
        await firstPost.click();
        await page.waitForLoadState('networkidle');
        await page.waitForTimeout(2000);
    } else {
        console.log('No posts found to click, capturing empty community page instead.');
    }

    await page.screenshot({ path: path.join(__dirname, '../docs/screenshots/post.png') });
    console.log('Saved post.png');

    await browser.close();
    console.log('All screenshots taken successfully!');
})();
