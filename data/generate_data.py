"""
Realistic Data Generator for ExpertLink
Generates comprehensive, realistic content for the knowledge platform
"""

import json
import random
from datetime import datetime, timedelta

# Realistic first and last names
FIRST_NAMES = [
    "Alexandre", "Marie", "Thomas", "Sophie", "Pierre", "Julie", "Nicolas", "Camille",
    "Antoine", "Emma", "Lucas", "Léa", "Mathieu", "Chloé", "David", "Sarah",
    "Julien", "Laura", "Sébastien", "Manon", "François", "Alice", "Baptiste", "Clara",
    "Guillaume", "Lucie", "Romain", "Anaïs", "Maxime", "Pauline", "Olivier", "Marion",
    "Vincent", "Louise", "Jérôme", "Margot", "Laurent", "Justine", "Benjamin", "Charlotte",
    "Michaël", "Amandine", "Christophe", "Nadia", "Yannick", "Fatima", "Malik", "Aisha",
    "James", "Emily", "Robert", "Jennifer", "Michael", "Sarah", "John", "Elizabeth",
    "William", "Lisa", "Daniel", "Amanda", "Christopher", "Rachel", "Kevin", "Michelle"
]

LAST_NAMES = [
    "Martin", "Bernard", "Dubois", "Thomas", "Robert", "Richard", "Petit", "Durand",
    "Leroy", "Moreau", "Simon", "Laurent", "Lefebvre", "Michel", "Garcia", "David",
    "Bertrand", "Roux", "Vincent", "Fournier", "Morel", "Girard", "André", "Mercier",
    "Dupont", "Lambert", "Bonnet", "François", "Martinez", "Nguyen", "Chen", "Kim",
    "López", "Smith", "Johnson", "Williams", "Brown", "Jones", "Wilson", "Taylor",
    "Anderson", "Thompson", "White", "Harris", "Clark", "Lewis", "Young", "Walker"
]

DEPARTMENTS = [
    "Engineering", "Data Science", "DevOps", "Security", "Cloud Infrastructure",
    "AI Research", "Web Development", "Mobile Development", "Quality Assurance",
    "Platform Engineering", "Machine Learning", "Architecture", "Product Development"
]

ROLES = [
    "Junior Developer", "Senior Developer", "Lead Developer", "Tech Lead",
    "Software Architect", "Data Scientist", "ML Engineer", "DevOps Engineer",
    "Security Engineer", "Cloud Architect", "Full Stack Developer", "Backend Developer",
    "Frontend Developer", "Principal Engineer", "Staff Engineer", "Engineering Manager",
    "Research Scientist", "Platform Engineer", "SRE", "Solutions Architect"
]

LOCATIONS = [
    "Paris, France", "Lyon, France", "Marseille, France", "Bordeaux, France",
    "Toulouse, France", "Nantes, France", "Strasbourg, France", "Lille, France",
    "London, UK", "Berlin, Germany", "Amsterdam, Netherlands", "Dublin, Ireland",
    "Brussels, Belgium", "Geneva, Switzerland", "Barcelona, Spain", "Milan, Italy",
    "New York, USA", "San Francisco, USA", "Toronto, Canada", "Singapore"
]

