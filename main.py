from bs4 import BeautifulSoup
import requests

url = 'https://wink.ru/faq?selected=7'
page = requests.get(url)
soup = BeautifulSoup(page.text, "html.parser")
problems = soup.findAll('span', class_='root_subtitle3_reg964v')
names = []
flag = False
for problem in problems:
    if problem.text == 'Подписки для ритейла':
        flag = True
    elif flag:
        names.append(problem.text)

print(names)

url = 'https://wink.ru/faq/'
res = [60, 61, 62, 63, 130, 64, 126, 152]
with open('nas.txt', 'w', encoding='utf-8') as file:
    for i in range(len(names)):
        page = requests.get(url + str(res[i]))
        soup = BeautifulSoup(page.text, "html.parser")
        problems = soup.findAll('p')
        num = 1
        print("Url", url + str(res[i]))
        lis = []
        for problem in problems:
            if problem.text == 'Техническая поддержка':
                file.write(names[i] + '$$$' + '___'.join(lis) + '\n')
                break
            if problem.text.strip() != '':
                lis.append(f"{num}) {problem.text}")
                num += 1