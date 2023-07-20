from flask import *
import os
from datetime import datetime
from flask_session import sessions
from DBConnection import Db

app = Flask(__name__)
app.secret_key = "nzee"
from flask import Flask


############################ User area #################################

@app.route('/')
def login():
    return render_template("login.html")


@app.route('/login_post', methods=['post'])
def login_post():
    email = request.form['email']
    passw = request.form['password']
    db = Db()
    qry = "select * from login where email = '" + email + "' and password='" + passw + "'"
    res = db.selectOne(qry)
    if res is None:
        return '''<script>alert("Invalid Username Or Password");window.location="/"</script>'''
    else:
        session["lid"] = str(res['lid'])
        return redirect('/home')


@app.route('/reg_post', methods=['post'])
def reg_post():
    u_name = request.form['username']
    e_mail = request.form['email']
    password = request.form['password']
    type = request.form['type']
    db = Db()
    qry1 = "insert into login (email,password,type) values('" + e_mail + "','" + password + "','" + type + "')"
    res1 = db.insert(qry1)
    lid = str(res1)
    qry = "insert into reg (uid,name) VALUES ('" + lid + "','" + u_name + "')"
    db.insert(qry)
    return redirect("/")


@app.route('/user-logout')
def user_logout():
    session.clear()
    return redirect('/')


@app.route('/home')
def home():
    lid = session.get('lid')
    if lid is None:
        return redirect('/')
    db = Db()
    qry = "SELECT product_id, name, price, image FROM products"
    res = db.select(qry)
    products = []
    for row in res:
        product = {
            'product_id': row['product_id'],
            'name': row['name'],
            'price': row['price'],
            'image': row['image']
        }
        products.append(product)
    qry1 = "SELECT name FROM reg WHERE  uid = '" + lid + "' "
    user_res = db.selectOne(qry1)
    if user_res is None:
        return redirect("/")
    user_name = user_res['name']
    return render_template("home.html", products=products, user_name=user_name)


@app.route('/cart')
def cart():
    lid = session.get('lid')
    if lid is None:
        return redirect('/')
    db = Db()
    qry = "SELECT name, price, image, product_id FROM cart WHERE uid = '"+ lid +"'"
    res = db.select(qry)
    products = []
    for row in res:
        product = {
            'product_id': row['product_id'],
            'name': row['name'],
            'price': row['price'],
            'image': row['image']
        }
        products.append(product)
    qry1 = "SELECT name FROM reg WHERE  uid = '" + lid + "' "
    user_res = db.selectOne(qry1)
    if user_res is None:
        return redirect("/")
    user_name = user_res['name']
    return render_template("cart.html", products=products, user_name=user_name)


@app.route('/add-cart-post', methods=['post'])
def add_cart():
    product_id = request.form['product_id']
    lid = session.get("lid")
    db = Db()
    # Check if the item already exists in the cart
    qry = "SELECT COUNT(*) FROM cart WHERE product_id = '" + product_id + "' AND uid = '" + lid + "' "
    count = db.selectOne(qry)['COUNT(*)']

    if count > 0:
        return '''<script> alert("Item already exists in the cart!"); window.location="/home"; </script>'''

    qry = "SELECT name, price, image FROM products WHERE product_id = '" + product_id + "' "
    product_details = db.selectOne(qry)
    if product_details is not None:
        cart_item = {
            'product_id': product_id,
            'name': product_details['name'],
            'price': product_details['price'],
            'image': product_details['image'],
            'user_id': lid
        }
        # Add the cart item to the cart table
        qry = "INSERT INTO cart (uid, name, price, image, product_id) VALUES ('" + cart_item['user_id'] + "' , '" + \
              cart_item['name'] + "' ,'" + str(cart_item['price']) + "' ,'" + cart_item['image'] + "' ,'" + cart_item[
                  'product_id'] + "' )"
        db.insert(qry)

        return '''<script> alert(" Item added to the cart !!");window.location="/home" </script>'''
    else:
        return '''<script> alert("The item not found !!");window.location="/home" </script>'''


@app.route('/rm-from-cart', methods=['post'])
def rm_from_cart():
    lid = session.get("lid")
    print(lid)
    product_id = request.form['product_id']
    db = Db()
    qry = " DELETE FROM cart WHERE product_id = '" + product_id + "' AND uid = '" + lid + "' "
    if lid is not None:
        res = db.delete(qry)
        qry1 = " SELECT name FROM cart WHERE product_id = '" + product_id + "' "
        res = db.selectOne(qry1)
        return ''' <script> alert(" Item removed!!! ");window.location="/cart" </script> '''
    else:
        return ''' <script> alert(" User not Found ! ");window.location="/cart" </script> '''


@app.route('/orders')
def orders():
    lid = session.get("lid")
    db = Db()
    qry = "SELECT * FROM `order_table` WHERE `uid` = '" + lid + "'"
    res = db.select(qry)
    qry1 = "SELECT name FROM reg WHERE  uid = '" + lid + "' "
    user_res = db.selectOne(qry1)
    if user_res is None:
        return redirect("/")
    user_name = user_res['name']
    return render_template('order_view.html', orders=res, user_name=user_name)


@app.route('/check-out', methods=['post'])
def check_out():
    lid = session.get("lid")
    product_id = request.form['product_id']
    product_name = request.form['product_name']
    product_price = request.form['product_price']
    product_image = request.form['product_img']
    db = Db()
    qry1 = "SELECT name FROM reg WHERE  uid = '" + lid + "' "
    user_res = db.selectOne(qry1)
    if user_res is None:
        return redirect("/")
    user_name = user_res['name']
    qry = " DELETE FROM cart WHERE product_id = '" + product_id + "'"
    db.delete(qry)
    return render_template("check-out.html", user_name=user_name, product_id=product_id, product_name=product_name,
                           product_price=product_price, product_image=product_image)


