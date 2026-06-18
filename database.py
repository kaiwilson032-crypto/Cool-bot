import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_FILE = "startup_simulator.db"

def init_db():
    """Initialize the database with all required tables"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Companies table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS companies (
            user_id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            industry TEXT NOT NULL,
            founder_type TEXT NOT NULL,
            cash INTEGER DEFAULT 50000,
            knowledge INTEGER DEFAULT 100,
            revenue INTEGER DEFAULT 0,
            expenses INTEGER DEFAULT 0,
            reputation INTEGER DEFAULT 1000,
            customers INTEGER DEFAULT 0,
            knowledge_earned INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            level INTEGER DEFAULT 1,
            ownership_percentage INTEGER DEFAULT 100,
            total_revenue_earned INTEGER DEFAULT 0,
            total_knowledge_earned INTEGER DEFAULT 0,
            data JSON DEFAULT '{}'
        )
    ''')
    
    # Employees table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            type TEXT NOT NULL,
            skill INTEGER DEFAULT 5,
            loyalty INTEGER DEFAULT 100,
            salary INTEGER NOT NULL,
            experience INTEGER DEFAULT 0,
            rarity TEXT DEFAULT 'Common',
            hired_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(user_id)
        )
    ''')
    
    # Products table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            quality INTEGER DEFAULT 5,
            popularity INTEGER DEFAULT 1,
            revenue INTEGER DEFAULT 5000,
            customers INTEGER DEFAULT 1000,
            upgrade_level INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_id) REFERENCES companies(user_id)
        )
    ''')
    
    # Research table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS research (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            started_at TEXT DEFAULT CURRENT_TIMESTAMP,
            completion_time INTEGER NOT NULL,
            status TEXT DEFAULT 'in_progress',
            FOREIGN KEY(company_id) REFERENCES companies(user_id)
        )
    ''')
    
    # Partnerships table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS partnerships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_a INTEGER NOT NULL,
            company_b INTEGER NOT NULL,
            type TEXT NOT NULL,
            started_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(company_a) REFERENCES companies(user_id),
            FOREIGN KEY(company_b) REFERENCES companies(user_id)
        )
    ''')
    
    # Acquisitions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS acquisitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            acquirer_id INTEGER NOT NULL,
            target_id INTEGER NOT NULL,
            price INTEGER NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(acquirer_id) REFERENCES companies(user_id),
            FOREIGN KEY(target_id) REFERENCES companies(user_id)
        )
    ''')
    
    # World Events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS world_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            type TEXT DEFAULT 'global',
            duration INTEGER NOT NULL,
            started_at TEXT DEFAULT CURRENT_TIMESTAMP,
            data JSON DEFAULT '{}'
        )
    ''')
    
    # News table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Daily Rewards table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_rewards (
            user_id INTEGER PRIMARY KEY,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES companies(user_id)
        )
    ''')
    
    # Weekly Rewards table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weekly_rewards (
            user_id INTEGER PRIMARY KEY,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES companies(user_id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Company Functions
def get_company(user_id: int) -> dict:
    """Get company data by user ID"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM companies WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    
    if not row:
        conn.close()
        return None
    
    company = dict(row)
    
    # Get associated data
    cursor.execute('SELECT * FROM employees WHERE company_id = ?', (user_id,))
    employees = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute('SELECT * FROM products WHERE company_id = ?', (user_id,))
    products = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute('SELECT * FROM research WHERE company_id = ?', (user_id,))
    research = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute('SELECT * FROM partnerships WHERE company_a = ? OR company_b = ?', (user_id, user_id))
    partnerships = [dict(r) for r in cursor.fetchall()]
    
    company['employees'] = employees
    company['products'] = products
    company['research'] = research
    company['partnerships'] = partnerships
    
    # Parse JSON data
    if company.get('data'):
        company['data'] = json.loads(company['data'])
    else:
        company['data'] = {}
    
    conn.close()
    return company

