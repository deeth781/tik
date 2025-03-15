from flask import Flask, render_template, request, jsonify
import json
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def get_tiktok_links(keyword, max_videos):
    driver = get_driver()
    url = f"https://www.tiktok.com/search?q={keyword.replace(' ', '%20')}"
    driver.get(url)

    time.sleep(5)  # Đợi TikTok tải trang

    links = set()
    video_count = 0

    while video_count < max_videos:
        videos = driver.find_elements(By.TAG_NAME, "a")
        
        for video in videos:
            href = video.get_attribute("href")
            if "/video/" in href and href not in links:
                links.add(href)
                video_count += 1
                if video_count >= max_videos:
                    break

        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
        time.sleep(2)

    driver.quit()
    return list(links)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        keyword = request.form.get('keyword')
        max_videos = int(request.form.get('max_videos'))
        links = get_tiktok_links(keyword, max_videos)
        return render_template('index.html', links=links)
    return render_template('index.html', links=None)

if __name__ == '__main__':
    app.run(debug=True)

# Tạo file index.html
template_html = """<!DOCTYPE html>
<html lang='vi'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>TikTok Scraper</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            background: linear-gradient(135deg, #667eea, #764ba2);
            padding: 20px;
            color: white;
        }
        h1 {
            font-size: 2em;
            margin-bottom: 20px;
        }
        form {
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
            display: inline-block;
            text-align: left;
            max-width: 400px;
            width: 100%;
            color: black;
        }
        input, button {
            margin: 10px 0;
            padding: 12px;
            width: calc(100% - 24px);
            border-radius: 6px;
            border: 1px solid #ccc;
            font-size: 1em;
        }
        button {
            background-color: #ff4081;
            color: white;
            border: none;
            cursor: pointer;
            transition: background 0.3s;
            font-weight: bold;
        }
        button:hover {
            background-color: #e60073;
        }
        .results {
            margin-top: 20px;
            text-align: left;
            display: inline-block;
            max-width: 500px;
            width: 100%;
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
            color: black;
        }
        ul {
            list-style: none;
            padding: 0;
        }
        li {
            margin: 5px 0;
        }
        a {
            text-decoration: none;
            color: #007bff;
            font-weight: bold;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>Tìm kiếm video TikTok</h1>
    <form method='post'>
        <label for='keyword'>Từ khóa:</label>
        <input type='text' name='keyword' required>
        <label for='max_videos'>Số lượng video:</label>
        <input type='number' name='max_videos' min='1' required>
        <button type='submit'>Tìm kiếm</button>
    </form>
    {% if links %}
    <div class='results'>
        <h2>Kết quả tìm kiếm:</h2>
        <ul>
            {% for link in links %}
            <li><a href='{{ link }}' target='_blank'>{{ link }}</a></li>
            {% endfor %}
        </ul>
    </div>
    {% endif %}
</body>
</html>"""

with open('templates/index.html', 'w', encoding='utf-8') as f:
    f.write(template_html)
