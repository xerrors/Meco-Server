from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True,ssl_context=('./cert/6048997_www.xerrors.fun.pem', './cert/6048997_www.xerrors.fun.key'))

