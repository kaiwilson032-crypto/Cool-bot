#!/usr/bin/env python3
"""
Startup Simulator Discord Bot
A multiplayer business strategy game on Discord
"""

import discord
from discord.ext import commands, tasks
import sqlite3
import json
import os
from datetime import datetime, timedelta
import random
import math
from typing import Optional, Tuple, List
import traceback

# Import database module
from database import (
    init_db, get_company, create_company, update_company,
    get_all_companies, delete_company, get_company_by_name,
    add_cash, add_knowledge, deduct_cash, deduct_knowledge,
    get_employees, hire_employee, fire_employee, promote_employee,
    get_products, create_product, upgrade_product,
    get_research, start_research, cancel_research,
    add_partnership, remove_partnership, get_partnerships,
    create_acquisition, get_acquisition_status,
    add_event, get_events, add_news,
    add_daily_reward, get_daily_reward, add_weekly_reward, get_weekly_reward,
    update_market_share, get_market_share, get_market_leaders
)

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Global game state
GAME_STATE = {
    "events": [],
    "markets": {},
    "news_log": []
}

# Configuration
CONFIG = {
    "startup_cash": 50000,
    "startup_knowledge": 100,
    "daily_reward_cash": 5000,
    "daily_reward_knowledge": 500,
    "weekly_reward_cash": 25000,
    "weekly_reward_knowledge": 3000,
    "global_event_interval": 3600,  # 1 hour
}

INDUSTRIES = ["AI", "Gaming", "Social Media", "Robotics", "Cybersecurity", "FinTech", "E-Commerce", "Software"]

FOUNDER_TYPES = {
    "Visionary": {"customer_growth": 1.15, "reputation": 1.10},
    "Engineer": {"research_speed": 1.15, "product_quality": 1.10},
    "Marketer": {"marketing_effectiveness": 1.15, "customer_acquisition": 1.10},
    "Financier": {"investor_offers": 1.20, "starting_cash": 1.15}
}

PRODUCTS_BY_INDUSTRY = {
    "AI": ["Chatbot", "Image Generator", "Coding Assistant", "Autonomous AI Agent"],
    "Gaming": ["Mobile Game", "Indie Game", "MMO", "Game Engine"],
    "Social Media": ["Messaging App", "Streaming Platform", "Social Network", "Content Creator Tool"],
    "Robotics": ["Industrial Robot", "Consumer Robot", "Autonomous Drone", "Robotic Assistant"],
    "Cybersecurity": ["VPN Service", "Antivirus", "Enterprise Security Platform", "Incident Response Tool"],
    "FinTech": ["Payment Platform", "Investment App", "Blockchain Wallet", "Trading Bot"],
    "E-Commerce": ["Online Marketplace", "Shopping App", "Dropshipping Platform", "Store Builder"],
    "Software": ["Project Management", "Collaboration Tool", "CRM System", "Analytics Platform"]
}

RESEARCH_TREE = {
    "Beginner": {
        "Basic Marketing": {"cash": 10000, "knowledge": 200, "time": 3600},
        "Agile Development": {"cash": 15000, "knowledge": 250, "time": 3600},
        "Data Analytics": {"cash": 12000, "knowledge": 200, "time": 3600}
    },
    "Intermediate": {
        "Cloud Computing": {"cash": 50000, "knowledge": 500, "time": 7200},
        "Automation Systems": {"cash": 45000, "knowledge": 450, "time": 7200},
        "Advanced Networking": {"cash": 40000, "knowledge": 400, "time": 7200}
    },
    "Advanced": {
        "Artificial Intelligence": {"cash": 100000, "knowledge": 1000, "time": 14400},
        "Robotics": {"cash": 120000, "knowledge": 1200, "time": 14400},
        "Blockchain": {"cash": 80000, "knowledge": 900, "time": 14400},
        "Virtual Reality": {"cash": 90000, "knowledge": 950, "time": 14400}
    },
    "Endgame": {
        "Quantum Computing": {"cash": 500000, "knowledge": 5000, "time": 28800},
        "Autonomous Systems": {"cash": 450000, "knowledge": 4500, "time": 28800},
        "AGI Research": {"cash": 600000, "knowledge": 6000, "time": 28800}
    }
}

GLOBAL_EVENTS_LIST = [
    {"name": "AI Boom", "duration": 86400, "effects": {"AI": 1.30}, "cash_multiplier": 1.0, "knowledge_multiplier": 1.0},
    {"name": "Gaming Craze", "duration": 86400, "effects": {"Gaming": 1.25}, "cash_multiplier": 1.0, "knowledge_multiplier": 1.0},
    {"name": "Cybersecurity Crisis", "duration": 172800, "effects": {"Cybersecurity": 1.40}, "cash_multiplier": 1.0, "knowledge_multiplier": 1.0},
    {"name": "Economic Recession", "duration": 259200, "effects": {"all": 0.85}, "cash_multiplier": 0.85, "knowledge_multiplier": 1.0},
    {"name": "Tech Investment Wave", "duration": 172800, "effects": {"all": 1.20}, "cash_multiplier": 1.5, "knowledge_multiplier": 1.0},
    {"name": "Government Regulation", "duration": 259200, "effects": {"all": 1.0}, "cash_multiplier": 0.9, "knowledge_multiplier": 1.2},
    {"name": "Cloud Computing Breakthrough", "duration": 172800, "effects": {"all": 1.0}, "cash_multiplier": 1.0, "knowledge_multiplier": 1.25},
    {"name": "Mobile Revolution", "duration": 86400, "effects": {"Gaming": 1.20}, "cash_multiplier": 1.0, "knowledge_multiplier": 1.0},
]

