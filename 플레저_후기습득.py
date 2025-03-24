import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ✅ 크롬 옵션 설정
chrome_options = Options()
chrome_options.headless = False  # 필요 시 True로 변경 가능
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_argument("--disable-infobars")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--start-maximized")
chrome_options.page_load_strategy = "eager"
chrome_options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
chrome_options.add_experimental_option("detach", True)

# ✅ 웹드라이버 실행
driver = webdriver.Chrome(options=chrome_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

# ✅ 강남언니 카카오 로그인 URL
login_url = "https://accounts.kakao.com/login/?continue=https%3A%2F%2Fkauth.kakao.com%2Foauth%2Fauthorize%3Fclient_id%3D36cf3898c3072e555ea6a49b299f8a06%26redirect_uri%3Dhttps%253A%252F%252Fwww.gangnamunni.com%252Fsignup%252Foauth%252Fkakao%26response_type%3Dcode%26scope%3Daccount_email%252Cbirthday%252Cname%252Cphone_number%252Ctalk_message%26through_account%3Dtrue#login"
driver.get(login_url)

# ✅ 사용자가 수동으로 로그인할 시간 제공
print("🔐 로그인하세요. 로그인 후 70초 내로 페이지가 자동으로 진행됩니다...")
try:
    WebDriverWait(driver, 90).until(
        EC.presence_of_element_located((By.CLASS_NAME, "GlobalHeader__StyledUserImage-sc-35f0e887-9"))
    )
    print("✅ 로그인 성공! 크롤링을 시작합니다.")
except:
    print("⚠️ 로그인 실패! 수동 로그인 확인 필요.")

# ✅ 크롤링할 병원 리뷰 페이지 URL
page_url = "https://www.gangnamunni.com/reviews?hospitalId=2991"
driver.get(page_url)
time.sleep(5)  # 페이지 로딩 대기

# ✅ "더보기" 버튼이 존재하면 클릭 (반복 실행)
def click_more_button():
    """더보기 버튼이 존재하면 계속 클릭하여 리뷰 추가 로드"""
    while True:
        try:
            more_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[span[contains(text(), '더보기')]]"))
            )
            driver.execute_script("arguments[0].click();", more_button)
            print("✅ '더보기' 버튼 클릭됨")
            time.sleep(random.uniform(2, 4))
        except:
            print("📌 '더보기' 버튼이 더 이상 존재하지 않음")
            break  # 더 이상 버튼이 없으면 종료

# ✅ 스크롤 다운하여 새로운 리뷰 로드
def scroll_to_bottom():
    """스크롤을 끝까지 내려 새로운 리뷰 로드"""
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    cnt = 1
    while True: 
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.uniform(2, 3))
        
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            print("🚀 모든 리뷰 크롤링 완료! 더 이상 추가 로드할 리뷰 없음.")
            break
        last_height = new_height        
        if cnt >= 6000:
            break    
        else :
            cnt += 1 

# ✅ "더보기" 버튼 클릭 실행
click_more_button()

# ✅ 스크롤 다운 실행
scroll_to_bottom()

# ✅ 저장할 리스트
reviews_data = []

def scrape_reviews():
    """현재 페이지에서 리뷰 데이터를 크롤링하는 함수"""
    review_elements = driver.find_elements(By.CSS_SELECTOR, "div.new__StyledContainer-sc-1ee6cb43-0")

    print(f"🔍 {len(review_elements)}개의 리뷰 감지됨")

    for review in review_elements:
        try:
            # ✅ 작성자 정보
            author = review.find_element(By.CSS_SELECTOR, "h3.UserProfile__StyledName-sc-36315857-4").text.strip()

            # ✅ 작성자 레벨 (예: Lv.1, Lv.2)
            try:
                level = review.find_element(By.CSS_SELECTOR, "span.UserProfile__StyeldLevel-sc-36315857-5").text.strip()
            except:
                level = "레벨 없음"

            # ✅ 리뷰 날짜
            date = review.find_element(By.CSS_SELECTOR, "span.new__StyledDate-sc-1ee6cb43-4").text.strip()

            # ✅ 평점
            # rating = review.find_element(By.CSS_SELECTOR, "span.new__StyledRating-sc-1ee6cb43-7").text.strip()
            try:
                rating = review.find_element(By.CSS_SELECTOR, "span[class*='Rating']").text.strip()
            except:
                rating = "평점 없음"
            # ✅ 해시태그 (시술명)
            try:
                hashtags = review.find_element(By.CSS_SELECTOR, "p.new__StyledTreatmentTagList-sc-1ee6cb43-8").text.strip()
            except:
                hashtags = "태그 없음"

            # ✅ 리뷰 본문
            try:
                content = review.find_element(By.CSS_SELECTOR, "p.new__StyledDescription-sc-1ee6cb43-10").text.strip()
            except:
                content = "내용 없음"

            # ✅ 데이터 저장
            reviews_data.append([author, level, date, rating, hashtags, content]) 
             

        except Exception as e:
            print(f"❌ 리뷰 크롤링 오류: {e}")

# ✅ 리뷰 크롤링 실행
scrape_reviews()

# ✅ 크롤링된 데이터 저장
df = pd.DataFrame(reviews_data, columns=["작성자", "레벨", "작성 날짜", "평점", "태그", "내용"])
df.to_csv("gangnamunni_reviews.csv", index=False, encoding="utf-8-sig")

print("✅ 크롤링 완료! 데이터가 'gangnamunni_reviews.csv' 파일에 저장되었습니다.")

# ✅ 드라이버 종료
driver.quit()