@app.route('/place-order', methods=['post'])
def place_order():
    lid = session.get("lid")
    db = Db()
    qry1 = "SELECT name FROM reg WHERE  uid = '" + lid + "' "
    user_res = db.selectOne(qry1)
    if user_res is None:
        return redirect("/")
    user_name = user_res['name']
    product_id = request.form['product_id']
    product_name = request.form['product_name']
    product_price = request.form['product_price']
    product_image = request.form['product_img']
    address = request.form['address']
    mobile = request.form['mobile']
    zipcode = request.form['zipcode']
    payment_method = request.form['paymentMethod']
    if payment_method == "cod":
        qry = "INSERT INTO order_table (product_id, uid, name, price, image, address, mobile, zipcode, status) VALUES ('" + product_id + "','" + lid + "','" + product_name + "','" + product_price + "','" + product_image + "','" + address + "','" + mobile + "','" + zipcode + "','placed')"
        db.insert(qry)
        qry = " SELECT order_id FROM order_table WHERE uid='" + lid + "' AND product_id='" + product_id + "' "
        res = db.selectOne(qry)
        return render_template("order_succes.html", user_name=user_name, order_id=res)
    else:
        return '''<script>alert("This feature is in development, select another option");window.location="/cart"</script>'''


@app.route('/cancel-order', methods=['post'])
def cancel_order():
    order_id = request.form['order_id']
    db = Db()
    qry = " DELETE FROM order_table WHERE order_id = '" + order_id + "'"
    res = db.delete(qry)
    if res is not None:
        return '''<script>alert("Order canceled success");window.location="/orders"</script>'''
    else:
        return '''<script>alert("Order unable to be canceled !!! ");window.location="/orders"</script>'''


@app.route("/contact")
def contact():
    lid = session.get("lid")
    db = Db()
    qry1 = "SELECT name FROM reg WHERE  uid = '" + lid + "' "
    user_res = db.selectOne(qry1)
    if user_res is None:
        return redirect("/")
    user_name = user_res['name']
    return render_template("contact.html", user_name=user_name)


#################################### Admin area ######################################

@app.route('/admin-login')
def admin_login():
    return render_template("admin-login.html")


@app.route('/admin-login-post', methods=['post'])
def admin_login_post():
    u_name = request.form['email']
    passw = request.form['password']
    db = Db()
    qry = "select * from login where email = '" + u_name + "' and password = '" + passw + "' and type = 'seller'"
    res = db.selectOne(qry)
    if res is None:
        return '''<script>alert("Invalid Credential");window.location="/admin-login"</script>'''
    else:
        if res['type'] == 'seller':
            session["lid"] = str(res['lid'])
            session["email"] = res['email']
            return redirect('/admin')
        else:
            return '''<script>alert("Invalid Credential");window.location="/admin-login"</script>'''


@app.route('/admin-logout')
def admin_logout():
    session.clear()
    return redirect('/admin-login')


@app.route('/admin')
def admin():
    lid = session.get("lid")
    db = Db()
    qry = "SELECT product_id, name, price, image FROM products WHERE uid = '"+ lid +"' "
    res = db.select(qry)
    username = session.get('email')  # Retrieve the user's name from the session
    products = []
    for row in res:
        product = {
            'product_id': row['product_id'],
            'name': row['name'],
            'price': row['price'],
            'image': row['image']
        }
        products.append(product)
    if not username:
        return redirect('/admin-login')  # Redirect to login if the user is not logged in
    qry = " SELECT product_id FROM products "
    res = db.select(qry)
    # Continue with the rest of the admin route logic
    return render_template("admin.html", products=products, username=username, id=res)


@app.route('/add-product')
def add_product():
    return render_template("add-product.html")


@app.route('/add-product-post', methods=["post"])
def add_product_post():
    lid = session.get("lid")
    name = request.form['name']
    price = float(request.form['price'])
    image = request.files['image']
    if image:
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{current_time}_{image.filename}"
        image_url = os.path.join('static/images/', filename)
        image_path = os.path.join('../static/images/', filename)
        os.makedirs('/static/images/', exist_ok=True)
        image.save(image_url)
        print(image_url)
    else:
        return '''<script>alert("Upload an image also");window.location="/add-product"</script>'''
    db = Db()
    qry = "insert into products (name,price,image,uid) values('" + name + "','" + str(price) + "','" + image_path + "','"+ lid +"')"
    db.insert(qry)
    return '"<script>alert("Product added successfully");window.location="/add-product"</script>"'


@app.route('/delete-product-post', methods=['POST'])
def delete_product():
    product_id = request.form['product_id']
    db = Db()
    qry = " SELECT image FROM products WHERE product_id = '" + product_id + "' "
    result = db.selectOne(qry)
    if result is None:
        return ''' <script>alert(" the product not found ");window.location="/admin"</script> '''

    image_path = result['image']
    image_path = image_path.replace("../", "")

    qry = "DELETE FROM products WHERE product_id = '" + product_id + "'"
    db.delete(qry)
    if image_path:
        try:
            os.remove(image_path)
        except OSError:
            pass
    return redirect('/admin')


# @app.route('/admin-orders')
# def admin_orders():
#     username = session.get('email')
#     db = Db()
#     qry = " SELECT lid FROM login WHERE email = '" + username + "' "
#     res = db.selectOne(qry)
#     if not username:
#         return redirect('/admin-login')
#     qry = "SELECT * FROM `order_table` WHERE `uid` = '" + str(res['lid']) + "'"
#     res = db.select(qry)
#     return render_template("admin-order-view.html", username=username, orders=res)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)