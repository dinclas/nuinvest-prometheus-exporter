from flask import Flask, Response, request, jsonify
from pynuinvest import NuInvest
import os
app = Flask(__name__)

nu = NuInvest(solverr_url=os.environ["SOLVERR_URL"])

try:
    if ('NUINVEST_EASYTOKEN' in os.environ):
        nu.authenticate(os.environ['NUINVEST_USERNAME'], os.environ['NUINVEST_PASSWORD'], os.environ['NUINVEST_DEVICE_ID'],
                        os.environ['NUINVEST_EASYTOKEN'])
    else:
        nu.authenticate(os.environ['NUINVEST_USERNAME'], os.environ['NUINVEST_PASSWORD'], os.environ['NUINVEST_DEVICE_ID'])
    print('Authenticated')
except Exception as e:
    print('Failed to authenticate: ' + str(e))


@app.route('/metrics')
def metrics():  # put application's code here
    investments = nu.get_investment_data()
    result = ''
    result += "total_balance {}\n".format(investments['totalBalance'])

    for invesment in investments['investments']:
        result += "invested{{investment=\"{}\"}} {}\n".format(invesment["nickName"], invesment["investedCapital"])
        result += "net_value{{investment=\"{}\"}} {}\n".format(invesment["nickName"], invesment["netValue"])

    return Response(result, mimetype='text/plain')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    payload = request.json
    nu.authenticate(os.environ['NUINVEST_USERNAME'],
                    os.environ['NUINVEST_PASSWORD'],
                    os.environ['NUINVEST_DEVICE_ID'],
                    payload['otp'])

    return jsonify({ "result": "ok", "otp": payload['otp'] })

@app.route('/trust')
def trust_device():
    nu.trust_device(os.environ['NUINVEST_DEVICE_ID'])

if __name__ == '__main__':
    app.run()
