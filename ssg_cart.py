from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import configparser as Parser
driver = webdriver.Chrome()

### 설정 세팅 ###

#프로퍼티 파일 읽기
properties = parser.ConfigParser()
properties.read('./config.ini')
user_config = properties['USER']

shopping_url = 'https://www.ssg.com/item/itemView.ssg?itemId=1000367120406&siteNo=6001&salestrNo=2037&tlidSrchWd=%EC%BD%A4%EB%B6%80%EC%B0%A8&srchPgNo=1&src_area=ssglist'
loginUrl = 'https://member.ssg.com/member/login.ssg'

id = user_config['id']
pw = user_config['pw']

# 장바구니 담기 => 로그인 여부 확인 => 로그인

def setup_chrome():
    chrome_options = Options()

    # 필수 옵션
    # chrome_options.add_argument('--headless')  # UI 없이 백그라운드에서 실행
    chrome_options.add_argument('--no-sandbox') # 샌드박스 비활성화 (리눅스에서 필요)
    chrome_options.add_argument('--disable-dev-shm-usage') # 공유 메모리 사용 비활성화

    # 성능 최적화
    chrome_options.add_argument('--disable-extensions') # 확장 프로그램 비활성화
    chrome_options.add_argument('--disable-popup-blocking')  # 팝업 차단 비활성화
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')  # 이미지 로딩 비활성화

    # 사용자 에이전트 설정
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    # 드라이버 생성
    driver = webdriver.Chrome(options=chrome_options)
    return driver


def check_login(driver,wait):
    try:
        
        driver.get(loginUrl)
        wait.until(EC.presence_of_element_located((By.ID, "mem_id"))).send_keys(id)
        wait.until(EC.presence_of_element_located((By.ID, "mem_pw"))).send_keys(pw)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".cmem_btn.cmem_btn_ornge"))).click()

        time.sleep(3)  # 기본 대기
        try:
            wait.until(EC.presence_of_element_located((By.ID, "logoutBtn")))
            print("로그인 성공 확인")
        except:
            print("로그인 확인 실패")
            return False
        
        return True
    except Exception as e:
        print("로그인 버튼이 존재하지 않거나, 로그인이 되어 있음: ",e)
        return False

def add_to_cart(driver,wait):
    try:
            driver.get(shopping_url)
            driver.implicitly_wait(5)
            
            wait.until(EC.element_to_be_clickable((By.ID, "actionCart"))).click()
            print("장바구니 선택 성공")
            
            wait.until(EC.element_to_be_clickable((By.ID, "mbrCartCntInfo"))).click()
            print("장바구니 이동 성공")

            return True
    except Exception as e:
        print("장바구니에 상품 담기 실패: ",e)
        return False


def main():
    driver = setup_chrome()
    wait = WebDriverWait(driver,10)
    try:
        if check_login(driver,wait):
            if add_to_cart(driver,wait):
                print("성공")
            while True:
                time.sleep(1)
    except Exception as e:
        print(f"에러 발생: {e}")
    finally:
        pass

if __name__ =="__main__":
    main()