import os

from flask import Flask, render_template, url_for, request, jsonify, send_from_directory

import xmlLogic

app = Flask(__name__)
cals_to_delete = list()

@app.route('/')
def index():
    # get_classes_urll = url_for(get_classes)
    return render_template('index.html', title="Plan -> Calendar")


@app.route('/get_classes')
def get_classes():
    urls = request.args.getlist('urls')
    print(urls)
    to_return = [xmlLogic.getDataFromXml(url) for url in urls]
    # adding checked property
    to_return = [xmlLogic.addCheckedProperty(data) for data in to_return]
    print(to_return)
    return jsonify(to_return)


@app.route('/gen_cal', methods=['POST'])  # GET requests will be blocked
def gen_cal():
    req_data = request.get_json()
    cal_file_name = xmlLogic.create_cal(req_data)
    return jsonify(cal_file_name)


@app.route('/download_cal/<cal_file_name>')  # GET requests will be blocked
def download_cal(cal_file_name):
    cals_to_delete.append(cal_file_name)
    return send_from_directory('converted_cals', str(cal_file_name) + '.ics', as_attachment=False)


if __name__ == '__main__':
    app.run(debug=True, host= '0.0.0.0')