def get_company_by_name(name: str) -> dict:
    """Get company by name"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM companies WHERE name = ?', (name,))
    row = cursor.fetchone()
    
    conn.close()
    
    if not row:
        return None
    
    return dict(row)

def get_all_companies() -> list:
    """Get all companies"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM companies')
    rows = cursor.fetchall()
    
    companies = []
    for row in rows:
        company = dict(row)
        
        cursor.execute('SELECT * FROM employees WHERE company_id = ?', (row['user_id'],))
        employees = [dict(r) for r in cursor.fetchall()]
        
        cursor.execute('SELECT * FROM products WHERE company_id = ?', (row['user_id'],))
        products = [dict(r) for r in cursor.fetchall()]
        
        cursor.execute('SELECT * FROM research WHERE company_id = ?', (row['user_id'],))
        research = [dict(r) for r in cursor.fetchall()]
        
        company['employees'] = employees
        company['products'] = products
        company['research'] = research
        
        companies.append(company)
    
    conn.close()
    return companies

def create_company(user_id: int, company_data: dict):
    """Create a new company"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO companies 
        (user_id, name, industry, founder_type, cash, knowledge, reputation, knowledge_earned, created_at, data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id,
        company_data['name'],
        company_data['industry'],
        company_data['founder_type'],
        company_data['cash'],
        company_data['knowledge'],
        company_data['reputation'],
        company_data.get('knowledge_earned', 0),
        company_data.get('created_at', datetime.now().isoformat()),
        json.dumps(company_data.get('data', {}))
    ))
    
    conn.commit()
    conn.close()

def update_company(user_id: int, company_data: dict):
    """Update company data"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Remove nested data before update
    employees = company_data.pop('employees', [])
    products = company_data.pop('products', [])
    research = company_data.pop('research', [])
    partnerships = company_data.pop('partnerships', [])
    
    cursor.execute('''
        UPDATE companies SET 
        cash = ?, knowledge = ?, revenue = ?, expenses = ?, 
        reputation = ?, customers = ?, knowledge_earned = ?,
        level = ?, ownership_percentage = ?, total_revenue_earned = ?,
        total_knowledge_earned = ?, data = ?
        WHERE user_id = ?
    ''', (
        company_data.get('cash', 0),
        company_data.get('knowledge', 0),
        company_data.get('revenue', 0),
        company_data.get('expenses', 0),
        company_data.get('reputation', 0),
        company_data.get('customers', 0),
        company_data.get('knowledge_earned', 0),
        company_data.get('level', 1),
        company_data.get('ownership_percentage', 100),
        company_data.get('total_revenue_earned', 0),
        company_data.get('total_knowledge_earned', 0),
        json.dumps(company_data.get('data', {})),
        user_id
    ))
    
    # Update employees
    cursor.execute('DELETE FROM employees WHERE company_id = ?', (user_id,))
    for emp in employees:
        cursor.execute('''
            INSERT INTO employees 
            (company_id, name, type, skill, loyalty, salary, experience, rarity)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, emp.get('name'), emp.get('type'), emp.get('skill', 5),
            emp.get('loyalty', 100), emp.get('salary', 0),
            emp.get('experience', 0), emp.get('rarity', 'Common')
        ))
    
    # Update products
    cursor.execute('DELETE FROM products WHERE company_id = ?', (user_id,))
    for prod in products:
        cursor.execute('''
            INSERT INTO products
            (company_id, name, quality, popularity, revenue, customers, upgrade_level)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, prod.get('name'), prod.get('quality', 5),
            prod.get('popularity', 1), prod.get('revenue', 0),
            prod.get('customers', 0), prod.get('upgrade_level', 0)
        ))
    
    # Update research
    cursor.execute('DELETE FROM research WHERE company_id = ?', (user_id,))
    for res in research:
        cursor.execute('''
            INSERT INTO research
            (company_id, name, started_at, completion_time, status)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            user_id, res.get('name'), res.get('started_at', datetime.now().isoformat()),
            res.get('completion_time', 0), res.get('status', 'in_progress')
        ))
    
    conn.commit()
    conn.close()

def delete_company(user_id: int):
    """Delete a company"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM employees WHERE company_id = ?', (user_id,))
    cursor.execute('DELETE FROM products WHERE company_id = ?', (user_id,))
    cursor.execute('DELETE FROM research WHERE company_id = ?', (user_id,))
    cursor.execute('DELETE FROM partnerships WHERE company_a = ? OR company_b = ?', (user_id, user_id))
    cursor.execute('DELETE FROM companies WHERE user_id = ?', (user_id,))
    
    conn.commit()
    conn.close()

# Currency Functions
def add_cash(user_id: int, amount: int):
    """Add cash to company"""
    company = get_company(user_id)
    if company:
        company['cash'] += amount
        update_company(user_id, company)

def add_knowledge(user_id: int, amount: int):
    """Add knowledge to company"""
    company = get_company(user_id)
    if company:
        company['knowledge'] += amount
        company['knowledge_earned'] += amount
        company['total_knowledge_earned'] += amount
        update_company(user_id, company)

def deduct_cash(user_id: int, amount: int) -> bool:
    """Deduct cash from company"""
    company = get_company(user_id)
    if company and company['cash'] >= amount:
        company['cash'] -= amount
        update_company(user_id, company)
        return True
    return False

def deduct_knowledge(user_id: int, amount: int) -> bool:
    """Deduct knowledge from company"""
    company = get_company(user_id)
    if company and company['knowledge'] >= amount:
        company['knowledge'] -= amount
        update_company(user_id, company)
        return True
    return False

# Employee Functions
def get_employees(user_id: int) -> list:
    """Get all employees for a company"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM employees WHERE company_id = ?', (user_id,))
    rows = cursor.fetchall()
    
    conn.close()
    return [dict(r) for r in rows]

def hire_employee(user_id: int, employee_data: dict):
    """Hire a new employee"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO employees 
        (company_id, name, type, skill, loyalty, salary, experience, rarity)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id, employee_data['name'], employee_data['type'],
        employee_data.get('skill', 5), employee_data.get('loyalty', 100),
        employee_data['salary'], employee_data.get('experience', 0),
        employee_data.get('rarity', 'Common')
    ))
    
    conn.commit()
    conn.close()

def fire_employee(user_id: int, employee_name: str):
    """Fire an employee"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM employees WHERE company_id = ? AND name = ?', (user_id, employee_name))
    
    conn.commit()
    conn.close()

def promote_employee(user_id: int, employee_name: str):
    """Promote an employee"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE employees SET skill = skill + 1, loyalty = loyalty + 10, salary = salary * 1.2
        WHERE company_id = ? AND name = ?
    ''', (user_id, employee_name))
    
    conn.commit()
    conn.close()

