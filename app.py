import io
import csv
import os
from datetime import datetime, timezone
from flask import Flask, redirect, render_template, request, url_for, flash, Response, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from werkzeug.middleware.proxy_fix import ProxyFix

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)

# Reverse proxy support for Vercel
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# Secret key for session management and flash messages
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'inventra-secure-secret-key-2026')

# Database Configuration (supports Vercel /tmp, local instance/, and custom DATABASE_URL/POSTGRES_URL)
is_vercel = os.environ.get('VERCEL') == '1' or os.environ.get('VERCEL_ENV') is not None
database_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')

if database_url:
    # Modern SQLAlchemy 2.0 requires postgresql:// instead of postgres://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
elif is_vercel:
    # On Vercel (Linux serverless), /tmp is the only writable directory.
    import tempfile
    tmp_dir = '/tmp' if os.path.exists('/tmp') else tempfile.gettempdir()
    db_path = os.path.join(tmp_dir, 'inventory.db').replace('\\', '/')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
else:
    os.makedirs(app.instance_path, exist_ok=True)
    db_path = os.path.join(app.instance_path, 'inventory.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
}
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)


# ==============================================================================
# Database Models
# ==============================================================================

class Supplier(db.Model):
    __tablename__ = "supplier"

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False, unique=True)
    contact_person = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    address = db.Column(db.String(250), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship to Items (cascade delete orphans)
    items = db.relationship('Item', backref='supplier', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return self.company_name


class Item(db.Model):
    __tablename__ = "item"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(50), nullable=True, unique=True)
    category = db.Column(db.String(50), default="General", nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Float, nullable=False, default=0.0)
    min_stock = db.Column(db.Integer, default=10, nullable=False)
    
    supplier_id = db.Column(
        db.Integer,
        db.ForeignKey('supplier.id', ondelete='CASCADE'),
        nullable=False
    )

    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    @property
    def total_value(self):
        return round(self.price * self.quantity, 2)

    @property
    def stock_status(self):
        if self.quantity <= 0:
            return "Out of Stock"
        elif self.quantity <= self.min_stock:
            return "Low Stock"
        return "In Stock"

    def __repr__(self):
        return f"<Item {self.name} (Qty: {self.quantity})>"


class StockTransaction(db.Model):
    __tablename__ = "stock_transaction"

    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id', ondelete='SET NULL'), nullable=True)
    item_name = db.Column(db.String(100), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'IN', 'OUT', 'ADJUSTMENT', 'INITIAL'
    quantity_change = db.Column(db.Integer, nullable=False)
    quantity_after = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.String(255), nullable=True)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<Transaction {self.transaction_type} {self.item_name} ({self.quantity_change})>"


# ==============================================================================
# Helper Functions
# ==============================================================================

def seed_initial_demo_data():
    """Populates realistic starter demo data if tables are empty."""
    if Supplier.query.count() == 0:
        # Create Suppliers
        supp1 = Supplier(
            company_name="Apex Electronics Corp",
            contact_person="Rohan Verma",
            phone="+91 98765 43210",
            email="sales@apexelectronics.in",
            address="Sector 62, Noida, Uttar Pradesh, 201309"
        )
        supp2 = Supplier(
            company_name="Global Office Supplies Ltd",
            contact_person="Priya Nair",
            phone="+91 98111 22334",
            email="contact@globaloffices.com",
            address="Connaught Place, New Delhi, 110001"
        )
        supp3 = Supplier(
            company_name="Swift Hardware & Logistics",
            contact_person="Vikram Singh",
            phone="+91 99223 34455",
            email="support@swifthardware.in",
            address="Industrial Area Phase 2, Greater Noida, 201306"
        )

        db.session.add_all([supp1, supp2, supp3])
        db.session.commit()

        # Create Items
        demo_items = [
            Item(name="Logitech MX Master 3S Mouse", sku="INV-ELEC-001", category="Electronics", quantity=35, price=8999.00, min_stock=10, supplier_id=supp1.id),
            Item(name="Dell UltraSharp 27\" 4K Monitor", sku="INV-ELEC-002", category="Electronics", quantity=14, price=38499.00, min_stock=5, supplier_id=supp1.id),
            Item(name="Mechanical RGB Gaming Keyboard", sku="INV-ELEC-003", category="Electronics", quantity=6, price=4599.00, min_stock=12, supplier_id=supp1.id),
            Item(name="Ergonomic Mesh Office Chair", sku="INV-FURN-001", category="Furniture", quantity=18, price=11200.00, min_stock=8, supplier_id=supp2.id),
            Item(name="Heavy Duty Shredder Machine", sku="INV-OFF-001", category="Office Equipment", quantity=4, price=6500.00, min_stock=5, supplier_id=supp2.id),
            Item(name="Cat6 High-Speed Ethernet Cable 15m", sku="INV-NET-001", category="Networking", quantity=60, price=499.00, min_stock=20, supplier_id=supp3.id),
            Item(name="Industrial Cable Ties (Pack of 500)", sku="INV-HARD-001", category="Hardware", quantity=2, price=299.00, min_stock=15, supplier_id=supp3.id),
            Item(name="USB-C 100W Fast Charging Cable", sku="INV-ELEC-004", category="Electronics", quantity=0, price=799.00, min_stock=10, supplier_id=supp1.id),
        ]

        db.session.add_all(demo_items)
        db.session.commit()

        # Log initial transactions
        for item in demo_items:
            t = StockTransaction(
                item_id=item.id,
                item_name=item.name,
                transaction_type="INITIAL",
                quantity_change=item.quantity,
                quantity_after=item.quantity,
                notes="Initial inventory setup"
            )
            db.session.add(t)
        db.session.commit()


# ==============================================================================
# Routes
# ==============================================================================

@app.route("/")
@app.route("/home")
def home():
    """Main dashboard overview with KPIs, low stock warnings, and recent activity."""
    total_products = Item.query.count()
    total_suppliers = Supplier.query.count()
    total_stock_units = db.session.query(db.func.sum(Item.quantity)).scalar() or 0
    inventory_value = db.session.query(db.func.sum(Item.price * Item.quantity)).scalar() or 0
    
    # Low stock & out of stock items
    low_stock_items = Item.query.filter(Item.quantity <= Item.min_stock).all()
    low_stock_count = len(low_stock_items)
    out_of_stock_count = Item.query.filter(Item.quantity <= 0).count()

    # Recent transactions
    recent_transactions = StockTransaction.query.order_by(StockTransaction.timestamp.desc()).limit(6).all()

    return render_template(
        "index.html",
        total_products=total_products,
        total_suppliers=total_suppliers,
        total_stock_units=total_stock_units,
        inventory_value=round(inventory_value, 2),
        low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count,
        low_stock_items=low_stock_items[:5],
        recent_transactions=recent_transactions
    )


@app.route("/inventory")
def inventory():
    """Inventory catalog listing with search, category filters, and quick stock updates."""
    category_filter = request.args.get("category", "").strip()
    status_filter = request.args.get("status", "").strip()
    search_query = request.args.get("q", "").strip()

    query = Item.query

    if category_filter:
        query = query.filter(Item.category == category_filter)

    if status_filter == "low_stock":
        query = query.filter(Item.quantity > 0, Item.quantity <= Item.min_stock)
    elif status_filter == "out_of_stock":
        query = query.filter(Item.quantity <= 0)
    elif status_filter == "in_stock":
        query = query.filter(Item.quantity > Item.min_stock)

    if search_query:
        query = query.filter(
            (Item.name.ilike(f"%{search_query}%")) |
            (Item.sku.ilike(f"%{search_query}%")) |
            (Item.category.ilike(f"%{search_query}%"))
        )

    items = query.order_by(Item.id.desc()).all()
    suppliers = Supplier.query.order_by(Supplier.company_name).all()
    
    # Distinct categories for filter buttons
    categories = [cat[0] for cat in db.session.query(Item.category).distinct().all() if cat[0]]

    # Quick overview metrics
    total_items_count = len(items)
    total_items_value = sum(item.total_value for item in items)
    low_stock_items_count = sum(1 for item in items if item.quantity <= item.min_stock)

    return render_template(
        "inventory.html",
        items=items,
        suppliers=suppliers,
        categories=categories,
        selected_category=category_filter,
        selected_status=status_filter,
        search_query=search_query,
        total_items_count=total_items_count,
        total_items_value=round(total_items_value, 2),
        low_stock_items_count=low_stock_items_count
    )


@app.route("/add_product", methods=["POST"])
def add_product():
    """Add a new item to inventory with validation and transaction logging."""
    try:
        name = request.form["name"].strip()
        sku = request.form.get("sku", "").strip() or None
        category = request.form.get("category", "General").strip() or "General"
        quantity = int(request.form.get("quantity", 0))
        price = float(request.form.get("price", 0.0))
        min_stock = int(request.form.get("min_stock", 10))
        supplier_id = int(request.form["supplier_id"])

        if quantity < 0 or price < 0:
            flash("Quantity and Price cannot be negative.", "danger")
            return redirect(url_for("inventory"))

        supplier = db.session.get(Supplier, supplier_id)
        if not supplier:
            flash("Selected supplier does not exist. Please register the supplier first.", "danger")
            return redirect(url_for("inventory"))

        # Auto-generate SKU if not provided
        if not sku:
            prefix = category[:3].upper() if category else "INV"
            sku = f"{prefix}-{datetime.now().strftime('%m%d%H%M%S')}"

        item = Item(
            name=name,
            sku=sku,
            category=category,
            quantity=quantity,
            price=price,
            min_stock=min_stock,
            supplier_id=supplier_id
        )

        db.session.add(item)
        db.session.flush()  # Generates item.id

        # Log transaction
        tx = StockTransaction(
            item_id=item.id,
            item_name=item.name,
            transaction_type="INITIAL",
            quantity_change=quantity,
            quantity_after=quantity,
            notes="Product initial stock added"
        )
        db.session.add(tx)
        db.session.commit()

        flash(f"Product '{item.name}' added successfully!", "success")
    except IntegrityError:
        db.session.rollback()
        flash("A product with this SKU code already exists. Please choose a unique SKU.", "danger")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding product: {str(e)}", "danger")

    return redirect(url_for("inventory"))


@app.route("/edit_product", methods=["POST"])
def edit_product():
    """Update existing product details."""
    try:
        product_id = request.form.get("id")
        if not product_id:
            flash("Product ID is required for editing.", "danger")
            return redirect(url_for("inventory"))

        item = db.session.get(Item, int(product_id))
        if not item:
            flash(f"Product with ID #{product_id} not found.", "danger")
            return redirect(url_for("inventory"))

        old_quantity = item.quantity

        if request.form.get("name"):
            item.name = request.form["name"].strip()

        if request.form.get("sku"):
            item.sku = request.form["sku"].strip()

        if request.form.get("category"):
            item.category = request.form["category"].strip()

        if request.form.get("price") is not None and request.form.get("price") != "":
            item.price = float(request.form["price"])

        if request.form.get("min_stock") is not None and request.form.get("min_stock") != "":
            item.min_stock = int(request.form["min_stock"])

        if request.form.get("supplier_id"):
            item.supplier_id = int(request.form["supplier_id"])

        if request.form.get("quantity") is not None and request.form.get("quantity") != "":
            new_quantity = int(request.form["quantity"])
            if new_quantity != old_quantity:
                qty_diff = new_quantity - old_quantity
                item.quantity = new_quantity
                tx = StockTransaction(
                    item_id=item.id,
                    item_name=item.name,
                    transaction_type="ADJUSTMENT",
                    quantity_change=qty_diff,
                    quantity_after=new_quantity,
                    notes="Manual inventory quantity update via Edit"
                )
                db.session.add(tx)

        db.session.commit()
        flash(f"Product '{item.name}' updated successfully!", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Update failed: SKU code must be unique.", "danger")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating product: {str(e)}", "danger")

    return redirect(url_for("inventory"))


@app.route("/remove_product", methods=["POST"])
def remove_product():
    """Remove product from database."""
    try:
        product_id = request.form.get("id")
        if not product_id:
            flash("Product ID missing.", "danger")
            return redirect(url_for("inventory"))

        item = db.session.get(Item, int(product_id))
        if item:
            item_name = item.name
            db.session.delete(item)
            db.session.commit()
            flash(f"Product '{item_name}' (ID: #{product_id}) removed successfully.", "info")
        else:
            flash(f"Product with ID #{product_id} not found.", "warning")
    except Exception as e:
        db.session.rollback()
        flash(f"Error removing product: {str(e)}", "danger")

    return redirect(url_for("inventory"))


@app.route("/quick_adjust_stock", methods=["POST"])
def quick_adjust_stock():
    """Quick stock adjustment (+/- stock by custom amount)."""
    try:
        item_id = int(request.form["id"])
        action = request.form.get("action", "add")  # 'add' or 'subtract'
        amount = int(request.form.get("amount", 1))
        reason = request.form.get("reason", "Quick adjustment").strip()

        item = db.session.get(Item, item_id)
        if not item:
            flash("Product not found.", "danger")
            return redirect(url_for("inventory"))

        if action == "add":
            item.quantity += amount
            qty_change = amount
            tx_type = "IN"
        else:
            if item.quantity < amount:
                flash(f"Cannot subtract {amount} units. Current stock is only {item.quantity}.", "warning")
                return redirect(url_for("inventory"))
            item.quantity -= amount
            qty_change = -amount
            tx_type = "OUT"

        tx = StockTransaction(
            item_id=item.id,
            item_name=item.name,
            transaction_type=tx_type,
            quantity_change=qty_change,
            quantity_after=item.quantity,
            notes=reason
        )
        db.session.add(tx)
        db.session.commit()

        flash(f"Stock for '{item.name}' updated to {item.quantity} units.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating stock: {str(e)}", "danger")

    return redirect(request.referrer or url_for("inventory"))


@app.route("/supplier")
def supplier():
    """Suppliers directory with search and active inventory metrics."""
    search_query = request.args.get("q", "").strip()
    query = Supplier.query

    if search_query:
        query = query.filter(
            (Supplier.company_name.ilike(f"%{search_query}%")) |
            (Supplier.contact_person.ilike(f"%{search_query}%")) |
            (Supplier.email.ilike(f"%{search_query}%")) |
            (Supplier.phone.ilike(f"%{search_query}%"))
        )

    suppliers = query.order_by(Supplier.company_name).all()
    total_suppliers = len(suppliers)

    return render_template(
        "supplier.html",
        suppliers=suppliers,
        total_suppliers=total_suppliers,
        search_query=search_query
    )


@app.route("/add_supplier", methods=["POST"])
def add_supplier():
    """Register a new supplier."""
    try:
        company_name = request.form["company_name"].strip()
        contact_person = request.form["contact_person"].strip()
        phone = request.form["phone"].strip()
        email = request.form["email"].strip()
        address = request.form["address"].strip()

        supplier = Supplier(
            company_name=company_name,
            contact_person=contact_person,
            phone=phone,
            email=email,
            address=address
        )

        db.session.add(supplier)
        db.session.commit()
        flash(f"Supplier '{company_name}' registered successfully!", "success")
    except IntegrityError:
        db.session.rollback()
        flash("A supplier with this Company Name or Email already exists.", "danger")
    except Exception as e:
        db.session.rollback()
        flash(f"Error adding supplier: {str(e)}", "danger")

    return redirect(url_for("supplier"))


@app.route("/edit_supplier", methods=["POST"])
def edit_supplier():
    """Edit supplier information."""
    try:
        supplier_id = request.form.get("id")
        if not supplier_id:
            flash("Supplier ID is missing.", "danger")
            return redirect(url_for("supplier"))

        supplier = db.session.get(Supplier, int(supplier_id))
        if not supplier:
            flash(f"Supplier ID #{supplier_id} not found.", "danger")
            return redirect(url_for("supplier"))

        if request.form.get("company_name"):
            supplier.company_name = request.form["company_name"].strip()

        if request.form.get("contact_person"):
            supplier.contact_person = request.form["contact_person"].strip()

        if request.form.get("phone"):
            supplier.phone = request.form["phone"].strip()

        if request.form.get("email"):
            supplier.email = request.form["email"].strip()

        if request.form.get("address"):
            supplier.address = request.form["address"].strip()

        db.session.commit()
        flash(f"Supplier '{supplier.company_name}' updated successfully!", "success")
    except IntegrityError:
        db.session.rollback()
        flash("Update failed: Company name or email must be unique.", "danger")
    except Exception as e:
        db.session.rollback()
        flash(f"Error updating supplier: {str(e)}", "danger")

    return redirect(url_for("supplier"))


@app.route("/remove_supplier", methods=["POST"])
def remove_supplier():
    """Remove supplier and its dependent products."""
    try:
        supplier_id = request.form.get("id")
        if not supplier_id:
            flash("Supplier ID is missing.", "danger")
            return redirect(url_for("supplier"))

        supplier = db.session.get(Supplier, int(supplier_id))
        if supplier:
            company = supplier.company_name
            items_count = len(supplier.items)
            db.session.delete(supplier)
            db.session.commit()
            if items_count > 0:
                flash(f"Supplier '{company}' and {items_count} linked product(s) were removed.", "info")
            else:
                flash(f"Supplier '{company}' removed successfully.", "info")
        else:
            flash(f"Supplier ID #{supplier_id} not found.", "warning")
    except Exception as e:
        db.session.rollback()
        flash(f"Error removing supplier: {str(e)}", "danger")

    return redirect(url_for("supplier"))


@app.route("/reports")
def reports():
    """Comprehensive analytical reports with charts, KPIs, and audit log."""
    total_products = Item.query.count()
    total_suppliers = Supplier.query.count()
    total_units = db.session.query(db.func.sum(Item.quantity)).scalar() or 0
    inventory_value = db.session.query(db.func.sum(Item.price * Item.quantity)).scalar() or 0
    
    low_stock_items = Item.query.filter(Item.quantity <= Item.min_stock).all()
    low_stock = len(low_stock_items)
    out_of_stock = Item.query.filter(Item.quantity <= 0).count()

    # Product names and values (sorted top by value for chart)
    products = Item.query.all()
    sorted_by_val = sorted(products, key=lambda p: p.total_value, reverse=True)[:10]
    product_names = [p.name for p in sorted_by_val]
    inventory_values = [p.total_value for p in sorted_by_val]

    # Category distribution
    category_summary = db.session.query(
        Item.category,
        db.func.sum(Item.quantity),
        db.func.sum(Item.price * Item.quantity)
    ).group_by(Item.category).all()

    category_labels = [c[0] for c in category_summary]
    category_quantities = [int(c[1] or 0) for c in category_summary]
    category_values = [round(float(c[2] or 0.0), 2) for c in category_summary]

    # Supplier contributions
    suppliers = Supplier.query.all()
    supplier_labels = [s.company_name for s in suppliers]
    supplier_products = [len(s.items) for s in suppliers]

    # Recent Audit Log / Transactions
    recent_transactions = StockTransaction.query.order_by(StockTransaction.timestamp.desc()).limit(20).all()

    return render_template(
        "reports.html",
        total_products=total_products,
        total_suppliers=total_suppliers,
        total_units=total_units,
        inventory_value=round(inventory_value, 2),
        low_stock=low_stock,
        out_of_stock=out_of_stock,
        low_stock_items=low_stock_items,
        product_names=product_names,
        inventory_values=inventory_values,
        category_labels=category_labels,
        category_quantities=category_quantities,
        category_values=category_values,
        supplier_labels=supplier_labels,
        supplier_products=supplier_products,
        recent_transactions=recent_transactions
    )


@app.route("/search")
def search():
    """Global search across inventory products and suppliers."""
    q = request.args.get("q", "").strip()
    if not q:
        return redirect(url_for("home"))

    items = Item.query.filter(
        (Item.name.ilike(f"%{q}%")) |
        (Item.sku.ilike(f"%{q}%")) |
        (Item.category.ilike(f"%{q}%"))
    ).all()

    suppliers = Supplier.query.filter(
        (Supplier.company_name.ilike(f"%{q}%")) |
        (Supplier.contact_person.ilike(f"%{q}%")) |
        (Supplier.email.ilike(f"%{q}%")) |
        (Supplier.phone.ilike(f"%{q}%")) |
        (Supplier.address.ilike(f"%{q}%"))
    ).all()

    return render_template(
        "search_results.html",
        query=q,
        items=items,
        suppliers=suppliers,
        total_results=len(items) + len(suppliers)
    )


@app.route("/export/inventory")
def export_inventory():
    """Export inventory catalog as downloadable CSV file."""
    items = Item.query.order_by(Item.id).all()
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Header
    writer.writerow(["ID", "SKU", "Product Name", "Category", "Quantity", "Price (INR)", "Total Value (INR)", "Min Stock", "Stock Status", "Supplier"])
    
    for item in items:
        writer.writerow([
            item.id,
            item.sku or "",
            item.name,
            item.category,
            item.quantity,
            item.price,
            item.total_value,
            item.min_stock,
            item.stock_status,
            item.supplier.company_name if item.supplier else "N/A"
        ])
    
    output.seek(0)
    filename = f"inventra_inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.route("/export/suppliers")
def export_suppliers():
    """Export suppliers directory as downloadable CSV file."""
    suppliers = Supplier.query.order_by(Supplier.id).all()
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["ID", "Company Name", "Contact Person", "Phone", "Email", "Address", "Total Products Supplied"])

    for s in suppliers:
        writer.writerow([
            s.id,
            s.company_name,
            s.contact_person,
            s.phone,
            s.email,
            s.address,
            len(s.items)
        ])

    output.seek(0)
    filename = f"inventra_suppliers_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@app.route("/seed_demo_data")
