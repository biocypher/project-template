sleep 15
echo "Creating database 'docker'"
cypher-shell -u $NEO4J_USER -p $NEO4J_PASSWORD "create database docker;"
echo "Database created!"