RANDOM_EVENTS_POSITIVE = [
    {"name": "Product Goes Viral", "cash_bonus": 50000, "knowledge_bonus": 1000, "customer_bonus": 5000},
    {"name": "Celebrity Endorsement", "cash_bonus": 75000, "knowledge_bonus": 500, "customer_bonus": 10000},
    {"name": "Government Grant", "cash_bonus": 100000, "knowledge_bonus": 2000, "customer_bonus": 0},
    {"name": "Breakthrough Discovery", "cash_bonus": 25000, "knowledge_bonus": 5000, "customer_bonus": 1000},
]

RANDOM_EVENTS_NEGATIVE = [
    {"name": "Data Breach", "cash_loss": 50000, "reputation_loss": 1000},
    {"name": "Server Outage", "cash_loss": 30000, "reputation_loss": 500},
    {"name": "Employee Resignation", "cash_loss": 10000, "reputation_loss": 200},
    {"name": "Lawsuit", "cash_loss": 75000, "reputation_loss": 1500},
    {"name": "Market Crash", "cash_loss": 100000, "reputation_loss": 2000},
]

EMPLOYEES_POOL = [
    {"name": "Alice Chen", "type": "Developer", "skill": 8, "rarity": "Uncommon", "salary": 5000},
    {"name": "Bob Smith", "type": "Designer", "skill": 7, "rarity": "Common", "salary": 4000},
    {"name": "Carol Johnson", "type": "Marketer", "skill": 9, "rarity": "Rare", "salary": 6000},
    {"name": "David Lee", "type": "Salesperson", "skill": 8, "rarity": "Uncommon", "salary": 4500},
    {"name": "Eva Martinez", "type": "Researcher", "skill": 10, "rarity": "Rare", "salary": 7000},
    {"name": "Frank Wilson", "type": "Manager", "skill": 7, "rarity": "Common", "salary": 5500},
    {"name": "Grace Park", "type": "Executive", "skill": 9, "rarity": "Epic", "salary": 10000},
    {"name": "Henry Zhang", "type": "Developer", "skill": 9, "rarity": "Rare", "salary": 6500},
    {"name": "Iris Thompson", "type": "Designer", "skill": 8, "rarity": "Uncommon", "salary": 4500},
    {"name": "Jack Robinson", "type": "Marketer", "skill": 7, "rarity": "Common", "salary": 4000},
    {"name": "Karen White", "type": "Researcher", "skill": 9, "rarity": "Rare", "salary": 6500},
    {"name": "Leo Brown", "type": "Executive", "skill": 10, "rarity": "Legendary", "salary": 15000},
    {"name": "Maria Garcia", "type": "Salesperson", "skill": 8, "rarity": "Uncommon", "salary": 4500},
    {"name": "Nathan Black", "type": "Developer", "skill": 7, "rarity": "Common", "salary": 4500},
    {"name": "Olivia Davis", "type": "Manager", "skill": 8, "rarity": "Uncommon", "salary": 6000},
]

def get_company_level(knowledge_earned: int) -> int:
    """Calculate company level from total knowledge earned"""
    levels = [0, 0, 100, 500, 1000, 2500, 5000, 10000, 15000, 25000, 50000,
              75000, 100000, 150000, 200000, 250000, 350000, 450000, 600000, 800000]
    for i, threshold in enumerate(levels):
        if knowledge_earned < threshold:
            return max(1, i - 1)
    return len(levels) - 1

def get_company_valuation(company: dict) -> int:
    """Calculate company valuation"""
    base = company['cash'] * 2
    revenue_mult = company['revenue'] * 10 if company['revenue'] > 0 else 0
    customer_mult = company['customers'] * 100
    knowledge_mult = company['knowledge_earned'] * 5
    return int(base + revenue_mult + customer_mult + knowledge_mult)

def get_innovation_score(company: dict) -> int:
    """Calculate innovation score"""
    research_score = len(company.get('research', [])) * 500
    knowledge_score = company['knowledge_earned'] // 10
    product_score = len(company.get('products', [])) * 1000
    return research_score + knowledge_score + product_score

def format_currency(amount: int) -> str:
    """Format currency with K/M suffixes"""
    if amount >= 1000000:
        return f"£{amount/1000000:.1f}M"
    elif amount >= 1000:
        return f"£{amount/1000:.1f}K"
    return f"£{amount}"

def format_number(amount: int) -> str:
    """Format numbers with K/M suffixes"""
    if amount >= 1000000:
        return f"{amount/1000000:.1f}M"
    elif amount >= 1000:
        return f"{amount/1000:.1f}K"
    return str(amount)

# Event Handlers
@bot.event
async def on_ready():
    print(f"✅ Bot logged in as {bot.user}")
    init_db()
    background_tasks.start()
    offline_progression.start()
    market_simulation.start()
    global_events_trigger.start()
    daily_events_trigger.start()
    employee_market_rotation.start()
    investor_generation.start()

@bot.event
async def on_command_error(ctx, error):
    """Handle command errors"""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument: {error.param.name}")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Command not found.")
    else:
        print(f"Error: {error}")
        traceback.print_exc()
        await ctx.send(f"❌ An error occurred: {str(error)}")

