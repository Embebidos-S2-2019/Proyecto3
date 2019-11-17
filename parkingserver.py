from flask import Flask, jsonify, Response, request, render_template, send_file, abort
import parkingdetector as pkd
from subprocess import call
import json
# from ..pkdparkingdetector import ParkingDetector
# from ..pkd.parkingdetector import ParkingDetector


from random import seed
from random import random
# seed random number generator
seed(1)

app = Flask(__name__)
cal_img_path = "/home/images/calibration_image.jpg"
#cal_img_path = "../shape-detection/photo5.jpg"


webcam_image_path = "/home/images/img.jpg"
#webcam_image_path = "../shape-detection/photo3.jpg"
take_picture = "/home/images/takePicture.sh"

# root login information
root_user = "admin"
root_psswd = "admin"

parking_reservations = []
prk_dtc = pkd.ParkingDetector()


@app.route('/user/login', methods=['POST'])
def user_authentication():

    return

    # still todo

    # return jsonify(get_home_status())

@app.route('/parking/spaces', methods=['GET'])
def get_parking_spaces():

    # still todo
    # Run take picture script
    try:
        call(take_picture, shell=True)
        prk_dtc.detect_empty_spaces(webcam_image_path)
        res = prk_dtc.get_parking_spaces()
        print(parking_reservations)
        return jsonify(res)
    except:
        print("error:500") #abort(500)
        return jsonify([{"empty": 'false',"id": 0},{"empty": 'false',"id": 1}])

@app.route('/parking/spaces/req/<int:parking_space_id>', methods=['POST'])
def request_parking_space(parking_space_id):

    # still todo
    try:
        key = random()
        for i in parking_reservations:
        	print(i)
        	tt=json.loads(i.text)
        	print(tt)
        	if(tt["parking_space"]==parking_space_id):
        		return jsonify({"result": 'Cant reserve', "message": key})
        parking_reservations.append(
            {"user_id": 0, "reservation_code": key, "parking_space": parking_space_id})
        return jsonify({"result": 'OK', "message": key})
    except:
        abort(500)

@app.route('/parking/spaces/rele/<int:parking_space_id>', methods=['POST'])
def release_parking_space(parking_space_id):
    # still todo
    try:
        #key = random()
        for i in range(0, len(parking_reservations)):
        	tt=json.loads(parking_reservations[i].text)
        	print(tt)
        	if(tt["parking_space"]==parking_space_id):
        		parking_reservations.pop(i)

        return jsonify({"result": 'OK', "message": key})
    except:
        abort(500)
        
@app.route('/parking/open/', methods=['POST'])
def open_parking_space():
    reservation_code = float(request.args["reservation_code"])
    print(reservation_code)
    # Find the parking reservation by key
    prk_req = next(
        (item for item in parking_reservations if item["reservation_code"] == reservation_code), None)
    print(parking_reservations)

    if prk_req == None:
        abort(400)

    return "OK"
    # Open the parking space

    # delete reservation?

    # use driver to


################################################################################
###################### Admin API ###############################################
################################################################################


@app.route('/parking/calibrate', methods=['GET'])
def get_calibrate_image():

    try:
        # Run take picture script
        call(take_picture, shell=True)
        prk_dtc.init_calibrate_parking_spaces(webcam_image_path)
        # print(prk_dtc.parking_spaces)
        return send_file(cal_img_path)
    except:
        abort(500)


@app.route('/parking/calibrate', methods=['POST'])
def confirm_calibration():

    changed = prk_dtc.confirm_calibration()
    if not changed:
        return "Not Changed"
    return "OK"


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