def seed_demo_data():
    """Seed demo data endpoint."""
    seed_initial_demo_data()
    flash("Demo products, suppliers, and transaction records loaded successfully!", "success")
    return redirect(url_for("home"))


@app.route("/contact", methods=["GET", "POST"])
def contact():
    """Contact page with direct feedback submission."""
    if request.method == "POST":
        name = request.form.get("name", "User")
        email = request.form.get("email", "")
        message = request.form.get("message", "")
        flash(f"Thank you, {name}! Your message has been received. Our team will contact you at {email}.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")


@app.route("/debug-env")
def debug_env():
    """Diagnostic route for Vercel serverless environment verification."""
    return jsonify({
        "path": request.path,
        "full_path": request.full_path,
        "environ_PATH_INFO": request.environ.get("PATH_INFO"),
        "environ_REQUEST_URI": request.environ.get("REQUEST_URI"),
        "environ_RAW_URI": request.environ.get("RAW_URI"),
        "HTTP_X_MATCHED_PATH": request.environ.get("HTTP_X_MATCHED_PATH"),
        "HTTP_X_FORWARDED_URI": request.environ.get("HTTP_X_FORWARDED_URI"),
        "HTTP_X_FORWARDED_PATH": request.environ.get("HTTP_X_FORWARDED_PATH"),
        "headers": {k: v for k, v in request.headers.items() if "cookie" not in k.lower() and "auth" not in k.lower()}
    })


# ==============================================================================
# Run Application
# ==============================================================================

def init_db():
    with app.app_context():
        db.create_all()
        # Automatically populate demo data if newly initialized database is empty
        if Supplier.query.count() == 0 and Item.query.count() == 0:
            seed_initial_demo_data()

# Ensure database tables and initial demo data are ready upon import (crucial for Vercel serverless)
try:
    init_db()
except Exception as e:
    print(f"Database initialization notice: {e}")

if __name__ == "__main__":
    app.run(debug=True)