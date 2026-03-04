"""
Learning Resources Pipeline
Curates YouTube videos and W3Schools tutorials for skill-based learning paths.
Provides endpoints for browsing, searching, and getting AI-recommended resources.
"""

import json
import random
from typing import List, Optional
from pathlib import Path
from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/learning-resources", tags=["Learning Resources"])


# ── YouTube Video & W3Schools Tutorial Data ────────────────────────

YOUTUBE_CATALOG = {
    "Python": [
        {"id": "yt-py-1", "title": "Python Full Course for Beginners", "channel": "Programming with Mosh", "video_id": "kqtD5dpn9C8", "duration": "6:14:07", "level": "Beginner", "views": "30M+"},
        {"id": "yt-py-2", "title": "Learn Python - Full Course for Beginners", "channel": "freeCodeCamp", "video_id": "rfscVS0vtbw", "duration": "4:26:52", "level": "Beginner", "views": "40M+"},
        {"id": "yt-py-3", "title": "Intermediate Python Programming", "channel": "freeCodeCamp", "video_id": "HGOBQPFzWKo", "duration": "5:55:46", "level": "Intermediate", "views": "5M+"},
        {"id": "yt-py-4", "title": "Python OOP Tutorial", "channel": "Corey Schafer", "video_id": "ZDa-Z5JzLYM", "duration": "1:27:00", "level": "Intermediate", "views": "4M+"},
        {"id": "yt-py-5", "title": "Advanced Python - Complete Course", "channel": "NeuralNine", "video_id": "KSiRzuci_6E", "duration": "3:12:00", "level": "Advanced", "views": "1M+"},
    ],
    "JavaScript": [
        {"id": "yt-js-1", "title": "JavaScript Tutorial Full Course", "channel": "Bro Code", "video_id": "lfmg-EJ8gm4", "duration": "12:00:00", "level": "Beginner", "views": "10M+"},
        {"id": "yt-js-2", "title": "JavaScript Crash Course for Beginners", "channel": "Traversy Media", "video_id": "hdI2bqOjy3c", "duration": "1:40:30", "level": "Beginner", "views": "12M+"},
        {"id": "yt-js-3", "title": "JavaScript ES6+ Features", "channel": "The Net Ninja", "video_id": "0Mp2kwE8xY0", "duration": "0:51:00", "level": "Intermediate", "views": "2M+"},
        {"id": "yt-js-4", "title": "Async JavaScript Crash Course", "channel": "Traversy Media", "video_id": "PoRJizFvM7s", "duration": "0:25:36", "level": "Intermediate", "views": "3M+"},
        {"id": "yt-js-5", "title": "JavaScript Design Patterns", "channel": "Fireship", "video_id": "tv-_1er1mWI", "duration": "0:12:21", "level": "Advanced", "views": "2M+"},
    ],
    "React": [
        {"id": "yt-react-1", "title": "React Course for Beginners", "channel": "freeCodeCamp", "video_id": "bMknfKXIFA8", "duration": "11:55:27", "level": "Beginner", "views": "8M+"},
        {"id": "yt-react-2", "title": "React JS Full Course 2024", "channel": "Programming with Mosh", "video_id": "SqcY0GlETPk", "duration": "1:03:50", "level": "Beginner", "views": "5M+"},
        {"id": "yt-react-3", "title": "React Hooks Full Course", "channel": "Codevolution", "video_id": "LlvBzyy-558", "duration": "4:10:00", "level": "Intermediate", "views": "3M+"},
        {"id": "yt-react-4", "title": "React TypeScript Tutorial", "channel": "Codevolution", "video_id": "FJDVKeh7RJI", "duration": "2:15:00", "level": "Intermediate", "views": "1M+"},
        {"id": "yt-react-5", "title": "React Performance Optimization", "channel": "Jack Herrington", "video_id": "KNGsNRbxz6A", "duration": "0:32:00", "level": "Advanced", "views": "500K+"},
    ],
    "Machine Learning": [
        {"id": "yt-ml-1", "title": "Machine Learning Course for Beginners", "channel": "freeCodeCamp", "video_id": "NWONeJKn6kc", "duration": "9:52:19", "level": "Beginner", "views": "4M+"},
        {"id": "yt-ml-2", "title": "Machine Learning with Python", "channel": "Sentdex", "video_id": "OGxgnH8y2NM", "duration": "6:30:00", "level": "Beginner", "views": "5M+"},
        {"id": "yt-ml-3", "title": "Scikit-Learn Course - Machine Learning in Python", "channel": "freeCodeCamp", "video_id": "pqNCD_5r0IU", "duration": "2:54:00", "level": "Intermediate", "views": "2M+"},
        {"id": "yt-ml-4", "title": "Neural Networks from Scratch", "channel": "3Blue1Brown", "video_id": "aircAruvnKk", "duration": "0:19:13", "level": "Advanced", "views": "15M+"},
    ],
    "Data Science": [
        {"id": "yt-ds-1", "title": "Data Science Full Course", "channel": "Simplilearn", "video_id": "-ETQ97mXXF0", "duration": "11:36:00", "level": "Beginner", "views": "7M+"},
        {"id": "yt-ds-2", "title": "Pandas Tutorial - Python Data Analysis", "channel": "Corey Schafer", "video_id": "vmEHCJofslg", "duration": "1:00:00", "level": "Intermediate", "views": "3M+"},
        {"id": "yt-ds-3", "title": "Data Visualization with Matplotlib", "channel": "Sentdex", "video_id": "q7Bo_J8x_dw", "duration": "0:45:00", "level": "Intermediate", "views": "1M+"},
    ],
    "SQL": [
        {"id": "yt-sql-1", "title": "SQL Tutorial - Full Database Course", "channel": "freeCodeCamp", "video_id": "HXV3zeQKqGY", "duration": "4:20:37", "level": "Beginner", "views": "15M+"},
        {"id": "yt-sql-2", "title": "MySQL Full Course for Beginners", "channel": "Bro Code", "video_id": "5OdVJbNCSso", "duration": "3:03:00", "level": "Beginner", "views": "4M+"},
        {"id": "yt-sql-3", "title": "Advanced SQL Tutorial", "channel": "TechTFQ", "video_id": "nWeW3sCmD2k", "duration": "2:00:00", "level": "Advanced", "views": "2M+"},
    ],
    "Docker": [
        {"id": "yt-docker-1", "title": "Docker Tutorial for Beginners", "channel": "TechWorld with Nana", "video_id": "3c-iBn73dDE", "duration": "2:46:14", "level": "Beginner", "views": "7M+"},
        {"id": "yt-docker-2", "title": "Docker Crash Course for Absolute Beginners", "channel": "TechWorld with Nana", "video_id": "pg19Z8LL06w", "duration": "1:07:37", "level": "Beginner", "views": "2M+"},
        {"id": "yt-docker-3", "title": "Docker Compose Tutorial", "channel": "NetworkChuck", "video_id": "DM65_JyGxCo", "duration": "0:22:00", "level": "Intermediate", "views": "1M+"},
    ],
    "Node.js": [
        {"id": "yt-node-1", "title": "Node.js Full Course for Beginners", "channel": "freeCodeCamp", "video_id": "Oe421EPjeBE", "duration": "8:16:00", "level": "Beginner", "views": "6M+"},
        {"id": "yt-node-2", "title": "Node.js Crash Course", "channel": "Traversy Media", "video_id": "fBNz5xF-Kx4", "duration": "1:30:00", "level": "Beginner", "views": "4M+"},
        {"id": "yt-node-3", "title": "Express.js Full Course", "channel": "freeCodeCamp", "video_id": "nH9E25nkk3I", "duration": "3:30:00", "level": "Intermediate", "views": "1M+"},
    ],
    "TypeScript": [
        {"id": "yt-ts-1", "title": "TypeScript Full Course for Beginners", "channel": "Dave Gray", "video_id": "gieEQFIfgYc", "duration": "8:04:29", "level": "Beginner", "views": "3M+"},
        {"id": "yt-ts-2", "title": "TypeScript Crash Course", "channel": "Traversy Media", "video_id": "BCg4U1FzODs", "duration": "0:53:00", "level": "Beginner", "views": "5M+"},
        {"id": "yt-ts-3", "title": "Advanced TypeScript", "channel": "Matt Pocock", "video_id": "F2Z5eFrNLms", "duration": "1:45:00", "level": "Advanced", "views": "800K+"},
    ],
    "CSS": [
        {"id": "yt-css-1", "title": "CSS Tutorial - Full Course for Beginners", "channel": "freeCodeCamp", "video_id": "OXGznpKZ_sA", "duration": "11:08:00", "level": "Beginner", "views": "9M+"},
        {"id": "yt-css-2", "title": "CSS Flexbox in 15 Minutes", "channel": "Web Dev Simplified", "video_id": "fYq5PXgSsbE", "duration": "0:15:21", "level": "Intermediate", "views": "3M+"},
        {"id": "yt-css-3", "title": "CSS Grid Tutorial", "channel": "Fireship", "video_id": "uuOXPWCh-6o", "duration": "0:13:36", "level": "Intermediate", "views": "2M+"},
    ],
    "HTML": [
        {"id": "yt-html-1", "title": "HTML Full Course for Beginners", "channel": "Dave Gray", "video_id": "mJgBOIoGihA", "duration": "4:10:00", "level": "Beginner", "views": "4M+"},
        {"id": "yt-html-2", "title": "HTML Crash Course For Absolute Beginners", "channel": "Traversy Media", "video_id": "UB1O30fR-EE", "duration": "1:00:00", "level": "Beginner", "views": "10M+"},
    ],
    "Git": [
        {"id": "yt-git-1", "title": "Git and GitHub for Beginners - Crash Course", "channel": "freeCodeCamp", "video_id": "RGOj5yH7evk", "duration": "1:08:29", "level": "Beginner", "views": "5M+"},
        {"id": "yt-git-2", "title": "Git Tutorial for Beginners", "channel": "Programming with Mosh", "video_id": "8JJ101D3knE", "duration": "1:09:14", "level": "Beginner", "views": "6M+"},
    ],
    "Neo4j": [
        {"id": "yt-neo4j-1", "title": "Neo4j Graph Database Tutorial", "channel": "freeCodeCamp", "video_id": "8jNPelugC2s", "duration": "2:00:00", "level": "Beginner", "views": "500K+"},
        {"id": "yt-neo4j-2", "title": "Getting Started with Neo4j", "channel": "Neo4j", "video_id": "bPM9hVorPSM", "duration": "0:35:00", "level": "Beginner", "views": "200K+"},
    ],
    "Apache Spark": [
        {"id": "yt-spark-1", "title": "Apache Spark Full Course", "channel": "Simplilearn", "video_id": "_C8kWso4ne4", "duration": "5:30:00", "level": "Beginner", "views": "2M+"},
        {"id": "yt-spark-2", "title": "PySpark Tutorial", "channel": "freeCodeCamp", "video_id": "_jPF0clBqps", "duration": "3:00:00", "level": "Intermediate", "views": "800K+"},
    ],
    "FastAPI": [
        {"id": "yt-fastapi-1", "title": "FastAPI Full Course", "channel": "freeCodeCamp", "video_id": "tLKKmouUams", "duration": "5:22:00", "level": "Beginner", "views": "1M+"},
        {"id": "yt-fastapi-2", "title": "FastAPI - A Python Framework", "channel": "TechWorld with Nana", "video_id": "XnYYwcOfcn8", "duration": "1:00:00", "level": "Beginner", "views": "300K+"},
    ],

    # ── Finance & Accounting ──
    "Financial Analysis": [
        {"id": "yt-fin-1", "title": "Financial Analysis Course for Beginners", "channel": "Corporate Finance Institute", "video_id": "JI-mVHod32g", "duration": "4:30:00", "level": "Beginner", "views": "3M+"},
        {"id": "yt-fin-2", "title": "Financial Modeling & Valuation", "channel": "Aswath Damodaran", "video_id": "znmQ7oMiQrM", "duration": "2:15:00", "level": "Intermediate", "views": "2M+"},
        {"id": "yt-fin-3", "title": "Investment Banking Explained", "channel": "The Plain Bagel", "video_id": "KcrJkpWPAME", "duration": "0:18:00", "level": "Beginner", "views": "1M+"},
    ],
    "Accounting": [
        {"id": "yt-acc-1", "title": "Accounting Basics Explained", "channel": "Accounting Stuff", "video_id": "yYX4bvQSqbo", "duration": "0:33:00", "level": "Beginner", "views": "4M+"},
        {"id": "yt-acc-2", "title": "Financial Accounting Full Course", "channel": "freeCodeCamp", "video_id": "ldiAyJbMJgM", "duration": "8:40:00", "level": "Beginner", "views": "2M+"},
        {"id": "yt-acc-3", "title": "Advanced Financial Statements", "channel": "Accounting Stuff", "video_id": "Q8iGJoGTrLQ", "duration": "0:45:00", "level": "Intermediate", "views": "1M+"},
    ],

    # ── Marketing & Communications ──
    "Digital Marketing": [
        {"id": "yt-dm-1", "title": "Digital Marketing Full Course", "channel": "Simplilearn", "video_id": "nU-IIXBWlS4", "duration": "11:32:00", "level": "Beginner", "views": "8M+"},
        {"id": "yt-dm-2", "title": "SEO Tutorial for Beginners", "channel": "Ahrefs", "video_id": "DvwS7cV9GmQ", "duration": "2:10:00", "level": "Beginner", "views": "5M+"},
        {"id": "yt-dm-3", "title": "Social Media Marketing Strategy", "channel": "HubSpot Marketing", "video_id": "rXRpoFhTZZE", "duration": "0:42:00", "level": "Intermediate", "views": "2M+"},
        {"id": "yt-dm-4", "title": "Google Ads Full Course", "channel": "Surfside PPC", "video_id": "oQw8pn-xgZY", "duration": "3:15:00", "level": "Intermediate", "views": "1M+"},
    ],
    "Content Marketing": [
        {"id": "yt-cm-1", "title": "Content Marketing Strategy", "channel": "Neil Patel", "video_id": "8hu3PYLsTn0", "duration": "0:22:00", "level": "Beginner", "views": "1M+"},
        {"id": "yt-cm-2", "title": "Copywriting Full Course", "channel": "Alex Cattoni", "video_id": "9xbKCMjzY44", "duration": "1:45:00", "level": "Intermediate", "views": "2M+"},
    ],

    # ── Design & Creative ──
    "Graphic Design": [
        {"id": "yt-gd-1", "title": "Graphic Design Full Course", "channel": "Envato Tuts+", "video_id": "9QTCvayLhCA", "duration": "7:00:00", "level": "Beginner", "views": "3M+"},
        {"id": "yt-gd-2", "title": "Adobe Photoshop Tutorial", "channel": "Envato Tuts+", "video_id": "IyR_uYsRdPs", "duration": "3:30:00", "level": "Beginner", "views": "5M+"},
        {"id": "yt-gd-3", "title": "Logo Design Masterclass", "channel": "Will Paterson", "video_id": "ZLoJMkGCdKU", "duration": "1:20:00", "level": "Intermediate", "views": "2M+"},
    ],
    "UX Design": [
        {"id": "yt-ux-1", "title": "UX Design Course for Beginners", "channel": "Google Career Certificates", "video_id": "uL2ZB7XXIgg", "duration": "5:00:00", "level": "Beginner", "views": "4M+"},
        {"id": "yt-ux-2", "title": "Figma Tutorial for Beginners", "channel": "Flux Academy", "video_id": "kbZejnPXyLM", "duration": "2:30:00", "level": "Beginner", "views": "3M+"},
        {"id": "yt-ux-3", "title": "Advanced UI Design Patterns", "channel": "DesignCourse", "video_id": "HlBMp1yV34s", "duration": "0:35:00", "level": "Advanced", "views": "800K+"},
    ],

    # ── Healthcare & Medicine ──
    "Medical Sciences": [
        {"id": "yt-med-1", "title": "Human Anatomy Full Course", "channel": "Ninja Nerd", "video_id": "h31a5lXoZ24", "duration": "12:00:00", "level": "Beginner", "views": "6M+"},
        {"id": "yt-med-2", "title": "Pharmacology Made Easy", "channel": "Simple Nursing", "video_id": "pSK9pOYq1BI", "duration": "2:00:00", "level": "Intermediate", "views": "3M+"},
        {"id": "yt-med-3", "title": "Clinical Research Fundamentals", "channel": "CITI Program", "video_id": "j2FbRC_F7NU", "duration": "1:15:00", "level": "Beginner", "views": "500K+"},
    ],
    "Public Health": [
        {"id": "yt-ph-1", "title": "Introduction to Public Health", "channel": "Greg Martin", "video_id": "wLF2eFEJNRg", "duration": "1:30:00", "level": "Beginner", "views": "1M+"},
        {"id": "yt-ph-2", "title": "Epidemiology Explained", "channel": "Khan Academy", "video_id": "RYEo__JQfnI", "duration": "0:45:00", "level": "Intermediate", "views": "800K+"},
    ],

    # ── Business & Management ──
    "Project Management": [
        {"id": "yt-pm-1", "title": "Project Management Full Course", "channel": "Google Career Certificates", "video_id": "uWPIsaYpY7U", "duration": "6:40:00", "level": "Beginner", "views": "5M+"},
        {"id": "yt-pm-2", "title": "Agile Project Management", "channel": "Simplilearn", "video_id": "thsFsPnUHRA", "duration": "4:00:00", "level": "Intermediate", "views": "2M+"},
        {"id": "yt-pm-3", "title": "PMP Certification Prep", "channel": "Vargas Management", "video_id": "GC7pN8Mjot8", "duration": "3:30:00", "level": "Advanced", "views": "3M+"},
    ],
    "Business Strategy": [
        {"id": "yt-bs-1", "title": "Business Strategy Explained", "channel": "Harvard Business Review", "video_id": "iuYlGRnC7J8", "duration": "0:30:00", "level": "Beginner", "views": "2M+"},
        {"id": "yt-bs-2", "title": "MBA Full Course - Business Management", "channel": "freeCodeCamp", "video_id": "MijZq6q7KNc", "duration": "8:00:00", "level": "Intermediate", "views": "4M+"},
    ],
    "Entrepreneurship": [
        {"id": "yt-ent-1", "title": "How to Start a Business", "channel": "Ali Abdaal", "video_id": "8rHF6MCt4Rg", "duration": "0:35:00", "level": "Beginner", "views": "3M+"},
        {"id": "yt-ent-2", "title": "Startup Funding Explained", "channel": "Y Combinator", "video_id": "tKesSCBGbtA", "duration": "0:28:00", "level": "Intermediate", "views": "2M+"},
    ],

    # ── Legal ──
    "Business Law": [
        {"id": "yt-law-1", "title": "Business Law 101", "channel": "The Business Professor", "video_id": "z5VBMkJmEz0", "duration": "3:00:00", "level": "Beginner", "views": "1M+"},
        {"id": "yt-law-2", "title": "Contract Law Explained", "channel": "The Law Simplified", "video_id": "B62rMCBfpKE", "duration": "1:20:00", "level": "Intermediate", "views": "800K+"},
    ],
    "Intellectual Property": [
        {"id": "yt-ip-1", "title": "Intellectual Property Law Crash Course", "channel": "CrashCourse", "video_id": "RQOJgEA5e1k", "duration": "0:42:00", "level": "Beginner", "views": "2M+"},
    ],

    # ── Communication & Soft Skills ──
    "Public Speaking": [
        {"id": "yt-ps-1", "title": "Public Speaking Full Course", "channel": "TED", "video_id": "HAnw168huqA", "duration": "1:30:00", "level": "Beginner", "views": "10M+"},
        {"id": "yt-ps-2", "title": "How to Speak So People Want to Listen", "channel": "TED", "video_id": "eIho2S0ZahI", "duration": "0:10:00", "level": "Beginner", "views": "40M+"},
    ],
    "Leadership": [
        {"id": "yt-lead-1", "title": "Leadership Skills for Managers", "channel": "Brian Tracy", "video_id": "pYKH2uSax8o", "duration": "1:45:00", "level": "Intermediate", "views": "5M+"},
        {"id": "yt-lead-2", "title": "Emotional Intelligence at Work", "channel": "TED", "video_id": "n9h8fG1DKhA", "duration": "0:18:00", "level": "Beginner", "views": "8M+"},
    ],

    # ── Education & Teaching ──
    "Instructional Design": [
        {"id": "yt-id-1", "title": "Instructional Design Full Course", "channel": "Devlin Peck", "video_id": "Q8wYLlhnZE0", "duration": "3:00:00", "level": "Beginner", "views": "500K+"},
        {"id": "yt-id-2", "title": "Creating Effective eLearning", "channel": "Tim Slade", "video_id": "k58AaK3WRQI", "duration": "1:00:00", "level": "Intermediate", "views": "300K+"},
    ],

    # ── Environmental & Sustainability ──
    "Sustainability": [
        {"id": "yt-sust-1", "title": "Sustainability in Business", "channel": "MIT OpenCourseWare", "video_id": "zx04Kl8y4dE", "duration": "1:30:00", "level": "Beginner", "views": "1M+"},
        {"id": "yt-sust-2", "title": "Environmental Science Full Course", "channel": "CrashCourse", "video_id": "GK_vRtHJZu4", "duration": "5:00:00", "level": "Beginner", "views": "3M+"},
    ],
}