# Detailed document content templates
DOCUMENT_CONTENT = {
    "DevOps": {
        "titles": [
            "CI/CD Pipeline Best Practices with Jenkins and GitLab",
            "Kubernetes Deployment Strategies for Production",
            "Infrastructure as Code with Terraform and AWS",
            "Docker Container Security and Optimization",
            "GitOps Workflow Implementation Guide",
            "Monitoring and Observability with Prometheus and Grafana",
            "Microservices Architecture Deployment Patterns",
            "Ansible Automation for Configuration Management",
            "Container Orchestration with Kubernetes",
            "Zero-Downtime Deployment Strategies"
        ],
        "overviews": [
            "This guide introduces DevOps with practical guidance and examples.",
            "Comprehensive overview of modern DevOps practices and toolchains.",
            "Step-by-step tutorial for implementing DevOps in enterprise environments.",
            "Best practices for continuous integration and deployment pipelines.",
            "Practical guide to automating infrastructure and deployment processes."
        ],
        "key_concepts": [
            "- Why DevOps matters in modern software development",
            "- Typical use cases and common pitfalls to avoid",
            "- Best practices to get started with CI/CD",
            "- Infrastructure automation principles",
            "- Container orchestration fundamentals",
            "- Monitoring and alerting strategies"
        ],
        "walkthroughs": [
            "1) Understand the basics of DevOps culture and practices",
            "2) Set up your development environment and tools",
            "3) Configure version control with branching strategies",
            "4) Implement automated testing pipelines",
            "5) Deploy to staging and production environments",
            "6) Monitor and iterate on your deployment process"
        ]
    },
    "Machine Learning": {
        "titles": [
            "Deep Learning with TensorFlow and PyTorch",
            "Natural Language Processing Fundamentals",
            "Computer Vision with Convolutional Neural Networks",
            "Feature Engineering and Data Preprocessing",
            "Model Deployment and MLOps Best Practices",
            "Reinforcement Learning: Theory and Applications",
            "Time Series Forecasting with LSTM Networks",
            "Transfer Learning for Image Classification",
            "Ensemble Methods and Model Stacking",
            "Neural Network Optimization Techniques"
        ],
        "overviews": [
            "This guide covers machine learning fundamentals with hands-on examples.",
            "Comprehensive introduction to ML algorithms and their applications.",
            "Practical tutorial for building and deploying ML models.",
            "Deep dive into neural network architectures and training strategies.",
            "From data preprocessing to model deployment in production."
        ],
        "key_concepts": [
            "- Supervised vs unsupervised learning approaches",
            "- Neural network architectures and backpropagation",
            "- Hyperparameter tuning and model selection",
            "- Cross-validation and evaluation metrics",
            "- Feature engineering best practices",
            "- Model interpretability and explainability"
        ],
        "walkthroughs": [
            "1) Set up your ML development environment",
            "2) Load and preprocess the dataset",
            "3) Explore data and perform feature engineering",
            "4) Train and validate your model",
            "5) Optimize hyperparameters and evaluate performance",
            "6) Deploy the model to production"
        ]
    },
    "Cloud": {
        "titles": [
            "AWS Architecture Design for Scalable Applications",
            "Multi-Cloud Strategy and Implementation",
            "Serverless Computing with AWS Lambda and Azure Functions",
            "Cloud Cost Optimization Strategies",
            "Hybrid Cloud Infrastructure Design",
            "Cloud Security and Compliance Framework",
            "Container Services: EKS, AKS, and GKE Comparison",
            "Database Migration to Cloud Platforms",
            "Cloud Networking and VPC Configuration",
            "Auto-scaling and High Availability Patterns"
        ],
        "overviews": [
            "This guide explains cloud computing with practical examples.",
            "Comprehensive overview of cloud architecture patterns.",
            "Step-by-step tutorial for cloud migration and deployment.",
            "Best practices for building resilient cloud infrastructure.",
            "From concept to production with cloud-native applications."
        ],
        "key_concepts": [
            "- Cloud service models: IaaS, PaaS, SaaS",
            "- Scalability and elasticity principles",
            "- High availability and disaster recovery",
            "- Cost management and optimization",
            "- Security and compliance in the cloud",
            "- Multi-region and multi-cloud strategies"
        ],
        "walkthroughs": [
            "1) Assess your current infrastructure and requirements",
            "2) Design the target cloud architecture",
            "3) Set up networking and security groups",
            "4) Deploy core services and applications",
            "5) Configure monitoring and alerting",
            "6) Optimize for cost and performance"
        ]
    },
    "Security": {
        "titles": [
            "Application Security Testing and OWASP Guidelines",
            "Zero Trust Architecture Implementation",
            "Penetration Testing Methodology and Tools",
            "Identity and Access Management Best Practices",
            "Secure Coding Practices for Developers",
            "Incident Response and Forensics Guide",
            "Network Security and Firewall Configuration",
            "Encryption and Key Management Strategies",
            "Vulnerability Assessment and Management",
            "Security Operations Center (SOC) Setup"
        ],
        "overviews": [
            "This guide covers security best practices with real-world examples.",
            "Comprehensive overview of cybersecurity frameworks and standards.",
            "Practical tutorial for implementing security controls.",
            "From threat modeling to incident response procedures.",
            "Security strategies for modern application development."
        ],
        "key_concepts": [
            "- OWASP Top 10 vulnerabilities and mitigations",
            "- Defense in depth security strategy",
            "- Authentication and authorization patterns",
            "- Security monitoring and threat detection",
            "- Compliance requirements and audit trails",
            "- Secure development lifecycle"
        ],
        "walkthroughs": [
            "1) Perform threat modeling for your application",
            "2) Implement secure authentication mechanisms",
            "3) Configure encryption for data at rest and in transit",
            "4) Set up security monitoring and alerting",
            "5) Conduct regular vulnerability assessments",
            "6) Establish incident response procedures"
        ]
    },
    "Web Development": {
        "titles": [
            "Modern React Development with Hooks and Context",
            "Full-Stack Development with Node.js and Express",
            "Progressive Web Applications Best Practices",
            "RESTful API Design and Implementation",
            "Frontend Performance Optimization Techniques",
            "TypeScript for Large-Scale Applications",
            "State Management with Redux and MobX",
            "Next.js Server-Side Rendering Guide",
            "GraphQL API Development",
            "Responsive Design and CSS Grid Layouts"
        ],
        "overviews": [
            "This guide covers web development with practical examples.",
            "Comprehensive overview of modern frontend and backend technologies.",
            "Step-by-step tutorial for building full-stack applications.",
            "Best practices for creating performant web applications.",
            "From design to deployment with modern frameworks."
        ],
        "key_concepts": [
            "- Component-based architecture patterns",
            "- State management strategies",
            "- API design and REST principles",
            "- Performance optimization techniques",
            "- Accessibility and responsive design",
            "- Testing and debugging web applications"
        ],
        "walkthroughs": [
            "1) Set up your development environment",
            "2) Design the application architecture",
            "3) Build reusable UI components",
            "4) Implement business logic and API integration",
            "5) Add authentication and authorization",
            "6) Deploy and monitor the application"
        ]
    },
    "AI": {
        "titles": [
            "Large Language Models: Fine-tuning and Deployment",
            "Generative AI Applications and Use Cases",
            "AI Ethics and Responsible Development",
            "Conversational AI and Chatbot Development",
            "Computer Vision Applications in Industry",
            "AI-Powered Recommendation Systems",
            "Speech Recognition and Synthesis",
            "AI for Document Processing and OCR",
            "Predictive Analytics with AI Models",
            "Edge AI and Mobile ML Deployment"
        ],
        "overviews": [
            "This guide covers AI fundamentals with practical examples.",
            "Comprehensive overview of artificial intelligence techniques.",
            "Step-by-step tutorial for building AI-powered applications.",
            "From concept to production with AI models.",
            "Best practices for responsible AI development."
        ],
        "key_concepts": [
            "- Neural network fundamentals",
            "- Natural language understanding",
            "- Computer vision and image processing",
            "- Model training and fine-tuning",
            "- AI ethics and bias mitigation",
            "- Deployment and scaling AI systems"
        ],
        "walkthroughs": [
            "1) Define the problem and success metrics",
            "2) Collect and prepare training data",
            "3) Select and configure the AI model",
            "4) Train and evaluate the model",
            "5) Optimize for performance and accuracy",
            "6) Deploy and monitor in production"
        ]
    }
}

