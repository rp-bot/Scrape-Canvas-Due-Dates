from selenium import webdriver
from getpass import getpass
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from selenium.common.exceptions import NoSuchElementException

import time
import json


OPTIONS = Options()
OPTIONS.add_argument(
    "--user-data-dir=./user_data")
OPTIONS.page_load_strategy = 'normal'

DRIVER = webdriver.Chrome(service=Service(
    ChromeDriverManager().install()), options=OPTIONS)
DRIVER.get("http://ivylearn.ivytech.edu/")


def get_course_links():
    # Dashboard of courses
    dashboard = DRIVER.find_element(
        By.XPATH, '//*[@id="DashboardCard_Container"]/div/div')

    # Finds the element containing the href of each course
    courses = dashboard.find_elements(By.CLASS_NAME, "ic-DashboardCard__link")
    course_urls = list()  # Initiate a list to be later apended to

    # finds the links and appends to list.
    for i, elements in enumerate(courses):
        course_urls.append(DRIVER.find_element(
            By.XPATH, f"//*[@id='DashboardCard_Container']/div/div/div[{i+1}]/div/a").get_attribute('href'))

    return course_urls


def open_course_links(url_list):
    tab_index = list()
    for url in url_list:
        DRIVER.execute_script(f"window.open('{url}');")
        tab_index.append(url)
    return tab_index


def get_course_summary(course_index: int):  # TODO course_index: list

    DRIVER.switch_to.window(DRIVER.window_handles[course_index+1])

    section_tabs = DRIVER.find_element(By.XPATH, '//*[@id="section-tabs"]')

    if section_tabs.find_element(By.CLASS_NAME, 'syllabus'):
        section_tabs.find_element(By.CLASS_NAME, 'syllabus').click()

    time.sleep(2)
    table_body = DRIVER.find_elements(
        By.XPATH, '//*[@id="syllabusTableBody"]/tr[*]')

    table_data = {
        "Row Index": [],
        "Assignment": [],
        "Assignment URL": [],
        "Due Date": [],
        "Due Time": []
    }

    # for i, header in enumerate(headers):
    #     header_txt.append(header.text)

    for row_num in range(len(table_body)):
        table_data["Row Index"].append(row_num)
        # assignment name
        table_data["Assignment"].append(DRIVER.find_element(
            By.XPATH, f'//*[@id="syllabusTableBody"]/tr[{row_num+1}]/td[*]/a').text)

        # assignment url
        table_data["Assignment URL"].append(DRIVER.find_element(
            By.XPATH, f'//*[@id="syllabusTableBody"]/tr[{row_num+1}]/td[*]/a').get_attribute("href"))

        try:  # TODO If Row Span is greater than one then
            # assignment due date
            table_data["Due Date"].append(DRIVER.find_element(
                By.XPATH, f'//*[@id="syllabusTableBody"]/tr[{row_num+1}]/td[1]').get_attribute("data-date"))

            # assignment due time
            table_data["Due Time"].append(DRIVER.find_element(
                By.XPATH, f'//*[@id="syllabusTableBody"]/tr[{row_num+1}]/td[3]/span').text)

        except NoSuchElementException:
            table_data["Due Date"].append("n/a")
            table_data["Due Time"].append("n/a")

    return table_data


time.sleep(2)
course_list = open_course_links(get_course_links())

time.sleep(2)

# TODO accept a dictionary to name files
# FIXME enumerate is not working

for i, tab_url in enumerate(course_list):
    with open(f"Course_{i}.json", "w")as f:
        json.dump(get_course_summary(i), f, indent=4)
