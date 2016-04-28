import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)

x = 'rx-nasacort'
y = x[x.find('-') + 1:len(x)]

def stringshort(key):
	y = key[key.find('-') + 1:len(key)]
	return y

longterms = r.keys('*')
short_list = []
for x in longterms:
	short_list.append(stringshort(x))

print short_list 