SKILL_CATEGORIES = {
    "Programming Languages": [
        ("Python", "Advanced", 95), ("JavaScript", "Advanced", 92), ("TypeScript", "Advanced", 88),
        ("Java", "Advanced", 85), ("Go", "Intermediate", 75), ("Rust", "Intermediate", 65),
        ("C++", "Advanced", 60), ("C#", "Advanced", 70), ("Ruby", "Intermediate", 45),
        ("PHP", "Intermediate", 50), ("Kotlin", "Intermediate", 55), ("Swift", "Intermediate", 52)
    ],
    "Frameworks": [
        ("React", "Advanced", 90), ("Vue.js", "Advanced", 70), ("Angular", "Advanced", 65),
        ("Django", "Advanced", 75), ("FastAPI", "Intermediate", 80), ("Spring Boot", "Advanced", 70),
        ("Node.js", "Advanced", 88), ("Next.js", "Advanced", 82), ("Flask", "Intermediate", 65),
        ("Express.js", "Advanced", 75), ("NestJS", "Intermediate", 60), ("Rails", "Intermediate", 45)
    ],
    "Cloud Platforms": [
        ("AWS", "Advanced", 92), ("Azure", "Advanced", 85), ("Google Cloud", "Advanced", 78),
        ("Kubernetes", "Advanced", 88), ("Docker", "Advanced", 95), ("Terraform", "Advanced", 82),
        ("AWS Lambda", "Intermediate", 75), ("Azure Functions", "Intermediate", 65)
    ],
    "Data & AI": [
        ("TensorFlow", "Advanced", 80), ("PyTorch", "Advanced", 82), ("Scikit-learn", "Advanced", 75),
        ("Pandas", "Advanced", 90), ("NumPy", "Advanced", 88), ("Spark", "Intermediate", 70),
        ("Kafka", "Intermediate", 65), ("Elasticsearch", "Advanced", 72), ("MongoDB", "Advanced", 78),
        ("PostgreSQL", "Advanced", 85), ("Redis", "Advanced", 80), ("GraphQL", "Intermediate", 68)
    ],
    "DevOps & Tools": [
        ("Git", "Advanced", 98), ("Jenkins", "Advanced", 75), ("GitLab CI", "Advanced", 80),
        ("GitHub Actions", "Advanced", 85), ("Ansible", "Intermediate", 65), ("Prometheus", "Intermediate", 70),
        ("Grafana", "Intermediate", 72), ("ArgoCD", "Intermediate", 55), ("Helm", "Intermediate", 60)
    ],
    "Security": [
        ("OWASP", "Advanced", 70), ("Penetration Testing", "Intermediate", 55),
        ("Security Auditing", "Intermediate", 60), ("IAM", "Advanced", 75),
        ("Encryption", "Advanced", 80), ("Network Security", "Intermediate", 65)
    ]
}

