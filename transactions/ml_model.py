def predict_risk(amount):
    if amount > 15000:
        return 0.8
    elif amount > 8000:
        return 0.5
    else:
        return 0.2
