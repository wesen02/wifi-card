from database import connect_db

def get_ads():
    try:
        conn, cursor = connect_db()

        cursor.execute("""
            SELECT tablename 
            FROM pg_tables 
            WHERE tablename LIKE 'ad_campaigns_%';
        """)

        tables = cursor.fetchall()

        all_data = []

        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT * FROM {table_name} WHERE verify = %s", (False,))
            data = cursor.fetchall()
            if data:
                all_data.append((table_name, data))

        cursor.close()
        conn.close()

        return all_data

    except Exception as e:
        return f"An error occurred: {e}"

def update_ads(table_data):
    try:
        # Extract table name and ad_id
        parts = table_data.split("/")
        table_name = parts[1]
        ad_id = parts[-1]

        conn, cursor = connect_db()

        update_query = f"""
            UPDATE {table_name}
            SET verify = %s
            WHERE id = %s
        """
        cursor.execute(update_query, (True, ad_id))
        conn.commit()

        cursor.close()
        conn.close()

        return {"status": "success", "message": f"Update {table_name} successfully"}

    except Exception as e:
        return {"status": "error", "message": f"An error occurred: {e}"}