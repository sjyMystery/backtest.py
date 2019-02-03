git pull
docker build -t backtest .
docker run -it --link mysql:db --rm --name backtest backtest