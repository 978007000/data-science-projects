import yaml
import os
from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client

credentials = yaml.load(open(os.path.expanduser('~/api_neo4j_cred.yml')))

USER_NAME = credentials['ec2_neo4j']['user']
USER_PASSWORD = credentials['ec2_neo4j']['password']

db = GraphDatabase("http://ec2-54-91-189-236.compute-1.amazonaws.com:7474", username=USER_NAME,
                   password=USER_PASSWORD)

# Create some nodes with labels
user = db.labels.create("Organizer")
u1 = db.nodes.create(name="Rob")
user.add(u1)
u2 = db.nodes.create(name="Toby")
user.add(u2)
u3 = db.nodes.create(name="Howard")
user.add(u3)

topics = db.labels.create("Topics")
t1 = db.nodes.create(name="Social Networking")
t2 = db.nodes.create(name="Entrepreneurship")
t3 = db.nodes.create(name="Web Technology")
# You can associate a label with many nodes in one go
topics.add(t1, t2, t3)

# User-organizes->Topic relationships
u1.relationships.create("organizes", t1)
u2.relationships.create("organizes", t2)
u3.relationships.create("organizes", t3)
# Bi-directional relationship?
u1.relationships.create("friends", u2)
u1.relationships.create("friends", u3)
u2.relationships.create("friends", u3)

q = 'MATCH (u:User)-[r:organizes]->(m:Topics) WHERE u.name="Rob" RETURN u, type(r), m'
# "db" as defined above
results = db.query(q, returns=(client.Node, str, client.Node))
for r in results:
    print("(%s)-[%s]->(%s)" % (r[0]["name"], r[1], r[2]["name"]))
