from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def format_money(value):
    try:
        amount = Decimal(str(value or 0))
    except (InvalidOperation, ValueError):
        amount = Decimal('0')

    if amount == amount.to_integral_value():
        formatted = f'{int(amount):,}'.replace(',', ' ')
    else:
        amount = amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        formatted = f'{amount:,.2f}'.replace(',', ' ').rstrip('0').rstrip('.')

    return f'€{formatted}'
