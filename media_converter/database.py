import psycopg2

DB_NAME = "wifi_card"
DB_USER = "admin"
DB_PASS = "admin"
DB_HOST = "localhost"
DB_PORT = "5432"

def connect_db():
    # Connect to the database
    conn = psycopg2.connect(
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )
    print("Database connected successfully")
    
    # Create a cursor object
    cursor = conn.cursor()

    return conn, cursor

def read_ads_db():
    try:
        conn, cursor = connect_db()

        # Define your SQL query
        query = "SELECT * FROM ad_campaigns"

        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the result
        rows = cursor.fetchall()

        conn.commit()

        return rows

    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def update_ads(data_id):
    # done_ads()
    try:
        conn, cursor = connect_db()

        query = "SELECT * FROM ad_campaigns WHERE id = %s"
        cursor.execute(query, (data_id,))

        data = cursor.fetchone()

        create_table_query = '''
            CREATE TABLE IF NOT EXISTS done_ad_campaigns (
            id SERIAL PRIMARY KEY,
            company_name TEXT NOT NULL,
            budget NUMERIC(10, 2) NOT NULL,
            campaign_title TEXT NOT NULL,
            start_date DATE NOT NULL,
            duration INT NOT NULL,
            ad_category TEXT NOT NULL,
            notes TEXT,
            ad_video TEXT NOT NULL,
            url_link TEXT NOT NULL, 
            exposure INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        '''

        # Execute the query
        cursor.execute(create_table_query)

        # Commit the transaction
        conn.commit()

        insert_query = """
        INSERT INTO done_ad_campaigns (id, company_name, budget, campaign_title, start_date, duration, ad_category, notes, ad_video, url_link, exposure) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        # Execute the query
        cursor.execute(insert_query, data[:-1])
        
        # Commit the transaction
        conn.commit()

        query = "DELETE FROM ad_campaigns WHERE id = %s"
        cursor.execute(query, (data_id,))

        conn.commit()

    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    