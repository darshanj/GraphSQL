from sql import *
from util import *

def hello():
    print "HELLO WORD"


def file_to_table(db_instance, name="", data_path=""):
    lines = [line.rstrip('\r\n') for line in open(data_path)]
    cursor = db_instance.cursor()

    for line in lines:
        if line[0] == "#":
            continue
        vertice = line.split("\t")
        i = insert_table(name, [int(vertice[0]), int(vertice[1])])
        cursor.execute(i)
    db_instance.commit()
    return


def ugraph(db_instance, graph_src, graph_dst):
    cursor = db_instance.cursor()

    s = create_ugraph(graph_src, graph_dst)
    cursor.execute(s)
    db_instance.commit()


def get_ugraph_degree(db_instance, name=""):
    cursor = db_instance.cursor()
    query = graph_out_degree(name)
    cursor.execute(query)
    return cursor.fetchall()


def get_ugraph_k_degree_node(db_instance, name="", k=0):
    cursor = db_instance.cursor()
    query = graph_k_degree_top_one(name, k)
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows


def degree_distribution(db_instance ,data_path=""):
    cursor = db_instance.cursor()

    GRAPH_TABLE_TEST = "graph_temp"
    GRAPH_TABLE = "graph"
    GRAPH_SCHEMA = {"src_id":"INT", "dst_id":"INT"}

    g1 = create_table(GRAPH_TABLE, GRAPH_SCHEMA)
    #g1_index_op = creat_index_on_two_columns(GRAPH_TABLE, "dst_id", "src_id")
    #g1_index_op_2 = creat_index(GRAPH_TABLE, "dst_id")
    #g1_index_op_2_cluster = create_clustered_index(GRAPH_TABLE, "dst_id")
    cursor.execute(g1)
    #cursor.execute(g1_index_op)
    #cursor.execute(g1_index_op_2)
    #cursor.execute(g1_index_op_2_cluster)
    db_instance.commit()

    g2 = create_table(GRAPH_TABLE_TEST, GRAPH_SCHEMA)
    cursor.execute(g2)
    db_instance.commit()

    # load data into table
    file_to_table(db_instance, GRAPH_TABLE_TEST, data_path)

    # # create a undirected graph
    ugraph(db_instance, GRAPH_TABLE_TEST, GRAPH_TABLE)

    # create degree table
    DEGREE_TABLE = "degree_dis"
    DEGREE_SCHEMA = {"degree":"INT PRIMARY KEY", "count":"INT"}
    g4 = create_table(DEGREE_TABLE, DEGREE_SCHEMA)
    cursor.execute(g4)
    db_instance.commit()

    # generate degree table
    req = ugraph_insert_degree_distribution(DEGREE_TABLE, GRAPH_TABLE)
    cursor.execute(req)

    req = drop_table_if_exist(GRAPH_TABLE_TEST)
    cursor.execute(req)
    req = drop_table_if_exist(GRAPH_TABLE)
    cursor.execute(req)
    req = drop_table_if_exist(DEGREE_TABLE)
    cursor.execute(req)

    db_instance.commit()


def kcore(db_instance ,data_path="", index=False, composite_index=False, clustering_index=False):
    cursor = db_instance.cursor()

    GRAPH_TABLE_TEST = "graph_temp_kecore"
    GRAPH_TABLE = "graph_kcore"
    GRAPH_SCHEMA = {"src_id":"INT", "dst_id":"INT"}

    g1 = create_table(GRAPH_TABLE, GRAPH_SCHEMA)
    cursor.execute(g1)
    db_instance.commit()

    g2 = create_table(GRAPH_TABLE_TEST, GRAPH_SCHEMA)
    cursor.execute(g2)
    db_instance.commit()

    # load data into table
    file_to_table(db_instance, GRAPH_TABLE_TEST, data_path)

    # # create a undirected graph
    ugraph(db_instance, GRAPH_TABLE_TEST, GRAPH_TABLE)

    # build index on graph table
    if index == True:
        index_op= creat_index(GRAPH_TABLE, "dst_id")
        cursor.execute(index_op)
    elif composite_index == True:
        index_op = creat_index_on_two_columns(GRAPH_TABLE, "dst_id", "src_id")
        cursor.execute(index_op)

    if index == True and clustering_index == True:
        index_op = create_clustered_index(GRAPH_TABLE, "dst_id")
        cursor.execute(index_op)

    if (index or composite_index or clustering_index):
        db_instance.commit()

    # create coreness table
    CORENESS = "coreness"
    CORENESS_SCHEMA = {"id":"INT PRIMARY KEY", "core":"INT"}

    g3 = create_table(CORENESS, CORENESS_SCHEMA)
    cursor.execute(g3)
    db_instance.commit()

    # create degree table
    DEGREE_TABLE = "degree_table_kcore"
    DEGREE_SCHEMA = {"id":"INT PRIMARY KEY", "degree":"INT"}

    g4 = create_table(DEGREE_TABLE, DEGREE_SCHEMA)
    cursor.execute(g4)
    db_instance.commit()

    # generate degree table
    req = insert_out_degree(GRAPH_TABLE, DEGREE_TABLE)
    cursor.execute(req)
    db_instance.commit()

    # read degree table into memory
    req = select_from(DEGREE_TABLE)
    cursor.execute(req)
    # for each tuple in rows, id is the first element, degree is second.
    rows = cursor.fetchall()
    degree_dict = tuple_list_to_dict(rows)
    k = 2
    while len(degree_dict) != 0 :
        node_id = -1
        for id, degree in degree_dict.iteritems():
            if degree < k:
                node_id = id
                break
        if node_id == -1:
            k += 1
            continue

        # find one candidate which should be removed from graph.
        # and the coreness should be k-1
        insert_req = insert_table(CORENESS, [k-1, node_id])
        cursor.execute(insert_req)

        # After vertex removal, update the degree list
        # first step is delete current vertex
        degree_dict.pop(node_id, None)

        # get the neighbors of current vertex
        condition = " dst_id = %d" % id
        req = select_from(GRAPH_TABLE, "src_id", condition)
        cursor.execute(req)
        nodes = cursor.fetchall()
        for node in nodes:
            if node[0] in degree_dict:
                degree_dict[node[0]] -= 1
                if degree_dict[node[0]] == 0:
                    degree_dict.pop(node[0], None)
                    insert_req = insert_table(CORENESS, [k-1, node[0]])
                    cursor.execute(insert_req)
    db_instance.commit()
    req = drop_table_if_exist(GRAPH_TABLE_TEST)
    cursor.execute(req)
    req = drop_table_if_exist(GRAPH_TABLE)
    cursor.execute(req)
    req = drop_table_if_exist(DEGREE_TABLE)
    cursor.execute(req)
    req = drop_table_if_exist(CORENESS)
    cursor.execute(req)
    db_instance.commit()

def main():
    lines = [line.rstrip('\r\n') for line in open("/Users/amaliujia/Documents/github/GraphSQL/unit_test_sets/kcore_1.txt")]

    for line in lines:
        vertice = line.split("\t")
        i = insert_table("a", [int(vertice[0]), int(vertice[1])])
        print i



if __name__ == "__main__":
    main()
