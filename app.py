from flask import Flask, Response
from pynuinvest import NuInvest
import os
app = Flask(__name__)

nu = NuInvest(solverr_url=os.environ["SOLVERR_URL"])
nu.authenticate(os.environ['NUINVEST_USERNAME'], os.environ['NUINVEST_PASSWORD'], os.environ['NUINVEST_DEVICE_ID'], os.environ['NUINVEST_EASYTOKEN'])

@app.route('/metrics')
def metrics():  # put application's code here
    investments = nu.get_investment_data()
    result = ''
    result += "total_balance {}\n".format(investments['totalBalance'])

    for invesment in investments['investments']:
        result += "invested{{investment=\"{}\"}} {}\n".format(invesment["nickName"], invesment["investedCapital"])
        result += "net_value{{investment=\"{}\"}} {}\n".format(invesment["nickName"], invesment["netValue"])

    return Response(result, mimetype='text/plain')

if __name__ == '__main__':
    app.run()
