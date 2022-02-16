import requests
import sys
import json
import os

try:
	ASTROMETRY_KEY = os.environ['ASTROMETRY_KEY']
except KeyError as error:
	print("Save {} in environment variables.".format(error))
	sys.exit(1)


def login():
	url = "http://nova.astrometry.net/api/login"
	payload = {
		'request-json': json.dumps(
			{
				'apikey': ASTROMETRY_KEY
			}
		)
	}
	login_data = requests.post(url, data=payload).json()
	return login_data


def url_upload(image_url, login_data):
	url = "http://nova.astrometry.net/api/url_upload"
	payload = {
		'request-json': json.dumps(
			{
				'session':login_data['session'],
				'url':image_url,
				'allow_commercial_usage':'n',
				'allow_modifications':'n',
				'publicly_visible':'n'
			}
		)
	}
	upload_response = requests.post(url, data=payload).json()
	return upload_response


def get_submission_status(subid):
	url="http://nova.astrometry.net/api/submissions/" + str(subid)
	submission_status = requests.get(url).json()
	return submission_status


def get_job_status(jobid):
	url = "http://nova.astrometry.net/api/jobs/" + str(jobid)
	job_status = requests.get(url).json()
	return job_status


def get_job_info(jobid):
	url = "http://nova.astrometry.net/api/jobs/"+str(jobid)+"/info/"
	job_info = requests.get(url).json()
	return job_info


def get_final_image(jobid):
	return ("http://nova.astrometry.net/annotated_display/" + str(jobid))
