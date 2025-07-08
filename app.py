from flask import Flask
app = Flask(__name__)

import psutil
import platform

@app.route('/')
def hello_world():
    return 'Hello from Koyeb'

@app.route('/cpu')
def cpu_info():
    cpu_data = {
        "physical_cores": psutil.cpu_count(logical=False),
        "total_cores": psutil.cpu_count(logical=True),
        "cpu_freq": psutil.cpu_freq()._asdict(),
        "cpu_percent_per_core": psutil.cpu_percent(percpu=True, interval=1),
        "cpu_percent_total": psutil.cpu_percent(interval=1),
        "load_average": {
            "1min": round(psutil.getloadavg()[0], 2),
            "5min": round(psutil.getloadavg()[1], 2),
            "15min": round(psutil.getloadavg()[2], 2),
        },
        "machine_info": {
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "platform": platform.platform()
        }
    }
    return jsonify(cpu_data)

@app.route('/')
def home():
    return '访问 /cpu 来查看 CPU 信息'


if __name__ == "__main__":
    app.run()