# Product Functions
def get_products(user_id: int) -> list:
    """Get all products for a company"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM products WHERE company_id = ?', (user_id,))
    rows = cursor.fetchall()
    
    conn.close()
    return [dict(r) for r in rows]

def create_product(user_id: int, product_data: dict):
    """Create a new product"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO products
        (company_id, name, quality, popularity, revenue, customers, upgrade_level)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        user_id, product_data['name'], product_data.get('quality', 5),
        product_data.get('popularity', 1), product_data.get('revenue', 5000),
        product_data.get('customers', 1000), product_data.get('upgrade_level', 0)
    ))
    
    conn.commit()
    conn.close()

def upgrade_product(user_id: int, product_name: str):
    """Upgrade a product"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE products SET 
        quality = quality + 1, upgrade_level = upgrade_level + 1,
        revenue = revenue * 1.15, customers = customers * 1.1
        WHERE company_id = ? AND name = ?
    ''', (user_id, product_name))
    
    conn.commit()
    conn.close()

# Research Functions
def get_research(user_id: int) -> list:
    """Get all research projects"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM research WHERE company_id = ?', (user_id,))
    rows = cursor.fetchall()
    
    conn.close()
    return [dict(r) for r in rows]

def start_research(user_id: int, research_data: dict):
    """Start a research project"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO research
        (company_id, name, started_at, completion_time, status)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        user_id, research_data['name'],
        research_data.get('started_at', datetime.now().isoformat()),
        research_data['completion_time'], 'in_progress'
    ))
    
    conn.commit()
    conn.close()

def cancel_research(user_id: int, research_name: str):
    """Cancel a research project"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM research WHERE company_id = ? AND name = ?', (user_id, research_name))
    
    conn.commit()
    conn.close()

