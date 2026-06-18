"""
Discord Server Setup Bot - Professional Edition
Pre-built templates for professional Discord servers with detailed configurations,
role permissions, read-only channels, admin-only channels, and custom colors.
"""

import sys
import unittest.mock as mock
sys.modules['audioop'] = mock.MagicMock()

import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv
import logging
import sqlite3
from typing import List, Dict, Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BOT_COLOR = 0x5865F2
DATABASE_FILE = "server_setup.db"

# Role colors (hex codes)
COLORS = {
    "admin": 0xFF0000,      # Red
    "moderator": 0xFF9900,  # Orange
    "staff": 0xFFFF00,      # Yellow
    "members": 0x00FF00,    # Green
    "vip": 0x9900FF,        # Purple
    "verified": 0x00FFFF,   # Cyan
    "support": 0xFF00FF,    # Magenta
    "developer": 0x0099FF,  # Blue
}

# ============================================================================
# PROFESSIONAL TEMPLATES
# ============================================================================

TEMPLATES = {
    "Professional": {
        "server_name": "Professional Server",
        "description": "A complete professional workspace with announcements, projects, and team communication.",
        "roles": [
            {
                "name": "Owner",
                "color": COLORS["admin"],
                "permissions": ["administrator"]
            },
            {
                "name": "Management",
                "color": COLORS["moderator"],
                "permissions": ["manage_messages", "manage_roles", "manage_channels", "manage_guild"]
            },
            {
                "name": "Team Lead",
                "color": COLORS["staff"],
                "permissions": ["manage_messages", "kick_members"]
            },
            {
                "name": "Team Member",
                "color": COLORS["members"],
                "permissions": []
            },
            {
                "name": "Intern",
                "color": COLORS["verified"],
                "permissions": []
            }
        ],
        "categories": [
            {
                "name": "📢 Announcements",
                "channels": [
                    {
                        "name": "announcements",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Important company announcements"
                    },
                    {
                        "name": "updates",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Project and system updates"
                    },
                    {
                        "name": "policy-changes",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "New policies and guidelines"
                    }
                ]
            },
            {
                "name": "💼 Management",
                "channels": [
                    {
                        "name": "leadership",
                        "type": "text",
                        "read_only": False,
                        "admin_only": True,
                        "description": "Leadership discussions"
                    },
                    {
                        "name": "strategy",
                        "type": "text",
                        "read_only": False,
                        "admin_only": True,
                        "description": "Strategic planning and decisions"
                    },
                    {
                        "name": "performance-reviews",
                        "type": "text",
                        "read_only": False,
                        "admin_only": True,
                        "description": "Employee performance discussions"
                    }
                ]
            },
            {
                "name": "👥 Teams",
                "channels": [
                    {
                        "name": "general",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "General team discussion"
                    },
                    {
                        "name": "projects",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Project management and tracking"
                    },
                    {
                        "name": "team-voice",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Team voice chat"
                    },
                    {
                        "name": "meetings",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Meeting room"
                    }
                ]
            },
            {
                "name": "📚 Resources",
                "channels": [
                    {
                        "name": "documentation",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Technical documentation"
                    },
                    {
                        "name": "knowledge-base",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Company knowledge base"
                    },
                    {
                        "name": "templates",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Shared templates and resources"
                    }
                ]
            },
            {
                "name": "💬 Social",
                "channels": [
                    {
                        "name": "watercooler",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Off-topic casual chat"
                    },
                    {
                        "name": "celebrations",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Team celebrations and milestones"
                    },
                    {
                        "name": "lounge",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Casual voice hang out"
                    }
                ]
            }
        ]
    },
    
    "Gaming Community": {
        "server_name": "Gaming Community",
        "description": "A vibrant gaming community with guilds, tournaments, streaming content, and social channels.",
        "roles": [
            {
                "name": "Owner",
                "color": COLORS["admin"],
                "permissions": ["administrator"]
            },
            {
                "name": "Admin",
                "color": COLORS["moderator"],
                "permissions": ["manage_messages", "manage_roles", "manage_channels", "manage_guild", "ban_members"]
            },
            {
                "name": "Moderator",
                "color": COLORS["staff"],
                "permissions": ["manage_messages", "kick_members", "manage_channels"]
            },
            {
                "name": "Streamer",
                "color": COLORS["vip"],
                "permissions": ["manage_messages"]
            },
            {
                "name": "Verified",
                "color": COLORS["verified"],
                "permissions": []
            },
            {
                "name": "Member",
                "color": COLORS["members"],
                "permissions": []
            }
        ],
        "categories": [
            {
                "name": "📢 Announcements",
                "channels": [
                    {
                        "name": "announcements",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Server announcements and news"
                    },
                    {
                        "name": "updates",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Game and server updates"
                    },
                    {
                        "name": "rules",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Server rules and guidelines"
                    }
                ]
            },
            {
                "name": "🎮 Gaming",
                "channels": [
                    {
                        "name": "general",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "General gaming discussion"
                    },
                    {
                        "name": "lfg",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Looking for group / team recruitment"
                    },
                    {
                        "name": "tournaments",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Tournament information and signups"
                    },
                    {
                        "name": "strategy",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Strategy guides and tips"
                    }
                ]
            },
            {
                "name": "🎙️ Voice Channels",
                "channels": [
                    {
                        "name": "gaming-1",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Gaming voice chat 1"
                    },
                    {
                        "name": "gaming-2",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Gaming voice chat 2"
                    },
                    {
                        "name": "gaming-3",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Gaming voice chat 3"
                    }
                ]
            },
            {
                "name": "🎬 Content",
                "channels": [
                    {
                        "name": "streams",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Stream announcements and links"
                    },
                    {
                        "name": "stream-archive",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Archived stream VODs"
                    },
                    {
                        "name": "creator-tips",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Content creation tips and tricks"
                    }
                ]
            },
            {
                "name": "👥 Guilds",
                "channels": [
                    {
                        "name": "guild-announcements",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Guild news and updates"
                    },
                    {
                        "name": "guild-recruitment",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Guild recruitment and applications"
                    },
                    {
                        "name": "guild-voice",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Guild voice operations"
                    }
                ]
            },
            {
                "name": "💬 Community",
                "channels": [
                    {
                        "name": "introductions",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Introduce yourself"
                    },
                    {
                        "name": "events",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Community events and activities"
                    },
                    {
                        "name": "off-topic",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Off-topic discussion"
                    },
                    {
                        "name": "hangout",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Casual voice hang out"
                    }
                ]
            },
            {
                "name": "🛡️ Management",
                "channels": [
                    {
                        "name": "admin-chat",
                        "type": "text",
                        "read_only": False,
                        "admin_only": True,
                        "description": "Admin discussions"
                    },
                    {
                        "name": "mod-logs",
                        "type": "text",
                        "read_only": True,
                        "admin_only": True,
                        "description": "Moderation action logs"
                    },
                    {
                        "name": "reports",
                        "type": "text",
                        "read_only": False,
                        "admin_only": True,
                        "description": "User reports and appeals"
                    }
                ]
            }
        ]
    },

    "Content Creator": {
        "server_name": "Creator Hub",
        "description": "A dedicated space for content creators with community engagement, sponsorships, and collaboration.",
        "roles": [
            {
                "name": "Creator",
                "color": COLORS["admin"],
                "permissions": ["administrator"]
            },
            {
                "name": "Manager",
                "color": COLORS["moderator"],
                "permissions": ["manage_messages", "manage_roles", "manage_channels"]
            },
            {
                "name": "Editor",
                "color": COLORS["staff"],
                "permissions": ["manage_messages"]
            },
            {
                "name": "Collaborator",
                "color": COLORS["vip"],
                "permissions": []
            },
            {
                "name": "Sponsor",
                "color": COLORS["vip"],
                "permissions": []
            },
            {
                "name": "Community Member",
                "color": COLORS["verified"],
                "permissions": []
            }
        ],
        "categories": [
            {
                "name": "📢 Creator Info",
                "channels": [
                    {
                        "name": "announcements",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Upload schedule and news"
                    },
                    {
                        "name": "content-calendar",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Upcoming content schedule"
                    },
                    {
                        "name": "creator-studio",
                        "type": "text",
                        "read_only": False,
                        "admin_only": True,
                        "description": "Creator's private workspace"
                    }
                ]
            },
            {
                "name": "🎬 Content",
                "channels": [
                    {
                        "name": "content-ideas",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Brainstorm and suggest content"
                    },
                    {
                        "name": "collaboration",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Collaboration opportunities"
                    },
                    {
                        "name": "behind-the-scenes",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Behind the scenes content"
                    }
                ]
            },
            {
                "name": "🤝 Sponsorships",
                "channels": [
                    {
                        "name": "sponsor-info",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Sponsor information and perks"
                    },
                    {
                        "name": "sponsor-lounge",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Exclusive sponsor chat"
                    },
                    {
                        "name": "sponsorship-deals",
                        "type": "text",
                        "read_only": False,
                        "admin_only": True,
                        "description": "Sponsorship negotiations"
                    }
                ]
            },
            {
                "name": "👥 Community",
                "channels": [
                    {
                        "name": "general",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "General community chat"
                    },
                    {
                        "name": "fan-theories",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Community theories and discussions"
                    },
                    {
                        "name": "fan-art",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Community fan art showcase"
                    }
                ]
            },
            {
                "name": "🎙️ Voice",
                "channels": [
                    {
                        "name": "hangout",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Community hangout voice"
                    },
                    {
                        "name": "recording",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Recording sessions"
                    }
                ]
            }
        ]
    },

    "Community Server": {
        "server_name": "Community Hub",
        "description": "A welcoming community server with discussion forums, events, and social activities.",
        "roles": [
            {
                "name": "Admin",
                "color": COLORS["admin"],
                "permissions": ["administrator"]
            },
            {
                "name": "Moderator",
                "color": COLORS["moderator"],
                "permissions": ["manage_messages", "kick_members", "ban_members", "manage_channels"]
            },
            {
                "name": "Event Organizer",
                "color": COLORS["staff"],
                "permissions": ["manage_messages"]
            },
            {
                "name": "Verified",
                "color": COLORS["verified"],
                "permissions": []
            },
            {
                "name": "Member",
                "color": COLORS["members"],
                "permissions": []
            }
        ],
        "categories": [
            {
                "name": "📜 Welcome",
                "channels": [
                    {
                        "name": "welcome",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Welcome message and rules"
                    },
                    {
                        "name": "introductions",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Introduce yourself to the community"
                    },
                    {
                        "name": "announcements",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Important announcements"
                    }
                ]
            },
            {
                "name": "💬 Discussion",
                "channels": [
                    {
                        "name": "general",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "General discussion"
                    },
                    {
                        "name": "off-topic",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Off-topic conversations"
                    },
                    {
                        "name": "questions",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Ask questions to the community"
                    }
                ]
            },
            {
                "name": "🎉 Events",
                "channels": [
                    {
                        "name": "events",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Event announcements and sign-ups"
                    },
                    {
                        "name": "game-nights",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Game night coordination"
                    },
                    {
                        "name": "events-voice",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Voice for events"
                    }
                ]
            },
            {
                "name": "🏆 Spotlight",
                "channels": [
                    {
                        "name": "achievements",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Share community achievements"
                    },
                    {
                        "name": "member-spotlight",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Featured member of the month"
                    }
                ]
            },
            {
                "name": "🎙️ Voice",
                "channels": [
                    {
                        "name": "general-voice",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "General voice chat"
                    },
                    {
                        "name": "lounge",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Casual hangout voice"
                    }
                ]
            },
            {
                "name": "🛡️ Moderation",
                "channels": [
                    {
                        "name": "reports",
                        "type": "text",
                        "read_only": False,
                        "admin_only": True,
                        "description": "User reports"
                    },
                    {
                        "name": "mod-logs",
                        "type": "text",
                        "read_only": True,
                        "admin_only": True,
                        "description": "Moderation action logs"
                    }
                ]
            }
        ]
    },

    "Education": {
        "server_name": "Learning Hub",
        "description": "Educational platform with courses, classrooms, study groups, and tutoring channels.",
        "roles": [
            {
                "name": "Instructor",
                "color": COLORS["admin"],
                "permissions": ["administrator"]
            },
            {
                "name": "Teaching Assistant",
                "color": COLORS["moderator"],
                "permissions": ["manage_messages", "manage_channels"]
            },
            {
                "name": "Subject Expert",
                "color": COLORS["staff"],
                "permissions": ["manage_messages"]
            },
            {
                "name": "Student",
                "color": COLORS["members"],
                "permissions": []
            },
            {
                "name": "Auditor",
                "color": COLORS["verified"],
                "permissions": []
            }
        ],
        "categories": [
            {
                "name": "📚 Courses",
                "channels": [
                    {
                        "name": "course-announcements",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Course syllabus and announcements"
                    },
                    {
                        "name": "lectures",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Lecture notes and materials"
                    },
                    {
                        "name": "assignments",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Assignment briefs and due dates"
                    }
                ]
            },
            {
                "name": "🎓 Classroom",
                "channels": [
                    {
                        "name": "general-discussion",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Classroom discussion"
                    },
                    {
                        "name": "questions",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Ask questions to instructors"
                    },
                    {
                        "name": "resources",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Share study resources"
                    }
                ]
            },
            {
                "name": "👥 Study Groups",
                "channels": [
                    {
                        "name": "study-groups",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Form and join study groups"
                    },
                    {
                        "name": "group-voice",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Group study sessions"
                    }
                ]
            },
            {
                "name": "🆘 Tutoring",
                "channels": [
                    {
                        "name": "tutoring-requests",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Request tutoring help"
                    },
                    {
                        "name": "tutor-office-hours",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Tutor office hours"
                    }
                ]
            },
            {
                "name": "💬 Community",
                "channels": [
                    {
                        "name": "introductions",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Introduce yourself"
                    },
                    {
                        "name": "general",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Off-topic chat"
                    }
                ]
            },
            {
                "name": "🛡️ Admin",
                "channels": [
                    {
                        "name": "instructor-lounge",
                        "type": "text",
                        "read_only": False,
                        "admin_only": True,
                        "description": "Instructor discussions"
                    },
                    {
                        "name": "mod-logs",
                        "type": "text",
                        "read_only": True,
                        "admin_only": True,
                        "description": "Moderation logs"
                    }
                ]
            }
        ]
    },

    "Startup": {
        "server_name": "Startup Workspace",
        "description": "Fast-paced startup environment with product, engineering, marketing, and fundraising channels.",
        "roles": [
            {
                "name": "Founder",
                "color": COLORS["admin"],
                "permissions": ["administrator"]
            },
            {
                "name": "Executive",
                "color": COLORS["moderator"],
                "permissions": ["manage_messages", "manage_channels", "manage_roles"]
            },
            {
                "name": "Team Lead",
                "color": COLORS["staff"],
                "permissions": ["manage_messages"]
            },
            {
                "name": "Team Member",
                "color": COLORS["members"],
                "permissions": []
            },
            {
                "name": "Advisor",
                "color": COLORS["vip"],
                "permissions": []
            },
            {
                "name": "Investor",
                "color": COLORS["verified"],
                "permissions": []
            }
        ],
        "categories": [
            {
                "name": "📢 Announcements",
                "channels": [
                    {
                        "name": "company-news",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Major company announcements"
                    },
                    {
                        "name": "metrics",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Weekly KPIs and metrics"
                    },
                    {
                        "name": "milestones",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Company milestones achieved"
                    }
                ]
            },
            {
                "name": "🚀 Product",
                "channels": [
                    {
                        "name": "product-roadmap",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Product roadmap and planning"
                    },
                    {
                        "name": "feature-discussion",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Feature ideas and feedback"
                    },
                    {
                        "name": "bugs-issues",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Report bugs and issues"
                    }
                ]
            },
            {
                "name": "👨‍💻 Engineering",
                "channels": [
                    {
                        "name": "tech-discussion",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Technical discussions"
                    },
                    {
                        "name": "code-review",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Code review coordination"
                    },
                    {
                        "name": "devops",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "DevOps and deployment"
                    }
                ]
            },
            {
                "name": "📈 Growth",
                "channels": [
                    {
                        "name": "marketing-strategy",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Marketing campaigns and strategy"
                    },
                    {
                        "name": "partnerships",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Partnership opportunities"
                    },
                    {
                        "name": "customer-feedback",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Customer feedback and insights"
                    }
                ]
            },
            {
                "name": "💰 Fundraising",
                "channels": [
                    {
                        "name": "funding-strategy",
                        "type": "text",
                        "read_only": False,
                        "admin_only": True,
                        "description": "Funding strategy discussions"
                    },
                    {
                        "name": "investor-relations",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Investor updates and relations"
                    },
                    {
                        "name": "cap-table",
                        "type": "text",
                        "read_only": True,
                        "admin_only": True,
                        "description": "Cap table and equity info"
                    }
                ]
            },
            {
                "name": "💬 General",
                "channels": [
                    {
                        "name": "watercooler",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Casual team chat"
                    },
                    {
                        "name": "random",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Random fun stuff"
                    },
                    {
                        "name": "events",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Team events and hangouts"
                    }
                ]
            },
            {
                "name": "🛡️ Executive",
                "channels": [
                    {
                        "name": "leadership",
                        "type": "text",
                        "read_only": False,
                        "admin_only": True,
                        "description": "Executive leadership discussions"
                    },
                    {
                        "name": "board-room",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": True,
                        "description": "Board meetings"
                    }
                ]
            }
        ]
    },

    "Hobby & Interests": {
        "server_name": "Community Hub",
        "description": "Casual server for hobby communities with discussion, events, showcases, and meetups.",
        "roles": [
            {
                "name": "Owner",
                "color": COLORS["admin"],
                "permissions": ["administrator"]
            },
            {
                "name": "Moderator",
                "color": COLORS["moderator"],
                "permissions": ["manage_messages", "manage_channels", "kick_members"]
            },
            {
                "name": "Expert",
                "color": COLORS["staff"],
                "permissions": ["manage_messages"]
            },
            {
                "name": "Active Member",
                "color": COLORS["verified"],
                "permissions": []
            },
            {
                "name": "Member",
                "color": COLORS["members"],
                "permissions": []
            }
        ],
        "categories": [
            {
                "name": "📢 Community Info",
                "channels": [
                    {
                        "name": "announcements",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Community announcements"
                    },
                    {
                        "name": "rules",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Community rules and guidelines"
                    },
                    {
                        "name": "faq",
                        "type": "text",
                        "read_only": True,
                        "admin_only": False,
                        "description": "Frequently asked questions"
                    }
                ]
            },
            {
                "name": "💬 Discussion",
                "channels": [
                    {
                        "name": "general",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Main discussion"
                    },
                    {
                        "name": "introductions",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Introduce yourself"
                    },
                    {
                        "name": "questions",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Ask the community"
                    },
                    {
                        "name": "tips-tricks",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Share tips and tricks"
                    }
                ]
            },
            {
                "name": "🏆 Showcase",
                "channels": [
                    {
                        "name": "showcases",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Share your work and creations"
                    },
                    {
                        "name": "gallery",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Photo and media gallery"
                    }
                ]
            },
            {
                "name": "🎉 Events",
                "channels": [
                    {
                        "name": "meetups",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Plan local meetups"
                    },
                    {
                        "name": "competitions",
                        "type": "text",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Community competitions"
                    },
                    {
                        "name": "events-voice",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Event hangout voice"
                    }
                ]
            },
            {
                "name": "🎙️ Voice",
                "channels": [
                    {
                        "name": "hangout",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Casual hangout"
                    },
                    {
                        "name": "study-group",
                        "type": "voice",
                        "read_only": False,
                        "admin_only": False,
                        "description": "Study or practice together"
                    }
                ]
            },
            {
                "name": "🛡️ Moderation",
                "channels": [
                    {
                        "name": "reports",
                        "type": "text",
                        "read_only": False,
                        "admin_only": True,
                        "description": "Report issues to mods"
                    },
                    {
                        "name": "mod-logs",
                        "type": "text",
                        "read_only": True,
                        "admin_only": True,
                        "description": "Moderation action logs"
                    }
                ]
            }
        ]
    }
}

