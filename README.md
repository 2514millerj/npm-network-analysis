# A Guide to Breaking the Web
The goal of this project is to identify both critical and weak links in the NPM dependecy graph. Anyone who has worked with NPM and Javascript knows of the "dependency hell" that awaits many frontend projects. I am using this as a playground to learn about graph databases and expand my graph and network theory knowledge. This repo contains the scripts I used to set up and run this project. This README is a summary of my experiments and conclusions along the way.

## Getting Data
NPM is run on top of Apache CouchDB, a document database with is built with the web in mind. Since it is a public-facing service there is actually an HTTP endpoint that allows for downloading the full database as JSON documents seperated by a new line. Running this command will pull all of the package.json data that has been registered to NPM:

	wget https://replicate.npmjs.com/_all_docs?include_docs=true npm_dataset.json

WARNING: at the time of download, this turned into a 40GB file.

## Loading Data
I chose Neo4j as my database to run queries against, mostly because I wanted to learn more about graph databases and this was an obvious application of a graph theory problem. At the time of this writing, the graph-data-science plugin is mostly still in alpha, but provides a lot of cool graph-based algorithms for centrality. Since it is so new and I like Docker, I had to pull and build my own docker image of neo4j in order to use the graph data science plugin:

	git clone https://github.com/neo4j/docker-neo4j.git
	NEO4JVERSION=3.5.17 make clean build
	docker run --publish=7474:7474 --publish=7687:7687 --rm --env NEO4JLABS_PLUGINS='["graph-data-science"]' custom-neo4j
	python3 insert_neo4j.py

## Centrality Tests and Results
These tests will identify critical nodes in the dependency graph. If these projects disappeared, there would be maximum damage to the network and a lot of things would break.

### Get packages with most dependents
I thought degree centrality was a good place to start analysis. Understanding which packages have the most dependents gives an idea of the most significant packages currently being used in the NPM ecosystem.

	MATCH (p:Package)
	RETURN p.name AS name,
	size((p)-[:DEPENDS_ON]->()) AS depends_on,
	size((p)<-[:DEPENDS_ON]-()) AS dependents
	ORDER BY dependents DESC

### Article rank query

	CALL gds.alpha.articleRank.stream({
	  nodeProjection: 'Package',
	  relationshipProjection: 'DEPENDS_ON',
	  maxIterations: 20,
	  dampingFactor: 0.85
	})
	YIELD nodeId, score
	RETURN gds.util.asNode(nodeId).name AS package,score
	ORDER BY score DESC

### Results

## Weak Link Tests and Results
The goal of these tests is to identify weak links in the network that would have strong cascading effects. For example, a lesser known package is being used by 3 popular packages. If it were to disappear, the 3 popular packages may break causing a large disruption.