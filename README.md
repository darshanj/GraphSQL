# GraphSQL
Graph Mining on SQL


### Relations

* Directed graph schema.
``` sql
TABLE GRAPH (src_id INT, desc_id INT, weight REAL)
```
note: Undirected graph schema is exaclty the same as directed graph, but each edge has doubly direction.

* Matrix schema
``` sql
TABLE MATRIX (row_id INT, col_id INT, value REAL)
```
* Vector schema
``` sql
TABLE VECTOR (id INT, value REAL)
```

### Fundemental SQL
- L2 norm of vector
``` sql
SELECT sqrt(sum((value)^2)) AS L2Norm FROM [vector table];
```
- vector dot product
``` sql
SELECT sum([vector table 1].value * [vector table 2].value) AS Dotproduct
FROM [vector table 1] INNER JOIN [vector table 2]
ON [vector table 1].id = [vector table 2].id;
```

- vector substraction
``` sql
--- vector minus vector
SELECT (COALESCE(A.value, 0) - COALESCE(B.value, 0)) AS diff
FROM [TABLE_TEST] AS A
FULL OUTER JOIN [TABLE_TEST_2] AS B
ON A.id = B.id;
``

- Matrix Multiplication (A X B)
``` sql
SELECT A.row_id, B.col_id, sum(A.value * B.value)
FROM [Matrix 1] AS A INNER JOIN [Matrix 2] AS B
ON A.col_id = B.row_id
GROUP BY A.row_id, B.col_id;
```
- Graph table times vector
``` sql
SELECT A.src_id, sum(A.weight, B.value)
FROM [Matrix 1] AS A INNER JOIN [Vector 1] AS B
ON A.col_id = B.id
GROUP BY A.src_id
```
- retrieve undirected graph from directed graph
``` sql
INSERT INTO [un_graph](src_id, dest_id, weight)
  SELECT src_id, dest_id, weight FROM [d_graph]
  UNION ALL
  SELECT dest_id "src_id", src_id "dest_id", weight FROM [d_graph];
```

### Degree
``` sql
-- graph out degree
CREATE VIEW graph_out_degree_view AS
  SELECT A.src_id, count(*) AS out_degree
  FROM GRAPH_TEST  AS A
  GROUP BY A.src_id
  ORDER BY A.src_id ASC;

-- graph in degree
CREATE VIEW graph_in_degree_view AS
  SELECT A.dest_id, count(*) AS in_degree
  FROM GRAPH_TEST  AS A
  GROUP BY A.dest_id
  ORDER BY A.dest_id ASC;


-- graph in degree distribution
CREATE VIEW graph_in_degree_dis_view AS
  SELECT degree_table.in_degree, count(*) AS count
  FROM (
    SELECT count(*) AS in_degree
    FROM GRAPH_TEST  AS A
    GROUP BY A.dest_id
  ) AS degree_table
  GROUP BY in_degree
  ORDER BY in_degree ASC;


-- graph out degree distribution
CREATE VIEW graph_out_degree_dis_view AS
  SELECT out_degree, count(*) AS count
  FROM (
    SELECT count(*) AS out_degree
    FROM GRAPH_TEST  AS A
    GROUP BY A.src_id
  ) AS degree_table
  GROUP BY out_degree
  ORDER BY out_degree ASC;

-- Degree distribution
CREATE VIEW graph_degree_dis_view AS
  SELECT degree, count(*) AS count
  FROM (
    SELECT count(*) AS degree
    FROM GRAPH_TEST  AS A
    GROUP BY A.dest_id
    UNION ALL
    SELECT count(*) AS Degree
    FROM GRAPH_TEST  AS A
    GROUP BY A.src_id
  ) AS degree_table
  GROUP BY degree
  ORDER BY degree ASC;
```

### Connected Component
```sql
--- Strongly Connected Component
--- need one more relation vertex_column
INSERT INTO [component_temp]
  SELECT T.id, MIN(T.component_id) AS component_id
  FROM (
    SELECT G.src_id as id, MIN(C.component_id) AS component_id
    FROM [graph table] AS G INNER JOIN [compenent] AS C
    ON G.dest_id = C.id
    GROUP BY G.src_id
    UNION
    SELECT * FROM [compenent]
  ) AS T
  GROUP BY T.id;
```
