from hashlib import md5
from app import db, app
from flask import url_for
from flask.ext.sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy_searchable import SearchQueryMixin, Searchable
from sqlalchemy_utils.types import TSVectorType



#association table that links Course and Category
course_categories = db.Table('course_categories',
                          db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
                          db.Column('category_id', db.Integer, db.ForeignKey('category.id'))

                    )

#association table that links Professor and Course
course_professors = db.Table('course_professors',
                             db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
                             db.Column('professor_id', db.Integer, db.ForeignKey('professor.id'))
                             

                          )

class CourseQuery(BaseQuery, SearchQueryMixin):
    pass

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True )
    net_id = db.Column(db.String(10), unique= True, nullable =False)
    user_reviews = db.relationship('Review', backref = 'user', lazy = 'dynamic')
    user_likes = db.relationship('Like', backref = 'user', lazy ='dynamic')

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)
    
    def avatar(self, size):
        default_image ='https://dl.dropboxusercontent.com/u/73165478/avatar.png'
        return 'http://www.gravatar.com/avatar/' + md5(self.net_id+'@nyu.edu').hexdigest() + '?d='+default_image+'&s=' + str(size)+'&f=y'


    def __repr__(self):
        return '< User %r>'%self.net_id
    def __str__(self):
        return self.net_id
    
     
class Course(db.Model, Searchable):
    query_class = CourseQuery
    
    __searchable_columns__ = ['course_name']
    __search_options__ = {
        'tablename': 'course',
        'search_vector_name': 'search_vector',
        'search_trigger_name': '{table}_search_update',
        'search_index_name': '{table}_search_index',
    }
    __tablename__ = 'course'
    search_vector = db.Column(TSVectorType)
    id = db.Column(db.Integer, primary_key = True )
    course_name =db.Column(db.String(120), index = True, nullable = False)
    course_description = db.Column(db.Text, nullable = False)
    course_reviews = db.relationship('Review', backref ='course', lazy ='dynamic')
    categories = db.relationship('Category', secondary=course_categories, backref = 'courses', lazy='dynamic')
    
    def totalreviews(self):
        return len(self.course_reviews.all())
    
    def __repr__(self):
        return '< Course %r >'%(self.course_name)
    def __str__(self):
        return self.course_name
    

class Professor(db.Model):
    id = db.Column(db.Integer, primary_key = True )
    professor_name = db.Column (db.String(80), unique= True, nullable = False, index = True)
    courses = db.relationship('Course', secondary = course_professors , backref ='professor', collection_class=set)
     
    def __repr__(self):
        return '< Professor %r>'%self.professor_name
    def __str__(self):
        return self.professor_name



    

class Category(db.Model):
    id = db.Column(db.Integer, primary_key = True )
    category_name = db.Column(db.String(40), unique = True, nullable= False)

    def courses_count(self):
        return Course.query.with_parent(self,'courses').count() 

    def __repr__(self):
        return '< Category %r>'%self.category_name
    def __str__(self):
        return self.category_name

     



class Review(db.Model):
    __table_args__ = ( db.UniqueConstraint('course_id', 'user_id'), { } )
    id = db.Column(db.Integer, primary_key = True )
    review_date = db.Column(db.DateTime)
    review_comment = db.Column(db.Text, index = True, nullable = False)
    rating = db.Column(db.SmallInteger, nullable = False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id') )
    user_id = db.Column(db.Integer, db.ForeignKey('user.id') )
    review_likes = db.relationship('Like', backref = 'review', lazy = 'dynamic')
    
         
    def __repr__(self):
        return '< Review %r>'%self.id
    def __str__(self):
        return self.review_comment



class Like(db.Model):
    id = db.Column(db.Integer, primary_key = True )
    like = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    review_id = db.Column(db.Integer, db.ForeignKey('review.id'))
 
    def __repr__(self):
        return '< Like value %r>'%self.like



