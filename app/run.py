from climateapp import app
import secrets

if __name__ == "__main__":
    app.secret_key = secrets.token_hex(32)
    app.run(debug=True, ssl_context=('cert.pem', 'key.pem'))