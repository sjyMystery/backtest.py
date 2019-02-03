docker_name=db_mysql
password=123456
expose_port=3399
temp_path="/tmp/$docker_name"

echo $temp_path

if [ ! -d "$temp_path/" ]; then
    mkdir $temp_path
fi

gran_path="$temp_path/gran.sql"

rm -rf $gran_path

cp ./gran.sql $temp_path/gran.sql
cp ./grant.sh $temp_path/grant.sh
docker run -it --name $docker_name -e MYSQL_ROOT_PASSWORD=$password -v $temp_path:/fuck_script_saving_path -p $expose_port:3306 -d mysql:5.6


# temporaily deleted this line....
# docker exec -ti -w /fuck_script_saving_path $docker_name sh -c "mysql $password -h 127.0.0.1 -uroot -p123456"