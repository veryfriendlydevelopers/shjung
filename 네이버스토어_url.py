from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import pandas as pd
import random

# ✅ 크롬 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--headless")  # 백그라운드 실행
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # 자동화 감지 방지
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
chrome_options.add_experimental_option("detach", True)

# ✅ 웹드라이버 실행
driver = webdriver.Chrome(options=chrome_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")  # WebDriver 탐지 우회
driver.implicitly_wait(5)  # 페이지 로딩 대기
driver.set_window_size(1920, 1080)  # 창 크기 설정

# ✅ 크롤링할 URL (네이버 브랜드 페이지)
page_url = "https://brand.naver.com/cetaphilshop/products/11528152893#REVIEW"
driver.get(page_url)
time.sleep(5)  # 페이지 로딩 대기

# ✅ 저장할 리스트
reviews_data = []

def scrape_reviews():
    """현재 페이지에서 리뷰 데이터를 크롤링하는 함수"""
    review_elements = driver.find_elements(By.CSS_SELECTOR, "div._1CkGh7Rgzq")
    print(f"🔍 {len(review_elements)}개의 리뷰 감지됨")

    for review in review_elements:
        try:
            # 작성자 정보
            author = review.find_element(By.CSS_SELECTOR, "strong._3eMaa46Quy").text.strip()

            # 리뷰 날짜
            date = review.find_elements(By.CSS_SELECTOR, "span._3eMaa46Quy")[1].text.strip()

            # 평점
            rating = review.find_element(By.CSS_SELECTOR, "em._15NU42F3kT").text.strip()

            # 리뷰 내용
            content = review.text 

            # 리뷰 이미지 (없으면 "이미지 없음")
            try:
                image_element = review.find_element(By.CSS_SELECTOR, "img")
                image_url = image_element.get_attribute("src")
            except:
                image_url = "이미지 없음"

            # 데이터 저장
            reviews_data.append([author, date, rating, content, image_url])

        except Exception as e:
            print(f"❌ 리뷰 크롤링 오류: {e}")

# ✅ 첫 번째 페이지 리뷰 크롤링
print("🚀 첫 번째 페이지 크롤링 중...")
scrape_reviews()

# ✅ 다음 페이지 이동 및 크롤링 실행 (최대 10페이지)
for i in range(1, 11):  # 2페이지부터 10페이지까지 이동
    try:
        print(f"📢 {i} 페이지 이동 중...")

        # ✅ 페이지 번호를 가진 a 태그 클릭 (클래스 "UWN4IvaQza"를 사용)
        next_page_buttons = driver.find_elements(By.CLASS_NAME, "UWN4IvaQza")

        for button in next_page_buttons:
            if button.text == str(i):  # i 번째 페이지 찾기
                driver.execute_script("arguments[0].click();", button)  # JavaScript 클릭
                time.sleep(random.randint(3, 6))  # 페이지 로딩 대기
                break  # 해당 페이지를 찾으면 클릭 후 종료

        # ✅ 해당 페이지 리뷰 크롤링 실행
        scrape_reviews()

    except Exception as e:
        print(f"⚠️ {i} 페이지 이동 실패: {e}")
        break  # 페이지 이동 실패 시 반복 중단

# ✅ 크롤링된 데이터 저장
df = pd.DataFrame(reviews_data, columns=["작성자", "날짜", "평점", "내용", "이미지 URL"])
df.to_csv("naver_reviews.csv", index=False, encoding="utf-8-sig")

print("✅ 크롤링 완료! 데이터가 naver_reviews.csv 파일에 저장되었습니다.")

# ✅ 드라이버 종료
driver.quit()
