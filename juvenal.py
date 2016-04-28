#from gcloud import bigquery
import yaml
from oauth2client.client import GoogleCredentials
import time
import redis
import re
from flask import Flask, request, session, g, redirect, url_for, \
     abort, render_template, flash
import pyodbc
import getpass
from os import getenv
from collections import namedtuple




app = Flask(__name__)

with open("config.yml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

with open("arcadia.sql", 'r') as queryfile:
	query = queryfile.read()

conn = pyodbc.connect(cfg['odbc_connection_string'])
cur = conn.cursor()


r = redis.StrictRedis(host='localhost', port=6379, db=0)

bad_words = ['with', 'and', 'patient', 'patients', 'taking', 'diagnosed', 'from','on','or','prescribed','vistited','who','had','test','exam', 'an', 'are', 'issues']

SearchMsg = namedtuple('SearchMsg',['searchterm', 'results'])

def load_redis():
	r.flushall()
	print 'REDIS Flushed'
	#orderterm_query = client.run_sync_query("select typestring from ArcBenchmarkNorm.Benchmark where tabletype = 'OR' and typestring != 'Needs Update' group by typestring")
	#orderterm_query.run()
	#order_terms, order_term_count, extra =  orderterm_query.fetch_data()
	cur = conn.cursor()
	print 'Cursor to Execute'
	cur.execute(query)
	terms = []
	Data = []
	termid = namedtuple('termid',['pat', 'date', 'term'])
	print 'starting cursor'
	for pat, date, term in cur:
		row = termid(pat=pat, date=date, term=term)
		Data.append(row)
		terms.append(term)
	terms = set(terms)
	print 'loading redis %s' % str(len(terms))
	for term in terms:
		print term
		years = {}
		t_set = []
		for x in Data:
			if term == x.term:
				t_set.append(x.pat)
			if years.get(str(x.date), []) == []:
				years[str(x.date)] = []
			years[str(x.date)].append(x.pat)
		t_set = set(t_set)
		if len(t_set) > 0:
			r.sadd(term, *t_set)
		for year, pat_ids in years.iteritems():
			r.sadd(year, *pat_ids)
	print 'all loaded'
	stmt = "Redis has loaded %s Terms" % str(len(r.keys('*')))
	Data = []
	terms = []
	print stmt
	return stmt

def in_text(text):
	wordlist = re.sub("[^\w]", " ",  text).split()
	outlist = []
	for y in wordlist:
		if y.lower() not in bad_words:
			outlist.append(y.lower())
	return outlist 

def get_sets(words):
	key_list = []
	for word in words:
		searchterm = '*%s*' % word
		keys = r.keys(searchterm)
		y = word, keys
		key_list.append(y)
		#r.keys(searchterm)
	return key_list
		#print r.keys(searchterm)

def get_ids(keylist):
	ids = []
	for word, keys in keylist:
		subid = []
		if len(keys) == 1:
			subid = r.smembers(keys[0])
		elif len(keys) > 1:
			subid = r.sunion(keys)
		subid = set(subid)
		ids.append(subid)
	idset = set.intersection(*ids)
	return idset

def id_data(idnum):
	query = "Select * from ArcBenchmarkNorm.Benchmark where PatientID = {!r} and tabletype in ('RX','RT','AS') and year = 2015 order by  year desc, DateRank limit 1000".format(str(idnum))
	pat_query = client.run_sync_query(query)
	print pat_query
	pat_query.run()
	pat, patcount, patextra = pat_query.fetch_data()
	return pat 

#load_redis()
#test = in_text('hydrocodone hypertension')
#keys = get_sets(test)
#get_ids(keys)




@app.route('/')
def juvenal():
    return render_template('juvenal.html', link=cfg['analytics_link'], pat=None, res=None )

@app.route('/loadredis')
def redis():
	msg = load_redis()
	flash(msg, 'msg')
	return render_template('juvenal.html', link=cfg['analytics_link'], pat=None, res=None)

@app.route('/search', methods=['GET','POST'])
def search():
    searchterm = request.form['searchterm']
    flash(searchterm, 'msg')
    id_ret = get_ids(get_sets(in_text(searchterm)))
    id_ret = list(id_ret)
    patcount = len(id_ret)
    if len(id_ret) > 200:
    	id_ret = id_ret[0:200]
    res = SearchMsg(searchterm, patcount)
    msg = 'Found %s IDs' % str(patcount)
    flash(msg, 'msg')
    print msg
    return render_template('juvenal.html', link=cfg['analytics_link'], pat=id_ret, res=res)

@app.route('/trace/<id>', methods=['GET','POST'])
def trace(id):
	pat = id_data(id)
	return render_template('trace.html', pat=pat)







app.secret_key = cfg['secret_key']

if __name__ == '__main__':
    app.run(debug=True)


##huge credit to http://codepen.io/anon/pen/OMEREJ

