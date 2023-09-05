# changecredentialsbeforeusing
while True:
    import time
    import datetime
    from datetime import datetime

    def get_current_time():
        current_time = datetime.now()
        time_str = current_time.strftime('%H%M%S')
        return int(time_str)
    current_time = get_current_time()
    if 90000 <= current_time <= 150100:

        import re
        from NorenRestApiPy.NorenApi import NorenApi
        import pandas as pd

        class ShoonyaApiPy(NorenApi):
            def __init__(self):
                NorenApi.__init__(self, host='https://api.shoonya.com/NorenWClientTP/',
                                  websocket='wss://api.shoonya.com/NorenWSTP/')
                global api
                api = self

        # import logging
        import pyotp
        # enable dbug to see request and responses
        # logging.basicConfig(level=logging.DEBUG)
        import urllib3
        # Set the connect timeout to 60 seconds
        timeout = urllib3.util.timeout.Timeout(connect=150)
        # Set the timeout as the default timeout for all HTTPS connections
        urllib3.util.ssl_.DEFAULT_TIMEOUT = timeout

        # start of our program
        api = ShoonyaApiPy()
        # credentials

        uid = 'user id'
        pwd = 'password'
        vc = 'vander code'
        app_key = 'api key'
        imei = 'abc1234'
        token = 'totp'
        twoFA = pyotp.TOTP(token).now
        ret = api.login(userid=uid, password=pwd, twoFA=pyotp.TOTP(
            token).now(), vendor_code=vc, api_secret=app_key, imei=imei)

        sd = api.searchscrip('NFO', 'NIFTY')
        sd = (sd['values'])
        for Symbol in sd:
            (Symbol['tsym'])

        tsym_values = [Symbol['tsym'] for Symbol in sd]

        dates = [re.search(r'\d+[A-Z]{3}\d+', tsym).group()
                 for tsym in tsym_values]
        formatted_dates = [datetime.strptime(
            date, '%d%b%y').strftime('%Y-%m-%d') for date in dates]
        sorted_formatted_dates = sorted(formatted_dates)
        sorted_dates = [datetime.strptime(
            date, '%Y-%m-%d').strftime('%d%b%y').upper() for date in sorted_formatted_dates]
        Expiry_date = (sorted_dates[0])
        print(Expiry_date)

        def retry_api_call(api_call_function, *args, max_attempts=5, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return api_call_function(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    print(
                        f'API call {api_call_function.__name__} failed: {e}. Retrying...')
            raise Exception(f'API call failed after {max_attempts} attempts.')

        def get_order_status(norenordno):
            OB = api.get_order_book()
            for item in OB:
                if item['norenordno'] == norenordno and item['status'] == 'REJECTED':
                    return item['rejreason']
            print(f"{norenordno} successfully placed")
            return ""

        def get_fillprice(norenordno):
            TB = api.get_trade_book()
            if TB is None:
                print('no order placed for the day')
            else:
                for item in TB:
                    if item['norenordno'] == norenordno:
                        return item['flprc']
            return "1"

        Mtm_SL = 1600
        # Mtm_target=4000

        import time

        def get_daily_mtm():
            while True:
                try:
                    ret = api.get_positions()
                    break
                except Exception:
                    print('Error Fetching MTM')
                    time.sleep(1)
                    continue
            mtm = 0
            pnl = 0
            day_m2m = ''
            try:
                for i in ret:
                    mtm += float(i['urmtom'])
                    pnl += float(i['rpnl'])
                    day_m2m = round(mtm + pnl, 2)
            except TypeError:
                print(
                    'no open positions for the day, waiting for 1 minute before checking again')
                time.sleep(60)
            return (day_m2m)

        def CE_entry(CE_SYMBOL):
            CE_order = api.place_order(buy_or_sell='S', product_type='I', exchange='NFO', tradingsymbol=CE_SYMBOL,
                                       quantity=50, discloseqty=0, price_type='MKT', price=0, trigger_price=0, retention='DAY', remarks='CEleg')
            time.sleep(2)
            CE_orderno = CE_order['norenordno']

            CE_orderSL = api.place_order(buy_or_sell='B', product_type='I', exchange='NFO', tradingsymbol=CE_SYMBOL, quantity=50,
                                         discloseqty=0, price_type='SL-LMT', price=SL_CE, trigger_price=SLT_CE, retention='DAY', remarks='my_CE-SL')
            time.sleep(3)
            SL_CE_Number = CE_orderSL['norenordno']

            for_call_entry_sl = [CE_orderno, SL_CE_Number, CE_order]
            return for_call_entry_sl

        def PE_entry(PE_SYMBOL):
            PE_order = api.place_order(buy_or_sell='S', product_type='I', exchange='NFO', tradingsymbol=PE_SYMBOL,
                                       quantity=50, discloseqty=0, price_type='MKT', price=0, trigger_price=0, retention='DAY', remarks='PEleg')
            time.sleep(2)
            PE_orderno = PE_order['norenordno']

            PE_orderSL = api.place_order(buy_or_sell='B', product_type='I', exchange='NFO', tradingsymbol=PE_SYMBOL, quantity=50,
                                         discloseqty=0, price_type='SL-LMT', price=SL_PE, trigger_price=SLT_PE, retention='DAY', remarks='my_PE-SL')
            time.sleep(3)
            SL_PE_Number = PE_orderSL['norenordno']

            for_put_entry_sl = [PE_orderno, SL_PE_Number, PE_order]
            return for_put_entry_sl

        def sl_calculate(CE_orderno, PE_orderno):
            # you can change the stoploss here
            CE_fillprice = (get_fillprice(CE_orderno))
            PE_fillprice = (get_fillprice(PE_orderno))
            print(CE_fillprice, PE_fillprice)
            CE_fillprice = float(CE_fillprice)
            PE_fillprice = float(PE_fillprice)
            SL_CE = float(
                format(round(CE_fillprice * 0.9 / 0.05) * 0.05, '.2f'))
            SL_PE = float(
                format(round(PE_fillprice * 0.9 / 0.05) * 0.05, '.2f'))
            SLT_CE = format(round(SL_CE * .97 / 0.05) * 0.05, '.2f')
            SLT_PE = format(round(SL_PE * .97 / 0.05) * 0.05, '.2f')
            print(SL_PE, SLT_PE)
            print(SL_CE, SLT_CE)
            sls = [SL_CE, SL_PE, SLT_CE, SLT_PE]
            return sls

        def universal_exit():
            try:
                while True:
                    try:
                        k = api.get_positions()
                        k = pd.DataFrame(k)
                        ob = api.get_order_book()
                        ob = pd.DataFrame(ob)
                        break
                    except Exception:
                        print('uni_exit error fetching positions/orders')
                        time.sleep(1)
                        continue

                for i in ob.itertuples():
                    if i.status == 'TRIGGER_PENDING':
                        ret = api.cancel_order(i.norenordno)  # cancel all
                    if i.status == 'OPEN':
                        ret = api.cancel_order(i.norenordno)

                for i in k.itertuples():
                    if int(i.netqty) < 0:
                        api.place_order(buy_or_sell='B', product_type=i.prd, exchange=i.exch, tradingsymbol=i.tsym, quantity=abs(int(i.netqty)), discloseqty=0, price_type='MKT', price=0, trigger_price=None,
                                        retention='DAY', remarks='Buy_All')
                    if int(i.netqty) > 0:
                        api.place_order(buy_or_sell='S', product_type=i.prd, exchange=i.exch, tradingsymbol=i.tsym, quantity=int(i.netqty), discloseqty=0, price_type='MKT', price=0, trigger_price=None,
                                        retention='DAY', remarks='Sell_All')
                return True
            except Exception:
                return False

        exit_flag = False

        while True:
            current_time = get_current_time()
            if current_time > 145500:
                print("Time is greater than 145500")
                break
            elif current_time > 92500:
                def get_atm_symbol():
                    ret = api.get_quotes(exchange='NSE', token='26000')
                    time.sleep(3)
                    ltp = ret.get("lp")
                    ltp = float(ltp)
                    ltp_str = str(ltp)
                    sym = ret.get("symname")
                    ExpDate = Expiry_date
                    TYPE = "P"
                    Strike = int(round(ltp/50, 0)*50)

                    For_token = sym+ExpDate+TYPE+str(Strike)
                    CE_SYMBOL = sym+ExpDate+'C'+str(Strike)
                    PE_SYMBOL = sym+ExpDate+'P'+str(Strike)
                    print(CE_SYMBOL, PE_SYMBOL)
                    both_symbol = [CE_SYMBOL, PE_SYMBOL]
                    return both_symbol
                    # print(Strike)

                both_symbol = get_atm_symbol()
                CE_SYMBOL = both_symbol[0]
                PE_SYMBOL = both_symbol[1]

                CE_order_values = CE_entry(CE_SYMBOL).CE_order
                PE_order_values = PE_entry(PE_SYMBOL).PE_order
                CE_orderno = CE_order_values[0]
                SL_CE_Number = CE_order_values[1]
                PE_orderno = PE_order_values[0]
                SL_PE_Number = PE_order_values[1]
                CE_order = CE_order_values[2]
                PE_order = PE_order_values[2]

                if PE_order['stat'] == 'Ok' and CE_order['stat'] == 'Ok':
                    print(f"Order {CE_orderno} & {PE_orderno} Status is ok ")
                else:
                    print(CE_order['emsg'], PE_order['emsg'])
                time.sleep(3)

                print(get_order_status(CE_orderno), "FOR CE LEG")
                print(get_order_status(PE_orderno), "FOR PE LEG")

                sls = sl_calculate(CE_orderno, PE_orderno)
                SL_CE = sls[0]
                SL_PE = sls[1]
                SLT_CE = sls[2]
                SLT_PE = sls[3]

                print(SL_CE_Number, SL_PE_Number)
                time.sleep(3)

                print(get_order_status(SL_CE_Number), "FOR SL CE LEG")
                print(get_order_status(SL_PE_Number), "FOR SL PE LEG")
                time.sleep(5)

                while True:
                    mtm = get_daily_mtm()
                    try:
                        Sl_mtm = mtm <= (-Mtm_SL)
                        # Target_mtm = mtm >= Mtm_target
                    except TypeError:
                        pass
                    try:
                        if Sl_mtm:  # or Target_mtm :
                            print(
                                'MTM SL OR TARGET Exiting positions and cancelling all standing orders ')
                            universal_exit()
                            exit_flag = True  # set flag to exit outer loop
                            break  # exit inner loop
                    except NameError:
                        pass

                    time.sleep(1)

                    if get_current_time() > 145500:
                        print(
                            "It's after 3pm, calling universal exit-Exiting positions and cancelling all standing orders")
                        universal_exit()
                        exit_flag = True  # set flag to exit outer loop
                        break  # exit inner loop

            elif current_time < 92400:
                print("Time is less than 92400")
            if exit_flag:
                break  # exit outer loop
            time.sleep(20)
    else:
        print('Market is Close')
    time.sleep(120)
