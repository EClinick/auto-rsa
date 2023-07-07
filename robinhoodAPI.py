# Nelson Dane
# Robinhood API

import os
import traceback

import pyotp
import robin_stocks.robinhood as rh
from dotenv import load_dotenv

from helperAPI import Brokerage, printAndDiscord


def robinhood_init(ROBINHOOD_EXTERNAL=None):
    # Initialize .env file
    load_dotenv()
    # Import Robinhood account
    rh_obj = Brokerage("Robinhood")
    if not os.getenv("ROBINHOOD") and ROBINHOOD_EXTERNAL is None:
        print("Robinhood not found, skipping...")
        return None
    RH = (
        os.environ["ROBINHOOD"].strip().split(",")
        if ROBINHOOD_EXTERNAL is None
        else ROBINHOOD_EXTERNAL.strip().split(",")
    )
    # Log in to Robinhood account
    for account in RH:
        print("Logging in to Robinhood...")
        index = RH.index(account) + 1
        try:
            account = account.split(":")
            rh.login(
                username=account[0],
                password=account[1],
                mfa_code=None if account[2] == "NA" else pyotp.TOTP(account[2]).now(),
                store_session=False,
            )
            rh_obj.loggedInObjects.append(rh)
            rh_obj.add_account_number(
                f"Robinhood {index}", rh.account.load_account_profile(info="account_number")
            )
        except Exception as e:
            print(f"Error: Unable to log in to Robinhood: {e}")
            return None
        print("Logged in to Robinhood!")
    return rh_obj


def robinhood_holdings(rho, ctx=None, loop=None):
    print()
    print("==============================")
    print("Robinhood Holdings")
    print("==============================")
    print()
    rh = rho.loggedInObjects
    for obj in rh:
        try:
            # Get account holdings
            index = rh.index(obj) + 1
            positions = obj.get_open_stock_positions()
            if positions == []:
                printAndDiscord(f"No holdings in Robinhood {index}", ctx, loop)
            else:
                printAndDiscord(f"Holdings in Robinhood {index}:", ctx, loop)
                for item in positions:
                    # Get symbol, quantity, price, and total value
                    sym = item["symbol"] = obj.get_symbol_by_url(item["instrument"])
                    qty = float(item["quantity"])
                    try:
                        current_price = round(float(obj.stocks.get_latest_price(sym)[0]), 2)
                        total_value = round(qty * current_price, 2)
                    except TypeError as e:
                        if "NoneType" in str(e):
                            current_price = "N/A"
                            total_value = "N/A"
                    printAndDiscord(
                        f"{sym}: {qty} @ ${(current_price)} = ${total_value}", ctx, loop
                    )
        except Exception as e:
            printAndDiscord(f"Robinhood {index}: Error getting account holdings: {e}", ctx, loop)
            print(traceback.format_exc())


def robinhood_transaction(rho, action, stock, amount, price, time, DRY=True, ctx=None, loop=None):
    print()
    print("==============================")
    print("Robinhood")
    print("==============================")
    print()
    # printAndDiscord(
    #     "Robinhood transactions are temporarily disabled due to API issues. Please see https://github.com/jmfernandes/robin_stocks/pull/403 and https://github.com/jmfernandes/robin_stocks/issues/401 for more details.",
    #     ctx,
    #     loop,
    # )
    # return
    action = action.lower()
    stock = stock.upper()
    if amount == "all" and action == "sell":
        all_amount = True
    elif amount < 1:
        amount = float(amount)
    else:
        amount = int(amount)
        all_amount = False
    rh = rho.loggedInObjects
    for obj in rh:
        if not DRY:
            try:
                index = rh.index(obj) + 1
                # Buy Market order
                if action == "buy":
                    result = obj.order_buy_market(symbol=stock, quantity=amount)
                    printAndDiscord(f"Robinhood {index}: Bought {amount} of {stock}", ctx, loop)
                # Sell Market order
                elif action == "sell":
                    if all_amount:
                        # Get account holdings
                        positions = obj.get_open_stock_positions()
                        for item in positions:
                            sym = item["symbol"] = obj.get_symbol_by_url(item["instrument"])
                            if sym.upper() == stock:
                                amount = float(item["quantity"])
                                break
                    result = obj.order_sell_market(symbol=stock, quantity=amount)
                    printAndDiscord(
                        f"Robinhood {index}: Sold {amount} of {stock}: {result}", ctx, loop
                    )
                else:
                    print("Error: Invalid action")
                    return
            except Exception as e:
                printAndDiscord(f"Robinhood {index} Error submitting order: {e}", ctx, loop)
        else:
            printAndDiscord(
                f"Robinhood {index} Running in DRY mode. Trasaction would've been: {action} {amount} of {stock}",
                ctx,
                loop,
            )
