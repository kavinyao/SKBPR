"""
Orchestrate recommender/splitter/evaluators to run a SKBPR test.
"""

class Tester(object):
    def __init__(self, dbm, recommender, splitter, evaluator, N):
        self.dbm = dbm
        self.recommender = recommender
        self.splitter = splitter
        self.evaluator = evaluator
        self.N = N

    def run(self):
        self.splitter.split('query')

        _round = 1
        while self.splitter.more_rounds():
            # advance to next train/test set
            self.splitter.next_round()
            self.evaluator.round_start()
            print 'Round', _round

            # train recommender
            self.recommender.preprocess('query_train')
            self.round_statistics()

            # start test
            for row in self.dbm.get_rows('SELECT id, query from query_test'):
                actual_products = self.get_actual_products(row['id'])
                recommended_products = set(rec[0] for rec in self.recommender.recommend(row['query'], self.N))
                self.evaluator.evaluate(actual_products, recommended_products)

            # let evaluate record result of this round
            self.evaluator.round_end()
            _round += 1

        # output summary of all results
        self.evaluator.summary()

    def round_statistics(self):
        """Get number of query, keywords, products, keyword-product relations of current round."""
        n_query = self.dbm.get_value("SELECT COUNT(*) FROM query_train")
        n_keyword = self.dbm.get_value("SELECT COUNT(*) FROM keyword")
        n_product = self.dbm.get_value("SELECT COUNT(DISTINCT product) FROM keyword_product_weight")
        n_relation = self.dbm.get_value("SELECT COUNT(*) FROM keyword_product_weight")

        print 'query: %d, keyword: %d, product: %d, relation: %d, A/M: %.2f%%' % (n_query, n_keyword, n_product, n_relation, 100.0*n_relation / (n_keyword*n_product))

    def get_actual_products(self, query_id):
        return set(row['product_name'] for row in self.dbm.get_rows('SELECT product_name FROM query_product WHERE query_id = %s', (query_id,)))
