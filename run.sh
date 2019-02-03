git pull
docker build -t backtest .
docker run -it --rm --name backtest backtest