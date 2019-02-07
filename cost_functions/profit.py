def profit_(history_status,calculated,ctx):

    initial = ctx.account.start_cur
    return (calculated["total_assets"]-initial)/initial