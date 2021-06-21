import random

import datetime
from flask import Flask, render_template, request, session
from DBConnection import Db

app = Flask(__name__)
app.secret_key="hi"

static_path="C:\\Users\\ELCOT-Lenovo\\PycharmProjects\\public_key_encryption\\static\\"


@app.route('/')
def login():
    return render_template("login.html")
@app.route("/login_post",methods=['post'])
def login_post():
    user=request.form['username']
    psw=request.form['pass']
    db=Db()
    qry="select * from login where username='"+user+"' and password='"+psw+"'"
    res=db.selectOne(qry)
    if res is None:
        return "<script>alert('Incorrect Username and Password');window.location='/';</script>"
    else:
        session['lg']='yes'
        session['lid']=res['login_id']
        if res['type']=='admin':
            return render_template("admin/admin_home.html")
        elif res['type']=='user':
            res1=db.selectOne("select * from user where lid='"+str(res['login_id'])+"'")
            if res1 is not None:
                session['uname']=res1['name']
                return render_template("user/user_home.html")
            else:
                return "<script>alert('User not found');window.location='/';</script>"
            # return render_template("admin_panel.html")
        else:
            return "<script>alert('Unauthorised user');window.location='/';</script>"


###     ADMIN
@app.route("/admin_home")
def admin_home():
    return render_template("admin/admin_home.html")

@app.route("/view_complaints")
def view_complaints():
    db=Db()
    res=db.select("select complaint.*,user.name, user.image from user, complaint where user.lid=complaint.user_lid order by complaint_id desc")
    return  render_template("admin/view_complaints.html", data=res)

@app.route("/view_complaints_post", methods=['post'])
def view_complaints_post():
    fdate=request.form['textfield']
    tdate=request.form['textfield2']
    db=Db()
    res=db.select("select complaint.*,user.name, user.image from user, complaint where user.lid=complaint.user_lid and date between '"+fdate+"' and '"+tdate+"' order by complaint_id desc")
    return  render_template("admin/view_complaints.html", data=res)

@app.route("/send_reply/<id>")
def send_reply(id):
    db=Db()
    res=db.selectOne("select * from complaint where complaint_id='"+str(id)+"'")
    return render_template("admin/send_reply.html", comp=res['complaint'], cid=res['complaint_id'])

@app.route("/send_reply_post", methods=['post'])
def send_reply_post():
    rep=request.form['textarea']
    cid=request.form['cid']
    db=Db()
    db.update("update complaint set reply='"+rep+"' where complaint_id='"+cid+"'")
    return view_complaints()

@app.route("/view_reviews")
def view_reviews():
    db=Db()
    res=db.select("select reviews.*,user.name, user.image from user, reviews where user.lid=reviews.user_lid order by review_id desc")
    return render_template("admin/view_reviews.html", data=res)

@app.route("/view_reviews_post", methods=['post'])
def view_reviews_post():
    fdate = request.form['textfield']
    tdate = request.form['textfield2']
    db=Db()
    res=db.select("select reviews.*,user.name, user.image from user, reviews where user.lid=reviews.user_lid and date between '"+fdate+"' and '"+tdate+"' order by review_id desc")
    return render_template("admin/view_reviews.html", data=res)

@app.route("/view_users")
def view_users():
    db=Db()
    res=db.select("select * from user")
    return render_template("admin/view_users.html", data=res)

@app.route("/view_users_post", methods=['post'])
def view_users_post():
    name = request.form['textfield']
    db = Db()
    res = db.select("select * from user where name like '%"+name+"%'")
    return render_template("admin/view_users.html", data=res)



###         USER
@app.route("/user_reg")
def user_reg():
    return render_template("user/user_reg.html")
@app.route("/user_reg_post", methods=['post'])
def user_reg_post():
    name = request.form['first_name']
    email = request.form['email']
    phone = request.form['phone']
    hname = request.form['hname']
    place = request.form['place']
    post = request.form['post']
    pin = request.form['pin']
    img = request.files['img']
    password=random.randint(1000,9999)
    import time
    dt=time.strftime("%Y%d%m_%H%M%S")+".jpg"
    img.save(static_path+"user_img"+dt)
    path="/static/user_img/"+dt
    db=Db()
    lid=db.insert("insert into login(username,password,type) values('"+email+"','"+password+"','user')")
    db.insert("insert into user(name,email,phone,house,place,post,pin,image,lid) "
              "values('"+name+"','"+email+"','"+phone+"','"+hname+"','"+place+"','"+post+"','"+pin+"','"+path+"','"+str(lid)+"')")
    return "<script>alert('You have registered successfully');window.location='/';</script>"

@app.route("/user_home")
def user_home():
    return render_template("user/user_home.html")

@app.route("/user_view_profile")
def user_view_profile():
    db = Db()
    res = db.selectOne("select * from user where lid='" + str(session['lid']) + "'")
    return render_template("user/view_profile.html", data=res)

@app.route("/user_updt_profile", methods=['post'])
def user_updt_profile():
    name = request.form['name']
    phone = request.form['phone']
    hname = request.form['house']
    place = request.form['place']
    post = request.form['post']
    pin = request.form['pin']
    db=Db()
    if 'img' in request.files:
        img = request.files['img']
        if img.filename=='':
            db.update("update user set name='" + name + "', phone='" + phone + "', house='" + hname + "', place='" + place + "', post='" + post + "', pin='" + pin + "' where lid='" + str(session['lid']) + "'")
        else:
            import time
            dt = time.strftime("%Y%d%m_%H%M%S") + ".jpg"
            img.save(static_path + "user_img" + dt)
            path = "/static/user_img/" + dt
            db.update("update user set name='"+name+"', phone='"+phone+"', house='"+hname+"', place='"+place+"', post='"+post+"', pin='"+pin+"', image='"+path+"' where lid='"+str(session['lid'])+"'")
    else:
        db.update(
            "update user set name='" + name + "', phone='" + phone + "', house='" + hname + "', place='" + place + "', post='" + post + "', pin='" + pin + "' where lid='" + str(
                session['lid']) + "'")
    return "<script>alert('Profile updated successfully');window.location='/user_view_profile';</script>"

@app.route("/user_view_users")
def user_view_users():
    db=Db()
    res=db.select("select * from user where lid!='"+str(session['lid'])+"'")
    return render_template("user/view_users.html", data=res)

@app.route("/user_view_users_post", methods=['post'])
def user_view_users_post():
    name = request.form['textfield']
    db = Db()
    res = db.select("select * from user where name like '%"+name+"%' and lid!='"+str(session['lid'])+"'")
    return render_template("user/view_users.html", data=res)


@app.route("/user_send_complaint")
def user_send_complaint():
    return render_template("user/send_complaints.html")
@app.route("/user_send_complaint_post", methods=['post'])
def user_send_complaint_post():
    comp=request.form['textarea']
    db=Db()
    db.insert("insert into complaint(date,user_lid,complaint,reply) values(curdate(),'"+str(session['lid'])+"','"+comp+"','pending')")
    return user_send_complaint()
@app.route("/user_view_comp")
def user_view_comp():
    db=Db()
    res=db.select("select * from complaint where user_lid='"+str(session['lid'])+"'")
    return render_template("user/view_reply.html", data=res)
@app.route("/user_del_comp/<id>")
def user_del_comp(id):
    db=Db()
    db.delete("delete from complaint where complaint_id='"+id+"'")
    return user_view_comp()


if __name__ == '__main__':
    app.run()
