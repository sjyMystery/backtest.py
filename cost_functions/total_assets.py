def total_assets(history_status,calculated,ctx):
    return history_status.iloc[-1,:]["assets"]