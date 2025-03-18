
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time 
import pandas as pd
import re
import urllib.parse  # URL 인코딩을 위한 모듈

# 크롬 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--disable-blink-features=AutomationControlled")  # 자동화 감지 방지
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
chrome_options.add_argument("--headless")  # 백그라운드 실행
chrome_options.add_experimental_option("detach", True)

# 드라이버 실행
driver = webdriver.Chrome(options=chrome_options)
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")  # WebDriver 탐지 우회
driver.implicitly_wait(3)
driver.set_window_size(1920, 1080)

# 크롤링할 지역 목록
regions = [
    '서울', '도쿄', '부산', '제주도', '강릉', '인천', '경주', '해운대', '가평', '여수', '속초', 
    '괌' , '코타니카발루', '경기', '충남', '대구', '대전', '경남', '전북', '울산', '광주', '강원', '경북',
    '전남', '충북', '세종', '오사카','후쿠오카','도쿄','다낭','싱가포르','방콕','세부','나트랑',
    '교토','타이베이','보라카이','삿포로','유후','홍콩','오키나와','호치민','보홀','호이안',
    '파타야','타이중','발리','푸꾸옥','파리','하노이','사이판','푸켓','시드니','뉴욕',
    '로마','나고야','치앙마이','앙헬레스 시티','런던','바르셀로나','라스베이거스','고베',
    '로스앤젤레스','프라하','요코하마','기타큐슈','부다페스트','다랏','코사무이','크라비',
    '빈','멜버른','피렌체','가오슝','이스탄불','두바이','브리즈번','나가사키',
    '마드리드','헬싱키','퍼스','자카르타','프놈펜','밴쿠버','베이징','더블린'
]

# 데이터 크롤링 함수
def data_load(region):
    """주어진 지역(region)에 대해 숙소 데이터를 크롤링하는 함수"""
    data = []
    region_encoded = urllib.parse.quote(region)  # 지역명을 URL 인코딩
    base_url = f"https://www.yeogi.com/domestic-accommodations?keyword={region_encoded}&page="

    # 첫 페이지에서 검색 결과 개수 가져오기
    driver.get(base_url + "1")
    time.sleep(3)

    try:
        total_element = driver.find_element(By.CSS_SELECTOR, "header.css-1psit91")
        total_text = total_element.text.strip()
        match = re.search(r"[\d,]+", total_text)
        if match:
            total_count = int(match.group().replace(",", ""))
        else:
            print(f"[{region}] 검색 결과 수를 찾을 수 없습니다.")
            return []
    except Exception as e:
        print(f"[{region}] 오류 발생: {e}")
        return []

    # 페이지 수 계산 (한 페이지당 20개 기준)
    total_pages = min((total_count // 20) + 1, 1)  # 테스트용으로 최대 3페이지만 크롤링
    # total_pages = (total_count // 20) + 1
    print(f"[{region}] 총 검색 결과: {total_count}개, 크롤링할 페이지: {total_pages}개")

    for cnt in range(1, total_pages + 1):  
        print(f"[{region}] 페이지 {cnt} 크롤링 중...")
        driver.get(base_url + str(cnt))
        driver.implicitly_wait(4)
        time.sleep(3)
        
        # 숙소 링크 가져오기
        aList = driver.find_elements(By.CSS_SELECTOR, "a.gc-thumbnail-type-seller-card")  
        for a in aList:
            url = a.get_attribute("href")
            locationName = a.get_attribute("text")
            if url:
                # 지역 정보 추가
                data.append({"Region": region, "URL": url, "locationName" : locationName})  

    return data  # 지역별 크롤링 데이터 반환

# 모든 지역 크롤링 실행
all_data = []
for region in regions:
    all_data.extend(data_load(region))  # 각 지역의 데이터를 리스트에 추가

# 데이터 저장
df = pd.DataFrame(all_data)
df.to_csv("yeogi_urls.csv", index=False, encoding="utf-8")
print("크롤링 완료 및 CSV 저장 완료!")

# 드라이버 종료
driver.close()
