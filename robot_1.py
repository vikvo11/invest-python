from tinkoff.invest import Client, OrderDirection, OrderType, Quotation, StopOrderDirection, \
    StopOrderExpirationType, StopOrderType
import datetime
import creds

FIGI = "TCS00A1039N1"
lots = 1
fail_counter = 0

while (fail_counter < 6):
    with Client(creds.token_rw) as client:
        orders = client.orders.get_orders(account_id=creds.account_id).orders
        stop_orders = client.stop_orders.get_stop_orders(account_id=creds.account_id).stop_orders

        if len(orders) == 0 and len(stop_orders) == 0:

            market_order = client.orders.post_order(
                order_id=str(datetime.datetime.utcnow().timestamp()),
                figi=FIGI,
                quantity=lots,
                account_id=creds.account_id,
                direction=OrderDirection.ORDER_DIRECTION_BUY,
                order_type=OrderType.ORDER_TYPE_MARKET
            )

            print("Buy:" + str(market_order.initial_order_price.units) + ',' + str(market_order.initial_order_price.nano // 1000000))

            total_take_profit_price = (market_order.initial_order_price.units * 1000000000 + market_order.initial_order_price.nano) * 1.01
            price_take_profit_units = int(total_take_profit_price // 1000000000)
            price_take_profit_nano = int(total_take_profit_price % 1000000000 // 1000000 * 1000000)
            total_stop_loss_price = (market_order.initial_order_price.units * 1000000000 + market_order.initial_order_price.nano) * 0.99
            price_stop_loss_units = int(total_stop_loss_price // 1000000000)
            price_stop_loss_nano = int(total_stop_loss_price % 1000000000 // 1000000 * 1000000)

            limit_order_take_profit = client.orders.post_order(
                order_id=str(datetime.datetime.utcnow().timestamp()),
                figi=FIGI,
                quantity=lots,
                price=Quotation(units=price_take_profit_units, nano=price_take_profit_nano),
                account_id=creds.account_id,
                direction=OrderDirection.ORDER_DIRECTION_SELL,
                order_type=OrderType.ORDER_TYPE_LIMIT
            )

            print("TakeProfit price:" + str(price_take_profit_units) + ',' + str(price_take_profit_nano // 1000000))

            limit_order_stop_loss = client.stop_orders.post_stop_order(
                figi=FIGI,
                quantity=lots,
                stop_price=Quotation(units=price_stop_loss_units, nano=price_stop_loss_nano),
                direction=StopOrderDirection.STOP_ORDER_DIRECTION_SELL,
                account_id=creds.account_id,
                expiration_type=StopOrderExpirationType.STOP_ORDER_EXPIRATION_TYPE_GOOD_TILL_CANCEL,
                stop_order_type=StopOrderType.STOP_ORDER_TYPE_STOP_LOSS,
                expire_date=datetime.datetime(2023, 2, 22, 17, 29, 0, 420628, tzinfo=datetime.timezone.utc)
            )

            print("StopLoss price:" + str(price_stop_loss_units) + ',' + str(price_stop_loss_nano // 1000000))

        orders = client.orders.get_orders(account_id=creds.account_id).orders
        stop_orders = client.stop_orders.get_stop_orders(account_id=creds.account_id).stop_orders

        if len(orders) == 0 and len(stop_orders) != 0:

            stop_orders = client.stop_orders.get_stop_orders(account_id=creds.account_id).stop_orders

            cancel_stop_orders = client.stop_orders.cancel_stop_order(
                account_id=creds.account_id,
                stop_order_id=stop_orders[0].stop_order_id
            )

            fail_counter = 0
            lot = 1

            print("TakeProfit order completed")
            print(''
                  '')

        orders = client.orders.get_orders(account_id=creds.account_id).orders
        stop_orders = client.stop_orders.get_stop_orders(account_id=creds.account_id).stop_orders

        if len(orders) != 0 and len(stop_orders) == 0:

            cancel_orders = client.orders.cancel_all_orders(account_id=creds.account_id)

            fail_counter += 1
            lots *= 2

            print("StopLoss order completed" + "," + "FailCounter:" + str(fail_counter))
            print(''
                  '')
