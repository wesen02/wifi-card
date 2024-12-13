import hashlib
import psycopg2
import os
import argparse

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def rename_file(old_path, new_filename):
    # Extract directory and old filename
    directory, old_filename = os.path.split(old_path)
    
    # Replace the old filename with the new one
    new_path = os.path.join(directory, new_filename)
    
    # Rename the file
    try:
        os.rename(old_path, new_path)
        print(f"File renamed from '{old_path}' to '{new_path}'")
    except FileNotFoundError:
        print(f"Error: '{old_path}' does not exist.")
    except PermissionError:
        print(f"Error: Permission denied for renaming '{old_path}'.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def hash_text(text):
    # Encode the text to bytes, then hash using SHA-256
    hashed = hashlib.sha256(text.encode('utf-8')).hexdigest()
    return hashed

def read_ads_db(target_state, target_area):
    try:
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

        # Define your SQL query
        query = f"SELECT * FROM ad_campaigns_{target_state}_{target_area}"

        # Execute the query
        cursor.execute(query)

        # Fetch all rows from the result
        rows = cursor.fetchall()

        # Iterate through the rows and print them
        for row in rows:
            video_path = row[8]
            company_name = row[1]
            start_date = row[4]
            campaign_id = row[0]

            directory = os.path.dirname(video_path)
            file_extension = video_path.split(".")[-1]            

            video_name = hash_text(company_name + str(start_date))[:6] + "." + file_extension
            rename_file(video_path, video_name)

            new_video_path = os.path.join(directory, video_name)

            update_query = f"UPDATE ad_campaigns_{target_state}_{target_area} SET ad_video = %s WHERE id = %s"
            cursor.execute(update_query, (new_video_path, campaign_id))  # Assuming the first column is the ID
        
        conn.commit()

    except psycopg2.Error as e:
        print(f"Error connecting to database: {e}")
    finally:
        # Close the cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def main():
    # Create the argument parser
    parser = argparse.ArgumentParser(description="Insert file path")
    
    # Add an argument for the database name (optional)
    parser.add_argument(
        '--file_path', 
        type=str, 
        help="video file path",
        required=True
    )
    
    # Parse the arguments
    args = parser.parse_args()

    file_parts = args.file_path.split("@")
    print(file_parts)
    target_state = file_parts[1]
    target_area = file_parts[2].split(".")[0]

    read_ads_db(target_state, target_area)

if __name__=="__main__":
    main()