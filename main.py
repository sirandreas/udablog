#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import re
from string import letters

import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self,template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class FrontPage(Handler):
    def render_front(self, subject="", content=""):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC limit 10")
        self.render("FrontPage.html", subject=subject, content=content, posts=posts)

    def get(self):
        self.render_front()

class NewPostPage(Handler):
    def render_front(self, subject="", content="", error=""):
        self.render("NewPostPage.html", subject=subject, content=content, error=error)

    def get(self):
        self.render_front()
        
    def post(self):
        subject = self.request.get("subject")
        content = self.request.get("content")

        if subject and content:
            a = Post(subject = subject, content = content)
            a_key = a.put() #Key('Post',id)
            
            
            self.redirect("/blog/%d" %a_key.id())
        else:
            error = "We need both a Subject and come Content!"
            self.render_front(subject, content, error = error)

class Permalink(FrontPage):
    def get(self, post_id):
        s = Post.get_by_id(int(post_id))
        self.render("FrontPage.html",posts=[s])

app = webapp2.WSGIApplication([('/blog', FrontPage),('/blog/newpost', NewPostPage),('/blog/(\d+)',Permalink)],
                              debug=True)
