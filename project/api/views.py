# Importing all needed Flask classes
from flask import Flask, session, redirect, Blueprint, request, jsonify, g, url_for, make_response, Response, flash

# Importing firebase connection
from project.firebase_connection import firebaseConnect

# Importing random
import random

# Importing string
import string

# Importing time
from time import *

api = Blueprint('api', __name__)

# FIREBASE AUTHENTICATION
databaseConnect = firebaseConnect()

database = databaseConnect['database']

authe = databaseConnect['authe']

storage = databaseConnect['storage']

# Random id genorator
def randomString(stringLength=16):
    """Generate a random string of fixed length """
    letters= string.ascii_lowercase
    return ''.join(random.sample(letters,stringLength))

@api.route("/signup-api", methods=['GET', 'POST'])
def signUpApi():
	
	# Assigning variables equvilent to posted data
	name = request.json['name']
	username = request.json['username']
	email = request.json['email']
	address = request.json['address']
	city = request.json['city']
	zip_code = request.json['zip_code']
	
	# Variables for providers
	business_name = request.json['business_name']
	password = request.json['password']

	try:
		description = request.json['description']

		# Running create user function
		createdUser = createUserFunc(name, email, username, address, city, zip_code, description, business_name,  password)
	except Exception as e:
		print("user not provider")

		# Running create user function
		createdUser = createUserFunc(name, email, username, address, city, zip_code, 0, 0, password)

	return jsonify(createdUser)

def createUserFunc(name, email, username, address, city, zip_code, description, business_name, password):
	try:
		print(email)
		print(password)
		
		# Creating user in firebase
		user = authe.create_user_with_email_and_password(email,password)

		# Assigning uid which will be used to create paths in database
		uid = user['localId']

		# Assigning json data to variable to return to database
		if description and business_name != 0:
			userAccount = { "name" : name, "email" : email, "username" : username, "address" : address, "city": city , "description" : description, "business_name" : business_name, "provider": { "is_provider": True, "clean_shoes": False, "shoe_artist": False, "background_info": "", "about_brand_or_individual": "", "accepted": "" }, "setup_complete": False, "number_of_transactions": 0, "rating": 0, "created_at": time(), "profile_pic_url": "" }
		else:
			print("user not provider")
			userAccount = { "name" : name, "email" : email, "username" : username, "address" : address, "city": city , "description" : "", "business_name" : "", "provider": { "is_provider": False, "clean_shoes": False, "shoe_artist": False, "background_info": "", "about_brand_or_individual": "", "accepted": "" }, "setup_complete": True, "number_of_transactions": 0, "rating": 0, "created_at": time(), "profile_pic_url": ""  }

		transactionHistoryDict = { "title": "", "description": "", "date": "", "cost_paid": "" }
		message = { "sender": "", "reciever":"", "message":"", "date_time": "" }
		# Saving data to firebase
		database.child("users").child(uid).child("account").set(userAccount)
		database.child("users").child(uid).child("account").child("interest").child(0).set("null")
		database.child("users").child(uid).child("account").child("history").child("transactions").child(0).set(transactionHistoryDict)
		database.child("users").child(uid).child("account").child("history").child("messages").child(0).set(message)
		message = "success"
	except Exception as e:
		print(e)
		message = "failed"

	return message

@api.route("/signin-api", methods=['GET', 'POST'])
def signInApi():

	# Assigning variables equvilent to posted data
	name = request.json['name']
	password = request.json['password']

	# Running signin function
	signIn = signInFunc(name, password)

	return jsonify(signIn)

def signInFunc(email, password):
	# Creating empty dictionary
	userData = dict()
	try:
		print('aaaaaa')
		# Signing into firebase
		user = authe.sign_in_with_email_and_password(email,password)

		# Assigning uid which will be used to create paths in database
		uid = user['localId']

		# Getting data from firebase
		account = dict(database.child("users").child(uid).child("account").get().val())

		# Saving data in dictionary
		userData['user'] = user
		userData['account'] = account
		userData['message'] = "success"
	except Exception as e:
		userData['message'] = "failed"
		print(e)

	return userData

# Udpating providers setup
@api.route("/provider-setup-api", methods=['POST'])
def updateSetupApi():
	if request.method == "POST":

		# Website posted
		try:
			username = session['account']['username']

			# Checking if checkbox is empty
			try:
				clean_shoes = request.form.getlist('clean_shoes')
			except Exception as e:
				clean_shoes = 'false'
			try:
				shoe_artist = request.form.getlist('shoe_artist')
			except Exception as e:
				shoe_artist = 'false'


			if clean_shoes == 'false' and shoe_artist == 'false':
				flash('Check what service you provide')
				return redirect(url_for('profile.home',username=username))

			background_info = request.form['background_info']
			write_about_brand = request.form['write_about_brand']

			try:
				profile_pic = request.files['profile_pic']
			except Exception as e:
				flash('Profile Empty')
				return redirect(url_for('profile.home',username=username))

			if background_info == '' or write_about_brand == '':
				flash('Field Empty')
				return redirect(url_for('profile.home',username=username))

		except Exception as e:
			print(e)
			print('Not posted from website')
			# Assigning variables equvilent to posted data
			background_info = request.json['background_info']
			clean_shoes = request.json['clean_shoes']
			username = request.json['username']
			shoe_artist = request.json['shoe_artist']
			write_about_brand = request.json['write_about_brand']


		setup = updateSetup(background_info, write_about_brand, clean_shoes, username, shoe_artist, profile_pic)

		return redirect(url_for('profile.home',username=username))
	else:
		return jsonify({'message' : 'failed'})

