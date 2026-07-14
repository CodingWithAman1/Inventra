from flask import Flask, redirect, render_template, request,url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Database Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)


# ==========================
# Supplier Table
# ==========================
class Supplier(db.Model):
    __tablename__ = "supplier"

    id = db.Column(db.Integer, primary_key=True)

    company_name = db.Column(db.String(100), nullable=False, unique=True)

    contact_person = db.Column(db.String(100), nullable=False)

    phone = db.Column(db.String(20), nullable=False)

    email = db.Column(db.String(120), nullable=False, unique=True)

    address = db.Column(db.String(250), nullable=False)


# ==========================
# Item Table
# ==========================
class Item(db.Model):
    __tablename__ = "item"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    supplier=db.relationship('Supplier', backref=db.backref('items', lazy=True))

    supplier_id = db.Column(
        db.Integer,
        db.ForeignKey('supplier.id'),
        nullable=False
    )


# ==========================
# Routes
# ==========================
@app.route("/")
@app.route("/home")
def home():
    return render_template("index.html")


@app.route("/inventory")
def inventory():
    items = Item.query.all()
    suppliers = Supplier.query.all()

    return render_template(
        "inventory.html",
        items=items,
        suppliers=suppliers
    )

@app.route("/add_product", methods=["POST"])
def add_product():

    name = request.form["name"]
    quantity = int(request.form["quantity"])
    price = float(request.form["price"])
    supplier_id = int(request.form["supplier_id"])

    item = Item(
        name=name,
        quantity=quantity,
        price=price,
        supplier_id=supplier_id
    )

    db.session.add(item)
    db.session.commit()

    return redirect(url_for("inventory"))

@app.route("/remove_product", methods=["POST"])
def remove_product():

    product_id = request.form["id"]

    item = Item.query.get(product_id)

    if item:
        db.session.delete(item)
        db.session.commit()

    return redirect(url_for("inventory"))

@app.route("/edit_product", methods=["POST"])
def edit_product():

    product_id = request.form["id"]

    item = Item.query.get(product_id)

    if item:

        name = request.form.get("name")
        quantity = request.form.get("quantity")
        price = request.form.get("price")
        supplier_id = request.form.get("supplier_id")

        if name:
            item.name = name

        if quantity:
            item.quantity = int(quantity)

        if price:
            item.price = float(price)

        if supplier_id:
            item.supplier_id = int(supplier_id)

        db.session.commit()

    return redirect(url_for("inventory"))


@app.route("/supplier")
def supplier():
    suppliers = db.session.query(Supplier).all()
    return render_template("supplier.html", suppliers=suppliers)

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/reports")
def reports():
    suppliers = db.session.query(Supplier).all()
    items = Item.query.all()
    total_products = Item.query.count()
    total_suppliers = Supplier.query.count()
    inventory_value = db.session.query(
    db.func.sum(Item.price * Item.quantity)).scalar() or 0
    low_stock = Item.query.filter(Item.quantity < 10).count()
    products = Item.query.all()
    product_names = []
    inventory_values = []
    distribution_labels = []
    distribution_quantity = []
    low_stock_items = Item.query.filter(Item.quantity < 10).all()
    supplier_labels = []
    supplier_products = []

    suppliers = Supplier.query.all()

    for supplier in suppliers:
        supplier_labels.append(supplier.company_name)
        supplier_products.append(len(supplier.items))

    for product in products:
        distribution_labels.append(product.name)
        distribution_quantity.append(product.quantity)

    for product in products:
        product_names.append(product.name)
        inventory_values.append(product.price * product.quantity)

    return render_template(
    "reports.html",
    suppliers=suppliers,
    items=items,
    total_products=total_products,
    total_suppliers=total_suppliers,
    inventory_value=inventory_value,
    low_stock=low_stock,
    product_names=product_names,
    inventory_values=inventory_values,
    distribution_labels=distribution_labels,
    distribution_quantity=distribution_quantity,
    low_stock_items=low_stock_items,
    supplier_labels=supplier_labels,
    supplier_products=supplier_products
)

@app.route("/add_supplier", methods=["POST"])
def add_supplier():
    supplier = Supplier(
        company_name=request.form["company_name"],
        contact_person=request.form["contact_person"],
        phone=request.form["phone"],
        email=request.form["email"],
        address=request.form["address"]
    )

    db.session.add(supplier)
    db.session.commit()

    return redirect(url_for("supplier"))


@app.route("/remove_supplier", methods=["POST"])
def remove_supplier():
    supplier = Supplier.query.get(request.form["id"])

    if supplier:
        db.session.delete(supplier)
        db.session.commit()

    return redirect(url_for("supplier"))


@app.route("/edit_supplier", methods=["POST"])
def edit_supplier():
    supplier = Supplier.query.get(request.form["id"])

    if supplier:

        if request.form.get("company_name"):
            supplier.company_name = request.form["company_name"]

        if request.form.get("contact_person"):
            supplier.contact_person = request.form["contact_person"]

        if request.form.get("phone"):
            supplier.phone = request.form["phone"]

        if request.form.get("email"):
            supplier.email = request.form["email"]

        if request.form.get("address"):
            supplier.address = request.form["address"]

        db.session.commit()

    return redirect(url_for("supplier"))

# ==========================
# Run App
# ==========================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()     # Creates inventory.db and tables automatically

    app.run(debug=True)