# ============================================================================
# DATABASE
# ============================================================================

class Database:
    """SQLite database handler."""
    
    def __init__(self, db_file: str = DATABASE_FILE):
        self.db_file = db_file
        self._init_database()
    
    def _init_database(self):
        """Create tables if they don't exist."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS setups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    guild_id INTEGER NOT NULL,
                    user_id INTEGER NOT NULL,
                    template_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS created_roles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setup_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    role_id INTEGER NOT NULL,
                    role_name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (setup_id) REFERENCES setups(id)
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS created_channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setup_id INTEGER NOT NULL,
                    guild_id INTEGER NOT NULL,
                    channel_id INTEGER NOT NULL,
                    channel_name TEXT NOT NULL,
                    channel_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (setup_id) REFERENCES setups(id)
                )
            """)
            
            conn.commit()
            logger.info("Database initialized")
        except Exception as e:
            logger.error(f"Database init error: {e}")
        finally:
            conn.close()
    
    def save_setup(self, guild_id: int, user_id: int, template_name: str) -> int:
        """Save setup and return setup_id."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO setups (guild_id, user_id, template_name) VALUES (?, ?, ?)",
                (guild_id, user_id, template_name)
            )
            conn.commit()
            setup_id = cursor.lastrowid
            logger.info(f"Saved setup {setup_id} for guild {guild_id}")
            return setup_id
        except Exception as e:
            logger.error(f"Error saving setup: {e}")
            return None
        finally:
            conn.close()
    
    def add_role(self, setup_id: int, guild_id: int, role_id: int, role_name: str):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO created_roles (setup_id, guild_id, role_id, role_name) VALUES (?, ?, ?, ?)",
                (setup_id, guild_id, role_id, role_name)
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Error adding role: {e}")
        finally:
            conn.close()
    
    def add_channel(self, setup_id: int, guild_id: int, channel_id: int, channel_name: str, channel_type: str):
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO created_channels (setup_id, guild_id, channel_id, channel_name, channel_type) VALUES (?, ?, ?, ?, ?)",
                (setup_id, guild_id, channel_id, channel_name, channel_type)
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Error adding channel: {e}")
        finally:
            conn.close()
    
    def get_created_roles(self, setup_id: int) -> List[Tuple[int, str]]:
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT role_id, role_name FROM created_roles WHERE setup_id = ?",
                (setup_id,)
            )
            result = cursor.fetchall()
            return result
        except Exception as e:
            logger.error(f"Error getting roles: {e}")
            return []
        finally:
            conn.close()
    
    def get_created_channels(self, setup_id: int) -> List[Tuple[int, str, str]]:
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT channel_id, channel_name, channel_type FROM created_channels WHERE setup_id = ?",
                (setup_id,)
            )
            result = cursor.fetchall()
            return result
        except Exception as e:
            logger.error(f"Error getting channels: {e}")
            return []
        finally:
            conn.close()
    
    def get_guild_setups(self, guild_id: int) -> List[Tuple[int, str, str]]:
        """Get all setups for a guild (id, template_name, created_at)."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, template_name, created_at FROM setups WHERE guild_id = ? ORDER BY created_at DESC",
                (guild_id,)
            )
            result = cursor.fetchall()
            return result
        except Exception as e:
            logger.error(f"Error getting guild setups: {e}")
            return []
        finally:
            conn.close()
    
    def delete_setup(self, setup_id: int):
        """Delete a specific setup and its associated roles/channels."""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM created_roles WHERE setup_id = ?", (setup_id,))
            cursor.execute("DELETE FROM created_channels WHERE setup_id = ?", (setup_id,))
            cursor.execute("DELETE FROM setups WHERE id = ?", (setup_id,))
            conn.commit()
            logger.info(f"Setup {setup_id} deleted")
        except Exception as e:
            logger.error(f"Error deleting setup: {e}")
        finally:
            conn.close()