W3SCHOOLS_CATALOG = {
    "Python": [
        {"id": "w3-py-1", "title": "Python Tutorial", "url": "https://www.w3schools.com/python/", "topic": "Full Course", "level": "Beginner"},
        {"id": "w3-py-2", "title": "Python Data Types", "url": "https://www.w3schools.com/python/python_datatypes.asp", "topic": "Data Types", "level": "Beginner"},
        {"id": "w3-py-3", "title": "Python Functions", "url": "https://www.w3schools.com/python/python_functions.asp", "topic": "Functions", "level": "Beginner"},
        {"id": "w3-py-4", "title": "Python Classes/Objects", "url": "https://www.w3schools.com/python/python_classes.asp", "topic": "OOP", "level": "Intermediate"},
        {"id": "w3-py-5", "title": "Python File Handling", "url": "https://www.w3schools.com/python/python_file_handling.asp", "topic": "File I/O", "level": "Intermediate"},
        {"id": "w3-py-6", "title": "Python RegEx", "url": "https://www.w3schools.com/python/python_regex.asp", "topic": "Regex", "level": "Intermediate"},
        {"id": "w3-py-7", "title": "Python Try Except", "url": "https://www.w3schools.com/python/python_try_except.asp", "topic": "Error Handling", "level": "Beginner"},
        {"id": "w3-py-8", "title": "Python JSON", "url": "https://www.w3schools.com/python/python_json.asp", "topic": "JSON", "level": "Intermediate"},
    ],
    "JavaScript": [
        {"id": "w3-js-1", "title": "JavaScript Tutorial", "url": "https://www.w3schools.com/js/", "topic": "Full Course", "level": "Beginner"},
        {"id": "w3-js-2", "title": "JavaScript Functions", "url": "https://www.w3schools.com/js/js_functions.asp", "topic": "Functions", "level": "Beginner"},
        {"id": "w3-js-3", "title": "JavaScript Objects", "url": "https://www.w3schools.com/js/js_objects.asp", "topic": "Objects", "level": "Beginner"},
        {"id": "w3-js-4", "title": "JavaScript Async", "url": "https://www.w3schools.com/js/js_asynchronous.asp", "topic": "Async", "level": "Intermediate"},
        {"id": "w3-js-5", "title": "JavaScript AJAX", "url": "https://www.w3schools.com/js/js_ajax_intro.asp", "topic": "AJAX", "level": "Intermediate"},
        {"id": "w3-js-6", "title": "JavaScript JSON", "url": "https://www.w3schools.com/js/js_json.asp", "topic": "JSON", "level": "Intermediate"},
    ],
    "React": [
        {"id": "w3-react-1", "title": "React Tutorial", "url": "https://www.w3schools.com/react/", "topic": "Full Course", "level": "Beginner"},
        {"id": "w3-react-2", "title": "React JSX", "url": "https://www.w3schools.com/react/react_jsx.asp", "topic": "JSX", "level": "Beginner"},
        {"id": "w3-react-3", "title": "React Components", "url": "https://www.w3schools.com/react/react_components.asp", "topic": "Components", "level": "Beginner"},
        {"id": "w3-react-4", "title": "React Hooks", "url": "https://www.w3schools.com/react/react_hooks.asp", "topic": "Hooks", "level": "Intermediate"},
        {"id": "w3-react-5", "title": "React Router", "url": "https://www.w3schools.com/react/react_router.asp", "topic": "Routing", "level": "Intermediate"},
    ],
    "SQL": [
        {"id": "w3-sql-1", "title": "SQL Tutorial", "url": "https://www.w3schools.com/sql/", "topic": "Full Course", "level": "Beginner"},
        {"id": "w3-sql-2", "title": "SQL SELECT", "url": "https://www.w3schools.com/sql/sql_select.asp", "topic": "Queries", "level": "Beginner"},
        {"id": "w3-sql-3", "title": "SQL JOIN", "url": "https://www.w3schools.com/sql/sql_join.asp", "topic": "Joins", "level": "Intermediate"},
        {"id": "w3-sql-4", "title": "SQL GROUP BY", "url": "https://www.w3schools.com/sql/sql_groupby.asp", "topic": "Aggregation", "level": "Intermediate"},
    ],
    "CSS": [
        {"id": "w3-css-1", "title": "CSS Tutorial", "url": "https://www.w3schools.com/css/", "topic": "Full Course", "level": "Beginner"},
        {"id": "w3-css-2", "title": "CSS Flexbox", "url": "https://www.w3schools.com/css/css3_flexbox.asp", "topic": "Flexbox", "level": "Intermediate"},
        {"id": "w3-css-3", "title": "CSS Grid", "url": "https://www.w3schools.com/css/css_grid.asp", "topic": "Grid", "level": "Intermediate"},
        {"id": "w3-css-4", "title": "CSS Animations", "url": "https://www.w3schools.com/css/css3_animations.asp", "topic": "Animations", "level": "Intermediate"},
    ],
    "HTML": [
        {"id": "w3-html-1", "title": "HTML Tutorial", "url": "https://www.w3schools.com/html/", "topic": "Full Course", "level": "Beginner"},
        {"id": "w3-html-2", "title": "HTML Forms", "url": "https://www.w3schools.com/html/html_forms.asp", "topic": "Forms", "level": "Beginner"},
        {"id": "w3-html-3", "title": "HTML5 Semantic Elements", "url": "https://www.w3schools.com/html/html5_semantic_elements.asp", "topic": "Semantic HTML", "level": "Intermediate"},
    ],
    "Node.js": [
        {"id": "w3-node-1", "title": "Node.js Tutorial", "url": "https://www.w3schools.com/nodejs/", "topic": "Full Course", "level": "Beginner"},
        {"id": "w3-node-2", "title": "Node.js Modules", "url": "https://www.w3schools.com/nodejs/nodejs_modules.asp", "topic": "Modules", "level": "Beginner"},
        {"id": "w3-node-3", "title": "Node.js File System", "url": "https://www.w3schools.com/nodejs/nodejs_filesystem.asp", "topic": "File System", "level": "Intermediate"},
    ],
    "TypeScript": [
        {"id": "w3-ts-1", "title": "TypeScript Tutorial", "url": "https://www.w3schools.com/typescript/", "topic": "Full Course", "level": "Beginner"},
        {"id": "w3-ts-2", "title": "TypeScript Types", "url": "https://www.w3schools.com/typescript/typescript_simple_types.php", "topic": "Types", "level": "Beginner"},
        {"id": "w3-ts-3", "title": "TypeScript Functions", "url": "https://www.w3schools.com/typescript/typescript_functions.php", "topic": "Functions", "level": "Intermediate"},
    ],
    "Git": [
        {"id": "w3-git-1", "title": "Git Tutorial", "url": "https://www.w3schools.com/git/", "topic": "Full Course", "level": "Beginner"},
        {"id": "w3-git-2", "title": "Git Branch", "url": "https://www.w3schools.com/git/git_branch.asp", "topic": "Branching", "level": "Intermediate"},
    ],
    "Django": [
        {"id": "w3-django-1", "title": "Django Tutorial", "url": "https://www.w3schools.com/django/", "topic": "Full Course", "level": "Beginner"},
    ],
    "MongoDB": [
        {"id": "w3-mongo-1", "title": "MongoDB Tutorial", "url": "https://www.w3schools.com/mongodb/", "topic": "Full Course", "level": "Beginner"},
    ],
    # ── Non-IT Tutorial Resources (external learning platforms) ──
    "Financial Analysis": [
        {"id": "w3-fin-1", "title": "Financial Statements Explained", "url": "https://www.investopedia.com/terms/f/financial-statements.asp", "topic": "Financial Statements", "level": "Beginner"},
        {"id": "w3-fin-2", "title": "How to Read a Balance Sheet", "url": "https://www.investopedia.com/articles/04/031004.asp", "topic": "Balance Sheet", "level": "Beginner"},
        {"id": "w3-fin-3", "title": "Financial Ratios Guide", "url": "https://www.investopedia.com/financial-ratios-4689817", "topic": "Financial Ratios", "level": "Intermediate"},
    ],
    "Accounting": [
        {"id": "w3-acc-1", "title": "Accounting Basics", "url": "https://www.accountingcoach.com/accounting-basics/explanation", "topic": "Fundamentals", "level": "Beginner"},
        {"id": "w3-acc-2", "title": "Double-Entry Bookkeeping", "url": "https://www.investopedia.com/terms/d/double-entry.asp", "topic": "Bookkeeping", "level": "Beginner"},
    ],
    "Digital Marketing": [
        {"id": "w3-dm-1", "title": "Google Digital Marketing Certification", "url": "https://skillshop.withgoogle.com/", "topic": "Certification", "level": "Beginner"},
        {"id": "w3-dm-2", "title": "SEO Starter Guide", "url": "https://developers.google.com/search/docs/fundamentals/seo-starter-guide", "topic": "SEO", "level": "Beginner"},
        {"id": "w3-dm-3", "title": "HubSpot Marketing Hub Guide", "url": "https://www.hubspot.com/marketing", "topic": "Marketing Automation", "level": "Intermediate"},
    ],
    "Graphic Design": [
        {"id": "w3-gd-1", "title": "Design Principles Guide", "url": "https://www.canva.com/designschool/", "topic": "Design Principles", "level": "Beginner"},
        {"id": "w3-gd-2", "title": "Color Theory Basics", "url": "https://www.interaction-design.org/literature/topics/color-theory", "topic": "Color Theory", "level": "Beginner"},
    ],
    "UX Design": [
        {"id": "w3-ux-1", "title": "UX Design Fundamentals", "url": "https://www.interaction-design.org/courses", "topic": "UX Fundamentals", "level": "Beginner"},
        {"id": "w3-ux-2", "title": "Figma Learn", "url": "https://www.figma.com/resource-library/", "topic": "Figma", "level": "Beginner"},
    ],
    "Project Management": [
        {"id": "w3-pm-1", "title": "Project Management Guide", "url": "https://www.pmi.org/learning", "topic": "PM Fundamentals", "level": "Beginner"},
        {"id": "w3-pm-2", "title": "Agile Methodology Guide", "url": "https://www.atlassian.com/agile", "topic": "Agile", "level": "Intermediate"},
    ],
    "Business Strategy": [
        {"id": "w3-bs-1", "title": "Business Strategy Fundamentals", "url": "https://hbr.org/topic/strategy", "topic": "Strategy", "level": "Intermediate"},
    ],
    "Public Speaking": [
        {"id": "w3-ps-1", "title": "Public Speaking Tips", "url": "https://www.toastmasters.org/resources", "topic": "Speaking Skills", "level": "Beginner"},
    ],
    "Leadership": [
        {"id": "w3-lead-1", "title": "Leadership Development Guide", "url": "https://hbr.org/topic/leadership", "topic": "Leadership", "level": "Intermediate"},
    ],
    "Medical Sciences": [
        {"id": "w3-med-1", "title": "Khan Academy Medicine", "url": "https://www.khanacademy.org/science/health-and-medicine", "topic": "Medical Sciences", "level": "Beginner"},
    ],
    "Sustainability": [
        {"id": "w3-sust-1", "title": "UN Sustainability Goals", "url": "https://sdgs.un.org/goals", "topic": "SDGs", "level": "Beginner"},
    ],
    "Business Law": [
        {"id": "w3-law-1", "title": "Legal Basics for Business", "url": "https://www.law.cornell.edu/wex", "topic": "Business Law", "level": "Beginner"},
    ],
}

