#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import sys, os
sys.path.insert(0,os.path.abspath(os.path.pardir))
from selenium import webdriver
from PIL import Image
from io import BytesIO

def getdriver(browser):
    if browser == 'Firefox':
        driver = webdriver.Firefox()
    elif browser == 'Chrome':
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--incognito')
        chrome_options.add_argument('--ignore-certificate-errors')
        # chrome_options.add_argument('--headless') # gives wrong bb;
        chrome_options.add_argument('--start-maximized')
        driver = webdriver.Chrome(chrome_options=chrome_options)
    return driver

def screenshot(driver,url,pngname):
    driver.get(url)
    devicePixelRatio = driver.execute_script('return window.devicePixelRatio')
    scale = lambda value: int(value*devicePixelRatio)
    actions = webdriver.ActionChains(driver)
    table = driver.find_elements_by_tag_name('table')
    if table != []:
        table = table[0]
        x0 = table.location['x']
        y0 = table.location['y']
        x1 = x0 + table.size['width']
        y1 = y0 + table.size['height']
        bb = list(map(scale,[x0,y0,x1,y1]))
    td = driver.find_elements_by_tag_name('td')
    if td != []:
        actions.move_to_element(td[0]).perform()
    png = driver.get_screenshot_as_png()
    if table == []:
        bb = (0,0,2000,1500)
    im = Image.open(BytesIO(png))
    im = im.crop(bb)
    im.save(pngname)


if __name__ == '__main__':

    import time
    from multiprocessing import Process
    from hello import create_hello_app
    from queriesdemo import create_queriesdemo_app
    from templateview import create_templateview_app
    from basics import create_basics_app
    from attrsview import create_attrsview_app

    driver = getdriver('Chrome')
    driver.fullscreen_window()
    urlroot = 'http://localhost:5000/'
    for create_app,runs in [
            [create_hello_app,[
                [urlroot,'hello.png']]],
            [create_queriesdemo_app,[
                [urlroot,'queriesdemo.png']]],
            [create_templateview_app,[
                [urlroot,'templateview.png'],
                [urlroot+'view/tableview.htm','tableview.png']]],
            [create_basics_app,[
                [urlroot,'basics.png'],
                [urlroot+'stacktable','stacktable.png']]],
            [create_attrsview_app,[
                [urlroot,'attrsview.png'],
                [urlroot+'viewattrs/current_app/','current_app.png']]],
            ]:
        app = create_app()
        server = Process(target=app.run)
        server.start()
        time.sleep(1)
        for url,pngname in runs:
            screenshot(driver,url,pngname)
        server.terminate()
        server.join()
    driver.quit()