db = Database()

# ============================================================================
# BOT SETUP
# ============================================================================

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.guild_messages = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    """Called when bot is ready."""
    logger.info(f"Logged in as {bot.user}")
    print(f"✓ Bot online as {bot.user}")
    
    try:
        synced = await bot.tree.sync()
        logger.info(f"Synced {len(synced)} command(s)")
        print(f"✓ Synced {len(synced)} slash commands")
    except Exception as e:
        logger.error(f"Failed to sync commands: {e}")

# ============================================================================
# SERVER CREATOR
# ============================================================================

class ServerCreator:
    """Creates Discord server elements with advanced configuration."""
    
    @staticmethod
    async def create_roles(guild: discord.Guild, roles: List[Dict]) -> Tuple[List[discord.Role], List[str]]:
        """Create roles with colors and permissions."""
        created_roles = []
        errors = []
        existing_roles = {role.name.lower() for role in guild.roles}
        
        for role_data in roles:
            try:
                role_name = role_data.get("name", "").strip()
                
                if not role_name or role_name.lower() in existing_roles:
                    continue
                
                color = role_data.get("color", discord.Color.default())
                permissions = discord.Permissions()
                
                for perm in role_data.get("permissions", []):
                    if perm == "administrator":
                        permissions.administrator = True
                    elif perm == "manage_messages":
                        permissions.manage_messages = True
                    elif perm == "manage_roles":
                        permissions.manage_roles = True
                    elif perm == "manage_channels":
                        permissions.manage_channels = True
                    elif perm == "manage_guild":
                        permissions.manage_guild = True
                    elif perm == "kick_members":
                        permissions.kick_members = True
                    elif perm == "ban_members":
                        permissions.ban_members = True
                
                new_role = await guild.create_role(
                    name=role_name,
                    permissions=permissions,
                    color=color,
                    reason="Server setup by user"
                )
                
                created_roles.append(new_role)
                existing_roles.add(role_name.lower())
                logger.info(f"Created role: {role_name}")
                
            except discord.Forbidden:
                errors.append(f"Failed: No permission to create role '{role_name}'")
            except Exception as e:
                errors.append(f"Failed: Role creation error")
        
        return created_roles, errors
    
    @staticmethod
    async def create_categories_and_channels(
        guild: discord.Guild,
        categories: List[Dict],
        created_roles: List[discord.Role]
    ) -> Tuple[List[Tuple], List[str]]:
        """Create categories and channels with permissions and read-only settings."""
        created_structure = []
        errors = []
        existing_channels = {channel.name.lower() for channel in guild.channels}
        
        # Find admin and everyone roles
        admin_role = discord.utils.find(lambda r: r.name in ["Owner", "Admin"], guild.roles)
        everyone_role = guild.default_role
        
        for category_data in categories:
            try:
                category_name = category_data.get("name", "").strip()
                
                if not category_name:
                    continue
                
                category = await guild.create_category(
                    name=category_name,
                    reason="Server setup by user"
                )
                
                created_channels = []
                
                for channel_data in category_data.get("channels", []):
                    try:
                        channel_name = channel_data.get("name", "").strip()
                        channel_type = channel_data.get("type", "text").lower()
                        is_read_only = channel_data.get("read_only", False)
                        is_admin_only = channel_data.get("admin_only", False)
                        
                        if not channel_name or channel_type not in ["text", "voice"]:
                            continue
                        
                        if channel_name.lower() in existing_channels:
                            errors.append(f"Skipped: Channel '{channel_name}' already exists")
                            continue
                        
                        # Create channel
                        if channel_type == "voice":
                            channel = await guild.create_voice_channel(
                                name=channel_name,
                                category=category,
                                reason="Server setup by user"
                            )
                        else:
                            channel = await guild.create_text_channel(
                                name=channel_name,
                                category=category,
                                reason="Server setup by user"
                            )
                        
                        # Set permissions
                        overwrites = {}
                        
                        if is_admin_only and admin_role:
                            # Admin only: deny everyone, allow admin
                            overwrites[everyone_role] = discord.PermissionOverwrite(view_channel=False)
                            overwrites[admin_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, connect=True)
                        elif is_read_only:
                            # Read only: everyone can view but not send/write
                            if channel_type == "text":
                                overwrites[everyone_role] = discord.PermissionOverwrite(send_messages=False, send_tts_messages=False)
                            elif channel_type == "voice":
                                # Voice read-only = can't connect
                                overwrites[everyone_role] = discord.PermissionOverwrite(connect=False)
                        
                        if overwrites:
                            await channel.edit(overwrites=overwrites)
                        
                        created_channels.append(channel)
                        existing_channels.add(channel_name.lower())
                        logger.info(f"Created {channel_type} channel: {channel_name}")
                        
                    except Exception as e:
                        errors.append(f"Failed: Channel '{channel_data.get('name')}' creation error")
                
                created_structure.append((category, created_channels))
                
            except Exception as e:
                errors.append(f"Failed: Category creation error")
        
        return created_structure, errors
    
    @staticmethod
    async def delete_roles(guild: discord.Guild, role_ids: List[int]) -> Tuple[int, int]:
        """Delete roles."""
        deleted = 0
        skipped = 0
        
        for role_id in role_ids:
            try:
                role = guild.get_role(role_id)
                if not role:
                    skipped += 1
                    continue
                
                await role.delete(reason="Undo setup")
                deleted += 1
                logger.info(f"Deleted role: {role.name}")
            except Exception as e:
                skipped += 1
        
        return deleted, skipped
    
    @staticmethod
    async def delete_channels(guild: discord.Guild, channel_ids: List[int]) -> Tuple[int, int]:
        """Delete channels and remove empty categories."""
        deleted = 0
        skipped = 0
        
        for channel_id in channel_ids:
            try:
                channel = guild.get_channel(channel_id)
                if not channel:
                    skipped += 1
                    continue
                
                # Remember category before deletion
                category = channel.category
                
                await channel.delete(reason="Undo setup")
                deleted += 1
                logger.info(f"Deleted channel: {channel.name}")
                
                # Delete category if empty
                if category and not category.channels:
                    try:
                        await category.delete(reason="Undo setup - empty category")
                        logger.info(f"Deleted empty category: {category.name}")
                    except Exception as e:
                        logger.debug(f"Could not delete category: {e}")
                        
            except Exception as e:
                skipped += 1
        
        return deleted, skipped
    
    @staticmethod
    async def organize_channels(guild: discord.Guild, created_structure: List[Tuple]) -> None:
        """Reorder categories and channels by importance/usage frequency."""
        try:
            # Priority order (importance/usage frequency)
            priority_keywords = {
                "announcements": 0,
                "rules": 1,
                "general": 2,
                "questions": 3,
                "discussion": 4,
                "introductions": 5,
                "voice": 6,
                "lounge": 7,
                "hangout": 8,
                "off-topic": 9,
                "admin": 10,
                "mod": 10,
                "logs": 10,
                "report": 10,
            }
            
            # Get all categories in guild
            categories = guild.categories
            
            # Sort categories by position in created_structure and keywords
            category_priority = {}
            for idx, (category, channels) in enumerate(created_structure):
                # Base priority from creation order
                priority = idx * 10
                
                # Boost announcements, general, and community categories
                cat_name_lower = category.name.lower()
                if "announcement" in cat_name_lower:
                    priority -= 1000
                elif "general" in cat_name_lower or "community" in cat_name_lower:
                    priority -= 900
                elif "discussion" in cat_name_lower:
                    priority -= 800
                elif "voice" in cat_name_lower or "hangout" in cat_name_lower:
                    priority -= 700
                elif "management" in cat_name_lower or "admin" in cat_name_lower or "moderation" in cat_name_lower:
                    priority += 500
                
                category_priority[category.id] = priority
            
            # Reorder categories
            sorted_cats = sorted(category_priority.items(), key=lambda x: x[1])
            for new_position, (cat_id, _) in enumerate(sorted_cats):
                category = guild.get_channel(cat_id)
                if category and isinstance(category, discord.CategoryChannel):
                    try:
                        await category.edit(position=new_position, reason="Organizing by importance")
                        logger.info(f"Moved category {category.name} to position {new_position}")
                    except Exception as e:
                        logger.debug(f"Could not reorder category: {e}")
            
            # Reorder channels within categories
            for category, channels in created_structure:
                channel_priority = {}
                
                for idx, channel in enumerate(channels):
                    # Base priority from creation order
                    priority = idx * 10
                    
                    channel_name_lower = channel.name.lower()
                    
                    # Apply keyword priorities
                    for keyword, priority_val in priority_keywords.items():
                        if keyword in channel_name_lower:
                            priority = priority_val
                            break
                    
                    channel_priority[channel.id] = priority
                
                # Reorder channels
                sorted_channels = sorted(channel_priority.items(), key=lambda x: x[1])
                for new_position, (ch_id, _) in enumerate(sorted_channels):
                    channel = guild.get_channel(ch_id)
                    if channel and channel.category == category:
                        try:
                            await channel.edit(position=new_position, reason="Organizing by importance")
                            logger.info(f"Moved channel {channel.name} to position {new_position}")
                        except Exception as e:
                            logger.debug(f"Could not reorder channel: {e}")
        
        except Exception as e:
            logger.error(f"Error organizing channels: {e}")

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def update_progress(message: discord.Message, status: str, step: int, total_steps: int):
    """Update progress embed."""
    embed = discord.Embed(
        title="🔧 Server Setup in Progress",
        description=status,
        color=BOT_COLOR
    )
    
    steps = [
        "👥 Creating Roles",
        "📂 Creating Categories",
        "📨 Creating Channels",
        "🔐 Setting Permissions",
        "✅ Finalizing"
    ]
    
    progress_text = ""
    for i, step_name in enumerate(steps[:total_steps]):
        if i < step:
            progress_text += f"✅ {step_name}\n"
        elif i == step:
            progress_text += f"⏳ {step_name}\n"
        else:
            progress_text += f"⏬ {step_name}\n"
    
    embed.add_field(name="Progress", value=progress_text, inline=False)
    
    try:
        await message.edit(embed=embed)
    except discord.HTTPException:
        logger.warning("Failed to update progress")

