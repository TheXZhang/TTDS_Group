from waitress import serve
import app1
serve(app1.app, host='0.0.0.0', port=8080)