# Company Commands
@bot.command(name="startup")
async def startup_cmd(ctx, action: str, *, details: Optional[str] = None):
    """Create, manage, or view startup companies"""
    
    user_id = ctx.author.id
    
    if action.lower() == "create":
        # Check if user already has a company
        existing = get_company(user_id)
        if existing:
            await ctx.send("❌ You already own a company! Use `/startup delete` first.")
            return
        
        # Show creation modal-like interface
        embed = discord.Embed(
            title="🚀 Create Your Startup",
            description="Choose your company details",
            color=discord.Color.blue()
        )
        embed.add_field(name="Industries", value=", ".join(INDUSTRIES), inline=False)
        embed.add_field(name="Founder Types", value=", ".join(FOUNDER_TYPES.keys()), inline=False)
        embed.add_field(name="Usage", value="`!startup create <name> | <industry> | <founder_type>`\n\nExample: `!startup create TechVision | AI | Visionary`", inline=False)
        
        await ctx.send(embed=embed)
        return
    
    elif action.lower() == "create" and details:
        # Parse the details
        try:
            parts = [p.strip() for p in details.split("|")]
            if len(parts) != 3:
                await ctx.send("❌ Format: `!startup create <name> | <industry> | <founder_type>`")
                return
            
            company_name, industry, founder_type = parts
            
            if industry not in INDUSTRIES:
                await ctx.send(f"❌ Invalid industry. Choose from: {', '.join(INDUSTRIES)}")
                return
            
            if founder_type not in FOUNDER_TYPES:
                await ctx.send(f"❌ Invalid founder type. Choose from: {', '.join(FOUNDER_TYPES.keys())}")
                return
            
            # Check name uniqueness
            if get_company_by_name(company_name):
                await ctx.send(f"❌ Company name already taken!")
                return
            
            # Create company
            starting_cash = int(CONFIG["startup_cash"] * (1.15 if founder_type == "Financier" else 1.0))
            
            company_data = {
                "user_id": user_id,
                "name": company_name,
                "industry": industry,
                "founder_type": founder_type,
                "cash": starting_cash,
                "knowledge": CONFIG["startup_knowledge"],
                "revenue": 0,
                "expenses": 0,
                "reputation": 1000,
                "customers": 0,
                "knowledge_earned": 0,
                "created_at": datetime.now().isoformat(),
                "level": 1,
                "employees": [],
                "products": [],
                "research": [],
                "technologies": [],
                "partnerships": [],
                "ownership_percentage": 100,
                "total_revenue_earned": 0,
                "total_knowledge_earned": 0,
            }
            
            create_company(user_id, company_data)
            
            embed = discord.Embed(
                title=f"✅ {company_name} Created!",
                description=f"Welcome to the startup world, {ctx.author.mention}!",
                color=discord.Color.green()
            )
            embed.add_field(name="💰 Starting Cash", value=format_currency(starting_cash), inline=True)
            embed.add_field(name="🧠 Starting Knowledge", value=str(CONFIG["startup_knowledge"]), inline=True)
            embed.add_field(name="🏢 Industry", value=industry, inline=True)
            embed.add_field(name="👤 Founder Type", value=founder_type, inline=True)
            
            await ctx.send(embed=embed)
        
        except Exception as e:
            await ctx.send(f"❌ Error creating company: {str(e)}")
    
    elif action.lower() == "profile":
        company = get_company(user_id)
        if not company:
            await ctx.send("❌ You don't own a company. Use `!startup create` to start.")
            return
        
        level = get_company_level(company['knowledge_earned'])
        valuation = get_company_valuation(company)
        innovation = get_innovation_score(company)
        
        embed = discord.Embed(
            title=f"📊 {company['name']}",
            color=discord.Color.gold()
        )
        
        embed.add_field(name="👤 Founder", value=f"{ctx.author.mention}", inline=False)
        embed.add_field(name="🏢 Industry", value=company['industry'], inline=True)
        embed.add_field(name="📈 Level", value=f"Lvl {level}", inline=True)
        
        embed.add_field(name="💰 Cash", value=format_currency(company['cash']), inline=True)
        embed.add_field(name="🧠 Knowledge", value=str(company['knowledge']), inline=True)
        embed.add_field(name="📊 Valuation", value=format_currency(valuation), inline=True)
        
        embed.add_field(name="👥 Customers", value=format_number(company['customers']), inline=True)
        embed.add_field(name="⭐ Reputation", value=format_number(company['reputation']), inline=True)
        embed.add_field(name="💡 Innovation", value=format_number(innovation), inline=True)
        
        embed.add_field(name="💼 Revenue (Monthly)", value=format_currency(company['revenue']), inline=True)
        embed.add_field(name="💸 Expenses (Monthly)", value=format_currency(company['expenses']), inline=True)
        embed.add_field(name="📁 Ownership", value=f"{company['ownership_percentage']}%", inline=True)
        
        embed.add_field(name="👨‍💼 Employees", value=str(len(company['employees'])), inline=True)
        embed.add_field(name="📦 Products", value=str(len(company['products'])), inline=True)
        embed.add_field(name="🔬 Technologies", value=str(len(company['technologies'])), inline=True)
        
        embed.set_footer(text=f"Created: {company['created_at']}")
        
        await ctx.send(embed=embed)
    
    elif action.lower() == "rename":
        if not details:
            await ctx.send("Usage: `!startup rename <new_name>`")
            return
        
        company = get_company(user_id)
        if not company:
            await ctx.send("❌ You don't own a company.")
            return
        
        if get_company_by_name(details):
            await ctx.send("❌ Company name already taken!")
            return
        
        company['name'] = details
        update_company(user_id, company)
        await ctx.send(f"✅ Company renamed to **{details}**")
    
    elif action.lower() == "delete":
        company = get_company(user_id)
        if not company:
            await ctx.send("❌ You don't own a company.")
            return
        
        delete_company(user_id)
        await ctx.send(f"✅ Company **{company['name']}** has been deleted.")

