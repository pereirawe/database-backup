import os
import subprocess
import datetime
from dotenv import load_dotenv


def create_database_dump():
    current_directory = os.getcwd()
    project_directory = os.path.abspath(
        os.path.join(current_directory, os.pardir, os.pardir)
    )
    env_file_path = os.path.join(project_directory, ".env")

    try:
        load_dotenv(env_file_path)
        con_params = {
            "host": "localhost",
            "database": os.getenv("DB_DATABASE"),
            "user": os.getenv("DB_USERNAME"),
            "port": os.getenv("DB_PORT"),
        }

        backup_path = os.getenv("BD_BACKUP_PATH")
        backup_folder_path = os.path.join(project_directory, "current", backup_path)
        current_date = datetime.datetime.today().isoformat()
        output_file = os.path.join(backup_folder_path, f"{current_date}_dump.sql")
        pg_dump_command = [
            "pg_dump",
            f"--host={con_params['host']}",
            f"--port={con_params['port']}",
            f"--username={con_params['user']}",
            f"--file={output_file}",
            con_params["database"],
        ]

        subprocess.run(pg_dump_command, check=True)
        print(f"Database dump created at {output_file}")

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

    if os.getenv("DB_DELETE_OLD_BACKUPS") == "true":
        maximum_file_limit = os.getenv("DB_KEEP_BACKUPS")
        cleanup_old_files(backup_folder_path, maximum_file_limit)


def cleanup_old_files(folder, limit):
    print(f"Cleaning ald Database dump...")

    try:
        files = []
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path) and os.path.splitext(filename)[1] == ".sql":
                created_timestamp = os.path.getctime(file_path)
                files.append((file_path, created_timestamp))

        files.sort(key=lambda x: x[1])

        files_to_delete = max(0, len(files) - int(limit))

        for i in range(files_to_delete):
            file_to_delete, _ = files[i]
            os.remove(file_to_delete)
    except Exception as e:
        print(f"An error occurred while cleaning up files: {e}")


if __name__ == "__main__":
    create_database_dump()
