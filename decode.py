from flanker import mime
from bs4 import BeautifulSoup
import json , re

raw_email = "./01.eml"

with open(raw_email, 'rb') as fhdl:
    raw_email = fhdl.read()

msg = mime.from_string(raw_email)
msg_item = msg.headers.items()
demo = json.dumps(msg_item)
msg_parts = len(msg.parts)
msg_body = msg.body
for part in msg.parts:
    container = []
    container2 = []
    search_jobs = []
    sex_list = []
    if(part.content_type == "text/html"):
        #print(part.body)
        #list1 = part.body.split()
        #print(str(list1))
        soup = BeautifulSoup(part.body, "html.parser")
        # text_file = open("output3.html", "w")
        # text_file.write(soup.prettify())
        # text_file.close()
        result = soup.select('[style*="font-size:24px"]')
        #for item in result:
            #print(item.text)
        result2 = soup.select('b[style*="font-size:15px"]')
        res = soup.table.table
        x = res.find_all("tr")
        print(type(x))
        for item in x:
            q = item.text.replace(" ","").replace('\u3000',"").replace('▍',"").splitlines()
            container.append(q)
        v = list(filter(lambda x: x, container))
        #print(v)
        v.pop()
        for i in v:
            container2.append(i[0])        
        container2.pop(0)
        container2.pop(0)
        container2.pop()
        for p in container2:
            if "求職條件職務類別" in p:
                search_jobs.append(p)
            if("女" in p) | ("男" in p):
                sex_list.append(p)
        #print(sex_list)
        #print(search_jobs)
        # v.pop(0)
        # v.pop(0)
        # v.pop()
        # v.pop()
        tfile = open("list2.txt","w")
        tfile.write(str(container2))
        tfile.close()
        
        #for item in result2:
            #print(item.text)
        # test = soup.find_all("table")
        #print(test[0].find_all('b'))
        # for item in test:
        #     x = item.find_all('table')
        #     for i in x:
        #         z = i.find_all('table')
        #         print(len(z))
                # for t in z:
                #     u = t.find_all("b")
                #     res = t.text.replace('\n','').split(" ")
                #     while "" in res:
                #         res.remove("")