import urllib2
import json
import time
import ast
from textblob import TextBlob
import grammar_check

gc = grammar_check.LanguageTool('en-US')
hdr = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
           'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
           'Accept-Encoding': 'none',
           'Accept-Language': 'en-US,en;q=0.8',
           'Connection': 'keep-alive'}
departments = [{"id":1,"name":"Accounting"},{"id":2,"name":"Agriculture"},{"id":3,"name":"Anthropology"},{"id":4,"name":"Architecture"},{"id":5,"name":"Art History"},{"id":93,"name":"Biochemistry"},{"id":6,"name":"Biology"},{"id":7,"name":"Business"},{"id":8,"name":"Chemistry"},{"id":62,"name":"Civil Engineering"},{"id":9,"name":"Classics"},{"id":10,"name":"Communication"},{"id":11,"name":"Computer Science"},{"id":12,"name":"Criminal Justice"},{"id":13,"name":"Culinary Arts"},{"id":14,"name":"Design"},{"id":15,"name":"Economics"},{"id":16,"name":"Education"},{"id":17,"name":"Engineering"},{"id":18,"name":"English"},{"id":680,"name":"Epidemiology"},{"id":19,"name":"Ethnic Studies"},{"id":20,"name":"Film"},{"id":21,"name":"Finance"},{"id":22,"name":"Fine Arts"},{"id":1734,"name":"Geo Engineering"},{"id":2436,"name":"Geography & Earth Sciences"},{"id":25,"name":"Graphic Arts"},{"id":26,"name":"Health Science"},{"id":27,"name":"History"},{"id":28,"name":"Hospitality"},{"id":29,"name":"Humanities"},{"id":2310,"name":"Indigenous Studies"},{"id":30,"name":"Information Science"},{"id":135,"name":"International Studies"},{"id":32,"name":"Journalism"},{"id":333,"name":"Kinesiology"},{"id":1795,"name":"Kinesiology & Health"},{"id":33,"name":"Languages"},{"id":34,"name":"Law"},{"id":35,"name":"Literature"},{"id":36,"name":"Management"},{"id":37,"name":"Marketing"},{"id":38,"name":"Mathematics"},{"id":69,"name":"Mechanical Engineering"},{"id":39,"name":"Medicine"},{"id":1002,"name":"Multimedia"},{"id":40,"name":"Music"},{"id":1365,"name":"Neurological Sciences"},{"id":41,"name":"Nursing"},{"id":2609,"name":"Pathology & Molecular Medicine"},{"id":42,"name":"Philosophy"},{"id":43,"name":"Physical Education"},{"id":44,"name":"Physics"},{"id":45,"name":"Political Science"},{"id":46,"name":"Psychology"},{"id":47,"name":"Religion"},{"id":1392,"name":"Research"},{"id":48,"name":"Science"},{"id":49,"name":"Social Science"},{"id":50,"name":"Social Work"},{"id":51,"name":"Sociology"},{"id":533,"name":"TA"},{"id":731,"name":"Technology"},{"id":52,"name":"Theater"},{"id":53,"name":"Women's Studies"},{"id":54,"name":"Writing"}]


def mergeDicts(x,y):
    z = x.copy()
    z.update(y)
    return z

def getAllProfs():
    profs = []
    for x in departments:
        try:
            departmentname = x['name']
            url = 'http://search.mtvnservices.com/typeahead/suggest/?solrformat=true&rows=20&callback=noCB&q=*%3A*+AND+schoolid_s%3A1440+AND+teacherdepartment_s%3A%22'+departmentname+'%22&defType=edismax&qf=teacherfirstname_t%5E2000+teacherlastname_t%5E2000+teacherfullname_t%5E2000+autosuggest&bf=pow(total_number_of_ratings_i%2C2.1)&sort=total_number_of_ratings_i+desc&siteName=rmp&rows=20&start=0&fl=pk_id+teacherfirstname_t+teacherlastname_t+total_number_of_ratings_i+averageratingscore_rf+schoolid_s&fq=&prefix=schoolname_t%3A%22McMaster+University%22'
            req = urllib2.Request(url,headers=hdr)
            page = urllib2.urlopen(req).read()[5:-2]
            pagedic = ast.literal_eval(page)
            for teacher in pagedic['response']['docs']:
                tid = teacher['pk_id']
                fname = teacher['teacherfirstname_t']
                lname = teacher['teacherlastname_t']
                profs.append((str(fname + ' ' + lname),tid))
        except:
            pass
    return profs

