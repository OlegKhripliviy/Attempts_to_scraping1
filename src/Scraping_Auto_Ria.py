import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


t1 = time.time()
agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
options = webdriver.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled') # отключение контроля автоматизации настроки для обхода ботов(ХЗ)
options.add_experimental_option("prefs",
                                {"profile.managed_default_content_settings.images": 2}) # отключение прогрузки изображений

driver = webdriver.Chrome(executable_path="D:/Учеба/Scraping/chromedriver/chromedriver.exe",
                          options=options)
action = ActionChains(driver)

url = 'https://auto.ria.com/uk/search/?indexName=auto,order_auto,newauto_search&year[0].' \
      'gte=2007&year[0].lte=2007&categories.main.id=1&brand.id[0]=70&model.id[0]=3011&country.' \
      'import.usa.not=-1&price.currency=1&fuel.id[0]=1&abroad.not=0&custom.not=1&page=0&size=10'
list_cars_url = []

try:
    driver.get(url)
    pages = driver.find_elements(By.CLASS_NAME, 'page-item.mhide') # Кнопка последней страницы
    last_page = pages[-1].text # Значение последней страницы

    for i in range(1, int(last_page)+1):
        driver.get(url)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,
                                        '//*[@id="searchPagination"]/div/nav/span[11]/a')))
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        data = soup.find_all('a', class_='m-link-ticket')

        for j in data:
            card_url = j.get('href')
            list_cars_url.append(card_url)
        # Кнопка подтверждения cookies
        try:
            driver.find_element(By.XPATH, '//*[@id="gdpr-notifier"]/div[1]/div[2]/label[1]').click()
        except Exception as ex:
            print(ex.args[1])

        next_page = driver.find_element(By.XPATH, '//*[@id="searchPagination"]/div/nav/span[11]/a')
        # action.move_to_element(next_page).perform()
        action.click(next_page).perform() # клик кнопки "Вперед"
        time.sleep(1)
        url = driver.current_url # Передача в переменную url новую ссылку страницы

    for car_url in list_cars_url:
        driver.get(car_url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        name = soup.find('h1', class_='head').text
        try:
            engine = driver.find_element(By.XPATH, '//*[@id="details"]/dl/dd[3]/span[2]').text
        except Exception:
            print('Обьем двигателя не указан')
        try:
            mileage = driver.find_element(By.XPATH, '//*[@id="details"]/dl/dd[2]').text
        except Exception:
            print('Пробег не указан')
        try:
            description = soup.find('div', class_='full-description').text
        except Exception:
            pass
        """
        car_id - id обьявления из url
        data_hash - уникальный код для каждого обьявления 
        """
        car_id = car_url.split('_')[-1].replace('.html', '')
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/div[6]/div[10]/script[8]')))
        data_hash = driver.find_element(By.XPATH,
                                        '/html/body/div[6]/div[10]/script[8]').get_attribute('data-hash')

        driver.get(f'https://auto.ria.com/users/phones/{car_id}?hash={data_hash}&expires=2592000')
        number_dict = driver.find_element(By.XPATH, '/html/body/pre').text
        number = number_dict.split(':')[-1][1:-2:]
        print(name, engine, mileage, number, car_url)


except Exception as ex:
    print(ex.args)
finally:
    driver.close()
    driver.quit()
print(time.time() - t1)



