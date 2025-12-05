Installation
1) Clone repo:
git clone https://github.com/Taidanghoccode/mini-erp-internship.git
cd mini-erp-internship

2) Create virtual env: python -m venv venv
- venv\Scripts\activate   # Windows

3) Install dependencies: pip install -r requirements.txt

4) Configure database (config.py): SQLALCHEMY_DATABASE_URI = "postgresql://username:password@localhost:5432/erp_demo"

5) Initialize DB: python seed.py

6) Run: python main.py

Then visit:
http://127.0.0.1:5000

Token Refresh
Access token auto refresh every 25 minutes
Stored in localStorage + HttpOnly cookie
UI will re-trigger fetch if expired

👨‍💻 Author

Nguyễn Hữu Tài – FPT University Can Tho
Internship at FPT Software
