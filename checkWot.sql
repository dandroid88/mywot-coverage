CREATE TABLE IF NOT EXISTS chains
(
    chain_id INT NOT NULL,
	PRIMARY KEY (chain_id)
);

CREATE TABLE IF NOT EXISTS urls
(
	url_id INT NOT NULL,
	url VARCHAR(1024), 
	Trustworthiness INT, 
	Trust_confidence INT, 
	Vendor_Reliability INT, 
	Vendor_confidence INT, 
	Privacy INT, 
	Privacy_confidence INT, 
	Child_safety INT, 
	Child_confidence INT, 
    malicious INT,
    time_1 INT,
    time_2 INT,
    
    good_site INT,
    useful_informative INT,
    entertaining INT,
    good_cus_exper INT,
    child_friendly INT,
    spyware_adware INT,
    adult_content INT,
    other INT,

	PRIMARY KEY (url_id),
	FOREIGN KEY (url_id) REFERENCES chains(chain_id)
);

CREATE TABLE IF NOT EXISTS comments
(
	comment_id INT NOT NULL,
    comment_date date,
    author VARCHAR(100),
	text VARCHAR(64000),
    description VARCHAR(100),
    karma VARCHAR(100),
    upvotes INT,
    downvotes INT,
	PRIMARY KEY (comment_id),
	FOREIGN KEY (comment_id) REFERENCES urls(url_id)
);