@bot.command(name="stats")
async def stats_cmd(ctx):
    """View detailed company statistics"""
    company = get_company(ctx.author.id)
    if not company:
        await ctx.send("❌ You don't own a company.")
        return
    
    level = get_company_level(company['knowledge_earned'])
    valuation = get_company_valuation(company)
    innovation = get_innovation_score(company)
    
    embed = discord.Embed(
        title=f"📈 {company['name']} - Detailed Stats",
        color=discord.Color.blue(),
        timestamp=datetime.now()
    )
    
    # Financial Stats
    embed.add_field(name="💰 FINANCIAL", value="", inline=False)
    embed.add_field(name="Current Cash", value=format_currency(company['cash']), inline=True)
    embed.add_field(name="Monthly Revenue", value=format_currency(company['revenue']), inline=True)
    embed.add_field(name="Monthly Expenses", value=format_currency(company['expenses']), inline=True)
    embed.add_field(name="Total Revenue Earned", value=format_currency(company['total_revenue_earned']), inline=True)
    embed.add_field(name="Company Valuation", value=format_currency(valuation), inline=True)
    embed.add_field(name="Ownership %", value=f"{company['ownership_percentage']}%", inline=True)
    
    # Knowledge & Research
    embed.add_field(name="🧠 KNOWLEDGE & RESEARCH", value="", inline=False)
    embed.add_field(name="Current Knowledge", value=str(company['knowledge']), inline=True)
    embed.add_field(name="Total Knowledge Earned", value=str(company['total_knowledge_earned']), inline=True)
    embed.add_field(name="Technologies Unlocked", value=str(len(company['technologies'])), inline=True)
    
    # Company Growth
    embed.add_field(name="📊 GROWTH METRICS", value="", inline=False)
    embed.add_field(name="Company Level", value=f"Lvl {level}", inline=True)
    embed.add_field(name="Total Customers", value=format_number(company['customers']), inline=True)
    embed.add_field(name="Reputation", value=format_number(company['reputation']), inline=True)
    embed.add_field(name="Innovation Score", value=format_number(innovation), inline=True)
    
    # Business Units
    embed.add_field(name="🏢 BUSINESS UNITS", value="", inline=False)
    embed.add_field(name="Employees", value=str(len(company['employees'])), inline=True)
    embed.add_field(name="Products", value=str(len(company['products'])), inline=True)
    embed.add_field(name="Active Partnerships", value=str(len(company['partnerships'])), inline=True)
    
    await ctx.send(embed=embed)

# Employee Commands
@bot.command(name="hire")
async def hire_cmd(ctx):
    """View and hire employees"""
    company = get_company(ctx.author.id)
    if not company:
        await ctx.send("❌ You don't own a company.")
        return
    
    # Generate market if not exists
    if not hasattr(ctx.bot, 'employee_market'):
        ctx.bot.employee_market = random.sample(EMPLOYEES_POOL, min(5, len(EMPLOYEES_POOL)))
    
    embed = discord.Embed(
        title="👨‍💼 Employee Market",
        description="Available employees for hire",
        color=discord.Color.purple()
    )
    
    for i, emp in enumerate(ctx.bot.employee_market):
        salary_text = format_currency(emp['salary'])
        embed.add_field(
            name=f"{i+1}. {emp['name']} - {emp['type']}",
            value=f"Rarity: {emp['rarity']} | Skill: {emp['skill']}/10 | Salary: {salary_text}/month",
            inline=False
        )
    
    embed.set_footer(text="Reply with the employee number to hire them")
    await ctx.send(embed=embed)

@bot.command(name="employees")
async def employees_cmd(ctx):
    """View your company's employees"""
    company = get_company(ctx.author.id)
    if not company:
        await ctx.send("❌ You don't own a company.")
        return
    
    if not company['employees']:
        await ctx.send("❌ You have no employees. Use `!hire` to recruit.")
        return
    
    embed = discord.Embed(
        title=f"👨‍💼 {company['name']} - Team",
        color=discord.Color.purple()
    )
    
    total_salary = 0
    for emp in company['employees']:
        embed.add_field(
            name=f"{emp['name']} - {emp['type']}",
            value=f"Skill: {emp['skill']}/10 | Loyalty: {emp['loyalty']}% | Salary: {format_currency(emp['salary'])}/month | Experience: {emp['experience']} months",
            inline=False
        )
        total_salary += emp['salary']
    
    embed.add_field(name="Total Monthly Salary", value=format_currency(total_salary), inline=False)
    await ctx.send(embed=embed)

