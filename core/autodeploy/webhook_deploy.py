#!/usr/bin/env python3
import os
from flask import Flask, request, abort
import subprocess

app = Flask(__name__)

# Set a secret token for security
SECRET_TOKEN = "15577fd01175d947f97c61def13420451f7d19fff73f817d2665de382ffed470"

@app.route("/deploy", methods=["POST"])
def deploy():
    token = request.headers.get("X-Hub-Signature-256")
    if not token or token != SECRET_TOKEN:
        abort(403)

    # Change to your project directory
    os.chdir("/home/codewithmac3/DjangoEcommerce")

    # Activate virtualenv and run deploy script
    subprocess.run("source ~/.virtualenvs/myenv/bin/activate && ./deploy.sh", shell=True)

    return "Deployment triggered!", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)