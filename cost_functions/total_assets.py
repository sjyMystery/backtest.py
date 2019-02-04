def total_assets(history_status,calculated,ctx):

    now = history_status.iloc[-1,:]
    cash = now["currency"]
    goods = now["amounts"] * now["bid_low"]

    return cash+goods*(1-ctx["trade_cost"])