def getID(teacher):
    name = '+'.join(teacher.split())
    url = 'http://search.mtvnservices.com/typeahead/suggest/?solrformat=true&rows=20&callback=noCB&q='+name+'&defType=edismax&qf=teacherfirstname_t%5E2000+teacherlastname_t%5E2000+teacherfullname_t%5E2000+autosuggest&bf=pow(total_number_of_ratings_i%2C1.7)&sort=score+desc&siteName=rmp&group=on&group.field=content_type_s&group.limit=20'
    req = urllib2.Request(url,headers=hdr)
    page = urllib2.urlopen(req).read()[5:-2]
    pagedic = ast.literal_eval(page)

    teacherID = pagedic["grouped"]["content_type_s"]["groups"][0]["doclist"]['docs'][0]['pk_id']   
    return teacherID

def getRatings(ID):
    url = 'http://www.ratemyprofessors.com/paginate/professors/ratings?tid='+str(ID)+'&page=1'

    req = urllib2.Request(url,headers=hdr)
    try:
        page = json.load(urllib2.urlopen(req))
    except ValueError:
        page = {'remaining':0}
    result = {'id':ID,
              'date':[],
              'quality':[],
              'difficulty':[],
              'name':[],
              'credit':[],
              'attendance':[],
              'textbook':[],
              'would_take_again':[],
              'comments':[],
              'sentiment':[],
              'grammar': [],
              }
    remaining= int(page['remaining'])
    if remaining:
        for rating in page['ratings']:
            result['date'] += [rating['rDate']]
            result['quality'] += [rating['rOverall']]
            result['difficulty'] += [rating['rEasy']]
            result['name'] += [rating['rClass']]
            result['credit'] += [rating['takenForCredit']]
            result['attendance'] += [rating['attendance']]
            result['textbook'] += [rating['rTextBookUse']]
            result['would_take_again'] += [rating['rWouldTakeAgain']]
            result['comments'] += [rating['rComments']]
            result['sentiment'] += [TextBlob(rating['rComments']).sentiment.polarity]
            result['grammar'] += [len(gc.check(rating['rComments']))]
    else:
        pass
                
    npage = 1
    while remaining > 0:
        npage +=1
        url = 'http://www.ratemyprofessors.com/paginate/professors/ratings?tid='+str(ID)+'&page='+str(npage)
        req = urllib2.Request(url,headers=hdr)
        try:
            page = json.load(urllib2.urlopen(req))
        except ValueError:
            pass
        remaining= int(page['remaining'])
        for rating in page['ratings']:
            result['date'] += [rating['rDate']]
            result['quality'] += [rating['rOverall']]
            result['difficulty'] += [rating['rEasy']]
            result['name'] += [rating['rClass']]
            result['credit'] += [rating['takenForCredit']]
            result['attendance'] += [rating['attendance']]
            result['textbook'] += [rating['rTextBookUse']]
            result['would_take_again'] += [rating['rWouldTakeAgain']]
            result['comments'] += [rating['rComments']]
            result['sentiment'] += [TextBlob(rating['rComments']).sentiment.polarity]
            result['grammar'] += [len(gc.check(rating['rComments']))]
    return result

def main():
    final = {}
    for teacher in getAllProfs():
        final[teacher[0]] = getRatings(teacher[1])

    with open('C:\Users\pdkar\Desktop\RMPData.json','w+') as RMPJson:
        json.dump(final,RMPJson)

if __name__ == "__main__":
    main()