# Product Commands
@bot.command(name="product")
async def product_cmd(ctx, action: str, *, details: Optional[str] = None):
    """Create and manage products"""
    company = get_company(ctx.author.id)
    if not company:
        await ctx.send("❌ You don't own a company.")
        return
    
    if action.lower() == "create":
        if not details:
            industries_text = "\n".join([f"{ind}: {', '.join(PRODUCTS_BY_INDUSTRY[ind])}" for ind in INDUSTRIES])
            embed = discord.Embed(
                title="📦 Create Product",
                description="Available products by industry:",
                color=discord.Color.green()
            )
            embed.add_field(name="Products", value=industries_text, inline=False)
            embed.add_field(name="Cost", value="Cash: 50,000 | Knowledge: 500", inline=False)
            embed.add_field(name="Usage", value="`!product create <product_name>`", inline=False)
            await ctx.send(embed=embed)
            return
        
        # Check if product name is valid
        valid_products = [p for products in PRODUCTS_BY_INDUSTRY.values() for p in products]
        if details not in valid_products:
            await ctx.send(f"❌ Invalid product. Available products:\n{', '.join(valid_products)}")
            return
        
        # Check resources
        if company['cash'] < 50000 or company['knowledge'] < 500:
            await ctx.send("❌ Insufficient resources. Need £50,000 cash and 500 knowledge.")
            return
        
        # Create product
        deduct_cash(ctx.author.id, 50000)
        deduct_knowledge(ctx.author.id, 500)
        
        product = {
            "name": details,
            "quality": 5,
            "popularity": 1,
            "revenue": 5000,
            "customers": 1000,
            "upgrade_level": 0,
        }
        
        company['products'].append(product)
        update_company(ctx.author.id, company)
        
        embed = discord.Embed(
            title=f"✅ {details} Created!",
            color=discord.Color.green()
        )
        embed.add_field(name="Quality", value="5/10", inline=True)
        embed.add_field(name="Monthly Revenue", value=format_currency(5000), inline=True)
        embed.add_field(name="Starting Customers", value="1,000", inline=True)
        
        await ctx.send(embed=embed)
    
    elif action.lower() == "upgrade":
        if not details:
            await ctx.send("Usage: `!product upgrade <product_name>`")
            return
        
        product = next((p for p in company['products'] if p['name'].lower() == details.lower()), None)
        if not product:
            await ctx.send(f"❌ Product not found. Your products: {', '.join([p['name'] for p in company['products']])}")
            return
        
        # Upgrade costs
        upgrade_cost_cash = 30000 * (product['upgrade_level'] + 1)
        upgrade_cost_knowledge = 300 * (product['upgrade_level'] + 1)
        
        if company['cash'] < upgrade_cost_cash or company['knowledge'] < upgrade_cost_knowledge:
            await ctx.send(f"❌ Insufficient resources. Need {format_currency(upgrade_cost_cash)} and {upgrade_cost_knowledge} knowledge.")
            return
        
        deduct_cash(ctx.author.id, upgrade_cost_cash)
        deduct_knowledge(ctx.author.id, upgrade_cost_knowledge)
        
        product['quality'] += 1
        product['upgrade_level'] += 1
        product['revenue'] = int(product['revenue'] * 1.15)
        product['customers'] = int(product['customers'] * 1.1)
        
        update_company(ctx.author.id, company)
        
        await ctx.send(f"✅ **{details}** upgraded to Level {product['upgrade_level']}!\n• Quality: {product['quality']}/10\n• Monthly Revenue: {format_currency(product['revenue'])}\n• Customers: {format_number(product['customers'])}")
    
    elif action.lower() == "info":
        if not details:
            await ctx.send(f"Products: {', '.join([p['name'] for p in company['products']])}")
            return
        
        product = next((p for p in company['products'] if p['name'].lower() == details.lower()), None)
        if not product:
            await ctx.send("❌ Product not found.")
            return
        
        embed = discord.Embed(
            title=f"📦 {product['name']}",
            color=discord.Color.green()
        )
        embed.add_field(name="Quality", value=f"{product['quality']}/10", inline=True)
        embed.add_field(name="Popularity", value=f"{product['popularity']}/10", inline=True)
        embed.add_field(name="Upgrade Level", value=product['upgrade_level'], inline=True)
        embed.add_field(name="Monthly Revenue", value=format_currency(product['revenue']), inline=True)
        embed.add_field(name="Active Customers", value=format_number(product['customers']), inline=True)
        embed.add_field(name="Upgrade Cost", value=f"£{30000 * (product['upgrade_level'] + 1)} + {300 * (product['upgrade_level'] + 1)} Knowledge", inline=True)
        
        await ctx.send(embed=embed)
    
    elif action.lower() == "list":
        if not company['products']:
            await ctx.send("❌ You have no products. Use `!product create` to launch one.")
            return
        
        embed = discord.Embed(
            title=f"📦 {company['name']} - Products",
            color=discord.Color.green()
        )
        
        total_revenue = 0
        total_customers = 0
        for prod in company['products']:
            embed.add_field(
                name=prod['name'],
                value=f"Quality: {prod['quality']}/10 | Revenue: {format_currency(prod['revenue'])} | Customers: {format_number(prod['customers'])}",
                inline=False
            )
            total_revenue += prod['revenue']
            total_customers += prod['customers']
        
        embed.add_field(name="Total Monthly Revenue", value=format_currency(total_revenue), inline=False)
        embed.add_field(name="Total Customers", value=format_number(total_customers), inline=False)
        
        await ctx.send(embed=embed)

# Research Commands
@bot.command(name="research")
async def research_cmd(ctx, action: str, *, details: Optional[str] = None):
    """Manage research projects"""
    company = get_company(ctx.author.id)
    if not company:
        await ctx.send("❌ You don't own a company.")
        return
    
    if action.lower() == "tree":
        embed = discord.Embed(
            title="🔬 Research Tree",
            color=discord.Color.blue()
        )
        
        for tier, techs in RESEARCH_TREE.items():
            tech_list = "\n".join([f"• {tech}" for tech in techs.keys()])
            embed.add_field(name=tier, value=tech_list, inline=False)
        
        await ctx.send(embed=embed)
    
    elif action.lower() == "start":
        if not details:
            await ctx.send("Usage: `!research start <technology_name>`")
            return
        
        # Find technology
        tech_found = None
        for tier, techs in RESEARCH_TREE.items():
            if details in techs:
                tech_found = techs[details]
                break
        
        if not tech_found:
            await ctx.send("❌ Technology not found.")
            return
        
        # Check if already researching or researched
        if any(r['name'] == details for r in company.get('research', [])):
            await ctx.send(f"❌ Already researched or researching {details}.")
            return
        
        # Check resources
        if company['cash'] < tech_found['cash'] or company['knowledge'] < tech_found['knowledge']:
            await ctx.send(f"❌ Insufficient resources. Need {format_currency(tech_found['cash'])} and {tech_found['knowledge']} knowledge.")
            return
        
        deduct_cash(ctx.author.id, tech_found['cash'])
        deduct_knowledge(ctx.author.id, tech_found['knowledge'])
        
        research = {
            "name": details,
            "started_at": datetime.now().isoformat(),
            "completion_time": tech_found['time'],
            "status": "in_progress"
        }
        
        company['research'].append(research)
        update_company(ctx.author.id, company)
        
        embed = discord.Embed(
            title=f"✅ Research Started: {details}",
            color=discord.Color.blue()
        )
        embed.add_field(name="Completion Time", value=f"{tech_found['time']} seconds", inline=True)
        embed.add_field(name="Cost", value=f"{format_currency(tech_found['cash'])} + {tech_found['knowledge']} Knowledge", inline=True)
        
        await ctx.send(embed=embed)
    
    elif action.lower() == "status":
        if not company['research']:
            await ctx.send("❌ No active research projects.")
            return
        
        embed = discord.Embed(
            title="🔬 Research Status",
            color=discord.Color.blue()
        )
        
        for res in company['research']:
            embed.add_field(name=res['name'], value=f"Status: {res['status']}", inline=False)
        
        await ctx.send(embed=embed)

