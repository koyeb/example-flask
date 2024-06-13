from flask import Flask
import xmlrpc.client
app = Flask(__name__)
url = "http://alhorae.odoo.com:80"
db = "odooerp-ae-alhor1-main-4747584"
email = "yazansodan@gmail.com"
password = "15c033e53611eb0b8827e14aecd505601850e906"

common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
print(common.version())

