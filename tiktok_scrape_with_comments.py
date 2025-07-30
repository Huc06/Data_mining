import os
import time
import pandas as pd
from playwright.sync_api import sync_playwright
import yt_dlp

HASHTAG = "laptop"
LIMIT = 5
OUTPUT_DIR = "tiktok_data"

# Tạo thư mục lưu
os.makedirs(f"{OUTPUT_DIR}/videos", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/captions", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/comments", exist_ok=True)

metadata = []

def download_video(url):
    try:
        ydl_opts = {
            'outtmpl': f'{OUTPUT_DIR}/videos/%(id)s.%(ext)s',
            'quiet': True,
            'skip_download': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return {
                "id": info.get("id"),
                "caption": info.get("description"),
                "path": f"{OUTPUT_DIR}/videos/{info.get('id')}.mp4"
            }
    except Exception as e:
        print(f"[❌] Download error: {e}")
        return None

def extract_video_metrics(page):
    """Extract like count, share count, and other metrics from TikTok video page using actual selectors"""
    metrics = {
        "likes": 0,
        "shares": 0,
        "comments_count": 0
    }
    
    try:
        print("🔍 Đang tìm metrics trên trang...")
        time.sleep(3)  # Wait for page to load
        
        # Like count - selector từ HTML thực tế
        try:
            like_element = page.locator('[data-e2e="browse-like-count"]').first
            if like_element.is_visible():
                like_text = like_element.inner_text().strip()
                metrics["likes"] = parse_count(like_text)
                print(f"👍 Likes: {like_text} -> {metrics['likes']}")
        except Exception as e:
            print(f"⚠️ Không tìm thấy like count: {e}")
        
        # Comment count - selector từ HTML thực tế  
        try:
            comment_element = page.locator('[data-e2e="browse-comment-count"]').first
            if comment_element.is_visible():
                comment_text = comment_element.inner_text().strip()
                metrics["comments_count"] = parse_count(comment_text)
                print(f"💬 Comments: {comment_text} -> {metrics['comments_count']}")
        except Exception as e:
            print(f"⚠️ Không tìm thấy comment count: {e}")
        
        # Share count - selector từ HTML thực tế (undefined-count)
        try:
            share_element = page.locator('[data-e2e="undefined-count"]').first
            if share_element.is_visible():
                share_text = share_element.inner_text().strip()
                metrics["shares"] = parse_count(share_text)
                print(f"📤 Shares: {share_text} -> {metrics['shares']}")
        except Exception as e:
            print(f"⚠️ Không tìm thấy share count: {e}")
                
    except Exception as e:
        print(f"❌ Lỗi khi extract metrics: {e}")
    
    return metrics

def parse_count(count_text):
    """Convert count text like '1.2K', '500', '2.5M' to numbers"""
    if not count_text:
        return 0
        
    count_text = count_text.upper().replace(',', '').strip()
    
    try:
        if 'K' in count_text:
            return int(float(count_text.replace('K', '')) * 1000)
        elif 'M' in count_text:
            return int(float(count_text.replace('M', '')) * 1000000)
        elif 'B' in count_text:
            return int(float(count_text.replace('B', '')) * 1000000000)
        else:
            return int(count_text)
    except:
        return 0

def scrape_with_playwright():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Show browser window
        page = browser.new_page()
        
        print(f"🔍 Đang truy cập TikTok hashtag: {HASHTAG}")
        page.goto(f"https://www.tiktok.com/tag/{HASHTAG}", timeout=60000)
        time.sleep(5)

        print("🌐 Đã tải trang, đang tìm video links...")
        video_links = set()
        for scroll_attempt in range(10):
            print(f"📜 Cuộn trang lần {scroll_attempt + 1}/10...")
            page.mouse.wheel(0, 5000)
            time.sleep(3)
            links = page.locator("a").all()
            print(f"🔗 Tìm thấy {len(links)} links trên trang")
            
            for link in links:
                href = link.get_attribute("href")
                if href:
                    print(f"🔗 Link tìm thấy: {href}")
                if href and "/video/" in href:
                    video_links.add(href)
                    print(f"✅ Tìm thấy video link: {href}")
            
            print(f"📊 Tổng cộng đã tìm thấy {len(video_links)} video links")
            if len(video_links) >= LIMIT:
                break

        print(f"🎯 Sẽ xử lý {min(len(video_links), LIMIT)} videos")
        selected_links = list(video_links)[:LIMIT]

        if not selected_links:
            print("❌ Không tìm thấy video nào! Có thể:")
            print("  - Hashtag không tồn tại")  
            print("  - TikTok đang chặn truy cập")
            print("  - Cần đăng nhập")
            print("🔍 Đang lưu screenshot để debug...")
            page.screenshot(path="debug_tiktok_page.png")
            browser.close()
            return

        for i, link in enumerate(selected_links, 1):
            print(f"\n▶️ [{i}/{len(selected_links)}] Đang xử lý video: {link}")
            video_info = download_video(link)
            if not video_info:
                print(f"❌ Không thể tải video {link}")
                continue

            video_id = video_info["id"]
            caption = video_info["caption"]
            print(f"📝 Video ID: {video_id}")
            print(f"📄 Caption: {caption[:100]}..." if len(caption) > 100 else f"📄 Caption: {caption}")

            # Lưu caption
            with open(f"{OUTPUT_DIR}/captions/{video_id}.txt", "w", encoding="utf-8") as f:
                f.write(caption)
            print(f"💾 Đã lưu caption vào {OUTPUT_DIR}/captions/{video_id}.txt")

            # Đi đến trang video để lấy metrics và comments
            print(f"📊 Đang truy cập trang video để lấy metrics và comments...")
            page.goto(link, timeout=60000)
            time.sleep(5)
            
            # Extract video metrics (likes, shares, etc.) với selector thực tế
            print(f"📈 Đang extract likes, shares...")
            metrics = extract_video_metrics(page)
            
            # Lấy comment với selector được cập nhật
            print(f"💬 Đang lấy comments cho video {video_id}...")
            comments_data = []

            for scroll in range(10):  # cố gắng cuộn comment
                print(f"📜 Cuộn comments lần {scroll + 1}/10...")
                page.mouse.wheel(0, 2000)
                time.sleep(1)

            # Thử nhiều selector cho comments
            comment_blocks = []
            comment_selectors = [
                '[data-e2e="comment-item-list"] div[data-e2e="comment-item"]',
                '[data-e2e="comment-level-1"]',
                '.comment-item'
            ]
            
            for selector in comment_selectors:
                try:
                    blocks = page.locator(selector).all()
                    if blocks:
                        comment_blocks = blocks
                        print(f"🔍 Tìm thấy {len(comment_blocks)} comment blocks với selector: {selector}")
                        break
                except:
                    continue
            
            print(f"🔄 Đang xử lý {min(len(comment_blocks), 15)} comments...")
            for i, c in enumerate(comment_blocks[:15]):  # Giảm xuống 15 để tránh timeout
                if i % 5 == 0:  # Progress indicator
                    print(f"📝 Đã xử lý {i}/{min(len(comment_blocks), 15)} comments...")
                    
                try:
                    # Optimize selector - sử dụng selector đã biết từ HTML thực tế
                    text = ""
                    user = ""
                    
                    # Thử lấy text trực tiếp từ comment block
                    try:
                        # Selector từ HTML thực tế bạn cung cấp
                        text = c.inner_text().strip()
                        if text and len(text) > 5:  # Skip quá ngắn
                            # Tách user và content nếu có thể
                            if ":" in text:
                                parts = text.split(":", 1)
                                if len(parts) == 2:
                                    user = parts[0].strip()
                                    text = parts[1].strip()
                            
                            if user:
                                comments_data.append(f"{user}: {text}")
                                print(f"💬 {user}: {text[:30]}...")
                            else:
                                comments_data.append(text)
                                print(f"💬 {text[:50]}...")
                    except:
                        continue
                        
                except Exception as e:
                    continue
                    
            print(f"✅ Hoàn thành xử lý comments: {len(comments_data)} comments")

            # Lưu comment
            comment_file = f"{OUTPUT_DIR}/comments/{video_id}.txt"
            with open(comment_file, "w", encoding="utf-8") as f:
                f.write("\n".join(comments_data))
            print(f"💾 Đã lưu {len(comments_data)} comments vào {comment_file}")

            # Lưu metadata với metrics mới
            metadata.append({
                "id": video_id,
                "url": link,
                "caption": caption,
                "video_path": video_info["path"],
                "caption_path": f"{OUTPUT_DIR}/captions/{video_id}.txt",
                "comment_path": comment_file,
                "n_comments": len(comments_data),
                "likes": metrics.get("likes", 0),
                "shares": metrics.get("shares", 0),
                "comments_count_from_page": metrics.get("comments_count", 0)
            })
            print(f"✅ Hoàn thành xử lý video {i}/{len(selected_links)}")

        browser.close()

# Thực thi
scrape_with_playwright()
df = pd.DataFrame(metadata)
df.to_csv(f"{OUTPUT_DIR}/metadata.csv", index=False, encoding="utf-8")
print("\n✅ Đã thu thập xong dữ liệu bán hàng từ TikTok!")