# Marketing Commands
@bot.command(name="marketing")
async def marketing_cmd(ctx, action: str, *, details: Optional[str] = None):
    """Launch marketing campaigns"""
    company = get_company(ctx.author.id)
    if not company:
        await ctx.send("❌ You don't own a company.")
        return
    
    if action.lower() == "launch":
        if not details:
            embed = discord.Embed(
                title="📢 Marketing Campaigns",
                color=discord.Color.orange()
            )
            embed.add_field(name="Social Media Ads", value="Cost: £20,000 + 100 Knowledge\nEffect: +15% customers", inline=False)
            embed.add_field(name="Influencer Campaign", value="Cost: £50,000 + 250 Knowledge\nEffect: +30% customers", inline=False)
            embed.add_field(name="TV Advertising", value="Cost: £100,000 + 500 Knowledge\nEffect: +50% customers", inline=False)
            embed.add_field(name="Viral Campaign", value="Cost: £150,000 + 1000 Knowledge\nEffect: +100% customers", inline=False)
            embed.add_field(name="Usage", value="`!marketing launch <campaign_type>`", inline=False)
            await ctx.send(embed=embed)
            return
        
        campaigns = {
            "social media ads": {"cash": 20000, "knowledge": 100, "customer_mult": 1.15},
            "influencer campaign": {"cash": 50000, "knowledge": 250, "customer_mult": 1.30},
            "tv advertising": {"cash": 100000, "knowledge": 500, "customer_mult": 1.50},
            "viral campaign": {"cash": 150000, "knowledge": 1000, "customer_mult": 2.0},
        }
        
        campaign = campaigns.get(details.lower())
        if not campaign:
            await ctx.send("❌ Invalid campaign type.")
            return
        
        if company['cash'] < campaign['cash'] or company['knowledge'] < campaign['knowledge']:
            await ctx.send(f"❌ Insufficient resources.")
            return
        
        deduct_cash(ctx.author.id, campaign['cash'])
        deduct_knowledge(ctx.author.id, campaign['knowledge'])
        
        # Apply to all products
        for product in company['products']:
            product['customers'] = int(product['customers'] * campaign['customer_mult'])
            product['popularity'] = min(10, product['popularity'] + 2)
        
        company['reputation'] += int(500 * campaign['customer_mult'])
        update_company(ctx.author.id, company)
        
        await ctx.send(f"✅ {details.title()} launched!\n• Customer growth applied to all products\n• Reputation increased")

# Market Commands
@bot.command(name="market")
async def market_cmd(ctx, action: str = "leaders"):
    """View market information"""
    company = get_company(ctx.author.id)
    if not company:
        await ctx.send("❌ You don't own a company.")
        return
    
    if action.lower() == "leaders":
        all_companies = get_all_companies()
        
        # Group by industry
        industry_leaders = {}
        for comp in all_companies:
            ind = comp.get('industry')
            if ind not in industry_leaders:
                industry_leaders[ind] = []
            industry_leaders[ind].append(comp)
        
        embed = discord.Embed(
            title="📈 Market Leaders",
            color=discord.Color.gold()
        )
        
        for industry, companies in industry_leaders.items():
            sorted_comp = sorted(companies, key=lambda c: c.get('customers', 0), reverse=True)
            top_3 = sorted_comp[:3]
            
            if not top_3:
                continue
            
            total_market = sum(c.get('customers', 0) for c in sorted_comp)
            
            leaderboard = "\n".join([
                f"{i+1}. {c['name']}: {format_number(c.get('customers', 0))} ({int(c.get('customers', 0)/total_market*100) if total_market > 0 else 0}%)"
                for i, c in enumerate(top_3)
            ])
            
            embed.add_field(name=industry, value=leaderboard, inline=False)
        
        await ctx.send(embed=embed)

# Leaderboard Commands
@bot.command(name="leaderboard")
async def leaderboard_cmd(ctx, metric: str = "valuation"):
    """View global leaderboards"""
    all_companies = get_all_companies()
    
    if metric.lower() == "valuation":
        sorted_comp = sorted(all_companies, key=lambda c: get_company_valuation(c), reverse=True)
        title = "💎 Valuation Leaderboard"
        value_func = lambda c: format_currency(get_company_valuation(c))
    
    elif metric.lower() == "revenue":
        sorted_comp = sorted(all_companies, key=lambda c: c.get('revenue', 0), reverse=True)
        title = "💰 Revenue Leaderboard"
        value_func = lambda c: format_currency(c.get('revenue', 0))
    
    elif metric.lower() == "customers":
        sorted_comp = sorted(all_companies, key=lambda c: c.get('customers', 0), reverse=True)
        title = "👥 Customer Leaderboard"
        value_func = lambda c: format_number(c.get('customers', 0))
    
    elif metric.lower() == "knowledge":
        sorted_comp = sorted(all_companies, key=lambda c: c.get('knowledge_earned', 0), reverse=True)
        title = "🧠 Knowledge Leaderboard"
        value_func = lambda c: str(c.get('knowledge_earned', 0))
    
    elif metric.lower() == "level":
        sorted_comp = sorted(all_companies, key=lambda c: get_company_level(c.get('knowledge_earned', 0)), reverse=True)
        title = "📈 Company Level Leaderboard"
        value_func = lambda c: f"Level {get_company_level(c.get('knowledge_earned', 0))}"
    
    elif metric.lower() == "innovation":
        sorted_comp = sorted(all_companies, key=lambda c: get_innovation_score(c), reverse=True)
        title = "💡 Innovation Leaderboard"
        value_func = lambda c: str(get_innovation_score(c))
    
    else:
        await ctx.send("❌ Valid metrics: valuation, revenue, customers, knowledge, level, innovation")
        return
    
    embed = discord.Embed(title=title, color=discord.Color.gold())
    
    for i, comp in enumerate(sorted_comp[:10]):
        embed.add_field(
            name=f"{i+1}. {comp['name']}",
            value=value_func(comp),
            inline=False
        )
    
    await ctx.send(embed=embed)

