BEGIN;

DROP TABLE IF EXISTS keyword_product_weight;
DROP TABLE IF EXISTS keyword;

CREATE TABLE IF NOT EXISTS keyword_query(
    id BIGINT(10) PRIMARY KEY AUTO_INCREMENT,
    keyword VARCHAR(255),
    query_id BIGINT(10),
    UNIQUE (keyword, query_id)
);

CREATE TABLE IF NOT EXISTS keyword(
    keyword VARCHAR(255) PRIMARY KEY,
    count BIGINT(10)
);

CREATE TABLE IF NOT EXISTS keyword_product_weight(
    id BIGINT(10) PRIMARY KEY AUTO_INCREMENT,
    keyword VARCHAR(255) NOT NULL,
    product VARCHAR(255) NOT NULL,
    weight FLOAT(10),
    KEY (keyword)
);

COMMIT;