def updateSetup(background_info, about_brand_or_individual, clean_shoes, username, shoe_artist, profile_pic):
	print('setup')
	# Getting database
	usersData = dict(database.child("users").get().val())
	# Finding matching url username
	for user in usersData:
		iteratedUsername = usersData[user]['account']['username']
		print(user)
		print(username)
		if username == iteratedUsername:
			print(username)
			print(iteratedUsername)
			print('found')
			# Saving data
			database.child("users").child(user).child("account").child("provider").child("background_info").set(background_info)
			database.child("users").child(user).child("account").child("provider").child("about_brand_or_individual").set(about_brand_or_individual)
			database.child("users").child(user).child("account").child("provider").child("clean_shoes").set(clean_shoes)
			database.child("users").child(user).child("account").child("provider").child("shoe_artist").set(shoe_artist)
			database.child("users").child(user).child("account").child("provider").child("is_provider").set(True)
			database.child("users").child(user).child("account").child("setup_complete").set(True)
			putImg = storage.child("images").child(user).put(profile_pic, user)
			image_url = storage.child("images").child(user).get_url(user)
			database.child("users").child(user).child("account").child("profile_pic_url").set(image_url)
			return 'success'
		else:
			print('not found')
	return 'not found'

# New post 
@api.route("/new-post-api", methods=['POST'])
def newPostApi():
	if request.method == "POST":
		print('aaa')
		print(request.form)

		# Posted data from website
		try:
			print('aasas')

			# Handling type of post
			service_type = request.form.getlist('service_type')[0]

			if service_type == 'clean-shoes':
				clean_shoes = True
				shoe_artist = False
			elif service_type == 'design-shoes':
				clean_shoes = False
				shoe_artist = True
			
			if service_type == 'design-shoes':
				# Getting profile pic
				try:
					post_pic = request.files['post_pic']
					print(post_pic)
					shoeName = request.form['new-post-shoe']
					print('shoeName')
					shoeDescription = request.form['new-post-description']
					print('shoeName')

					cost = request.form['new-post-design-shoes-cost']
					print('shoeName')

					username = session['account']['username']
					print('shoeName')

				except Exception as e:
					flash('Post a picture of the shoes!')
					return redirect(url_for('explore.home'))
			elif service_type == 'clean-shoes':
				print('---')
				post_pic = 0

				shoeName = ''
				shoeDescription = ''
				cost = request.form['new-post-clean-shoes-cost']
				username = session['account']['username']
		except Exception as e:
			print(e)
			print('Not posted from website')

			# Assigning variables equvilent to posted data
			shoeName = request.json['shoe_name']
			shoeDescription = request.json['shoe_description']
			cost = request.form['cost']
			username = request.json['username']
			selectedTime = request.json['selected_time']
			clean_shoes = request.json['clean_shoes']
			shoe_artist = request.json['shoe_artist']
		print(post_pic)
		post = newPost(shoeName, shoeDescription, cost, username, clean_shoes, shoe_artist, post_pic)
		flash(f'Posted!', 'success')
		return redirect(url_for('explore.home'))
	else:
		return jsonify({'message' : 'failed'})


def newPost(shoeName, shoeDescription, cost, username, clean_shoes, shoe_artist, post_pic):
	print('setup')
	postId = randomString(16)

	# Checking if designer
	if post_pic != 0:
		putImg = storage.child("images").child("post").child(postId).put(post_pic, postId)
		image_url = storage.child("images").child("post").child(postId).get_url(postId)
	else:
		image_url = ""

	postJson = {"shoe_name": shoeName, "shoe_description": shoeDescription, "cost": cost, "username": username, "clean_shoes": clean_shoes, "shoe_artist": shoe_artist, "post_id": postId, "posted_at": time(), "post_pic_url": image_url }
	
	# updating database
	try:
		databasePost = database.child("posts").get().val()
		postCounter = 0
		for i in databasePost:
			postCounter += 1
			print(postCounter)
		database.child("posts").child(postCounter).set(postJson)
		return 'success'
	except Exception as e:
		print(e)
		print('first post')
		database.child("posts").child(0).set(postJson)
		return 'success'



