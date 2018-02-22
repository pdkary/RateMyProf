import urllib2
import json
import ast
from bs4 import BeautifulSoup
from django.utils.encoding import smart_str, smart_unicode
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
with open('C:\Users\pdkar\Desktop\RMPDataCompressed.json','r+') as RMP:
    rmpdata = json.load(RMP)

def getDept(ID):
    url = 'http://www.ratemyprofessors.com/ShowRatings.jsp?tid='+str(ID)
    
    req = urllib2.Request(url,headers=hdr)
    page = urllib2.urlopen(req).read()
    soup = BeautifulSoup(page,"lxml")

    divs = soup.find('div',{'class':'result-title'})
    return divs.getText().split()[3]

for prof in rmpdata:
    i=0
    for comment in rmpdata[prof]['comments']:
        comlist = comment.split(',')
        rmpdata[prof]['comments'][i] = ' '.join(comlist)
        i+=1
                
    resultlist = [x for x in rmpdata[prof]] + ['\n']
    for rl in range(len(rmpdata[prof]['attendance'])):
        for field in rmpdata[prof]:
            if field != 'id':
                resultlist.append(rmpdata[prof][field][rl])
            else:
                if rl == 0:
                    resultlist.append(getDept(rmpdata[prof]['id']))
        resultlist.append('\n')
    filename = 'C:\Users\pdkar\Desktop\Excel\RMP\\' +prof+ ' ' + str(rmpdata[prof]['id'])+'.csv'
    with open(filename,'w+') as newfile:
        for x in resultlist:
            if x != '\n':
                newfile.write(smart_str(x)+',')
            else:
                newfile.write(smart_str(x))


        
            

        



    
