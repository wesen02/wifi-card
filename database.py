import psycopg2
from psycopg2 import OperationalError, DatabaseError
import hashlib
import os

DB_NAME = "wifi_card"
DB_USER = "admin"
DB_PASS = "admin"
DB_HOST = "localhost"
DB_PORT = "5432"

def hash_text(text):
    # Encode the text to bytes, then hash using SHA-256
    hashed = hashlib.sha256(text.encode('utf-8')).hexdigest()
    return hashed

def shop_database(shop_info):
    if shop_info is None:
        return "No data found"
    else:
        shop_name = shop_info["shop_name"]
        phone_num = shop_info["phone_num"]
        wifi_name = shop_info["wifi_name"]
        wifi_password = shop_info["wifi_password"]
        security_type = shop_info["security_type"]
        location = shop_info["location"]
        shop_code = hash_text(shop_name + wifi_name)[:6]

        try:
            # Attempting to connect to the PostgreSQL database
            conn = psycopg2.connect(database=DB_NAME,
                                    user=DB_USER,
                                    password=DB_PASS,
                                    host=DB_HOST,
                                    port=DB_PORT)
            print("Database connected successfully")
            
            # Create a cursor object to interact with the database
            cursor = conn.cursor()

            # SQL query to create a table if it doesn't exist
            create_table_query = '''
                CREATE TABLE IF NOT EXISTS wifi_shops (
                id SERIAL PRIMARY KEY,
                shop_code VARCHAR(255) NOT NULL,
                shop_name VARCHAR(255) NOT NULL,
                phone_num VARCHAR(15) NOT NULL,
                wifi_name VARCHAR(255) NOT NULL,
                wifi_password VARCHAR(255) NOT NULL,
                security_type VARCHAR(10) NOT NULL CHECK (security_type IN ('WPA', 'WPA2', 'WEP', 'Open')),
                location TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            '''

            # Execute the query
            cursor.execute(create_table_query)

            # Commit the transaction
            conn.commit()

            check_query = """
            SELECT EXISTS (
                SELECT *
                FROM wifi_shops 
                WHERE shop_name = %s
            );
            """
            cursor.execute(check_query, (shop_name,))
            exists = cursor.fetchone()[0]  # Fetch the result

            if exists:
                return "Shop Exists"
            else:
                print("Table created successfully (if it didn't exist already).")

                insert_query = """
                INSERT INTO wifi_shops (shop_name, shop_code, phone_num, wifi_name, wifi_password, security_type, location)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
                """

                # Execute the query
                cursor.execute(insert_query, (shop_name, shop_code, phone_num, wifi_name, wifi_password, security_type, location))
                
                # Commit the transaction
                conn.commit()

                return "Data inserted successfully!"

        except OperationalError as e:
            # Handle specific operational errors (e.g., connection issues)
            print(f"OperationalError: {e}")
        except DatabaseError as e:
            # Handle database-related errors (e.g., invalid credentials or database not found)
            print(f"DatabaseError: {e}")
        except Exception as e:
            # Catch any other exceptions
            print(f"An unexpected error occurred: {e}")
        finally:
            # Ensure the connection is closed when done
            if 'conn' in locals() and conn:
                conn.close()
                print("Database connection closed.")

def ads_db(form_data, ad_video):

    company_name = form_data["company_name"]
    budget = form_data["budget"]
    campaign_title = form_data["campaign_title"]
    target_audience = form_data["target_audience"]
    start_date = form_data["start_date"]
    end_date = form_data["end_date"]
    ad_category = form_data["ad_category"]
    notes = form_data["notes"]
    url_link = form_data["url_link"]

    ad_video = os.path.join(os.getcwd(), ad_video)

    # video_name_hash = hash_text(company_name + start_date)[:6] + ".mp4"
    # rename_file(video_path, video_name_hash)

    try:
        # Attempting to connect to the PostgreSQL database
        conn = psycopg2.connect(database=DB_NAME,
                                user=DB_USER,
                                password=DB_PASS,
                                host=DB_HOST,
                                port=DB_PORT)
        print("Database connected successfully")
        
        # Create a cursor object to interact with the database
        cursor = conn.cursor()

        # SQL query to create a table if it doesn't exist
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS ad_campaigns (
            id SERIAL PRIMARY KEY,
            company_name TEXT NOT NULL,
            budget NUMERIC(10, 2) NOT NULL,
            campaign_title TEXT NOT NULL,
            target_audience TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            ad_category TEXT NOT NULL,
            notes TEXT,
            ad_video TEXT NOT NULL,
            url_link TEXT NOT NULL, 
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        '''

        # Execute the query
        cursor.execute(create_table_query)

        # Commit the transaction
        conn.commit()

        print("Table created successfully (if it didn't exist already).")

        insert_query = """
        INSERT INTO ad_campaigns (company_name, budget, campaign_title, target_audience, start_date, end_date, ad_category, notes, ad_video, url_link) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        # Execute the query
        cursor.execute(insert_query, (company_name, budget, campaign_title, target_audience, start_date, end_date, ad_category, notes, ad_video, url_link))
        
        # Commit the transaction
        conn.commit()

        return "Data inserted successfully!"

    except OperationalError as e:
        # Handle specific operational errors (e.g., connection issues)
        print(f"OperationalError: {e}")
    except DatabaseError as e:
        # Handle database-related errors (e.g., invalid credentials or database not found)
        print(f"DatabaseError: {e}")
    except Exception as e:
        # Catch any other exceptions
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure the connection is closed when done
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")

def video_database():
    try:
        # Attempting to connect to the PostgreSQL database
        conn = psycopg2.connect(database=DB_NAME,
                                user=DB_USER,
                                password=DB_PASS,
                                host=DB_HOST,
                                port=DB_PORT)
        print("Database connected successfully")
        
        # Create a cursor object to interact with the database
        cursor = conn.cursor()

        search_query = """
        SELECT * FROM ad_campaigns
        """
        cursor.execute(search_query)

        ad_data = cursor.fetchall()

        data_json = {}

        for data in ad_data:
            print(data)
            media_path = data[9]
            url_link = data[10]
            media_path = "/static/" + media_path.split("static")[-1]
            data_json = {
                "media_path": media_path,
                "url_link": url_link
            }

        # Commit the transaction
        conn.close()

        return data_json

    except OperationalError as e:
        # Handle specific operational errors (e.g., connection issues)
        print(f"OperationalError: {e}")
    except DatabaseError as e:
        # Handle database-related errors (e.g., invalid credentials or database not found)
        print(f"DatabaseError: {e}")
    except Exception as e:
        # Catch any other exceptions
        print(f"An unexpected error occurred: {e}")
    finally:
        # Ensure the connection is closed when done
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")