async def send_error(message: discord.Message, title: str, description: str):
    """Send error embed."""
    embed = discord.Embed(
        title=f"❌ {title}",
        description=description,
        color=discord.Color.red()
    )
    try:
        await message.edit(embed=embed)
    except discord.HTTPException:
        logger.warning("Failed to send error")

# ============================================================================
# TEMPLATE SELECT
# ============================================================================

class TemplateSelect(discord.ui.Select):
    """Select menu for templates."""
    
    def __init__(self):
        options = [
            discord.SelectOption(label="Professional", value="Professional", emoji="💼", description="Business workspace"),
            discord.SelectOption(label="Gaming Community", value="Gaming Community", emoji="🎮", description="Gaming guild setup"),
            discord.SelectOption(label="Content Creator", value="Content Creator", emoji="🎬", description="Creator hub"),
            discord.SelectOption(label="Community Server", value="Community Server", emoji="👥", description="Social community"),
            discord.SelectOption(label="Education", value="Education", emoji="📚", description="Learning platform"),
            discord.SelectOption(label="Startup", value="Startup", emoji="🚀", description="Fast-paced startup"),
            discord.SelectOption(label="Hobby & Interests", value="Hobby & Interests", emoji="🎨", description="Hobby community"),
        ]
        super().__init__(placeholder="Choose a template...", min_values=1, max_values=1, options=options)
    
    async def callback(self, interaction: discord.Interaction):
        """Handle template selection."""
        template_name = self.values[0]
        template = TEMPLATES.get(template_name)
        
        if not template:
            await interaction.response.send_message("Template not found.", ephemeral=True)
            return
        
        await interaction.response.defer()
        
        setup_id = db.save_setup(
            interaction.guild.id,
            interaction.user.id,
            template_name
        )
        
        if not setup_id:
            await interaction.response.send_message("❌ Failed to save setup.", ephemeral=True)
            return
        
        progress_embed = discord.Embed(title="🔧 Setting Up Template", color=BOT_COLOR)
        progress_message = await interaction.followup.send(embed=progress_embed)
        
        try:
            await update_progress(progress_message, "👥 Creating Roles...", 0, 6)
            
            created_roles, role_errors = await ServerCreator.create_roles(
                interaction.guild,
                template.get("roles", [])
            )
            
            for role in created_roles:
                db.add_role(setup_id, interaction.guild.id, role.id, role.name)
            
            await update_progress(progress_message, "📂 Creating Categories...", 1, 6)
            
            created_structure, channel_errors = await ServerCreator.create_categories_and_channels(
                interaction.guild,
                template.get("categories", []),
                created_roles
            )
            
            for category, channels in created_structure:
                for channel in channels:
                    db.add_channel(
                        setup_id,
                        interaction.guild.id,
                        channel.id,
                        channel.name,
                        "voice" if isinstance(channel, discord.VoiceChannel) else "text"
                    )
            
            await update_progress(progress_message, "🔄 Organizing Server...", 4, 6)
            
            # Reorder categories and channels by importance/usage
            await ServerCreator.organize_channels(interaction.guild, created_structure)
            
            await update_progress(progress_message, "✅ Setup Complete!", 5, 6)
            
            summary_embed = discord.Embed(
                title="✅ Server Setup Complete!",
                description=f"Set up **{template_name}** template",
                color=discord.Color.green()
            )
            
            summary_embed.add_field(
                name="📊 Summary",
                value=f"**Roles Created:** {len(created_roles)}\n"
                      f"**Categories Created:** {len(created_structure)}\n"
                      f"**Channels Created:** {sum(len(channels) for _, channels in created_structure)}",
                inline=False
            )
            
            if role_errors or channel_errors:
                all_errors = role_errors + channel_errors
                error_text = "\n".join(all_errors[:3])
                if len(all_errors) > 3:
                    error_text += f"\n... and {len(all_errors) - 3} more"
                summary_embed.add_field(name="⚠️ Notes", value=error_text, inline=False)
            
            summary_embed.add_field(
                name="✨ Features",
                value="✓ Read-only announcement channels\n"
                      "✓ Admin-only management channels\n"
                      "✓ Custom role colors and permissions\n"
                      "✓ Auto-organized by usage\n"
                      "✓ Professional structure",
                inline=False
            )
            
            summary_embed.add_field(
                name="🔄 Other Commands",
                value="• `/undo_setup` - Remove all created elements\n"
                      "• `/show_templates` - Browse templates again",
                inline=False
            )
            
            summary_embed.set_footer(text=f"Setup by {interaction.user}")
            await progress_message.edit(embed=summary_embed)
            
        except Exception as e:
            logger.error(f"Template error: {e}", exc_info=True)
            await send_error(progress_message, "Setup Error", f"Error: {str(e)}")

