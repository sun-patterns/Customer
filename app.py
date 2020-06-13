from flask import Flask, request, g, jsonify
import sqlite3
from database import connect_db, get_db
from functools import wraps

def protected(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == api_username and auth.password == api_password:
            return f(*args, **kwargs)
        return jsonify({'message' : 'Authentication failed!'}), 403
    return decorated 

app = Flask(__name__)
app.config['DEBUG'] = True

api_username = 'admin'
api_password = 'password'

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()

@app.route('/member', methods=['GET'])
@protected
def get_members():
   db = get_db()
   members_cur = db.execute('select id, name, email, level from customers')
   members = members_cur.fetchall()
   
   return_values = []
   for member in members:
       member_dict = {}
       member_dict['id'] = member['id']
       member_dict['name'] = member['name']
       member_dict['email'] = member['email']
       member_dict['level'] = member['level']
       print(member_dict)
       
       return_values.append(member_dict)

     
   #return jsonify({'members' : return_values})
   return jsonify({'members' : return_values})

@app.route('/member/<int:member_id>', methods=['GET'])
def get_member(member_id):
    db = get_db()
    member_cur = db.execute('select id, name, email, level from customers where id = ?', [member_id])
    member = member_cur.fetchone()

    
    return jsonify({'member' : {'id' : member['id'], 'name' : member['name'], 'email' : member['email'], 'level' : member['level']}})

@app.route('/member', methods=['POST'])
def add_member():
   new_member_data =  request.get_json()
   name = new_member_data['name']
   email = new_member_data['email']
   level = new_member_data['level']
   
   db = get_db()
   db.execute('insert into customers(name, email, level) values (?, ?, ?)', [name, email, level])
   db.commit()
   
   member_cur = db.execute('select id, name, email, level from customers where name = ?', [name])
   new_member = member_cur.fetchone()
   
   return jsonify({'id' : new_member['id'], 'name' : new_member['name'], 'email' : new_member['email'], 'level' : new_member['level']})

@app.route('/member/<int:member_id>', methods=['PUT', 'PATCH'])
def edit_member(member_id):
   new_member_data = request.get_json()
   
   #name = new_member_data['name']
   #email = new_member_data['email']
   level = new_member_data['level']
   
   db = get_db()
   db.execute('update customers set level = ? where id= ?', [level, member_id])
   db.commit()
   
   member_cur = db.execute('select id, name, email, level from customers where id = ?', [member_id])
   member = member_cur.fetchone()
   
   return jsonify({'member' : {'id' : member['id'], 'name' : member['name'], 'email' : member['email'], 'level' : member['level']}})


@app.route('/member/<int:member_id>', methods=['DELETE'])
def delete_member(member_id):
   return 'This removes a member by ID'

if __name__ == '__main__':
	app.run()