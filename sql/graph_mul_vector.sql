DROP TABLE IF EXISTS GRAPH_TEST;
DROP TABLE IF EXISTS VECTOR_TEST;


CREATE TABLE GRAPH_TEST(src_id INT, dest_id INT, weight REAL);
CREATE TABLE VECTOR_TEST(id INT, value REAL);


INSERT INTO GRAPH_TEST VALUES(0, 0, 0);
INSERT INTO GRAPH_TEST VALUES(0, 1, 0);
INSERT INTO GRAPH_TEST VALUES(1, 0, 1);
INSERT INTO GRAPH_TEST VALUES(1, 1, 1);
INSERT INTO GRAPH_TEST VALUES(2, 0, 2);
INSERT INTO GRAPH_TEST VALUES(2, 1, 2);



INSERT INTO VECTOR_TEST VALUES(0, 1);
INSERT INTO VECTOR_TEST VALUES(1, 0);


SELECT A.src_id, sum(A.weight * B.value)
FROM GRAPH_TEST AS A INNER JOIN VECTOR_TEST AS B
ON A.dest_id = B.id
GROUP BY A.src_id;


DROP TABLE IF EXISTS GRAPH_TEST;
DROP TABLE IF EXISTS VECTOR_TEST;