# ── Online Courses & Platforms (Free + Paid) ─────────────────────────
COURSES_CATALOG = {
    "Python": [
        {"id": "c-py-1", "title": "Python for Everybody", "platform": "Coursera", "url": "https://www.coursera.org/specializations/python", "instructor": "University of Michigan", "level": "Beginner", "price": "Free", "rating": 4.8, "duration": "8 months"},
        {"id": "c-py-2", "title": "100 Days of Code - Python Pro Bootcamp", "platform": "Udemy", "url": "https://www.udemy.com/course/100-days-of-code/", "instructor": "Dr. Angela Yu", "level": "Beginner", "price": "$13.99", "rating": 4.7, "duration": "60h"},
        {"id": "c-py-3", "title": "Introduction to Computer Science with Python", "platform": "edX", "url": "https://www.edx.org/learn/python/mit-introduction-to-computer-science-and-programming-using-python", "instructor": "MIT", "level": "Beginner", "price": "Free", "rating": 4.9, "duration": "9 weeks"},
        {"id": "c-py-4", "title": "Scientific Computing with Python", "platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/", "instructor": "freeCodeCamp", "level": "Intermediate", "price": "Free", "rating": 4.6, "duration": "300h"},
        {"id": "c-py-5", "title": "Learn Python 3", "platform": "Codecademy", "url": "https://www.codecademy.com/learn/learn-python-3", "instructor": "Codecademy", "level": "Beginner", "price": "Free", "rating": 4.5, "duration": "25h"},
        {"id": "c-py-6", "title": "Python Official Documentation", "platform": "Official Docs", "url": "https://docs.python.org/3/tutorial/", "instructor": "Python.org", "level": "Beginner", "price": "Free", "rating": 4.8, "duration": "Self-paced"},
        {"id": "c-py-7", "title": "Real Python Tutorials", "platform": "Real Python", "url": "https://realpython.com/", "instructor": "Real Python Team", "level": "Intermediate", "price": "Free / $20/mo", "rating": 4.7, "duration": "Self-paced"},
    ],
    "JavaScript": [
        {"id": "c-js-1", "title": "JavaScript Algorithms and Data Structures", "platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/", "instructor": "freeCodeCamp", "level": "Beginner", "price": "Free", "rating": 4.7, "duration": "300h"},
        {"id": "c-js-2", "title": "The Complete JavaScript Course 2024", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-javascript-course/", "instructor": "Jonas Schmedtmann", "level": "Beginner", "price": "$13.99", "rating": 4.8, "duration": "69h"},
        {"id": "c-js-3", "title": "JavaScript MDN Web Docs", "platform": "MDN", "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide", "instructor": "Mozilla", "level": "Beginner", "price": "Free", "rating": 4.9, "duration": "Self-paced"},
        {"id": "c-js-4", "title": "Learn JavaScript", "platform": "Codecademy", "url": "https://www.codecademy.com/learn/introduction-to-javascript", "instructor": "Codecademy", "level": "Beginner", "price": "Free", "rating": 4.5, "duration": "15h"},
        {"id": "c-js-5", "title": "JavaScript.info - The Modern JavaScript Tutorial", "platform": "Official Docs", "url": "https://javascript.info/", "instructor": "Ilya Kantor", "level": "Intermediate", "price": "Free", "rating": 4.8, "duration": "Self-paced"},
    ],
    "React": [
        {"id": "c-react-1", "title": "React - The Complete Guide", "platform": "Udemy", "url": "https://www.udemy.com/course/react-the-complete-guide-incl-redux/", "instructor": "Maximilian Schwarzmüller", "level": "Beginner", "price": "$13.99", "rating": 4.7, "duration": "68h"},
        {"id": "c-react-2", "title": "Front End Development Libraries", "platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/front-end-development-libraries/", "instructor": "freeCodeCamp", "level": "Intermediate", "price": "Free", "rating": 4.6, "duration": "300h"},
        {"id": "c-react-3", "title": "React Official Documentation", "platform": "Official Docs", "url": "https://react.dev/learn", "instructor": "React Team", "level": "Beginner", "price": "Free", "rating": 4.9, "duration": "Self-paced"},
        {"id": "c-react-4", "title": "Learn React", "platform": "Codecademy", "url": "https://www.codecademy.com/learn/react-101", "instructor": "Codecademy", "level": "Beginner", "price": "Free", "rating": 4.5, "duration": "20h"},
        {"id": "c-react-5", "title": "Full Stack Open - React", "platform": "University of Helsinki", "url": "https://fullstackopen.com/en/", "instructor": "University of Helsinki", "level": "Intermediate", "price": "Free", "rating": 4.8, "duration": "Self-paced"},
    ],
    "Machine Learning": [
        {"id": "c-ml-1", "title": "Machine Learning Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/machine-learning-introduction", "instructor": "Andrew Ng / Stanford", "level": "Beginner", "price": "Free", "rating": 4.9, "duration": "3 months"},
        {"id": "c-ml-2", "title": "Machine Learning with Python", "platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/machine-learning-with-python/", "instructor": "freeCodeCamp", "level": "Intermediate", "price": "Free", "rating": 4.6, "duration": "300h"},
        {"id": "c-ml-3", "title": "Machine Learning A-Z", "platform": "Udemy", "url": "https://www.udemy.com/course/machinelearning/", "instructor": "Kirill Eremenko", "level": "Beginner", "price": "$13.99", "rating": 4.5, "duration": "44h"},
        {"id": "c-ml-4", "title": "Practical Deep Learning for Coders", "platform": "fast.ai", "url": "https://course.fast.ai/", "instructor": "Jeremy Howard", "level": "Intermediate", "price": "Free", "rating": 4.9, "duration": "Self-paced"},
        {"id": "c-ml-5", "title": "Machine Learning Crash Course", "platform": "Google", "url": "https://developers.google.com/machine-learning/crash-course", "instructor": "Google", "level": "Beginner", "price": "Free", "rating": 4.7, "duration": "15h"},
    ],
    "Data Science": [
        {"id": "c-ds-1", "title": "Data Science Professional Certificate", "platform": "Coursera", "url": "https://www.coursera.org/professional-certificates/ibm-data-science", "instructor": "IBM", "level": "Beginner", "price": "Free", "rating": 4.6, "duration": "5 months"},
        {"id": "c-ds-2", "title": "Data Analysis with Python", "platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/data-analysis-with-python/", "instructor": "freeCodeCamp", "level": "Intermediate", "price": "Free", "rating": 4.5, "duration": "300h"},
        {"id": "c-ds-3", "title": "Data Scientist Career Path", "platform": "Codecademy", "url": "https://www.codecademy.com/learn/paths/data-science", "instructor": "Codecademy", "level": "Beginner", "price": "$39.99/mo", "rating": 4.6, "duration": "6 months"},
        {"id": "c-ds-4", "title": "Kaggle Learn", "platform": "Kaggle", "url": "https://www.kaggle.com/learn", "instructor": "Kaggle", "level": "Beginner", "price": "Free", "rating": 4.7, "duration": "Self-paced"},
    ],
    "SQL": [
        {"id": "c-sql-1", "title": "Databases and SQL for Data Science", "platform": "Coursera", "url": "https://www.coursera.org/learn/sql-data-science", "instructor": "IBM", "level": "Beginner", "price": "Free", "rating": 4.6, "duration": "6 weeks"},
        {"id": "c-sql-2", "title": "The Complete SQL Bootcamp", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-sql-bootcamp/", "instructor": "Jose Portilla", "level": "Beginner", "price": "$13.99", "rating": 4.7, "duration": "9h"},
        {"id": "c-sql-3", "title": "Learn SQL", "platform": "Codecademy", "url": "https://www.codecademy.com/learn/learn-sql", "instructor": "Codecademy", "level": "Beginner", "price": "Free", "rating": 4.5, "duration": "8h"},
        {"id": "c-sql-4", "title": "SQL Practice on HackerRank", "platform": "HackerRank", "url": "https://www.hackerrank.com/domains/sql", "instructor": "HackerRank", "level": "Intermediate", "price": "Free", "rating": 4.4, "duration": "Self-paced"},
    ],
    "Docker": [
        {"id": "c-docker-1", "title": "Docker Mastery", "platform": "Udemy", "url": "https://www.udemy.com/course/docker-mastery/", "instructor": "Bret Fisher", "level": "Beginner", "price": "$13.99", "rating": 4.7, "duration": "20h"},
        {"id": "c-docker-2", "title": "Docker Official Get Started", "platform": "Official Docs", "url": "https://docs.docker.com/get-started/", "instructor": "Docker Inc.", "level": "Beginner", "price": "Free", "rating": 4.8, "duration": "Self-paced"},
        {"id": "c-docker-3", "title": "Docker for Developers", "platform": "LinkedIn Learning", "url": "https://www.linkedin.com/learning/docker-for-developers-14493163", "instructor": "LinkedIn Learning", "level": "Intermediate", "price": "$29.99/mo", "rating": 4.5, "duration": "3h"},
    ],
    "Node.js": [
        {"id": "c-node-1", "title": "The Complete Node.js Developer Course", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-nodejs-developer-course-2/", "instructor": "Andrew Mead", "level": "Beginner", "price": "$13.99", "rating": 4.7, "duration": "35h"},
        {"id": "c-node-2", "title": "Node.js Official Docs", "platform": "Official Docs", "url": "https://nodejs.org/en/learn", "instructor": "Node.js Foundation", "level": "Beginner", "price": "Free", "rating": 4.8, "duration": "Self-paced"},
        {"id": "c-node-3", "title": "Server-side Development with Node.js", "platform": "Coursera", "url": "https://www.coursera.org/learn/server-side-nodejs", "instructor": "HKUST", "level": "Intermediate", "price": "Free", "rating": 4.5, "duration": "4 weeks"},
    ],
    "TypeScript": [
        {"id": "c-ts-1", "title": "Understanding TypeScript", "platform": "Udemy", "url": "https://www.udemy.com/course/understanding-typescript/", "instructor": "Maximilian Schwarzmüller", "level": "Beginner", "price": "$13.99", "rating": 4.7, "duration": "15h"},
        {"id": "c-ts-2", "title": "TypeScript Official Handbook", "platform": "Official Docs", "url": "https://www.typescriptlang.org/docs/handbook/", "instructor": "Microsoft", "level": "Beginner", "price": "Free", "rating": 4.9, "duration": "Self-paced"},
        {"id": "c-ts-3", "title": "Learn TypeScript", "platform": "Codecademy", "url": "https://www.codecademy.com/learn/learn-typescript", "instructor": "Codecademy", "level": "Beginner", "price": "Free", "rating": 4.4, "duration": "10h"},
    ],
    "CSS": [
        {"id": "c-css-1", "title": "Responsive Web Design", "platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/", "instructor": "freeCodeCamp", "level": "Beginner", "price": "Free", "rating": 4.7, "duration": "300h"},
        {"id": "c-css-2", "title": "MDN CSS Guide", "platform": "MDN", "url": "https://developer.mozilla.org/en-US/docs/Web/CSS", "instructor": "Mozilla", "level": "Beginner", "price": "Free", "rating": 4.9, "duration": "Self-paced"},
        {"id": "c-css-3", "title": "Advanced CSS and Sass", "platform": "Udemy", "url": "https://www.udemy.com/course/advanced-css-and-sass/", "instructor": "Jonas Schmedtmann", "level": "Advanced", "price": "$13.99", "rating": 4.8, "duration": "28h"},
    ],
    "HTML": [
        {"id": "c-html-1", "title": "Responsive Web Design Certification", "platform": "freeCodeCamp", "url": "https://www.freecodecamp.org/learn/2022/responsive-web-design/", "instructor": "freeCodeCamp", "level": "Beginner", "price": "Free", "rating": 4.7, "duration": "300h"},
        {"id": "c-html-2", "title": "MDN HTML Guide", "platform": "MDN", "url": "https://developer.mozilla.org/en-US/docs/Web/HTML", "instructor": "Mozilla", "level": "Beginner", "price": "Free", "rating": 4.9, "duration": "Self-paced"},
    ],
    "Git": [
        {"id": "c-git-1", "title": "Version Control with Git", "platform": "Coursera", "url": "https://www.coursera.org/learn/version-control-with-git", "instructor": "Atlassian", "level": "Beginner", "price": "Free", "rating": 4.6, "duration": "4 weeks"},
        {"id": "c-git-2", "title": "Git Official Documentation", "platform": "Official Docs", "url": "https://git-scm.com/doc", "instructor": "Git", "level": "Beginner", "price": "Free", "rating": 4.8, "duration": "Self-paced"},
        {"id": "c-git-3", "title": "Learn Git Branching (Interactive)", "platform": "Interactive", "url": "https://learngitbranching.js.org/", "instructor": "Community", "level": "Beginner", "price": "Free", "rating": 4.9, "duration": "2h"},
    ],
    "Neo4j": [
        {"id": "c-neo4j-1", "title": "Neo4j Graph Academy", "platform": "Neo4j Academy", "url": "https://graphacademy.neo4j.com/", "instructor": "Neo4j", "level": "Beginner", "price": "Free", "rating": 4.7, "duration": "Self-paced"},
    ],
    "FastAPI": [
        {"id": "c-fastapi-1", "title": "FastAPI Official Tutorial", "platform": "Official Docs", "url": "https://fastapi.tiangolo.com/tutorial/", "instructor": "Sebastián Ramírez", "level": "Beginner", "price": "Free", "rating": 4.9, "duration": "Self-paced"},
        {"id": "c-fastapi-2", "title": "FastAPI - The Complete Course", "platform": "Udemy", "url": "https://www.udemy.com/course/fastapi-the-complete-course/", "instructor": "Eric Roby", "level": "Beginner", "price": "$13.99", "rating": 4.6, "duration": "20h"},
    ],
    "Financial Analysis": [
        {"id": "c-fin-1", "title": "Financial Markets", "platform": "Coursera", "url": "https://www.coursera.org/learn/financial-markets-global", "instructor": "Yale / Robert Shiller", "level": "Beginner", "price": "Free", "rating": 4.8, "duration": "7 weeks"},
        {"id": "c-fin-2", "title": "The Complete Financial Analyst Course", "platform": "Udemy", "url": "https://www.udemy.com/course/the-complete-financial-analyst-course/", "instructor": "365 Careers", "level": "Beginner", "price": "$13.99", "rating": 4.6, "duration": "22h"},
        {"id": "c-fin-3", "title": "Finance & Quantitative Modeling", "platform": "Coursera", "url": "https://www.coursera.org/specializations/finance-quantitative-modeling-analysts", "instructor": "Wharton", "level": "Intermediate", "price": "Free", "rating": 4.7, "duration": "4 months"},
    ],
    "Digital Marketing": [
        {"id": "c-dm-1", "title": "Google Digital Marketing Certificate", "platform": "Coursera", "url": "https://www.coursera.org/professional-certificates/google-digital-marketing-ecommerce", "instructor": "Google", "level": "Beginner", "price": "Free", "rating": 4.8, "duration": "6 months"},
        {"id": "c-dm-2", "title": "The Complete Digital Marketing Course", "platform": "Udemy", "url": "https://www.udemy.com/course/learn-digital-marketing-course/", "instructor": "Rob Percival", "level": "Beginner", "price": "$13.99", "rating": 4.5, "duration": "22h"},
        {"id": "c-dm-3", "title": "HubSpot Academy", "platform": "HubSpot", "url": "https://academy.hubspot.com/", "instructor": "HubSpot", "level": "Beginner", "price": "Free", "rating": 4.7, "duration": "Self-paced"},
    ],
    "Graphic Design": [
        {"id": "c-gd-1", "title": "Graphic Design Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/graphic-design", "instructor": "CalArts", "level": "Beginner", "price": "Free", "rating": 4.7, "duration": "6 months"},
        {"id": "c-gd-2", "title": "Canva Design School", "platform": "Canva", "url": "https://www.canva.com/designschool/", "instructor": "Canva", "level": "Beginner", "price": "Free", "rating": 4.5, "duration": "Self-paced"},
    ],
    "UX Design": [
        {"id": "c-ux-1", "title": "Google UX Design Professional Certificate", "platform": "Coursera", "url": "https://www.coursera.org/professional-certificates/google-ux-design", "instructor": "Google", "level": "Beginner", "price": "Free", "rating": 4.8, "duration": "6 months"},
        {"id": "c-ux-2", "title": "Interaction Design Foundation", "platform": "IDF", "url": "https://www.interaction-design.org/courses", "instructor": "IDF", "level": "Beginner", "price": "$11/mo", "rating": 4.7, "duration": "Self-paced"},
    ],
    "Project Management": [
        {"id": "c-pm-1", "title": "Google Project Management Certificate", "platform": "Coursera", "url": "https://www.coursera.org/professional-certificates/google-project-management", "instructor": "Google", "level": "Beginner", "price": "Free", "rating": 4.8, "duration": "6 months"},
        {"id": "c-pm-2", "title": "PMP Exam Prep Seminar", "platform": "Udemy", "url": "https://www.udemy.com/course/pmp-pmbok6-35-pdus/", "instructor": "Joseph Phillips", "level": "Advanced", "price": "$13.99", "rating": 4.6, "duration": "35h"},
    ],
    "Business Strategy": [
        {"id": "c-bs-1", "title": "Business Strategy Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/business-strategy", "instructor": "University of Virginia", "level": "Intermediate", "price": "Free", "rating": 4.7, "duration": "6 months"},
    ],
    "Leadership": [
        {"id": "c-lead-1", "title": "Inspiring and Motivating Individuals", "platform": "Coursera", "url": "https://www.coursera.org/learn/motivate-people-teams", "instructor": "University of Michigan", "level": "Intermediate", "price": "Free", "rating": 4.8, "duration": "4 weeks"},
    ],
    "Public Speaking": [
        {"id": "c-ps-1", "title": "Introduction to Public Speaking", "platform": "Coursera", "url": "https://www.coursera.org/learn/public-speaking", "instructor": "University of Washington", "level": "Beginner", "price": "Free", "rating": 4.7, "duration": "5 weeks"},
    ],
    "Medical Sciences": [
        {"id": "c-med-1", "title": "Anatomy Specialization", "platform": "Coursera", "url": "https://www.coursera.org/specializations/anatomy", "instructor": "University of Michigan", "level": "Beginner", "price": "Free", "rating": 4.8, "duration": "4 months"},
        {"id": "c-med-2", "title": "Khan Academy Health & Medicine", "platform": "Khan Academy", "url": "https://www.khanacademy.org/science/health-and-medicine", "instructor": "Khan Academy", "level": "Beginner", "price": "Free", "rating": 4.9, "duration": "Self-paced"},
    ],
    "Accounting": [
        {"id": "c-acc-1", "title": "Financial Accounting Fundamentals", "platform": "Coursera", "url": "https://www.coursera.org/learn/uva-darden-financial-accounting", "instructor": "University of Virginia", "level": "Beginner", "price": "Free", "rating": 4.7, "duration": "5 weeks"},
    ],
    "Apache Spark": [
        {"id": "c-spark-1", "title": "Big Data with Apache Spark and Python", "platform": "Udemy", "url": "https://www.udemy.com/course/taming-big-data-with-apache-spark-hands-on/", "instructor": "Frank Kane", "level": "Intermediate", "price": "$13.99", "rating": 4.6, "duration": "7h"},
    ],
    "Sustainability": [
        {"id": "c-sust-1", "title": "Sustainability and Development", "platform": "Coursera", "url": "https://www.coursera.org/learn/sustainability", "instructor": "Columbia University", "level": "Beginner", "price": "Free", "rating": 4.7, "duration": "9 weeks"},
    ],
}


# ── API Endpoints ──────────────────────────────────────────────────

@router.get("/skills")
async def get_available_skills():
    """Get all skills with learning resources available."""
    yt_skills = set(YOUTUBE_CATALOG.keys())
    w3_skills = set(W3SCHOOLS_CATALOG.keys())
    course_skills = set(COURSES_CATALOG.keys())
    all_skills = sorted(yt_skills | w3_skills | course_skills)
    return {
        "skills": all_skills,
        "total": len(all_skills),
        "youtube_skills": sorted(yt_skills),
        "w3schools_skills": sorted(w3_skills),
        "course_skills": sorted(course_skills),
    }


@router.get("/by-skill/{skill}")
async def get_resources_for_skill(
    skill: str,
    level: Optional[str] = Query(None, description="Filter by level: Beginner, Intermediate, Advanced"),
    source: Optional[str] = Query(None, description="Filter by source: youtube, w3schools"),
):
    """
    Get all learning resources for a specific skill.
    Performs exact match first, then case-insensitive, then partial match,
    and always provides dynamic YouTube search links as a fallback.
    """
    skill_lower = skill.lower()

    # ── 1. Collect matching resources ─────────────────────────────
    matched_videos: list = []
    matched_tutorials: list = []
    matched_courses: list = []

    def _matches(cat_skill: str) -> bool:
        return (cat_skill == skill
                or cat_skill.lower() == skill_lower
                or skill_lower in cat_skill.lower()
                or cat_skill.lower() in skill_lower)

    for cat_skill, vids in YOUTUBE_CATALOG.items():
        if _matches(cat_skill):
            matched_videos.extend([{**v, "_matched_skill": cat_skill} for v in vids])

    for cat_skill, tuts in W3SCHOOLS_CATALOG.items():
        if _matches(cat_skill):
            matched_tutorials.extend([{**t, "_matched_skill": cat_skill} for t in tuts])

    for cat_skill, courses in COURSES_CATALOG.items():
        if _matches(cat_skill):
            matched_courses.extend([{**c, "_matched_skill": cat_skill} for c in courses])

    # ── 2. Apply level filter ─────────────────────────────────────
    if level:
        matched_videos = [v for v in matched_videos if v["level"] == level]
        matched_tutorials = [t for t in matched_tutorials if t["level"] == level]
        matched_courses = [c for c in matched_courses if c["level"] == level]

    # ── 3. Build response ─────────────────────────────────────────
    result: dict = {"skill": skill, "videos": [], "tutorials": [], "courses": []}

    if source != "w3schools":
        result["videos"] = [
            {
                **{k: v for k, v in v.items() if k != "_matched_skill"},
                "source": "youtube",
                "thumbnail": f"https://img.youtube.com/vi/{v['video_id']}/mqdefault.jpg",
                "url": f"https://www.youtube.com/watch?v={v['video_id']}",
                "embed_url": f"https://www.youtube.com/embed/{v['video_id']}",
            }
            for v in matched_videos
        ]

    if source != "youtube":
        result["tutorials"] = [
            {**{k: v for k, v in t.items() if k != "_matched_skill"}, "source": "w3schools", "icon": "w3schools"}
            for t in matched_tutorials
        ]

    # ── Courses from all platforms ────────────────────────────────
    result["courses"] = [
        {**{k: v for k, v in c.items() if k != "_matched_skill"}, "source": "course"}
        for c in matched_courses
    ]

    # ── 4. Dynamic YouTube search fallback ────────────────────────
    yt_search_query = skill.replace(" ", "+") + "+tutorial"
    result["youtube_search_url"] = f"https://www.youtube.com/results?search_query={yt_search_query}"
    result["google_search_url"] = f"https://www.google.com/search?q={skill.replace(' ', '+')}+learning+resources"

    if len(result["videos"]) == 0 and source != "w3schools":
        result["videos"] = [
            {
                "id": f"yt-search-{skill_lower.replace(' ', '-')}-{i+1}",
                "title": f"{skill} - {label}",
                "channel": "YouTube Search",
                "video_id": "",
                "duration": "",
                "level": lvl,
                "views": "",
                "source": "youtube_search",
                "thumbnail": "",
                "url": f"https://www.youtube.com/results?search_query={skill.replace(' ', '+')}+{label.lower().replace(' ', '+')}",
                "embed_url": "",
            }
            for i, (label, lvl) in enumerate([
                ("Full Course for Beginners", "Beginner"),
                ("Complete Tutorial", "Beginner"),
                ("Intermediate Guide", "Intermediate"),
                ("Advanced Concepts", "Advanced"),
            ])
        ]

    if len(result["tutorials"]) == 0 and source != "youtube":
        result["tutorials"] = [
            {
                "id": f"web-search-{skill_lower.replace(' ', '-')}-1",
                "title": f"Learn {skill} - Online Resources",
                "url": f"https://www.google.com/search?q={skill.replace(' ', '+')}+tutorial+guide",
                "topic": "Full Course",
                "level": "Beginner",
                "source": "web_search",
                "icon": "search",
            },
            {
                "id": f"web-search-{skill_lower.replace(' ', '-')}-2",
                "title": f"{skill} - Wikipedia Overview",
                "url": f"https://en.wikipedia.org/wiki/{skill.replace(' ', '_')}",
                "topic": "Overview",
                "level": "Beginner",
                "source": "web_search",
                "icon": "search",
            },
        ]

    result["total_videos"] = len(result["videos"])
    result["total_tutorials"] = len(result["tutorials"])
    result["total_courses"] = len(result["courses"])
    return result


@router.get("/search")
async def search_resources(
    q: str = Query(..., description="Search query"),
    level: Optional[str] = Query(None),
    source: Optional[str] = Query(None),
    limit: int = Query(20, le=50),
):
    """Search across all learning resources with smart keyword matching."""
    q_lower = q.lower().strip()
    results = []

    # Keyword aliases: map common search terms to relevant skill categories
    SKILL_ALIASES = {
        "ai": ["machine learning", "data science", "tensorflow", "pytorch", "python", "neo4j"],
        "artificial intelligence": ["machine learning", "data science", "tensorflow", "pytorch"],
        "ml": ["machine learning", "data science", "tensorflow", "pytorch"],
        "deep learning": ["machine learning", "tensorflow", "pytorch"],
        "web": ["javascript", "react", "css", "node.js", "typescript", "html", "django", "fastapi"],
        "frontend": ["javascript", "react", "css", "typescript", "html", "vue.js", "angular"],
        "backend": ["python", "node.js", "django", "fastapi", "java", "go", "sql"],
        "cloud": ["docker", "kubernetes", "aws", "azure", "terraform"],
        "devops": ["docker", "kubernetes", "git", "jenkins", "terraform", "ansible"],
        "data": ["data science", "python", "sql", "machine learning", "mongodb"],
        "database": ["sql", "mongodb", "neo4j", "postgresql"],
        "mobile": ["react", "swift", "kotlin", "flutter"],
        "design": ["graphic design", "ux design", "css"],
        "marketing": ["digital marketing", "content marketing"],
        "finance": ["financial analysis", "accounting"],
        "security": ["cybersecurity", "owasp", "network security"],
        "management": ["project management", "leadership", "entrepreneurship"],
    }

    # Get expanded skill set from aliases
    expanded_skills = set()
    for alias, mapped_skills in SKILL_ALIASES.items():
        if q_lower in alias or alias in q_lower:
            expanded_skills.update(mapped_skills)

    def _matches_query(text: str) -> int:
        """Return match score: 2=strong, 1=weak, 0=no match."""
        text_lower = text.lower()
        # For short queries (<=3 chars), use word boundary matching to avoid
        # false positives like 'ai' matching 'Sustainability'
        if len(q_lower) <= 3:
            import re
            if re.search(r'\b' + re.escape(q_lower) + r'\b', text_lower):
                return 2
            return 0
        if q_lower in text_lower:
            return 2
        # Check if any word of the query matches
        for word in q_lower.split():
            if len(word) >= 3 and word in text_lower:
                return 1
        return 0

    def _skill_matches(skill_name: str) -> int:
        """Check if a skill matches the query directly or via aliases."""
        skill_lower = skill_name.lower()
        # For short queries, require word boundary match in skill name too
        if len(q_lower) <= 3:
            import re
            if re.search(r'\b' + re.escape(q_lower) + r'\b', skill_lower):
                return 3
        elif q_lower in skill_lower:
            return 3  # Direct skill name match
        if skill_lower in expanded_skills:
            return 2  # Alias match
        return 0

    # Search YouTube catalog
    for skill, videos in YOUTUBE_CATALOG.items():
        skill_score = _skill_matches(skill)
        for v in videos:
            title_score = _matches_query(v["title"])
            channel_score = _matches_query(v["channel"])
            relevance = skill_score + title_score + channel_score

            if relevance == 0:
                continue
            if level and v["level"] != level:
                continue
            if source and source != "youtube":
                continue
            results.append({
                **v,
                "skill": skill,
                "source": "youtube",
                "thumbnail": f"https://img.youtube.com/vi/{v['video_id']}/mqdefault.jpg",
                "url": f"https://www.youtube.com/watch?v={v['video_id']}",
                "embed_url": f"https://www.youtube.com/embed/{v['video_id']}",
                "_relevance": relevance,
            })

    # Search W3Schools catalog
    for skill, tutorials in W3SCHOOLS_CATALOG.items():
        skill_score = _skill_matches(skill)
        for t in tutorials:
            title_score = _matches_query(t["title"])
            topic_score = _matches_query(t.get("topic", ""))
            relevance = skill_score + title_score + topic_score

            if relevance == 0:
                continue
            if level and t["level"] != level:
                continue
            if source and source != "w3schools":
                continue
            results.append({**t, "skill": skill, "source": "w3schools", "icon": "w3schools", "_relevance": relevance})

    # Search Courses catalog
    for skill, courses in COURSES_CATALOG.items():
        skill_score = _skill_matches(skill)
        for c in courses:
            title_score = _matches_query(c["title"])
            platform_score = _matches_query(c.get("platform", ""))
            relevance = skill_score + title_score + platform_score

            if relevance == 0:
                continue
            if level and c["level"] != level:
                continue
            if source and source not in ("course", "courses", None):
                continue
            results.append({**c, "skill": skill, "source": "course", "_relevance": relevance})

    # Sort by relevance (highest first)
    results.sort(key=lambda x: -x.get("_relevance", 0))

    # Remove internal relevance field before returning
    for r in results:
        r.pop("_relevance", None)

    return {"results": results[:limit], "total": len(results), "query": q}


@router.get("/recommend")
async def recommend_resources(
    current_skills: List[str] = Query(default=[], description="User's current skills"),
    interests: List[str] = Query(default=[], description="User's interests"),
    level: Optional[str] = Query(None),
    limit: int = Query(10, le=30),
):
    """
    AI-powered learning recommendations based on user skills and interests.
    Recommends resources for skills the user wants to learn or improve.
    """
    # Determine target skills: skills we have resources for that user doesn't know
    all_skills = set(YOUTUBE_CATALOG.keys()) | set(W3SCHOOLS_CATALOG.keys())
    known_set = set(current_skills)
    interest_set = set(interests)

    # Priority: interested skills user doesn't know > related skills > random
    recommended_skills = []

    # 1. Skills the user is interested in but doesn't have
    for skill in interest_set:
        if skill not in known_set and skill in all_skills:
            recommended_skills.append({"skill": skill, "reason": "Matches your interests"})

    # 2. Related skills based on common pairings
    SKILL_RELATIONS = {
        # Tech
        "Python": ["Machine Learning", "Data Science", "FastAPI", "Django"],
        "JavaScript": ["React", "TypeScript", "Node.js"],
        "React": ["TypeScript", "CSS", "Node.js"],
        "HTML": ["CSS", "JavaScript"],
        "CSS": ["HTML", "JavaScript", "React"],
        "SQL": ["Python", "Data Science"],
        "Machine Learning": ["Python", "Data Science", "Apache Spark"],
        "Data Science": ["Python", "SQL", "Machine Learning"],
        "Node.js": ["JavaScript", "TypeScript", "Docker"],
        "TypeScript": ["JavaScript", "React", "Node.js"],
        "Docker": ["Node.js", "Python", "Git"],
        "Git": ["Docker", "Python"],
        "Neo4j": ["Python", "Data Science"],
        "Apache Spark": ["Python", "Data Science"],
        "FastAPI": ["Python", "Docker"],
        # Finance
        "Financial Analysis": ["Accounting", "Business Strategy", "SQL"],
        "Accounting": ["Financial Analysis", "Business Law"],
        # Marketing
        "Digital Marketing": ["Content Marketing", "Graphic Design", "Public Speaking"],
        "Content Marketing": ["Digital Marketing", "Graphic Design", "Public Speaking"],
        # Design
        "Graphic Design": ["UX Design", "Content Marketing"],
        "UX Design": ["Graphic Design", "React", "Figma"],
        # Healthcare
        "Medical Sciences": ["Public Health", "Data Science"],
        "Public Health": ["Medical Sciences", "Sustainability"],
        # Business
        "Project Management": ["Leadership", "Business Strategy", "Entrepreneurship"],
        "Business Strategy": ["Financial Analysis", "Entrepreneurship", "Leadership"],
        "Entrepreneurship": ["Business Strategy", "Digital Marketing", "Financial Analysis"],
        # Legal
        "Business Law": ["Intellectual Property", "Accounting"],
        "Intellectual Property": ["Business Law"],
        # Soft Skills
        "Public Speaking": ["Leadership", "Content Marketing"],
        "Leadership": ["Project Management", "Public Speaking", "Business Strategy"],
        # Education
        "Instructional Design": ["Public Speaking", "UX Design"],
        # Environmental
        "Sustainability": ["Public Health", "Project Management"],
    }

    for known in current_skills:
        related = SKILL_RELATIONS.get(known, [])
        for rel in related:
            if rel not in known_set and rel in all_skills:
                if not any(r["skill"] == rel for r in recommended_skills):
                    recommended_skills.append({"skill": rel, "reason": f"Related to {known}"})

    # 3. Fill with popular skills across all domains
    popular = [
        "Python", "JavaScript", "React", "SQL", "Project Management",
        "Digital Marketing", "Financial Analysis", "UX Design",
        "Leadership", "Public Speaking", "Business Strategy",
    ]
    for p in popular:
        if p not in known_set and p in all_skills:
            if not any(r["skill"] == p for r in recommended_skills):
                recommended_skills.append({"skill": p, "reason": "Popular skill"})

    # Build resource recommendations
    recommendations = []
    for rec in recommended_skills[:limit]:
        skill = rec["skill"]
        videos = YOUTUBE_CATALOG.get(skill, [])
        tutorials = W3SCHOOLS_CATALOG.get(skill, [])

        if level:
            videos = [v for v in videos if v["level"] == level]
            tutorials = [t for t in tutorials if t["level"] == level]

        # Pick the best video (first one = usually most popular) and first tutorial
        top_video = None
        if videos:
            v = videos[0]
            top_video = {
                **v,
                "source": "youtube",
                "thumbnail": f"https://img.youtube.com/vi/{v['video_id']}/mqdefault.jpg",
                "url": f"https://www.youtube.com/watch?v={v['video_id']}",
                "embed_url": f"https://www.youtube.com/embed/{v['video_id']}",
            }

        top_tutorial = None
        if tutorials:
            t = tutorials[0]
            top_tutorial = {**t, "source": "w3schools"}

        recommendations.append({
            "skill": skill,
            "reason": rec["reason"],
            "total_videos": len(YOUTUBE_CATALOG.get(skill, [])),
            "total_tutorials": len(W3SCHOOLS_CATALOG.get(skill, [])),
            "top_video": top_video,
            "top_tutorial": top_tutorial,
        })

    return {
        "recommendations": recommendations,
        "total": len(recommendations),
        "based_on_skills": current_skills,
        "based_on_interests": interests,
    }


@router.get("/all")
async def get_all_resources(
    level: Optional[str] = Query(None),
    limit: int = Query(50, le=100),
):
    """Get all available learning resources."""
    all_resources = []

    for skill, videos in YOUTUBE_CATALOG.items():
        for v in videos:
            if level and v["level"] != level:
                continue
            all_resources.append({
                **v,
                "skill": skill,
                "source": "youtube",
                "thumbnail": f"https://img.youtube.com/vi/{v['video_id']}/mqdefault.jpg",
                "url": f"https://www.youtube.com/watch?v={v['video_id']}",
                "embed_url": f"https://www.youtube.com/embed/{v['video_id']}",
            })

    for skill, tutorials in W3SCHOOLS_CATALOG.items():
        for t in tutorials:
            if level and t["level"] != level:
                continue
            all_resources.append({**t, "skill": skill, "source": "w3schools"})

    return {"resources": all_resources[:limit], "total": len(all_resources)}