class TemplateSelectView(discord.ui.View):
    """View for template selection."""
    
    def __init__(self):
        super().__init__()
        self.add_item(TemplateSelect())

# ============================================================================
# COMMANDS
# ============================================================================

@bot.tree.command(
    name="show_templates",
    description="Browse and apply professional Discord server templates."
)
async def show_templates(interaction: discord.Interaction):
    """Show available templates."""
    
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="Only server administrators can use this command.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    embed = discord.Embed(
        title="🎨 Professional Server Templates",
        description="Select a template to instantly set up your server with roles, channels, and permissions.",
        color=BOT_COLOR
    )
    
    embed.add_field(
        name="💼 Professional",
        value="Business workspace with management, teams, announcements, and resources.",
        inline=False
    )
    
    embed.add_field(
        name="🎮 Gaming Community",
        value="Gaming guild with tournaments, streamers, voice channels, and community.",
        inline=False
    )
    
    embed.add_field(
        name="🎬 Content Creator",
        value="Creator hub with sponsorships, community, collaborations, and VODs.",
        inline=False
    )
    
    embed.add_field(
        name="👥 Community Server",
        value="Social community with discussions, events, spotlights, and meetups.",
        inline=False
    )
    
    embed.add_field(
        name="📚 Education",
        value="Learning platform with courses, classrooms, study groups, and tutoring.",
        inline=False
    )
    
    embed.add_field(
        name="🚀 Startup",
        value="Fast-paced startup with product, engineering, growth, and fundraising.",
        inline=False
    )
    
    embed.add_field(
        name="🎨 Hobby & Interests",
        value="Hobby community with discussions, showcases, meetups, and events.",
        inline=False
    )
    
    embed.add_field(
        name="✨ Features",
        value="✓ Pre-configured roles with custom colors\n"
              "✓ Read-only announcement channels\n"
              "✓ Admin-only management channels\n"
              "✓ Auto-organized by importance\n"
              "✓ Professional channel structure",
        inline=False
    )
    
    view = TemplateSelectView()
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

