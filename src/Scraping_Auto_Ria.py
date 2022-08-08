from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import xlsxwriter
import time


agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' \
        ' AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
options = webdriver.ChromeOptions()
options.add_argument(
    '--disable-blink-features=AutomationControlled')  # отключение контроля автоматизации настроки для обхода ботов(ХЗ)
options.add_experimental_option("prefs",
                                {
                                    "profile.managed_default_content_settings.images": 2})  # отключение прогрузки изображений

driver = webdriver.Chrome(executable_path="D:/Учеба/Scraping/chromedriver/chromedriver.exe",
                          options=options)
action = ActionChains(driver)

url = 'https://auto.ria.com/uk/search/?indexName=auto,order_auto,newauto_search&year[0].' \
      'gte=2007&year[0].lte=2007&categories.main.id=1&brand.id[0]=70&model.id[0]=3011&country.' \
      'import.usa.not=-1&price.currency=1&fuel.id[0]=1&abroad.not=0&custom.not=1&page=0&size=10'

list_cars_url = []


def get_page_url(url):
    t1 = time.time()
    try:
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'lxml')
        pages = soup.find('span', class_='page-item dhide text-c').text
        last_page = pages.split('/')[-1].strip()  # Поиск последней страницы
        if len(last_page) == 0:
            last_page = 1

        for i in range(1, int(last_page) + 1):
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH,
                                                                            '//*[@id="searchPagination"]/div/nav/span[11]/a')))
            action.move_to_element(driver.find_element(By.XPATH, '//*[@id="wrapperFooter"]/div/div/div[1]/div[3]/a'))
            time.sleep(1)
            html_new = driver.page_source
            soup = BeautifulSoup(html_new, 'lxml')
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
            next_page.click()  # клик кнопки "Вперед"
            time.sleep(1)
            driver.get(driver.current_url)

    except Exception as ex:
        print(ex)
    finally:
        print(time.time() - t1)
        time.sleep(1)
    return list_cars_url


def get_cars_information():
    global list_cars
    t1 = time.time()
    list_cars = []

    try:
        for car_url in list_cars_url:

            driver.get(car_url)
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')
            name = soup.find('h1', class_='head').text

            try:
                engine = driver.find_element(By.XPATH, '//*[@id="details"]/dl/dd[3]/span[2]').text
            except Exception:
                engine = 'Обьем двигателя не указан'
            try:
                mileage = driver.find_element(By.XPATH, '//*[@id="details"]/dl/dd[2]').text
            except Exception:
                mileage = 'Пробег не указан'
            try:
                description = soup.find('div', class_='full-description').text
            except Exception:
                description = 'Без описания'
            try:
                price = soup.find('div', class_='price_value').find('strong', class_='').text
            except Exception:
                price = 'Цена не указана'
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
            list_cars_one = [name, engine, mileage, price, number, car_url, description]
            list_cars.append(list_cars_one)
            time.sleep(1)
    except Exception as ex:
        print(ex.args)
    finally:
        driver.close()
        driver.quit()
        print(time.time() - t1)

    return list_cars


def writer(parametr): # функция в которую будет передавться массив данных
    book = xlsxwriter.Workbook(r'autoria_cars.xlsx') # создаем файл таблицы
    page = book.add_worksheet('skoda') #создается страница таблицы

    row = 0
    column = 0

    page.set_column("A:A", 21)
    page.set_column("B:B", 30)
    page.set_column("C:C", 20)
    page.set_column("D:D", 8)
    page.set_column("E:E", 15)
    page.set_column("F:F", 60)
    page.set_column("G:G", 100)

    for item in list_cars:
        page.write(row, column, item[0])
        page.write(row, column+1, item[1])
        page.write(row, column+2, item[2])
        page.write(row, column+3, item[3])
        page.write(row, column+4, item[4])
        page.write(row, column+5, item[5])
        page.write(row, column+6, item[6])
        row += 1
    book.close()


def main():
    get_page_url(url)
    get_cars_information()
    writer(list_cars)


if __name__ == '__main__':
    main()



