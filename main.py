import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys  
import time

############################################################  주요 로직 ############################################################

# 1.SSG 로그인
# 2.요청 URL의 상품 장바구니 수량입력
# 3.상품 장바구니 담기
# 4.장바구니 내역 확인

####################################################################################################################################

# 환경 변수에서 설정 읽기
login_url = os.environ.get('LOGIN_URL')
id = os.environ.get('USER_ID')
pw = os.environ.get('USER_PW')

#크롬 세팅
def setup_chrome():
   chrome_options = Options()
   
   # Lambda 환경에 맞는 Chrome 바이너리 경로 설정
   chrome_options.binary_location = '/opt/chrome/chrome'
   
   # Lambda 환경에 필요한 추가 옵션
   chrome_options.add_argument('--headless')
   chrome_options.add_argument('--no-sandbox')
   chrome_options.add_argument('--single-process')
   chrome_options.add_argument('--disable-dev-shm-usage')

   # 성능 최적화
   chrome_options.add_argument('--disable-extensions') # 확장 프로그램 비활성화
   chrome_options.add_argument('--disable-popup-blocking')  # 팝업 차단 비활성화
   chrome_options.add_argument('--blink-settings=imagesEnabled=false')  # 이미지 로딩 비활성화

   # 사용자 에이전트 설정
   chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

   #해상도 설정
   chrome_options.add_argument('--window-size=1920,1080')  # Full HD 해상도

   # 메모리 제한 설정
   chrome_options.add_argument('--js-flags=--max-old-space-size=512')  # JavaScript 힙 메모리 제한
   chrome_options.add_argument('--memory-pressure-off')  # 메모리 압력 모니터링 비활성화

   # 캐시 설정
   chrome_options.add_argument('--disk-cache-size=1')
   chrome_options.add_argument('--media-cache-size=1')

   # ChromeDriver 경로 지정
   service = webdriver.ChromeService(executable_path='/opt/chromedriver')
   return webdriver.Chrome(service=service, options=chrome_options)

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
       print('[add_to_cart] 장바구니 담기 실패',e)
       return result
   
#장바구니 목록 불러오기
def get_cart_items(driver):
   result = {
       'result' : False
       ,'message' : ''
       ,'itemsList' :[]
       ,'totalPrice': ''
   }
   try:
       items = driver.find_elements(By.XPATH, "//tr[contains(@class, 'pay_item_area')]")
       for item in items:
           name = item.find_element(By.CSS_SELECTOR, ".codr_unit_name .tx_ko").text
           amount = item.find_element(By.CLASS_NAME, "ordQty").get_attribute("value")
           item_info = {
               'name' : name
               ,'amount' : amount
           }
           result['itemsList'].append(item_info)
       result['totalPrice'] = driver.find_element(By.CSS_SELECTOR, ".codr_dl_totalprice .ssg_price").text
       result['result'] = True
       result['message'] = '장바구니 목록 성공'
       return result
   except Exception as e:
       result['message'] = f'장바구니 목록 실패: {e}'
       print('[get_cart_items] 장바구니 목록 실패',e)
       return result

   
def do_cart(shopping_url,amount):
   driver = None
   wait = None
   result = {
       'result' : False
       ,'message' : ''
       ,'error' : ''
   }

   try:
       driver = setup_chrome()
       wait = WebDriverWait(driver, 10)  # driver 생성 후 wait 초기화

       if check_login(driver,wait):
           add_to_cart_json = add_to_cart(driver,wait,shopping_url,amount)
           if add_to_cart_json['result']:
               result = get_cart_items(driver)
           else:
               result['result'] = False
               result['message'] = add_to_cart_json['message']
   except Exception as e:
       result['message'] = '[do_cart] 장바구니 담기 실패'
       result['error'] = str(e)
   finally:
       if driver:
           driver.quit()  # 드라이버 종료
           del driver    # 메모리에서 명시적 제거
   return result

def handler(event, context):
   try:
       # API Gateway에서 전달받은 JSON 데이터 파싱
       data = json.loads(event['body']) if 'body' in event else event
       
       if not data or 'shopping_url' not in data:
           return {
               'statusCode': 400,
               'body': json.dumps({
                   'result': False,
                   'error': '응답값 오류',
                   'message': 'shopping_url 인자값이 존재하지 않거나, 올바르지 않습니다.'
               })
           }

       shopping_url = data['shopping_url']
       amount = data.get('amount', 1) <= 0 if 1 else data.get('amount', 1)
       
       result = do_cart(shopping_url, amount)
       
       return {
           'statusCode': 200,
           'body': json.dumps(result, ensure_ascii=False)
       }
   except Exception as e:
       return {
           'statusCode': 500,
           'body': json.dumps({
               'result': False,
               'error': str(e),
               'message': 'Lambda 실행 중 오류가 발생했습니다.'
           }, ensure_ascii=False)
       }