@bot.tree.command(
    name="undo_setup",
    description="Remove channels and roles created by a setup."
)
async def undo_setup(interaction: discord.Interaction):
    """Undo a server setup."""
    
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="Only server administrators can use this command.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    setups = db.get_guild_setups(interaction.guild.id)
    
    if not setups:
        embed = discord.Embed(
            title="❌ No Setups Found",
            description="No server setups have been recorded.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Show setup selection
    embed = discord.Embed(
        title="🔄 Undo Setup",
        description="Select a setup to remove its channels and roles.",
        color=BOT_COLOR
    )
    
    setup_list = ""
    for setup_id, template_name, created_at in setups[:10]:
        setup_list += f"**{template_name}** - {created_at[:10]}\n"
    
    embed.add_field(name="Available Setups", value=setup_list or "No setups", inline=False)
    
    view = SetupSelectView(setups)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# ============================================================================
# REORDER COMMAND - Views and Modals
# ============================================================================

class SetupSelect(discord.ui.Select):
    """Select menu for choosing a setup to undo."""
    
    def __init__(self, setups: list):
        options = []
        for setup_id, template_name, created_at in setups[:25]:
            options.append(
                discord.SelectOption(
                    label=f"{template_name} ({created_at[:10]})",
                    value=str(setup_id),
                    emoji="🗑️"
                )
            )
        
        super().__init__(
            placeholder="Select a setup to undo...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.setups = {setup[0]: setup for setup in setups}
    
    async def callback(self, interaction: discord.Interaction):
        try:
            setup_id = int(self.values[0])
            setup_name = self.setups[setup_id][1]
            
            await interaction.response.defer()
            
            progress_embed = discord.Embed(title="🔄 Undoing Setup...", color=BOT_COLOR)
            progress_message = await interaction.followup.send(embed=progress_embed)
            
            # Get roles and channels for this setup
            created_roles = db.get_created_roles(setup_id)
            created_channels = db.get_created_channels(setup_id)
            
            if not created_roles and not created_channels:
                embed = discord.Embed(
                    title="❌ Nothing to Undo",
                    description=f"No channels or roles found for **{setup_name}**.",
                    color=discord.Color.red()
                )
                await progress_message.edit(embed=embed)
                return
            
            role_ids = [role[0] for role in created_roles]
            channel_ids = [channel[0] for channel in created_channels]
            
            # Delete channels and roles
            channels_deleted, channels_skipped = await ServerCreator.delete_channels(
                interaction.guild,
                channel_ids
            )
            
            roles_deleted, roles_skipped = await ServerCreator.delete_roles(
                interaction.guild,
                role_ids
            )
            
            # Remove from database
            db.delete_setup(setup_id)
            
            summary_embed = discord.Embed(
                title="✅ Setup Undone!",
                description=f"Removed **{setup_name}** setup and all its elements.",
                color=discord.Color.green()
            )
            
            summary_embed.add_field(
                name="📊 Summary",
                value=f"**Channels Deleted:** {channels_deleted}\n"
                      f"**Roles Deleted:** {roles_deleted}\n\n"
                      f"**Channels Skipped:** {channels_skipped}\n"
                      f"**Roles Skipped:** {roles_skipped}",
                inline=False
            )
            
            await progress_message.edit(embed=summary_embed)
            logger.info(f"Setup {setup_id} ({setup_name}) undone in guild {interaction.guild.id}")
            
        except Exception as e:
            logger.error(f"Undo error: {e}", exc_info=True)
            await interaction.response.send_message(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )

class SetupSelectView(discord.ui.View):
    """View for setup selection."""
    
    def __init__(self, setups: list):
        super().__init__()
        self.add_item(SetupSelect(setups))

# ============================================================================
# REORDER COMMAND - Views and Modals
# ============================================================================

class PriorityButton(discord.ui.Button):
    """Button for selecting priority."""
    
    def __init__(self, priority: int, category: discord.CategoryChannel):
        super().__init__(label=str(priority), style=discord.ButtonStyle.primary)
        self.priority = priority
        self.category = category
    
    async def callback(self, interaction: discord.Interaction):
        try:
            position = self.priority - 1
            await self.category.edit(position=position, reason=f"Reorder: Priority {self.priority}")
            
            priority_text = {
                1: "🔴 Most Important",
                2: "🟠 Very Important",
                3: "🟡 Important",
                4: "🟢 Less Important",
                5: "🔵 Least Important"
            }
            
            embed = discord.Embed(
                title="✅ Category Reordered",
                description=f"**{self.category.name}** → Priority {self.priority}",
                color=discord.Color.green()
            )
            
            embed.add_field(name="Level", value=priority_text[self.priority], inline=True)
            embed.add_field(name="Position", value=f"#{position + 1}", inline=True)
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
            logger.info(f"Reordered category {self.category.name} to priority {self.priority}")
            
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ No permission to reorder categories.",
                ephemeral=True
            )
        except Exception as e:
            logger.error(f"Priority button error: {e}", exc_info=True)
            await interaction.response.send_message(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )

class PriorityView(discord.ui.View):
    """View with priority buttons."""
    
    def __init__(self, category: discord.CategoryChannel):
        super().__init__()
        for priority in range(1, 6):
            self.add_item(PriorityButton(priority, category))

class CategorySelect(discord.ui.Select):
    """Select menu for choosing a category to reorder."""
    
    def __init__(self, categories: list):
        options = []
        for i, category in enumerate(categories[:25]):  # Discord limit is 25 options
            options.append(
                discord.SelectOption(
                    label=category.name[:100],
                    value=str(category.id),
                    description=f"{len(category.channels)} channels"
                )
            )
        
        super().__init__(
            placeholder="Select a category to reorder...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction: discord.Interaction):
        try:
            category_id = int(self.values[0])
            category = interaction.guild.get_channel(category_id)
            
            if not category or not isinstance(category, discord.CategoryChannel):
                await interaction.response.send_message(
                    "❌ Category not found.",
                    ephemeral=True
                )
                return
            
            embed = discord.Embed(
                title="📊 Set Category Priority",
                description=f"Select priority for **{category.name}**",
                color=BOT_COLOR
            )
            
            embed.add_field(
                name="Priority Scale",
                value="🔴 **1** = Most Important (top)\n"
                      "🟠 **2** = Very Important\n"
                      "🟡 **3** = Important\n"
                      "🟢 **4** = Less Important\n"
                      "🔵 **5** = Least Important (bottom)",
                inline=False
            )
            
            view = PriorityView(category)
            await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
            
        except Exception as e:
            logger.error(f"CategorySelect callback error: {e}", exc_info=True)
            await interaction.response.send_message(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )

class CategorySelectView(discord.ui.View):
    """View for category selection."""
    
    def __init__(self, categories: list):
        super().__init__()
        self.add_item(CategorySelect(categories))

@bot.tree.command(
    name="reorder",
    description="Reorder categories by importance (1-5)."
)
async def reorder(interaction: discord.Interaction):
    """Reorder server categories by priority."""
    
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="Only server administrators can use this command.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Get all categories in guild
    categories = [c for c in interaction.guild.categories]
    
    if not categories:
        embed = discord.Embed(
            title="❌ No Categories Found",
            description="This server has no categories to reorder.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    embed = discord.Embed(
        title="📊 Reorder Categories",
        description="Select a category and set its priority (1-5)\n\n"
                   "🔴 **1** = Most Important (top)\n"
                   "🟠 **2** = Very Important\n"
                   "🟡 **3** = Important\n"
                   "🟢 **4** = Less Important\n"
                   "🔵 **5** = Least Important (bottom)",
        color=BOT_COLOR
    )
    
    embed.add_field(
        name="Current Order",
        value="\n".join([f"{i+1}. {cat.name}" for i, cat in enumerate(categories[:10])]) 
              or "No categories",
        inline=False
    )
    
    view = CategorySelectView(categories)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# ============================================================================
# DELETE COMMAND
# ============================================================================

class ConfirmDeleteView(discord.ui.View):
    """Confirmation view for deleting all channels."""
    
    def __init__(self, channel_count: int, current_channel_name: str):
        super().__init__()
        self.confirmed = False
        self.channel_count = channel_count
        self.current_channel_name = current_channel_name
    
    @discord.ui.button(label="Confirm Delete", style=discord.ButtonStyle.danger, emoji="🗑️")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = True
        self.stop()
        
        await interaction.response.defer()
        
        progress_embed = discord.Embed(
            title="🔄 Deleting Channels...",
            description=f"Removing {self.channel_count} channels",
            color=BOT_COLOR
        )
        progress_message = await interaction.followup.send(embed=progress_embed)
        
        try:
            deleted = 0
            skipped = 0
            
            # Get all channels except the current one and categories
            channels_to_delete = [
                ch for ch in interaction.guild.channels 
                if ch.id != interaction.channel.id 
                and not isinstance(ch, discord.CategoryChannel)
            ]
            
            for channel in channels_to_delete:
                try:
                    await channel.delete(reason="Mass delete via /delete command")
                    deleted += 1
                    logger.info(f"Deleted channel: {channel.name}")
                except discord.Forbidden:
                    skipped += 1
                    logger.warning(f"Could not delete channel {channel.name} - no permission")
                except Exception as e:
                    skipped += 1
                    logger.error(f"Error deleting channel {channel.name}: {e}")
            
            # Delete empty categories
            categories_deleted = 0
            for category in interaction.guild.categories:
                if not category.channels:
                    try:
                        await category.delete(reason="Empty category after mass delete")
                        categories_deleted += 1
                        logger.info(f"Deleted empty category: {category.name}")
                    except Exception as e:
                        logger.debug(f"Could not delete category {category.name}: {e}")
            
            summary_embed = discord.Embed(
                title="✅ Channels Deleted!",
                description=f"Successfully removed all channels except **#{self.current_channel_name}**",
                color=discord.Color.green()
            )
            
            summary_embed.add_field(
                name="📊 Summary",
                value=f"**Channels Deleted:** {deleted}\n"
                      f"**Categories Deleted:** {categories_deleted}\n"
                      f"**Channels Skipped:** {skipped}",
                inline=False
            )
            
            if skipped > 0:
                summary_embed.add_field(
                    name="⚠️ Note",
                    value=f"{skipped} channels could not be deleted (permission issues)",
                    inline=False
                )
            
            await progress_message.edit(embed=summary_embed)
            
        except Exception as e:
            logger.error(f"Mass delete error: {e}", exc_info=True)
            error_embed = discord.Embed(
                title="❌ Delete Error",
                description=f"Error: {str(e)}",
                color=discord.Color.red()
            )
            await progress_message.edit(embed=error_embed)
    
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary, emoji="❌")
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.confirmed = False
        self.stop()
        
        await interaction.response.defer()
        
        cancel_embed = discord.Embed(
            title="❌ Cancelled",
            description="Channel deletion cancelled.",
            color=discord.Color.red()
        )
        await interaction.followup.send(embed=cancel_embed, ephemeral=True)

@bot.tree.command(
    name="delete",
    description="Delete all channels except the current one."
)
async def delete(interaction: discord.Interaction):
    """Delete all channels except the command channel."""
    
    if not interaction.user.guild_permissions.administrator:
        embed = discord.Embed(
            title="❌ Permission Denied",
            description="Only server administrators can use this command.",
            color=discord.Color.red()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    if not interaction.guild:
        await interaction.response.send_message(
            "❌ This command only works in a server.",
            ephemeral=True
        )
        return
    
    # Count channels to delete
    channels_to_delete = [
        ch for ch in interaction.guild.channels 
        if ch.id != interaction.channel.id 
        and not isinstance(ch, discord.CategoryChannel)
    ]
    
    if not channels_to_delete:
        embed = discord.Embed(
            title="ℹ️ No Channels to Delete",
            description="This is the only channel in the server.",
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    
    # Show confirmation
    embed = discord.Embed(
        title="⚠️ Confirm Channel Deletion",
        description=f"This will permanently delete **{len(channels_to_delete)} channels** (excluding **#{interaction.channel.name}**).",
        color=discord.Color.orange()
    )
    
    channel_list = ", ".join([f"#{ch.name}" for ch in channels_to_delete[:10]])
    if len(channels_to_delete) > 10:
        channel_list += f", and {len(channels_to_delete) - 10} more..."
    
    embed.add_field(name="Channels to Delete", value=channel_list, inline=False)
    embed.add_field(
        name="⚠️ Warning",
        value="This action **cannot be undone**. All messages and data will be lost.",
        inline=False
    )
    
    view = ConfirmDeleteView(len(channels_to_delete), interaction.channel.name)
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

# ============================================================================
# MAIN
# ============================================================================

async def main():
    """Start the bot."""
    async with bot:
        await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
