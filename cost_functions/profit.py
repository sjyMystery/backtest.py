def profit_(history_status,calculated,ctx):
    initial = history_status.iloc[0,:]["currency"]

    return (calculated["total_assets"]-initial)/initial