git pull
docker build -t backtest .
docker run -it --link mysql:mysql --rm --name backtest backtest