# Daily and Weekly Rewards
@bot.command(name="daily")
async def daily_cmd(ctx):
    """Claim daily reward"""
    user_id = ctx.author.id
    company = get_company(user_id)
    
    if not company:
        await ctx.send("❌ You don't own a company.")
        return
    
    last_daily = get_daily_reward(user_id)
    now = datetime.now()
    
    if last_daily:
        last_time = datetime.fromisoformat(last_daily['timestamp'])
        if (now - last_time).total_seconds() < 86400:  # 24 hours
            remaining = 86400 - (now - last_time).total_seconds()
            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            await ctx.send(f"⏳ Daily reward available in {hours}h {minutes}m")
            return
    
    # Scale rewards by level
    level = get_company_level(company['knowledge_earned'])
    cash_reward = int(CONFIG["daily_reward_cash"] * (1 + level * 0.1))
    knowledge_reward = int(CONFIG["daily_reward_knowledge"] * (1 + level * 0.05))
    
    add_cash(user_id, cash_reward)
    add_knowledge(user_id, knowledge_reward)
    add_daily_reward(user_id, now.isoformat())
    
    embed = discord.Embed(
        title="✅ Daily Reward Claimed!",
        color=discord.Color.green()
    )
    embed.add_field(name="💰 Cash", value=format_currency(cash_reward), inline=True)
    embed.add_field(name="🧠 Knowledge", value=str(knowledge_reward), inline=True)
    
    await ctx.send(embed=embed)

