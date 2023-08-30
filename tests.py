import pytest
from valid_data import valid_email, valid_password, valid_username
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import hashlib


@pytest.fixture(scope="session", autouse=True)
def auth_and_goto_mypets():
    pytest.driver = webdriver.Chrome()
    pytest.driver.implicitly_wait(8)  # criteria_1
    # Переходим на страницу авторизации
    pytest.driver.get('http://petfriends.skillfactory.ru/login')
    pytest.driver.set_window_size(1200, 800)
    pytest.driver.set_window_position(0, 0)

    WebDriverWait(pytest.driver, 5).until(EC.presence_of_element_located((By.ID, "email")))  # criteria_2

    pytest.driver.find_element(By.ID, 'email').send_keys(valid_email)
    pytest.driver.find_element(By.ID, 'pass').send_keys(valid_password)
    pytest.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
    pytest.driver.find_element(By.PARTIAL_LINK_TEXT, u"Мои питомцы").click()

    WebDriverWait(pytest.driver, 5).until(EC.presence_of_element_located((By.XPATH, "//tbody")))  # criteria_2

    pytest.driver.names = pytest.driver.find_elements(By.XPATH, '(//tbody//tr//td[1])')
    pytest.driver.breeds = pytest.driver.find_elements(By.XPATH, '(//tbody//tr//td[2])')
    pytest.driver.ages = pytest.driver.find_elements(By.XPATH, '(//tbody//tr//td[3])')

    yield pytest.driver

    pytest.driver.quit()


def get_pet_qty(text: list) -> int:
    text_lines = text.split('\n')
    for line in text_lines:
        if u'Питомцев' in line:
            return int(line.split(':')[1].strip())


def get_imgs_cnt(img_list: list) -> int:
    cnt_img = 0
    for img in img_list:
        if img.get_attribute('src') != '':
            cnt_img += 1
    return cnt_img


def is_absent_empty_text(elems_list: list) -> bool:
    for elem in elems_list:
        txt = elem.text.strip()
        # print('\nTxt:', txt)
        if not txt:
            return False
    return True


def test_pet_quantity(auth_and_goto_mypets):

    WebDriverWait(auth_and_goto_mypets, 5).until(EC.presence_of_element_located((By.TAG_NAME, 'h2')))

    assert auth_and_goto_mypets.find_element(By.TAG_NAME, 'h2').text == valid_username
    text_block = auth_and_goto_mypets.find_element(By.CSS_SELECTOR, 'div.\\.col-sm-4.left').text
    assert u'Питомцев' in text_block
    pet_qty = get_pet_qty(text_block)
    pet_lines = len(auth_and_goto_mypets.find_elements(By.XPATH, '//tbody/tr'))
    assert pet_qty == pet_lines, "Counter of pets on page misleading"


def test_at_least_half_pets_have_photo(auth_and_goto_mypets):
    imgs_qty = get_imgs_cnt(auth_and_goto_mypets.find_elements(By.XPATH, '//th[@scope="row"]/img'))
    pet_qty = len(auth_and_goto_mypets.find_elements(By.XPATH, '//tbody/tr'))
    assert imgs_qty >= pet_qty // 2, "Less than half pets have a photo"
    print(f'\n { imgs_qty = } >= {pet_qty}//2')


def test_all_pets_have_name_age_breed(auth_and_goto_mypets):
    names = auth_and_goto_mypets.names
    breeds = auth_and_goto_mypets.breeds
    ages = auth_and_goto_mypets.ages

    assert is_absent_empty_text(names) == True, 'Present an empty NAME pet field!'
    assert is_absent_empty_text(breeds) == True, 'Present an empty BREED pet field!'
    assert is_absent_empty_text(ages) == True, 'Present an empty AGE pet field!'


def test_all_pets_have_different_names(auth_and_goto_mypets):
    names = auth_and_goto_mypets.names
    set_names = set([name.text.strip() for name in names])
    qty_names = len(names)
    unique_names = len(set_names)

    assert qty_names == unique_names, "There are duplicates of names"
    # print(f'{ qty_names = } ----- { unique_names = }')


def test_all_pets_unique(auth_and_goto_mypets):
    names = auth_and_goto_mypets.names
    breeds = auth_and_goto_mypets.breeds
    ages = auth_and_goto_mypets.ages

    hash_nba = []
    pets_qty = len(names)
    for i in range(pets_qty):
        str_for_hash = str(names[i].text) + str(breeds[i].text) + str(ages[i].text) + '--seed'
        hash_nba.append(hashlib.sha1(str_for_hash.encode('utf-8')).hexdigest())

    set_of_hashes = set(hash_nba)
    unique_pets_qty = len(set_of_hashes)

    print(auth_and_goto_mypets.names)

    assert pets_qty == unique_pets_qty, "Present pet clones"