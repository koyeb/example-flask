# Import the necessary library
from woocommerce import API
from flask import Flask

# Define the fetch_order function
def fetch_order(url, consumer_key, consumer_secret, order_number):
    # Initialize the WooCommerce API client
    wcapi = API(
        url=url,
        consumer_key=consumer_key,
        consumer_secret=consumer_secret,
        wp_api=True,
        version="wc/v3"
    )

    # Call the WooCommerce API to fetch the order details
    return wcapi.get(f"orders/{order_number}")

# Define the Flask app
app = Flask(__name__)

# Define the route to fetch the order
@app.route('/')
def fetch_order_route():
    # Define your WooCommerce credentials and order number
    url = 'https://thecatchandthehatch.com'
    consumer_key = 'ck_799f027dd3d2f158cad2dd6c397e46de825d1eab'
    consumer_secret = 'cs_d90a21886d2ddf6ab3bfed02276515a05309a805'
    order_number = 'your_order_number_here'  # Replace with the actual order number

    # Call the fetch_order function to get order details
    order_details = fetch_order(url, consumer_key, consumer_secret, order_number)

    # Return the order details as a string
    return str(order_details)

# Run the Flask app
if __name__ == '__main__':
    app.run()
