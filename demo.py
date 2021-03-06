import random
import config
from database import DatabaseManager
from recommender import KeywordRecommender
from bottle import Bottle, run, request, view, static_file

N = 5

class get_dbm(object):
    def __enter__(self):
        self.dbm = DatabaseManager(config.DB_HOST, config.DB_USER, config.DB_PASSWORD, config.DB_NAME)
        return self.dbm

    def __exit__(self, type, value, traceback):
        self.dbm.close()

# Real business begins
app = Bottle()

# Serve static files
STATIC_DIRECTORY = './demo-static'
@app.route('/static/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath, root=STATIC_DIRECTORY)

@app.route('/')
@view('home')
def home():
    with get_dbm() as dbm:
        group = random.randint(1, 10)
        query = 'SELECT query FROM query WHERE group_id = %d ORDER BY RAND() LIMIT 10' % group
        queries = [row['query'] for row in dbm.get_rows(query)]
        products = transfrom_results(get_hot_products(dbm))

    if not queries:
        print 'No quries selected', group

    return {
        'queries': queries,
        'products': products,
    }

@app.post('/update')
@view('recommendations')
def update_suggestions():
    query = request.POST.query
    with get_dbm() as dbm:
        recommender = KeywordRecommender(dbm, config.WordSegmenter(), None)
        recommender.set_limit(N)
        products = [rec[0] for rec in recommender.recommend(query)]

        # make sure sufficient number of products is recommended
        rec_num = len(products)
        if rec_num < N:
            products.extend(get_hot_products(dbm)[:N-rec_num])

        products = transfrom_results(products)
    return {'products': products}

def get_hot_products(dbm):
    # source hot_cache.sql to make things go smoothly
    hot_product_query = 'SELECT product FROM hot_cache ORDER BY weight DESC LIMIT %d' % N
    products = [row['product'] for row in dbm.get_rows(hot_product_query)]
    return products

def get_image_url(p):
    i = abs(p.__hash__()) % 10 + 1
    return '/static/images/glasses%d.jpg' % i

def transfrom_results(products):
    return [(p, get_image_url(p)) for p in products]

run(app, host='localhost', port=8080, debug=True)
