DROP TABLE IF EXISTS GRAPH_TEST;
DROP TABLE IF EXISTS GRAPH_TEST_U;


CREATE TABLE GRAPH_TEST(src_id INT, dest_id INT, weight REAL);
CREATE TABLE GRAPH_TEST_U(src_id INT, dest_id INT, weight REAL);


INSERT INTO GRAPH_TEST VALUES(0, 1, 1);
INSERT INTO GRAPH_TEST VALUES(1, 2, 1);


INSERT INTO GRAPH_TEST_U(src_id, dest_id, weight)
  SELECT src_id, dest_id, weight FROM GRAPH_TEST
  UNION ALL
  SELECT dest_id "src_id", src_id "dest_id", weight FROM GRAPH_TEST;

SELECT * FROM GRAPH_TEST_U;


DROP TABLE IF EXISTS GRAPH_TEST;
DROP TABLE IF EXISTS GRAPH_TEST_U;
