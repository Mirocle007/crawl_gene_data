# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
Created on Sun Oct 21 15:22:08 2018

@author: ligantong
"""

import time
from selenium import webdriver
import csv
from lxml import etree
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys


# 总页数
TOTAL_PAGE = 192

# 开始页
START_PAGE = 1

# 封装成类
WARNING_TIME = 10
LOADING_TIME = 40


class GeneSpider:
    # 基础网址
    base_url = "https://portal.gdc.cancer.gov/exploration"

    def getHtml(self, url, browser, page):
        browser.get(url)
        # 第一页会弹出警告，点击跳过
        if page == START_PAGE:
            WebDriverWait(browser, WARNING_TIME).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, 'ReactModalPortal')))
            browser.find_element_by_xpath('//span[text()="Accept"]').click()

        # 防止还没加载完就获取源码
        WebDriverWait(browser, LOADING_TIME).until(
            expected_conditions.presence_of_element_located((By.CLASS_NAME, 'test-pagination-link')))
        if page == START_PAGE:
            # 第一页要勾选
            browser.find_element_by_xpath(
                '//div[text()="Sort Table"]/ancestor::button').click()
            WebDriverWait(browser, WARNING_TIME).until(
                expected_conditions.presence_of_element_located((By.CLASS_NAME, ' css-ip37cc')))
            browser.find_element_by_xpath(
                '//div[@class=" css-ip37cc"]//span[text()="Gene ID"]').click()
            browser.find_element_by_xpath(
                '//div[@class=" css-ip37cc"]//span[text()="Cytoband"]').click()
            browser.find_element_by_xpath(
                '//div[@class=" css-ip37cc"]//span[text()="Type"]').click()
            time.sleep(1)
        # 获取源码
        html = browser.page_source
        return html

    def parseHtml(self, html, pattern="*"):
        # 用xpath获取相关元素
        parsePage = etree.HTML(html)
        r_list = parsePage.xpath(pattern)
        return r_list

    def writeHtml(self, row, f):
        # 写入csv文件
        writer = csv.writer(f)
        writer.writerow(row)


if __name__ == "__main__":
    # 建立对象
    spider = GeneSpider()
    # 新建csv文件，用于存储数据
    f = open("gene.csv", "at", newline="")
    # 写表头
    writer = csv.writer(f)
    writer.writerow(["Gene ID", "Symbol", "Name", "Cytoband", "Type"])
    # 自动化工具控制Chromedriver浏览器

    page = 0
    # 因为获取页面时偶尔会出现未知错误，所以使用循环来重复获取
    while True:
        browser = webdriver.Chrome()
        if page == TOTAL_PAGE:
            browser.quit()
            break
        # 每页循环
        for page in range(START_PAGE, TOTAL_PAGE + 1):
            # url拼接
            #url = spider.base_url +'?filters=%7B"op"%3A"and"%2C"content"%3A%5B%7B"op"%3A"in"%2C"content"%3A%7B"field"%3A"cases.project.project_id"%2C"value"%3A%5B"TCGA-BRCA"%5D%7D%7D%2C%7B"op"%3A"in"%2C"content"%3A%7B"field"%3A"genes.gene_id"%2C"value"%3A%5B"set_id%3AAWaQYFhbDMMVwdN36E0f"%5D%7D%7D%5D%7D&genesTable_offset=' +str((page-1) * 100) + "&genesTable_size=100&searchTableTab=genes"
            url = spider.base_url + "?filters=%7B%22op%22%3A%22and%22%2C%22content%22%3A%5B%7B%22op%22%3A%22in%22%2C%22content%22%3A%7B%22field%22%3A%22cases.project.project_id%22%2C%22value%22%3A%5B%22TCGA-BRCA%22%5D%7D%7D%2C%7B%22op%22%3A%22in%22%2C%22content%22%3A%7B%22field%22%3A%22genes.gene_id%22%2C%22value%22%3A%5B%22set_id%3AAWaQYFhbDMMVwdN36E0f%22%5D%7D%7D%5D%7D&genesTable_offset=" + \
                str((page - 1) * 100) + \
                "&genesTable_size=100&searchTableTab=genes"

            print("开始下载第" + str(page) + "页......")
            # 获取网页
            try:
                html = spider.getHtml(url, browser, page)
            except Exception as e:
                print(e)
                START_PAGE = page
                browser.quit()
                break
            # 初步解析网页
            r_list = spider.parseHtml(html, pattern="//tbody/tr")
            # 初步解析结果取值，并进一步解析，拼成要存储的格式
            for r in r_list:
                Gid = r.xpath("./td[2]//text()")
                if not Gid:
                    Gid = ["#"]
                symbol = r.xpath("./td[3]//text()")
                if not symbol:
                    symbol = ["#"]
                name = r.xpath("./td[4]//text()")
                if not name:
                    name = ["#"]
                Cytoband = r.xpath("./td[5]//text()")
                if not Cytoband:
                    Cytoband = ["#"]
                Type = r.xpath("./td[6]//text()")
                if not Type:
                    Type = ["#"]
                for i, _ in enumerate(Gid):
                    row = [Gid[i].strip(), symbol[i].strip(), name[i].strip(), Cytoband[
                        i].strip(), Type[i].strip()]
                    # 将一行写入csv文件
                    spider.writeHtml(row, f)
            print("第" + str(page) + "页下载完成。")

    print("下载完成。")
    f.close()
    browser.quit()
