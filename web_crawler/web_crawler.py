import requests
import re
import csv
from bs4 import BeautifulSoup

def fetch_page(url, headers=None):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # 確保響應狀態是200
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    # 使用CSS选择器找到所有符合条件的div元素
    # matching_divs = soup.select('div[data-testid="asset-card"][class_*="resultCard_topNameCard_MHzBA"]')
    matching_divs = soup.select('div', class_='resultCard_topNameCard_MHzBA card')
    print(len(matching_divs))
    print(matching_divs)
    # 输出匹配的元素
    for div in matching_divs:
        print("===============================================================")
        print("Div: ",div.get_text())

def main():
    url = 'https://d3.app/'  # crawling website
    header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
    html = fetch_page(url, headers=header) # return response.text
    if html:
        parse_html(html)

if __name__ == "__main__":
    main()


#======================================================================================
# def main():
# 	url = 'https://d3.app/search?product=upbit.shib'
# 	header = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}
# 	response = requests.get(url, headers=header)
# 	html = response.text  # .text取得<></>中間的內容
# 	soup = BeautifulSoup(html)
# 	tags = soup.find_all('span', {'class': 'sc-14dd939d-6 kHVqMR cli-title-metadata-item'})
# 	d = {}
# 	for tag in tags:
# 		if tag.text.isdigit():  # 只取出純數字的結果，也就是只有年分
# 			year = tag.text
# 			if year not in d:
# 				d[year] = 1
# 			else:
# 				d[year] += 1
# 	for year, count in sorted(d.items(), key=lambda t: t[1]):
# 		print(year, '-->', count)


# if __name__ == '__main__':
# 	main()