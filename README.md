# 📦 INVENTRA - Smart Inventory Management System

<p align="center">
  <img src="static/asset/LOGO.png" alt="INVENTRA Logo" width="120">
</p>

<p align="center">
  <strong>Manage • Track • Grow</strong><br>
  A modern, responsive, full-stack Inventory & Supply Chain Management Web Application built with <strong>Python Flask</strong>, <strong>SQLAlchemy</strong>, <strong>SQLite</strong>, <strong>Bootstrap 5</strong>, and <strong>Chart.js</strong>.
</p>

---

## 🌟 Overview

**INVENTRA** simplifies warehouse cataloging, vendor relationship management, stock reordering, and business analytics. Designed for high efficiency with real-time stock adjustment, category-level organization, instant client-side table filtering, and automated transaction audit logging.

---

## 🚀 Key Features

### 1. 📊 Interactive Dashboard
- **Live KPI Metrics:** Total product count, total stock units, real-time inventory valuation (₹), and active registered vendors.
- **Low Stock Warning Banner:** Automated detection of products below safety thresholds with one-click reorder navigation.
- **Recent Stock Movement Feed:** Live audit log displaying recent incoming and outgoing stock adjustments.
- **Hero Carousel Showcase:** Visual walkthrough of warehouse capabilities and analytics.

### 2. 📦 Inventory Catalog Management
- **Full CRUD Operations:** Add, edit, and delete products with automatic confirmation modals.
- **SKU Code Support:** Automatic or custom alphanumeric SKU codes for every product.
- **Category Organization:** Segment stock by Electronics, Furniture, Hardware, Networking, and more.
- **In-Row Quick Stock Adjustments:** Instant `+1` / `-1` buttons and detailed stock-in/stock-out dialogs with reference notes.
- **Stock Status Badges:** Dynamic color-coded pill indicators (`In Stock`, `Low Stock`, `Out of Stock`).
- **Instant Client-Side Filtering:** Search and filter table rows instantly without page reloads.
- **CSV Data Export:** One-click download of the complete inventory database as a formatted CSV file.

### 3. 🏢 Supplier Relationship Directory
- **Vendor Profiles:** Track company name, contact person, phone number, email, and facility address.
- **Linked Inventory Counters:** Displays live count of active products provided by each vendor.
- **Safe Cascade Deletion:** Clear alerts and warnings before removing suppliers with linked items.
- **CSV Vendor Export:** Export vendor directories to CSV with a single click.

### 4. 📈 Reports & Business Intelligence
- **Valuation by Product:** Interactive Chart.js bar chart showing highest valuation assets.
- **Category Stock Distribution:** Interactive doughnut chart visualizing unit allocations.
- **Supplier Contribution Chart:** Horizontal bar chart illustrating vendor coverage.
- **Critical Reorder Priority List:** Automated urgency sorting (`Critical`, `Low`, `Reorder Soon`).
- **Complete Audit Trail:** Detailed log of all historical stock changes (initial, in, out, adjustment) with timestamps.
- **Printable Report View:** Clean print stylesheet for instant generation of hardcopy reports.

### 5. 🔍 Global Search & Navigation
- **Unified Global Search:** Search across product names, SKU codes, categories, supplier names, and contact emails simultaneously.
- **Active Navigation Indicators:** Responsive Bootstrap 5 navbar with quick action buttons.
- **Animated Flash Messages:** Dismissible feedback toasts for all create, update, and delete actions.

---

## 🛠️ Tech Stack

- **Backend:** [Python 3.x](https://www.python.org/), [Flask 3.x](https://flask.palletsprojects.com/)
- **Database ORM:** [Flask-SQLAlchemy 3.x](https://flask-sqlalchemy.palletsprojects.com/) + [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Database Engine:** [SQLite](https://www.sqlite.org/) (zero-configuration, portable)
- **Frontend Framework:** [Bootstrap 5.3](https://getbootstrap.com/), [Bootstrap Icons](https://icons.getbootstrap.com/), [Font Awesome 6](https://fontawesome.com/)
- **Data Visualization:** [Chart.js](https://www.chartjs.org/)
- **WSGI Production Server:** [Gunicorn](https://gunicorn.org/)

---

## 📂 Project Structure

```text
mysterious-mendeleev/
├── app.py                     # Main Flask application & SQLAlchemy models
├── requirements.txt           # Python dependencies
├── README.md                  # Project documentation & guide
├── .gitignore                 # Git ignore rules
├── static/
│   ├── asset/                 # Application logos, graphics, and carousel banners
│   │   ├── LOGO.png
│   │   ├── INVENTORY.png
│   │   ├── STOCK.png
│   │   ├── GRAPH.png
│   │   ├── 1.png, 2.png, 3.png
│   │   └── ...
│   ├── css/
│   │   └── style.css          # Custom modern UI styling & polish
│   └── js/
│       └── main.js            # Modal automation, live search, and stock adjusting
└── templates/
    ├── base.html              # Core base layout with navbar, alerts & footer
    ├── index.html             # Home dashboard & analytics overview
    ├── inventory.html         # Inventory catalog with CRUD modals & filters
    ├── supplier.html          # Supplier directory with vendor management
    ├── reports.html           # Business reports, Chart.js charts & audit log
    ├── contact.html           # Contact details, message dispatch & maps
    └── search_results.html    # Global search results view
```

---

## ⚙️ Installation & Setup

### 1. Clone the repository
```bash
git clone https://github.com/CodingWithAman1/Inventra.git
cd Inventra
```

### 2. Create and activate a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python app.py
```

Open your browser and navigate to:
```
http://127.0.0.1:5000
```
> **Note:** On first launch, if the database is newly initialized, INVENTRA will automatically seed a rich demo dataset of suppliers, products, and transaction records so you can immediately explore the charts and tables!

---

## 👤 Author & Developer

**Aman Sharma**
- **GitHub:** [@CodingWithAman1](https://github.com/CodingWithAman1)
- **LinkedIn:** [Aman Sharma](https://www.linkedin.com/in/aman-sharma-web/)
- **Email:** [shruti.sharma6386@gmail.com](mailto:shruti.sharma6386@gmail.com)

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
