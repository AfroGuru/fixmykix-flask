# Importing all needed Flask classes
from flask import Flask, render_template, session, flash, redirect, url_for, Blueprint, request

# Importing firebase connection
from project.firebase_connection import firebaseConnect

# Import time
from time import *

# FIREBASE AUTHENTICATION
databaseConnect = firebaseConnect()

database = databaseConnect['database']

# Defining Blueprint var
posts = Blueprint('posts', __name__, template_folder='templates', static_folder='static', static_url_path='/static/posts')

# Post function
@posts.route("/post/<postId>", methods=['GET', 'POST'])
def home(postId):
	print(postId)
	postsData = database.child("posts").get().val()
	for post in postsData:
		if post['post_id'] == postId:
			print('found')
			cost = post['cost']
			shoe_name = post['shoe_name']
			shoe_description = post['shoe_description']
			username = post['username']
			clean_shoes = post['clean_shoes']
			shoe_artist = post['shoe_artist']
			post_pic_url = post['post_pic_url']
			return render_template('posts/post.html', cost=cost, shoe_name=shoe_name, shoe_description=shoe_description, username=username, clean_shoes=clean_shoes, shoe_artist=shoe_artist, post_pic_url=post_pic_url)

