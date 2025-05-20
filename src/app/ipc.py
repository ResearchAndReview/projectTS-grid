from flask import Flask, request

app= Flask("HTTP API")

@app.route('/', methods=['GET'])
def test():
    return "Hello World", 200

def run_server():
    app.run(host="127.0.0.1", port=57858)