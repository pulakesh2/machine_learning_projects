from flask import Flask, render_template
import pandas as pd


# create our app
app = Flask(__name__)


def create_dataframe() -> pd.DataFrame:
    data:dict[str, list] = {
        "OrderID": [101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112],
        "Date": [
            "2025-01-05", "2025-01-07", "2025-01-10",
            "2025-02-03", "2025-02-15",
            "2025-03-01", "2025-03-05", "2025-03-12",
            "2025-04-01", "2025-04-15", "2025-04-20",
            "2025-05-01"
        ],
         "Customer": [
            "Rahul", "Priya", "Amit", "Sneha", "Rohan", "Anjali",
            "Vikram", "Neha", "Arjun", "Meera", "Rahul", "Priya"
        ],
        "City": [
            "Mumbai", "Delhi", "Kolkata", "Mumbai", "Delhi", "Bangalore",
            "Kolkata", "Mumbai", "Bangalore", "Delhi", "Mumbai", "Delhi"
        ],
        "Product": [
            "Laptop", "Mobile", "Chair", "Table", "Laptop", "Mobile",
            "Sofa", "Headphones", "Chair", "Table", "Mobile", "Sofa"
        ],
        "Category": [
            "Electronics", "Electronics", "Furniture", "Furniture",
            "Electronics", "Electronics", "Furniture", "Electronics",
            "Furniture", "Furniture", "Electronics", "Furniture"
        ],
        "Quantity": [1, 2, 4, 1, 1, 1, 1, 3, 2, 1, 1, 1],
        "Price": [
            55000, 20000, 1500, 7000, 55000, 20000,
            30000, 2000, 1500, 7000, 20000, 30000
        ],
        "PaymentMode": [
            "UPI", "Credit Card", "Cash", "UPI", "Credit Card", "UPI",
            "Cash", "UPI", "Credit Card", "UPI", "Cash", "UPI"
        ]
    }

    df = pd.DataFrame(data)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Revenue"] = df["Quantity"] * df["Price"]
    df['Month'] = df['Date'].dt.month_name()

    return df


@app.route("/")
def home():
    df = create_dataframe()
    total_revenue = df["Revenue"].sum()
    total_orders = df["OrderID"].count()
    total_quantity = df["Quantity"].sum()
    average_order_value = df["Revenue"].mean()

    city_revenue = df.groupby("City")["Revenue"].sum().sort_values(ascending=False)
    product_revenue = df.groupby("Product")["Revenue"].sum().sort_values(ascending=False)
    customer_revenue = df.groupby("Customer")["Revenue"].sum().sort_values(ascending=False)

    best_city = city_revenue.index[0]
    best_product = product_revenue.index[0]
    best_customer = customer_revenue.index[0]


    city_table = city_revenue.reset_index().to_html(
        classes="table",
        index=False
    )

    product_table = product_revenue.reset_index().to_html(
        classes="table",
        index=False
    )

    total_table = df.reset_index().to_html(
        classes='table',
        index=False
    )

    return render_template(
        "index.html",
        total_revenue=total_revenue,
        total_orders=total_orders,
        total_quantity=total_quantity,
        average_order_value=average_order_value,
        best_city=best_city,
        best_product=best_product,
        best_customer=best_customer,
        city_table=city_table,
        product_table=product_table,
        total_table = total_table
    )


if __name__ == "__main__":
    app.run(debug=True)