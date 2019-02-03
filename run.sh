git pull
./database/run.sh # run_mysql_first
docker build -t backtest .
docker run -it --link db_mysql:db --rm --name backtest backtest