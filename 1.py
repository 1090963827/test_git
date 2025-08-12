import os
import time
from random import random

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin


class WallpaperDownloader:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://bizhi1.com/'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def get_high_resolution_url(self, url):
        """智能获取高分辨率图片地址"""
        # 尝试去除small后缀
        if '-small.jpg' in url:
            return url.replace('-small.jpg', '.jpg')
        # 尝试调整尺寸参数
        if '7680x4320' in url:
            return url.replace('7680x4320', '8192x4608')
        return url

    def parse_page(self, url):
        """解析页面获取图片数据"""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            articles = soup.find_all('article', class_='post-item')
            if not articles:
                print("未找到文章列表，可能页面结构已变化")
                return []

            image_data = []
            for article in articles:
                try:
                    img_tag = article.find('img', class_='attachment-post-thumbnail')
                    if not img_tag:
                        continue

                    img_url = img_tag.get('src')
                    if not img_url:
                        continue

                    # 获取高分辨率版本
                    high_res_url = self.get_high_resolution_url(img_url)

                    # 获取图片信息
                    title = article.find('a', class_='post-title').text.strip()
                    resolution = f"{img_tag.get('width', '')}x{img_tag.get('height', '')}"

                    image_data.append({
                        'title': title,
                        'url': high_res_url,
                        'resolution': resolution
                    })
                except Exception as e:
                    print(f"解析文章出错: {str(e)}")
                    continue

            return image_data
        except Exception as e:
            print(f"解析页面失败: {str(e)}")
            return []

    def download_image(self, item, save_dir='wallpapers'):
        """下载单个图片"""
        os.makedirs(save_dir, exist_ok=True)

        # 生成安全文件名
        safe_title = "".join([c if c.isalnum() else '_' for c in item['title']])
        filename = f"{safe_title}_{item['resolution']}.jpg"
        filepath = os.path.join(save_dir, filename)

        # 跳过已下载文件
        if os.path.exists(filepath):
            print(f"文件已存在: {filename}")
            return True

        try:
            response = self.session.get(item['url'], stream=True, timeout=20)
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            print(f"成功下载: {filename}")
            return True
        except Exception as e:
            print(f"下载失败: {filename} - {str(e)}")
            return False

    def crawl(self, start_url, delay=2.5):
        """执行爬取流程"""
        print(f"开始解析页面: {start_url}")
        images = self.parse_page(start_url)

        if not images:
            print("未找到可下载的图片")
            return

        print(f"发现 {len(images)} 张图片")

        success = 0
        for idx, img in enumerate(images, 1):
            print(f"正在下载第 {idx}/{len(images)} 张: {img['title']}")
            if self.download_image(img):
                success += 1
            time.sleep(delay + abs(random.gauss(0, 0.5)))  # 随机延迟

        print(f"下载完成，成功 {success}/{len(images)} 张")


if __name__ == '__main__':
    # 使用示例
    downloader = WallpaperDownloader()

    # 多页示例（修改page参数）
    base_url = "https://bizhi1.com/item?a3=129&page={}"

    # 爬取前3页
    for page in range(1, 4):
        current_url = base_url.format(page)
        downloader.crawl(current_url)

        # 随机间隔防止封禁
        time.sleep(10 + random.randint(3, 8))
