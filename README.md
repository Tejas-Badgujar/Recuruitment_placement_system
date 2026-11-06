# Recruitment & Placement Management System (RPMS)

Python + MySQL console application.

## Initial setup (Windows PowerShell)

1. Open this folder in VS Code.
2. Create a virtual environment:

   ```powershell
   py -m venv .venv
   ```

3. Activate it:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, run this for the current terminal only:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

4. Install packages:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Copy `.env.example` to `.env` and enter the credentials for the MySQL server
   where `recruitment_placement_db` was created.

6. Test the connection:

   ```powershell
   python test_connection.py
   ```

7. Start the current application placeholder:

   ```powershell
   python main.py
   ```

## Important

- Use one MySQL server instance for this project.
- `DB_PORT` must match the port of that server (commonly 3306).
- For XAMPP, the default local root password is often blank, but use the
  actual password configured on your machine.
- For standalone MySQL, use the password configured during installation.
- Never share your `.env` file or commit it to Git.