# Partnership Functions
def add_partnership(company_a: int, company_b: int, partnership_type: str):
    """Create a partnership"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO partnerships (company_a, company_b, type)
        VALUES (?, ?, ?)
    ''', (company_a, company_b, partnership_type))
    
    conn.commit()
    conn.close()

def remove_partnership(company_a: int, company_b: int):
    """Remove a partnership"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        DELETE FROM partnerships 
        WHERE (company_a = ? AND company_b = ?) OR (company_a = ? AND company_b = ?)
    ''', (company_a, company_b, company_b, company_a))
    
    conn.commit()
    conn.close()

def get_partnerships(user_id: int) -> list:
    """Get all partnerships for a company"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM partnerships WHERE company_a = ? OR company_b = ?', (user_id, user_id))
    rows = cursor.fetchall()
    
    conn.close()
    return [dict(r) for r in rows]

# Acquisition Functions
def create_acquisition(acquirer_id: int, target_id: int, price: int):
    """Create acquisition offer"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO acquisitions (acquirer_id, target_id, price, status)
        VALUES (?, ?, ?, 'pending')
    ''', (acquirer_id, target_id, price))
    
    conn.commit()
    conn.close()

def get_acquisition_status(user_id: int) -> dict:
    """Get acquisition status"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM acquisitions 
        WHERE (acquirer_id = ? OR target_id = ?) AND status = 'pending'
    ''', (user_id, user_id))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(r) for r in rows]

# World Events Functions
def add_event(event_data: dict):
    """Add a world event"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO world_events (name, type, duration, data)
        VALUES (?, ?, ?, ?)
    ''', (
        event_data['name'],
        event_data.get('type', 'global'),
        event_data['duration'],
        json.dumps(event_data.get('data', {}))
    ))
    
    conn.commit()
    conn.close()

def get_events() -> list:
    """Get all active events"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM world_events')
    rows = cursor.fetchall()
    
    conn.close()
    return [dict(r) for r in rows]

# News Functions
def add_news(news_data: dict):
    """Add a news entry"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO news (title, content)
        VALUES (?, ?)
    ''', (news_data['title'], news_data['content']))
    
    conn.commit()
    conn.close()

def get_news(limit: int = 50) -> list:
    """Get latest news"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM news ORDER BY created_at DESC LIMIT ?', (limit,))
    rows = cursor.fetchall()
    
    conn.close()
    return [dict(r) for r in rows]

# Reward Functions
def add_daily_reward(user_id: int, timestamp: str):
    """Record daily reward claim"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('INSERT OR REPLACE INTO daily_rewards (user_id, timestamp) VALUES (?, ?)', (user_id, timestamp))
    
    conn.commit()
    conn.close()

def get_daily_reward(user_id: int) -> dict:
    """Get last daily reward"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM daily_rewards WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    
    conn.close()
    return dict(row) if row else None

def add_weekly_reward(user_id: int, timestamp: str):
    """Record weekly reward claim"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('INSERT OR REPLACE INTO weekly_rewards (user_id, timestamp) VALUES (?, ?)', (user_id, timestamp))
    
    conn.commit()
    conn.close()

def get_weekly_reward(user_id: int) -> dict:
    """Get last weekly reward"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM weekly_rewards WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    
    conn.close()
    return dict(row) if row else None

# Market Share Functions
def update_market_share(company_id: int, industry: str, share: float):
    """Update market share"""
    pass  # Market share calculated dynamically from customer counts

def get_market_share(industry: str) -> dict:
    """Get market share for an industry"""
    pass  # Market share calculated dynamically

def get_market_leaders(industry: str, limit: int = 5) -> list:
    """Get market leaders in an industry"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM companies WHERE industry = ?
        ORDER BY customers DESC LIMIT ?
    ''', (industry, limit))
    
    rows = cursor.fetchall()
    conn.close()
    
    return [dict(r) for r in rows]
