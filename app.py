import sys

from flask import Flask, Response, request, jsonify
from pynuinvest import NuInvest
import os
import time

app = Flask(__name__)

nu = NuInvest(solverr_url=os.environ["SOLVERR_URL"])

last_login = None

def login():
    global last_login
    if last_login and time.time() - last_login < 60 * 60:
        print('already logged')
        return

    try:
        if ('NUINVEST_EASYTOKEN' in os.environ):
            nu.authenticate(os.environ['NUINVEST_USERNAME'], os.environ['NUINVEST_PASSWORD'],
                            os.environ['NUINVEST_DEVICE_ID'],
                            os.environ['NUINVEST_EASYTOKEN'])
        else:
            nu.authenticate(os.environ['NUINVEST_USERNAME'], os.environ['NUINVEST_PASSWORD'],
                            os.environ['NUINVEST_DEVICE_ID'])
        last_login = time.time()
        print('Authenticated')
    except Exception as e:
        print('Failed to authenticate: ' + str(e))

@app.route('/metrics')
def metrics():
    login()

    investments = nu.get_investment_data()
    result = ''
    result += "total_balance {}\n".format(investments['totalBalance'])

    invested_in_fundos = 0
    total_in_fundos = 0

    for invesment in investments['investments']:
        if invesment['settlement'] or invesment['investmentType']['description'] != 'Fundos de Investimento':
            continue

        invested_in_fundos += invesment['investedCapital']
        total_in_fundos += invesment['netValue']

        investment_percentage = invesment['investedCapital'] / investments['totalBalance']
        investment_roe = (invesment["netValue"] - invesment["investedCapital"]) / invesment["investedCapital"] * 100
        investment_index = investment_percentage * investment_roe
        result += "invested{{investment=\"{}\"}} {}\n".format(invesment["nickName"], invesment["investedCapital"])
        result += "net_value{{investment=\"{}\"}} {}\n".format(invesment["nickName"], invesment["netValue"])
        result += "index{{investment=\"{}\"}} {}\n".format(invesment["nickName"], investment_index)

    result += "invested_in_fundos {}\n".format(invested_in_fundos)
    result += "total_in_fundos {}\n".format(total_in_fundos)

    return Response(result, mimetype='text/plain')


@app.route('/authenticate', methods=['POST'])
def authenticate():
    payload = request.json
    nu.authenticate(os.environ['NUINVEST_USERNAME'],
                    os.environ['NUINVEST_PASSWORD'],
                    os.environ['NUINVEST_DEVICE_ID'],
                    payload['otp'])

    return jsonify({"result": "ok", "otp": payload['otp']})


@app.route('/trust')
def trust_device():
    nu.trust_device(os.environ['NUINVEST_DEVICE_ID'])


if __name__ == '__main__':
    app.run()
