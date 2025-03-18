from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd
import os

# 크롬 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 백그라운드 실행
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # 자동화 감지 방지
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
chrome_options.add_experimental_option("detach", True)

# 웹드라이버 실행
driver = webdriver.Chrome(options=chrome_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.implicitly_wait(3)
driver.set_window_size(1920, 1080)

# CSV 파일 읽기
df = pd.read_csv("yeogi_urls.csv")  # CSV 파일명을 정확히 입력하세요

# 후기 크롤링 함수
def scrape_reviews(region, url):
    """주어진 URL에서 숙소 후기를 크롤링하고, 해당 지역 폴더에 저장"""
    driver.get(url)
    time.sleep(3)

    # 숙소 ID 추출
    accommodation_id = url.split("/")[-1].split("?")[0]

    try:
        # 글쓴이(작성자) 정보 크롤링
        review_authors = driver.find_elements(By.CSS_SELECTOR, "p.css-y9z2ll")  
        review_authors = [author.text.strip() if author.text.strip() else "익명" for author in review_authors]  
        
        # 리뷰 1 · 사진 1 · 장소 1
        review_info_elements = driver.find_elements(By.CSS_SELECTOR, "p.css-1h46h5d")          
        review_info_elements = [review_info.text.strip() if review_info.text.strip() else "익명" for review_info in review_info_elements]  
        
        # 후기 내용 크롤링
        review_elements = driver.find_elements(By.CSS_SELECTOR, "p.css-nyr29c")  
        reviews = [review.text.strip() for review in review_elements if review.text.strip()]
        
        # 지역별 폴더 생성
        region_path = os.path.join("reviews", region)
        os.makedirs(region_path, exist_ok=True)

        # 작성자와 후기 내용 매칭 (개수가 다를 경우 예외 처리)
        review_data = []   
        for i in range(min(len(review_authors), len(reviews))):  
            review_data.append(f"{review_authors[i]} || {review_info_elements[i]} || {reviews[i]}")

        # 파일 저장
        if len(review_data) > 1:  # 후기 개수만 있을 때 제외
            file_path = os.path.join(region_path, f"{accommodation_id}_reviews.txt")
            with open(file_path, "w", encoding="utf-8") as file:
                file.write("\n\n".join(review_data))
            print(f"✅ {region} - {accommodation_id}_reviews.txt 저장 완료!")
        else:
            print(f"⚠️ {region} - {accommodation_id}: 후기가 없습니다.")

    except Exception as e:
        print(f"❌ 오류 발생: {region} - {accommodation_id}, {e}")

# 모든 URL에 대해 후기 수집 실행
for _, row in df.iterrows():
    region = row["Region"]
    url = row["URL"]
    scrape_reviews(region, url)

# 드라이버 종료
driver.quit()
