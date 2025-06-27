# nanoarrow_pyarrow_validation.py


def check_environment():
    import importlib

    print("== Environment Check ==")
    for pkg in ["snowflake.snowpark", "pyarrow", "nanoarrow"]:
        spec = importlib.util.find_spec(pkg)
        status = "✅ found" if spec else "❌ not found"
        print(f"{pkg:<30} : {status}")


def validate_dataframe():
    from snowflake.snowpark import Session

    try:
        session = Session.builder.configs(
            {
                "account": "<your_account>",
                "user": "<your_user>",
                "password": "<your_password>",
                "role": "<your_role>",
                "warehouse": "<your_wh>",
                "database": "<your_db>",
                "schema": "<your_schema>",
            }
        ).create()

        df = session.sql("SELECT 42 AS answer").to_pandas()
        print(f"✅ DataFrame loaded: {df.head()}")
    except Exception as e:
        print(f"❌ DataFrame operation failed: {e}")


if __name__ == "__main__":
    check_environment()
    print()
    validate_dataframe()
