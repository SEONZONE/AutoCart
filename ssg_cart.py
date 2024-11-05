from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import configparser as Parser
driver = webdriver.Chrome()

from flask import Flask, request, jsonify
app = Flask(__name__)

############################################################  주요 로직 ############################################################

# 1.SSG 로그인
# 2.요청 URL의 상품 장바구니 담기

####################################################################################################################################


############################################################  설정 세팅 ############################################################

#프로퍼티 파일 읽기
properties = Parser.ConfigParser()
properties.read('./config.ini')

#프로퍼티 세션 읽기
user_config = properties['USER']
host_config = properties['HOST']
login_config = properties['LOGININFO']

#전역변수 값 세팅
login_url = login_config['login_url']
id = user_config['id']
pw = user_config['pw']
####################################################################################################################################


#크롬 세팅
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

#로그인 체크
def check_login(driver,wait):
    try:
        
        driver.get(login_url)
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

#장바구니 담기
def add_to_cart(driver,wait,shopping_url):
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


#메인 함수
def do_cart(shopping_url):
    driver = setup_chrome()
    wait = WebDriverWait(driver,10)
    result = {
        'result' : False
        ,'message' : ''
        ,'error' : ''
    }

    try:
        if check_login(driver,wait):
            if add_to_cart(driver,wait,shopping_url):
                print("성공")
                result['result'] = True
                result['message'] = '장바구니 담기 성공'
    except Exception as e:
        result['message'] = '장바구니 담기 실패'
        result['error'] = e
    finally:
        pass
    return result

#API 호출
@app.route('/api/cart',methods=['POST'])
def add_cart():
    data = request.get_json()
    print(data)
    shopping_url = data['shopping_url']
    result = do_cart(shopping_url)
    return jsonify(result)

if __name__ =="__main__":
    app.run(host=host_config['host'],port=host_config['port'])