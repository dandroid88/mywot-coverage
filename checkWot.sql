-- Drop all of the tables
-- drop table chains, urls, comments;


CREATE TABLE IF NOT EXISTS chains
(
    chain_id INT AUTO_INCREMENT PRIMARY KEY,
    original_url VARCHAR(1024)
);

INSERT INTO chains(original_url) VALUES ('Not a Chain');

CREATE TABLE IF NOT EXISTS urls
(
	url_id INT AUTO_INCREMENT PRIMARY KEY,
	url VARCHAR(1024), 
    
	Trustworthiness INT, 
	Trust_confidence INT, 
	Vendor_Reliability INT, 
	Vendor_confidence INT, 
	Privacy INT, 
	Privacy_confidence INT, 
	Child_safety INT, 
	Child_confidence INT, 

    spam INT,
    occurances INT,    
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

	FOREIGN KEY (url_id) REFERENCES chains(chain_id)
);

CREATE TABLE IF NOT EXISTS comments
(
	comment_id INT AUTO_INCREMENT PRIMARY KEY,
    comment_date date,
    author VARCHAR(100),
	text VARCHAR(64000),
    description VARCHAR(100),
    karma VARCHAR(100),
    votesEnabled INT,
    upvotes INT,
    downvotes INT,
	FOREIGN KEY (comment_id) REFERENCES urls(url_id)
);

