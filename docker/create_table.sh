#!/bin/bash
# echo "Starting Neo4j"
# neo4j start
sleep 10
echo "Creating database 'docker'"
cypher-shell -u neo4j -p neo4jpassword "create database docker;"
echo "Database created!"