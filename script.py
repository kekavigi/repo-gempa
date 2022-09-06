import datetime
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

# initiate
options = Options()
options.headless = True
driver = webdriver.Firefox(
    executable_path='./geckodriver',
    options=options)

start = datetime.date(2022, 6, 17)   # starting date
ended = datetime.date(2022, 9,  1)   # end date
delta = datetime.timedelta(days=1)

URL = 'http://repogempa.bmkg.go.id/repo_new/'


def retrieve(sY, sM, sD, eY, eM, eD):
    driver.get(URL)

    parameter = {'start_year' : str(sY),
                 'start_month': '{:>02d}'.format(sM),
                 'start_day'  : '{:>02d}'.format(sD),
                 'end_year'   : str(eY),
                 'end_month'  : '{:>02d}'.format(eM),
                 'end_day'    : '{:>02d}'.format(eD)}

    for k, v in parameter.items():
        elmt = driver.find_element(by=By.NAME, value=k)
        elmt.clear()
        elmt.send_keys(v)

    elmt = driver.find_element(by=By.NAME, value='Submit')
    elmt.send_keys(Keys.RETURN)

    # loading this page need a lot of time
    sleep(3)

    try:
        while driver.find_element(by=By.TAG_NAME, value='meta'):
            # wait for page loading all of its contents
            print(end='.')
            sleep(1)
    except Exception:
        pass
    finally:
        print()

    # save page as a HTML file... process it later
    filename = '{}{:>02d}{:>02d}.html'.format(sY, sM, sD)
    with open(filename, 'w') as f:
        f.write(driver.page_source)


while start < ended:
    print(start)
    tummo = start + delta
    retrieve(start.year, start.month, start.day,
             tummo.year, tummo.month, tummo.day)
    start = tummo
    
driver.close()