@bot.command(name="weekly")
async def weekly_cmd(ctx):
    """Claim weekly reward"""
    user_id = ctx.author.id
    company = get_company(user_id)
    
    if not company:
        await ctx.send("❌ You don't own a company.")
        return
    
    last_weekly = get_weekly_reward(user_id)
    now = datetime.now()
    
    if last_weekly:
        last_time = datetime.fromisoformat(last_weekly['timestamp'])
        if (now - last_time).total_seconds() < 604800:  # 7 days
            remaining = 604800 - (now - last_time).total_seconds()
            days = int(remaining // 86400)
            hours = int((remaining % 86400) // 3600)
            await ctx.send(f"⏳ Weekly reward available in {days}d {hours}h")
            return
    
    # Scale rewards by level
    level = get_company_level(company['knowledge_earned'])
    cash_reward = int(CONFIG["weekly_reward_cash"] * (1 + level * 0.15))
    knowledge_reward = int(CONFIG["weekly_reward_knowledge"] * (1 + level * 0.1))
    
    add_cash(user_id, cash_reward)
    add_knowledge(user_id, knowledge_reward)
    add_weekly_reward(user_id, now.isoformat())
    
    embed = discord.Embed(
        title="✅ Weekly Reward Claimed!",
        color=discord.Color.green()
    )
    embed.add_field(name="💰 Cash", value=format_currency(cash_reward), inline=True)
    embed.add_field(name="🧠 Knowledge", value=str(knowledge_reward), inline=True)
    
    await ctx.send(embed=embed)

# News and Events Commands
@bot.command(name="news")
async def news_cmd(ctx, action: str = "latest"):
    """View game news"""
    if action.lower() == "latest":
        if not GAME_STATE.get('news_log'):
            await ctx.send("❌ No news available yet.")
            return
        
        embed = discord.Embed(
            title="📰 Latest News",
            color=discord.Color.blue()
        )
        
        for news in GAME_STATE['news_log'][-10:]:
            embed.add_field(name=news['title'], value=news['content'], inline=False)
        
        await ctx.send(embed=embed)

@bot.command(name="events")
async def events_cmd(ctx):
    """View active world events"""
    if not GAME_STATE.get('events'):
        await ctx.send("❌ No active events.")
        return
    
    embed = discord.Embed(
        title="🌍 Active World Events",
        color=discord.Color.orange()
    )
    
    for event in GAME_STATE['events']:
        duration_remaining = event['end_time'] - datetime.now().timestamp()
        hours = int(duration_remaining // 3600)
        
        effects = "\n".join([f"• {k}: {v:.0%}" for k, v in event['effects'].items()])
        
        embed.add_field(
            name=f"{event['name']} ({hours}h remaining)",
            value=effects,
            inline=False
        )
    
    await ctx.send(embed=embed)

# Background Tasks
@tasks.loop(minutes=5)
async def background_tasks():
    """Main game loop - process monthly expenses and revenue"""
    all_companies = get_all_companies()
    
    for company in all_companies:
        # Calculate revenue from products
        total_revenue = sum(p['revenue'] for p in company.get('products', []))
        
        # Calculate expenses (salaries)
        total_salaries = sum(e['salary'] for e in company.get('employees', []))
        
        # Apply revenue and expenses
        company['revenue'] = total_revenue
        company['expenses'] = total_salaries
        
        new_cash = company['cash'] + total_revenue - total_salaries
        company['cash'] = max(0, new_cash)
        
        # Generate knowledge from researchers
        researchers = [e for e in company.get('employees', []) if e['type'] == 'Researcher']
        knowledge_gen = len(researchers) * 50  # 50 knowledge per researcher per cycle
        
        company['knowledge'] += knowledge_gen
        company['total_knowledge_earned'] += knowledge_gen
        
        company['total_revenue_earned'] += total_revenue
        
        # Update customers from marketing
        for product in company.get('products', []):
            base_growth = int(product['customers'] * 0.02)  # 2% growth per cycle
            developer_mult = len([e for e in company.get('employees', []) if e['type'] == 'Developer']) * 1.05
            product['customers'] += int(base_growth * developer_mult)
        
        # Update company
        user_id = company['user_id']
        update_company(user_id, company)

@tasks.loop(hours=1)
async def offline_progression():
    """Calculate offline progression for players"""
    pass  # Already handled by background tasks

@tasks.loop(minutes=10)
async def market_simulation():
    """Simulate market changes"""
    all_companies = get_all_companies()
    
    # Track market share by industry
    industries = {}
    
    for company in all_companies:
        industry = company['industry']
        if industry not in industries:
            industries[industry] = {'total_customers': 0, 'companies': []}
        
        industries[industry]['total_customers'] += company.get('customers', 0)
        industries[industry]['companies'].append(company)
    
    # Store market data
    GAME_STATE['markets'] = industries

@tasks.loop(hours=1)
async def global_events_trigger():
    """Trigger global world events"""
    if random.random() < 0.3:  # 30% chance each hour
        event_template = random.choice(GLOBAL_EVENTS_LIST)
        event = {
            "name": event_template['name'],
            "start_time": datetime.now().timestamp(),
            "end_time": datetime.now().timestamp() + event_template['duration'],
            "effects": event_template['effects'],
        }
        
        GAME_STATE['events'].append(event)
        
        news = {
            "title": f"🌍 {event_template['name']} Begins!",
            "content": f"A major event is affecting the market. {', '.join([f'{k}: {v:.0%}' for k, v in event_template['effects'].items()])}",
            "timestamp": datetime.now().isoformat()
        }
        
        GAME_STATE['news_log'].append(news)
    
    # Remove expired events
    now = datetime.now().timestamp()
    GAME_STATE['events'] = [e for e in GAME_STATE['events'] if e['end_time'] > now]

@tasks.loop(minutes=30)
async def daily_events_trigger():
    """Trigger random daily events for companies"""
    all_companies = get_all_companies()
    
    for company in all_companies:
        if random.random() < 0.1:  # 10% chance
            if random.random() < 0.6:  # 60% positive
                event = random.choice(RANDOM_EVENTS_POSITIVE)
                company['cash'] += event['cash_bonus']
                company['knowledge'] += event['knowledge_bonus']
                company['customers'] += event['customer_bonus']
                
                news = {
                    "title": f"✨ {company['name']}: {event['name']}!",
                    "content": f"Gained {format_currency(event['cash_bonus'])} and {event['knowledge_bonus']} knowledge!",
                    "timestamp": datetime.now().isoformat()
                }
            else:  # Negative event
                event = random.choice(RANDOM_EVENTS_NEGATIVE)
                company['cash'] = max(0, company['cash'] - event['cash_loss'])
                company['reputation'] = max(0, company['reputation'] - event['reputation_loss'])
                
                news = {
                    "title": f"⚠️ {company['name']}: {event['name']}!",
                    "content": f"Lost {format_currency(event['cash_loss'])} and {event['reputation_loss']} reputation!",
                    "timestamp": datetime.now().isoformat()
                }
            
            GAME_STATE['news_log'].append(news)
            update_company(company['user_id'], company)

@tasks.loop(hours=2)
async def employee_market_rotation():
    """Rotate employee market every 2 hours"""
    if not hasattr(bot, 'employee_market'):
        bot.employee_market = random.sample(EMPLOYEES_POOL, min(5, len(EMPLOYEES_POOL)))
    else:
        # 50% chance to add a rare employee
        if random.random() < 0.2:
            rare_emp = random.choice([e for e in EMPLOYEES_POOL if e['rarity'] in ['Rare', 'Epic', 'Legendary']])
            bot.employee_market[random.randint(0, len(bot.employee_market)-1)] = rare_emp
        else:
            bot.employee_market = random.sample(EMPLOYEES_POOL, min(5, len(EMPLOYEES_POOL)))

@tasks.loop(hours=4)
async def investor_generation():
    """Generate investor offers periodically"""
    pass  # Investors generated on demand

# Help command
@bot.command(name="help")
async def help_cmd(ctx):
    """Show help and commands"""
    embed = discord.Embed(
        title="🚀 Startup Simulator - Commands",
        description="Multiplayer Business Strategy Game",
        color=discord.Color.blue()
    )
    
    embed.add_field(name="Company", value="`!startup create <name> | <industry> | <founder>`\n`!startup profile`\n`!startup rename <name>`\n`!startup delete`\n`!stats`", inline=False)
    embed.add_field(name="Employees", value="`!hire`\n`!employees`\n`!fire <name>`\n`!promote <name>`", inline=False)
    embed.add_field(name="Products", value="`!product create <name>`\n`!product upgrade <name>`\n`!product info <name>`\n`!product list`", inline=False)
    embed.add_field(name="Research", value="`!research tree`\n`!research start <tech>`\n`!research status`", inline=False)
    embed.add_field(name="Markets", value="`!market leaders`\n`!leaderboard [metric]`", inline=False)
    embed.add_field(name="Marketing", value="`!marketing launch <type>`", inline=False)
    embed.add_field(name="Rewards", value="`!daily`\n`!weekly`", inline=False)
    embed.add_field(name="Game", value="`!news`\n`!events`", inline=False)
    
    await ctx.send(embed=embed)

# Run bot
if __name__ == "__main__":
    TOKEN = os.getenv("DISCORD_TOKEN")
    if not TOKEN:
        print("❌ DISCORD_TOKEN environment variable not set!")
        exit(1)
    
    bot.run(TOKEN)