PROJECT_DOMAINS = [
    "E-Commerce Platform", "Healthcare System", "Financial Services", "Education Platform",
    "IoT Platform", "Logistics System", "Media Streaming", "Social Network",
    "CRM System", "Supply Chain", "HR Management", "Analytics Dashboard",
    "Real-time Collaboration", "Marketplace", "Insurance Platform", "Gaming Backend"
]

PROJECT_TECH_STACKS = [
    "React, Node.js, PostgreSQL, AWS",
    "Vue.js, Python, MongoDB, GCP",
    "Angular, Java, MySQL, Azure",
    "Next.js, FastAPI, Redis, Kubernetes",
    "React Native, Go, Cassandra, AWS",
    "Flutter, Django, PostgreSQL, Docker",
    "Svelte, Rust, ScyllaDB, Cloudflare",
    "React, GraphQL, Neo4j, Vercel"
]


def generate_employees(count=100):
    """Generate realistic employee records"""
    employees = []
    for i in range(1, count + 1):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        name = f"{first_name} {last_name}"
        email = f"{first_name.lower()}.{last_name.lower()}@expertlink.com"
        
        experience = random.randint(1, 20)
        expertise = min(5, max(1, experience // 4 + random.randint(0, 2)))
        
        hire_date = datetime.now() - timedelta(days=random.randint(30, 365 * 10))
        
        employees.append({
            "id": f"emp_{i}",
            "name": name,
            "email": email,
            "department": random.choice(DEPARTMENTS),
            "role": random.choice(ROLES),
            "location": random.choice(LOCATIONS),
            "hire_date": hire_date.strftime("%Y-%m-%d"),
            "experience_years": experience,
            "expertise_level": expertise
        })
    return employees


def generate_documents(count=200, employees=None):
    """Generate realistic document records with full content"""
    documents = []
    topics = list(DOCUMENT_CONTENT.keys())
    doc_types = ["Guide", "Tutorial", "Case Study", "Documentation", "Report", "Article"]
    
    for i in range(1, count + 1):
        topic = random.choice(topics)
        content = DOCUMENT_CONTENT[topic]
        doc_type = random.choice(doc_types)
        
        title = random.choice(content["titles"])
        # Add a unique number to avoid exact duplicates
        title = f"{title} - {doc_type} {i}"
        
        overview = random.choice(content["overviews"])
        key_concepts = "\n".join(random.sample(content["key_concepts"], min(4, len(content["key_concepts"]))))
        walkthrough = "\n".join(random.sample(content["walkthroughs"], min(4, len(content["walkthroughs"]))))
        
        # Build full content
        full_content = f"""Overview
--------
{overview}

Key Concepts
------------
{key_concepts}

Walkthrough
----------
{walkthrough}"""
        
        author = random.choice(employees)["id"] if employees else f"emp_{random.randint(1, 100)}"
        date = (datetime.now() - timedelta(days=random.randint(1, 365 * 3))).strftime("%Y-%m-%d")
        
        documents.append({
            "id": f"doc_{i}",
            "title": title,
            "type": doc_type,
            "topic": topic,
            "content": full_content,
            "abstract": overview,
            "author": author,
            "date": date,
            "views": random.randint(50, 15000),
            "rating": round(random.uniform(3.0, 5.0), 1)
        })
    return documents


def generate_skills():
    """Generate skill records from predefined categories"""
    skills = []
    skill_id = 1
    
    for category, skill_list in SKILL_CATEGORIES.items():
        for skill_name, level, demand in skill_list:
            skills.append({
                "id": f"skill_{skill_id}",
                "name": skill_name,
                "category": category,
                "level": level,
                "demand": demand
            })
            skill_id += 1
    return skills


def generate_projects(count=50, employees=None):
    """Generate realistic project records"""
    projects = []
    statuses = ["Active", "Completed", "Planning", "On Hold"]
    priorities = ["High", "Medium", "Low", "Critical"]
    
    for i in range(1, count + 1):
        domain = random.choice(PROJECT_DOMAINS)
        date = (datetime.now() - timedelta(days=random.randint(-180, 365 * 2))).strftime("%Y-%m-%d")
        
        projects.append({
            "id": f"proj_{i}",
            "name": f"{domain} - Phase {random.randint(1, 5)}",
            "domain": domain.split()[0],
            "tech_stack": random.choice(PROJECT_TECH_STACKS),
            "date": date,
            "status": random.choice(statuses),
            "budget": random.randint(50000, 5000000),
            "priority": random.choice(priorities)
        })
    return projects


def save_jsonl(data, filename):
    """Save data to JSONL file"""
    with open(filename, 'w', encoding='utf-8') as f:
        for record in data:
            f.write(json.dumps(record, ensure_ascii=False) + '\n')
    print(f"Saved {len(data)} records to {filename}")


def main():
    print("Generating realistic ExpertLink data...")
    
    # Generate data
    employees = generate_employees(100)
    documents = generate_documents(200, employees)
    skills = generate_skills()
    projects = generate_projects(50, employees)
    
    # Save to files
    save_jsonl(employees, "employees_new.jsonl")
    save_jsonl(documents, "documents_new.jsonl")
    save_jsonl(skills, "skills_new.jsonl")
    save_jsonl(projects, "projects_new.jsonl")
    
    print("\nData generation complete!")
    print(f"- {len(employees)} employees")
    print(f"- {len(documents)} documents")
    print(f"- {len(skills)} skills")
    print(f"- {len(projects)} projects")


if __name__ == "__main__":
    main()
