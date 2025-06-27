# validate_nanoarrow_get_active_session.py

import sys
import traceback

from snowflake.snowpark.context import get_active_session


def main():
    print("🧪 Nanoarrow + Active Session Validation Starting...")
    try:
        session = get_active_session()
        print("✅ Active session acquired.")

        df = session.sql("SELECT 123 AS value").to_pandas()
        print("✅ DataFrame operation succeeded. Result:")
        print(df.head())

        # Diagnostic check for pyarrow
        pyarrow_loaded = "pyarrow" in sys.modules
        print(f"🔍 pyarrow loaded: {pyarrow_loaded}")

        nanoarrow_loaded = "nanoarrow" in sys.modules
        print(f"🔍 nanoarrow loaded: {nanoarrow_loaded}")

    except Exception as e:
        print("❌ Exception occurred during nanoarrow validation.")
        traceback.print_exc()


if __name__ == "__main__":
    main()
