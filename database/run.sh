$docker_name = db_mysql
$password = 123456

if [ ! -d "/var/lib/db_mysql" ]; then
    mkdir /var/lib/db_mysql
fi

rm -rf /var/lib/db_mysql/gran.sql
cp -f ./gran.sql /var/lib/db_mysql/gran.sql

docker run --name $docker_name -e MYSQL_ROOT_PASSWORD=123456 -v /var/lib/db_mysql:/var/lib/mysql -p 3306:3306 -d mysql

docker exec $docker_name "mysql -u root -p $password -h 127.0.0.1  /var/lib/mysql/gran.sql"