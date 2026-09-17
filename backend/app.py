from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import os
import time

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
CORS(app, resources={r"/api/*": {"origins": os.getenv("CORS_ALLOWED_ORIGINS", "*")}})


def get_db():
    retries = int(os.getenv("DB_CONNECT_RETRIES", "10"))
    wait_seconds = int(os.getenv("DB_CONNECT_WAIT_SECONDS", "3"))

    while retries > 0:
        try:
            conn = mysql.connector.connect(
                host=os.getenv("DB_HOST", "mysql"),
                port=int(os.getenv("DB_PORT", "3306")),
                user=os.getenv("DB_USER", "gardenuser"),
                password=os.getenv("DB_PASSWORD", "gardenpass"),
                database=os.getenv("DB_NAME", "gardening_db"),
                connection_timeout=10,
                autocommit=False,
            )
            return conn
        except mysql.connector.Error as exc:
            retries -= 1
            if retries == 0:
                raise RuntimeError(f"Could not connect to MySQL after retries: {exc}") from exc
            time.sleep(wait_seconds)

    raise RuntimeError("Could not connect to MySQL after retries")


@app.route("/api/health")
def health():
    try:
        conn = get_db()
        conn.close()
        return jsonify({"status": "ok", "database": "connected"})
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/api/dashboard")
def dashboard():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    stats = {}

    cur.execute("SELECT COUNT(*) AS total FROM products")
    stats["total_products"] = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM customers")
    stats["total_customers"] = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM employees")
    stats["total_employees"] = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) AS total FROM orders")
    stats["total_orders"] = cur.fetchone()["total"]

    cur.execute("SELECT COALESCE(SUM(total_amount),0) AS revenue FROM orders WHERE status='delivered'")
    stats["total_revenue"] = float(cur.fetchone()["revenue"])

    cur.execute("SELECT COUNT(*) AS total FROM garden_projects WHERE status='in_progress'")
    stats["active_projects"] = cur.fetchone()["total"]

    cur.execute("""
        SELECT o.status, COUNT(*) AS cnt
        FROM orders o GROUP BY o.status
    """)
    stats["order_breakdown"] = cur.fetchall()

    cur.execute("""
        SELECT category, COUNT(*) AS cnt, SUM(stock) AS total_stock
        FROM products GROUP BY category
    """)
    stats["product_categories"] = cur.fetchall()

    cur.close()
    conn.close()
    return jsonify(stats)


@app.route("/api/products")
def get_products():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM products ORDER BY category, name")
    data = cur.fetchall()
    for row in data:
        row["price"] = float(row["price"])
    cur.close()
    conn.close()
    return jsonify(data)


@app.route("/api/products", methods=["POST"])
def add_product():
    d = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO products (name,category,price,stock,description) VALUES (%s,%s,%s,%s,%s)",
        (d["name"], d["category"], d["price"], d.get("stock", 0), d.get("description", ""))
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    return jsonify({"id": new_id, "message": "Product added"}), 201


@app.route("/api/products/<int:pid>", methods=["DELETE"])
def delete_product(pid):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id=%s", (pid,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Deleted"})


@app.route("/api/customers")
def get_customers():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM customers ORDER BY name")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(data)


@app.route("/api/customers", methods=["POST"])
def add_customer():
    d = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO customers (name,email,phone,address) VALUES (%s,%s,%s,%s)",
        (d["name"], d["email"], d.get("phone", ""), d.get("address", ""))
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    return jsonify({"id": new_id, "message": "Customer added"}), 201


@app.route("/api/employees")
def get_employees():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM employees ORDER BY department, name")
    data = cur.fetchall()
    for row in data:
        if row.get("salary"):
            row["salary"] = float(row["salary"])
        if row.get("hire_date"):
            row["hire_date"] = str(row["hire_date"])
    cur.close()
    conn.close()
    return jsonify(data)


@app.route("/api/employees", methods=["POST"])
def add_employee():
    d = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO employees (name,role,department,email,phone,hire_date,salary) VALUES (%s,%s,%s,%s,%s,%s,%s)",
        (d["name"], d["role"], d.get("department", ""), d["email"], d.get("phone", ""), d.get("hire_date"), d.get("salary", 0))
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    return jsonify({"id": new_id, "message": "Employee added"}), 201


@app.route("/api/orders")
def get_orders():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT o.*, c.name AS customer_name
        FROM orders o LEFT JOIN customers c ON o.customer_id=c.id
        ORDER BY o.order_date DESC
    """)
    data = cur.fetchall()
    for row in data:
        row["total_amount"] = float(row["total_amount"])
        if row.get("order_date"):
            row["order_date"] = str(row["order_date"])
    cur.close()
    conn.close()
    return jsonify(data)


@app.route("/api/projects")
def get_projects():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("""
        SELECT gp.*, c.name AS customer_name, e.name AS employee_name
        FROM garden_projects gp
        LEFT JOIN customers c ON gp.customer_id=c.id
        LEFT JOIN employees e ON gp.assigned_employee_id=e.id
        ORDER BY gp.created_at DESC
    """)
    data = cur.fetchall()
    for row in data:
        if row.get("budget"):
            row["budget"] = float(row["budget"])
        if row.get("start_date"):
            row["start_date"] = str(row["start_date"])
        if row.get("end_date"):
            row["end_date"] = str(row["end_date"])
        if row.get("created_at"):
            row["created_at"] = str(row["created_at"])
    cur.close()
    conn.close()
    return jsonify(data)


@app.route("/api/projects", methods=["POST"])
def add_project():
    d = request.json
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO garden_projects 
        (title,customer_id,assigned_employee_id,project_type,status,start_date,end_date,budget,description)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (d["title"], d.get("customer_id"), d.get("assigned_employee_id"),
         d.get("project_type", ""), d.get("status", "planning"),
         d.get("start_date"), d.get("end_date"), d.get("budget", 0), d.get("description", ""))
    )
    conn.commit()
    new_id = cur.lastrowid
    cur.close()
    conn.close()
    return jsonify({"id": new_id, "message": "Project created"}), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)
