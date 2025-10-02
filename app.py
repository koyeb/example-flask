from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def home():
    # Dropbox image URL with ?raw=1 for direct access
    image_url = "https://www.dropbox.com/scl/fo/3tqthrort5vl37uw8ijgc/AH8rCi_N0D53tIwp-Vz-F-c?rlkey=ccs3m29g4e00o8utkxahba979&st=spg6wf7x&?raw=1"
    
    # HTML code to display the image
    html_code = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Image from Dropbox</title>
    </head>
    <body>
        <h1>Welcome to my Website</h1>
        <p>Here is an image from Dropbox:</p>
        <img src="{image_url}" alt="Image from Dropbox" />
    </body>
    </html>
    """
    return render_template_string(html_code)

if __name__ == '__main__':
    app.run(debug=True)
