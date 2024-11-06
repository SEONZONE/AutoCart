from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys  
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

    #해상도 설정
    chrome_options.add_argument('--window-size=1920,1080')  # Full HD 해상도

    # 드라이버 생성
    driver = webdriver.Chrome(options=chrome_options)
    return driver

#로그인 체크
def check_login(driver,wait):
    result = {
        'result' : False
        ,'message' : ''
    }
    try:
        
        driver.get(login_url)
        driver.find_element(By.ID,"mem_id").send_keys(id)
        driver.find_element(By.ID,"mem_pw").send_keys(pw)
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".cmem_btn.cmem_btn_ornge"))).click()

        time.sleep(1)
        try:
            wait.until(EC.presence_of_element_located((By.ID, "logoutBtn")))
            print("로그인 성공 확인")
        except Exception as e:
            print("로그인 확인 실패")
            result['message'] = f'로그인 실패: {e}'
            return result
        
        result['result'] = True   
        result['message'] = '로그인 성공'
        return result
    except Exception as e:
        result['message'] = f'로그인 실패: {e}'
        print('로그인 실패',e)
        return result

#장바구니 담기
def add_to_cart(driver,wait,shopping_url,amount=1):
    result = {
        'result' : False
        ,'message' : ''
    }
    try:
        driver.get(shopping_url)

        #수량 선택
        try:
            amount_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input#cdtl_item_amount1[title="수량입력"]')))
            amount_input.send_keys(Keys.CONTROL + "a", Keys.DELETE)
            amount_input.send_keys(str(amount))
            time.sleep(1)
            print("수량 입력 완료")
        except Exception as e:
            print(f"수량 입력 중 에러: {e}")
            result['message'] = f'수량 입력 실패: {e}'
            return result
        time.sleep(1)

        #장바구니 선택
        try:
            driver.find_element(By.XPATH,"//*[@id='actionCart']").click()
            print("장바구니 선택 완료")
        except Exception as e:
            print(f"장바구니 선택 중 에러: {e}")
            result['message'] = f'장바구니 선택 실패: {e}'
            return result

        #장바구니 이동
        try:
            driver.execute_script("ssgGnb.fn_btnClickCart();")
            print("장바구니 이동 완료")
        except Exception as e:
            print(f"장바구니 이동 중 에러: {e}")
            result['message'] = f'장바구니 이동 실패: {e}'
            return result

        result['result'] = True
        result['message'] = '장바구니 담기 성공'
        return result
    except Exception as e:
        result['message'] = f'장바구니 담기 실패: {e}'
        print('장바구니 담기 실패',e)
        return result

    
def do_cart(shopping_url,amount):
    driver = setup_chrome()
    wait = WebDriverWait(driver,10)
    result = {
        'result' : False
        ,'message' : ''
        ,'error' : ''
    }

    try:
        if check_login(driver,wait):
            add_to_cart_json = add_to_cart(driver,wait,shopping_url,amount)
            if add_to_cart_json['result']:
                result['result'] = True
                result['message'] = '장바구니 담기 성공'
            else:
                result['result'] = False
                result['message'] = add_to_cart_json['message']

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

    if not data or 'shopping_url' not in data:
        return jsonify({
            'result' : False
            ,'error' : '응답값 오류'
            ,'message' : 'shopping_url 인자값이 존재하지 않거나, 올바르지 않습니다.'
            
        })

    # 쇼핑 주소
    shopping_url = data['shopping_url']
    # 품목 수량
    amount = data.get('amount',1) <= 0 if 1 else data.get('amount',1)

    result = do_cart(shopping_url,amount)
    return jsonify(result)

if __name__ =="__main__":
    app.run(host=host_config['host'],port=host_config['port'])