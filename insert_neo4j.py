from neo4j import GraphDatabase
import ijson
import json

filename = 'npm_dataset.json'
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"), encrypted=False)

def add_dependency(tx, package, dependency):
    tx.run("MERGE (n:Package {name: $name}) "
           "SET n.name = $name", name=package)
    tx.run("MERGE (n:Package {name: $name}) "
           "SET n.name = $name", name=dependency)
    tx.run("MATCH (a:Package),(b:Package) "
           "WHERE a.name = $package AND b.name = $dependency "
           "CREATE (a)-[r:DEPENDS_ON]->(b)",
           package=package, dependency=dependency)

def print_friends(tx, name):
    for record in tx.run("MATCH (a:Person)-[:KNOWS]->(friend) WHERE a.name = $name "
                         "RETURN friend.name ORDER BY friend.name", name=name):
        print(record["friend.name"])


f = open(filename, 'r')
packages = ijson.items(f, 'rows.item')

with driver.session() as session:
    for pkg in packages:
        name = pkg['doc']['name']
        latest_version = pkg['doc']['dist-tags'].get('latest')
        if not latest_version:
            continue
        dependencies = pkg['doc']['versions'].get(latest_version, {}).get('dependencies', {})
        print(name)
        for dep in dependencies.keys():
            print(json.dumps(dep, indent=4))
            session.write_transaction(add_dependency, name, dep)

'''with driver.session() as session:
    session.write_transaction(add_friend, "Arthur", "Guinevere")
    session.write_transaction(add_friend, "Arthur", "Lancelot")
    session.write_transaction(add_friend, "Arthur", "Merlin")
    session.read_transaction(print_friends, "Arthur")

driver.close()'''
