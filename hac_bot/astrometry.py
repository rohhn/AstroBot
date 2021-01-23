import json
import requests

class Astrometry():

	get_photo, job_status = range(2)
	state = get_photo

	def __init__(self):
		self.args = {'allow_commercial_usage':'n',
					'allow_modifications':'n',
					'publicly_visible':'n',
					}


	def login(self, data):
		api_key = "pqudnwshqryknetf"
		url = "http://nova.astrometry.net/api/login"
		login_data = requests.post(url, data=data).json()
		return login_data

	def url_upload(self, data):
		url = "http://nova.astrometry.net/api/url_upload"
		data.update(self.args)
		upload_response = requests.post(url, data=data).json()
		return upload_response

	def get_submission_status(self, subid):
		url="http://nova.astrometry.net/api/submissions/" + str(subid)
		submission_status = requests.get(url).json()
		return submission_status


	def get_job_status(self, jobid):
		url = "http://nova.astrometry.net/api/jobs/" + str(jobid)
		job_status = requests.get(url).json()
		return job_status

	def get_job_info(self, jobid):
		url = "http://nova.astrometry.net/api/jobs/"+str(jobid)+"/info/"
		job_info = requests.get(url).json()
		return job_info

	def get_final_image(self, jobid):
		return ("http://nova.astrometry.net/annotated_display/" + str(jobid))






