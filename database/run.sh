if [ ! -d "/var/lib/db_mysql" ]; then
    mkdir /var/lib/db_mysql
fi

rm -rf /var/lib/db_mysql/gran.sql
cp -f ./gran.sql /var/lib/db_mysql/gran.sql

docker run --name db_mysql -e MYSQL_ROOT_PASSWORD=123456 -v /var/lib/db_mysql:/var/lib/mysql -p 3306:3306 -d mysql

docker exec db_mysql "bash /var/lib/mysql/gran.sql"