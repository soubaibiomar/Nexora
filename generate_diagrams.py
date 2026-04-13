"""
Generate professional UML diagrams for Nexora Conception chapter.
Uses matplotlib to create proper UML-style diagrams.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Arc
import numpy as np
import os

OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─── Colors ────────────────────────────────────────────────────────
BLUE = '#2B6CB0'
LIGHT_BLUE = '#BEE3F8'
VERY_LIGHT_BLUE = '#EBF8FF'
DARK = '#2D3748'
GRAY = '#A0AEC0'
WHITE = '#FFFFFF'
LIGHT_CYAN = '#B2F5EA'
ACTOR_COLOR = '#2B6CB0'


def save_fig(fig, name, dpi=200):
    path = os.path.join(OUTPUT_DIR, f"{name}.png")
    fig.savefig(path, dpi=dpi, bbox_inches='tight', facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"  -> Saved {path}")


# ═══════════════════════════════════════════════════════════════════
# 1. USE CASE DIAGRAM
# ═══════════════════════════════════════════════════════════════════
def draw_actor(ax, x, y, label, color=ACTOR_COLOR):
    """Draw a stick figure actor."""
    head_r = 0.15
    ax.add_patch(plt.Circle((x, y + 0.9), head_r, fill=False, edgecolor=color, linewidth=1.5))
    ax.plot([x, x], [y + 0.75, y + 0.35], color=color, linewidth=1.5)
    ax.plot([x - 0.2, x + 0.2], [y + 0.6, y + 0.6], color=color, linewidth=1.5)
    ax.plot([x - 0.15, x, x + 0.15], [y + 0.05, y + 0.35, y + 0.05], color=color, linewidth=1.5)
    ax.text(x, y - 0.15, label, ha='center', va='top', fontsize=8, fontweight='bold', color=DARK)


def draw_usecase(ax, x, y, label, w=2.4, h=0.45):
    """Draw a use case oval."""
    ellipse = mpatches.Ellipse((x, y), w, h, facecolor=LIGHT_CYAN, edgecolor=BLUE, linewidth=1.2, alpha=0.85)
    ax.add_patch(ellipse)
    ax.text(x, y, label, ha='center', va='center', fontsize=6.5, color=DARK, fontweight='medium')
    return (x, y)


def draw_line(ax, x1, y1, x2, y2, style='-', color=GRAY, lw=0.8):
    ax.plot([x1, x2], [y1, y2], linestyle=style, color=color, linewidth=lw)


def generate_usecase_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(14, 11))
    ax.set_xlim(-2, 14)
    ax.set_ylim(-1, 12.5)
    ax.set_aspect('equal')
    ax.axis('off')

    # System boundary
    rect = FancyBboxPatch((2.2, 0.2), 10.5, 11.8, boxstyle="round,pad=0.3",
                          facecolor=WHITE, edgecolor=BLUE, linewidth=2)
    ax.add_patch(rect)
    ax.text(7.5, 11.7, 'Plateforme Nexora', ha='center', fontsize=14,
            fontweight='bold', color=BLUE, style='italic')

    # ── Actors ──
    draw_actor(ax, 0.5, 9.0, 'Utilisateur')
    draw_actor(ax, 0.5, 5.5, 'Manager')
    draw_actor(ax, 0.5, 2.0, 'Administrateur')

    # Inheritance arrows (actor -> actor)
    ax.annotate('', xy=(0.5, 8.8), xytext=(0.5, 6.7),
                arrowprops=dict(arrowstyle='-|>', color=ACTOR_COLOR, lw=1.5, linestyle='dashed'))
    ax.annotate('', xy=(0.5, 5.3), xytext=(0.5, 3.2),
                arrowprops=dict(arrowstyle='-|>', color=ACTOR_COLOR, lw=1.5, linestyle='dashed'))

    # ── Use Cases: User ──
    uc_user = [
        (5.5, 11.0, "S'inscrire (UC01)"),
        (5.5, 10.2, "Se connecter (UC02)"),
        (5.5, 9.4, "Explorer le graphe 3D (UC03)"),
        (5.5, 8.6, "Rechercher un expert (UC04)"),
        (5.5, 7.8, "Recommandations IA (UC05)"),
        (5.5, 7.0, "Chatbot Veda (UC06)"),
        (5.5, 6.2, "Parcours d'apprentissage (UC07)"),
        (5.5, 5.4, "Team Builder (UC08)"),
    ]
    for x, y, label in uc_user:
        draw_usecase(ax, x, y, label)
        draw_line(ax, 0.8, 9.5, x - 1.2, y, color=GRAY)

    # ── Use Cases: Manager ──
    uc_mgr = [
        (9.5, 4.6, "Competences emergentes (UC11)"),
        (9.5, 3.8, "Previsions de demande (UC12)"),
        (9.5, 3.0, "Suggestions collaboration (UC13)"),
        (9.5, 2.2, "Dashboard analytique (UC14)"),
    ]
    for x, y, label in uc_mgr:
        draw_usecase(ax, x, y, label, w=2.8)
        draw_line(ax, 0.8, 6.0, x - 1.4, y, color=GRAY)

    # ── Use Cases: Admin ──
    uc_admin = [
        (5.5, 1.4, "Gerer les utilisateurs (UC15)"),
        (5.5, 0.6, "Modifier les roles (UC16)"),
        (9.5, 1.0, "Metriques Big Data (UC17)"),
    ]
    for x, y, label in uc_admin:
        draw_usecase(ax, x, y, label, w=2.6)
        draw_line(ax, 0.8, 2.5, x - 1.3, y, color=GRAY)

    # ── Include relationships ──
    ax.annotate('', xy=(9.3, 4.6), xytext=(5.7, 7.8),
                arrowprops=dict(arrowstyle='->', color=BLUE, lw=1, linestyle='dashed'))
    ax.text(7.8, 6.4, '<<include>>', ha='center', fontsize=6, color=BLUE, style='italic',
            rotation=-25)

    save_fig(fig, 'usecase_diagram')


# ═══════════════════════════════════════════════════════════════════
# 2. CLASS DIAGRAM
# ═══════════════════════════════════════════════════════════════════
def draw_class_box(ax, x, y, name, attributes, methods, w=3.8, color=BLUE):
    """Draw a UML class box with 3 compartments."""
    line_h = 0.28
    attr_h = len(attributes) * line_h + 0.15
    meth_h = len(methods) * line_h + 0.15
    name_h = 0.45
    total_h = name_h + attr_h + meth_h

    # Box background
    rect = FancyBboxPatch((x - w/2, y - total_h), w, total_h,
                          boxstyle="square,pad=0", facecolor=WHITE,
                          edgecolor=DARK, linewidth=1.5)
    ax.add_patch(rect)

    # Name compartment (colored header)
    header = FancyBboxPatch((x - w/2, y - name_h), w, name_h,
                            boxstyle="square,pad=0", facecolor=LIGHT_BLUE,
                            edgecolor=DARK, linewidth=1.5)
    ax.add_patch(header)
    ax.text(x, y - name_h/2, name, ha='center', va='center',
            fontsize=10, fontweight='bold', color=DARK, family='monospace')

    # Separator line
    ax.plot([x - w/2, x + w/2], [y - name_h, y - name_h], color=DARK, linewidth=1.5)

    # Attributes
    for i, attr in enumerate(attributes):
        ay = y - name_h - 0.1 - i * line_h - line_h/2
        ax.text(x - w/2 + 0.12, ay, attr, ha='left', va='center',
                fontsize=7, color=DARK, family='monospace')

    # Separator
    sep_y = y - name_h - attr_h
    ax.plot([x - w/2, x + w/2], [sep_y, sep_y], color=DARK, linewidth=1.5)

    # Methods
    for i, meth in enumerate(methods):
        my = sep_y - 0.1 - i * line_h - line_h/2
        ax.text(x - w/2 + 0.12, my, meth, ha='left', va='center',
                fontsize=7, color=BLUE, family='monospace')

    return (x, y, w, total_h)


def draw_relation(ax, x1, y1, x2, y2, label, label_pos=0.5, style='-', lw=1.2):
    """Draw a relationship line with label."""
    mx = x1 + (x2 - x1) * label_pos
    my = y1 + (y2 - y1) * label_pos
    ax.plot([x1, x2], [y1, y2], linestyle=style, color=DARK, linewidth=lw)
    ax.text(mx, my + 0.15, label, ha='center', va='bottom', fontsize=7,
            color=BLUE, fontweight='bold', style='italic',
            bbox=dict(boxstyle='round,pad=0.15', facecolor=WHITE, edgecolor='none', alpha=0.9))


def draw_multiplicity(ax, x, y, text):
    ax.text(x, y, text, ha='center', va='center', fontsize=7, color=DARK, fontweight='bold')


def generate_class_diagram():
    fig, ax = plt.subplots(1, 1, figsize=(16, 13))
    ax.set_xlim(-1, 19)
    ax.set_ylim(-5, 10)
    ax.set_aspect('equal')
    ax.axis('off')

    # Title
    ax.text(9, 9.5, 'Diagramme de Classes -- Nexora', ha='center', fontsize=16,
            fontweight='bold', color=BLUE)

    # ── Expert (center) ──
    draw_class_box(ax, 9, 8.5, 'Expert', [
        '- id: String',
        '- name: String',
        '- email: String',
        '- department: String',
        '- role: String',
        '- location: String',
        '- experience_years: Integer',
        '- expertise_level: Integer',
        '- hire_date: Date',
    ], [
        '+ getSkills(): List<Skill>',
        '+ getProjects(): List<Project>',
        '+ getDocuments(): List<Document>',
        '+ getInfluenceScore(): Float',
    ], w=4.2)

    # ── Skill (left) ──
    draw_class_box(ax, 2.5, 5.5, 'Skill', [
        '- id: String',
        '- name: String',
        '- category: String',
        '- level: String',
        '- demand: Integer',
    ], [
        '+ getExperts(): List<Expert>',
        '+ getAdoptionRate(): Float',
    ], w=3.6)

    # ── Project (right) ──
    draw_class_box(ax, 15.5, 5.5, 'Project', [
        '- id: String',
        '- name: String',
        '- domain: String',
        '- status: String',
        '- budget: Float',
        '- required_skills: List',
    ], [
        '+ getTeam(): List<Expert>',
        '+ getSkillCoverage(): Float',
    ], w=3.6)

    # ── Document (top right) ──
    draw_class_box(ax, 15.5, 8.5, 'Document', [
        '- id: String',
        '- title: String',
        '- type: String',
        '- topic: String',
        '- content: String',
        '- author: String',
        '- date: Date',
        '- views: Integer',
        '- rating: Float',
    ], [
        '+ getAuthor(): Expert',
        '+ classify(): String',
    ], w=3.6)

    # ── User (bottom center) ──
    draw_class_box(ax, 9, 0.5, 'User', [
        '- username: String',
        '- email: String',
        '- hashed_password: String',
        '- role: Enum(admin,manager,user)',
    ], [
        '+ verifyPassword(): Boolean',
        '+ generateToken(): String',
        '+ hasRole(r: String): Boolean',
    ], w=4.2)

    # ── Relations ──
    # Expert -- HAS_SKILL --> Skill
    draw_relation(ax, 6.8, 5.8, 4.3, 5.2, 'HAS_SKILL', 0.5)
    draw_multiplicity(ax, 6.5, 5.5, 'N')
    draw_multiplicity(ax, 4.5, 5.5, 'M')

    # Expert -- WORKS_ON --> Project
    draw_relation(ax, 11.2, 5.8, 13.7, 5.2, 'WORKS_ON', 0.5)
    draw_multiplicity(ax, 11.5, 5.5, 'N')
    draw_multiplicity(ax, 13.5, 5.5, 'M')

    # Expert -- AUTHORED --> Document
    draw_relation(ax, 11.2, 7.5, 13.7, 7.5, 'AUTHORED', 0.5)
    draw_multiplicity(ax, 11.5, 7.2, '1')
    draw_multiplicity(ax, 13.5, 7.2, 'N')

    # Project -- REQUIRES_SKILL --> Skill
    draw_relation(ax, 13.7, 3.2, 4.3, 3.2, 'REQUIRES_SKILL', 0.5)
    draw_multiplicity(ax, 13.2, 3.5, 'N')
    draw_multiplicity(ax, 4.8, 3.5, 'M')

    # Expert -- KNOWS --> Expert (self)
    ax.annotate('', xy=(7, 4.2), xytext=(7, 3.0),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=1.2,
                                connectionstyle='arc3,rad=0.8'))
    ax.text(5.5, 3.6, 'KNOWS (N:M)', ha='center', fontsize=7, color=BLUE,
            fontweight='bold', style='italic',
            bbox=dict(boxstyle='round,pad=0.15', facecolor=WHITE, edgecolor='none'))

    save_fig(fig, 'class_diagram')


# ═══════════════════════════════════════════════════════════════════
# 3. SEQUENCE DIAGRAM: Authentication
# ═══════════════════════════════════════════════════════════════════
def draw_lifeline(ax, x, top_y, bottom_y, label, color=LIGHT_BLUE):
    """Draw a lifeline with box at top."""
    bw, bh = 1.6, 0.5
    rect = FancyBboxPatch((x - bw/2, top_y - bh/2), bw, bh,
                          boxstyle="round,pad=0.05", facecolor=color,
                          edgecolor=DARK, linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x, top_y, label, ha='center', va='center', fontsize=8,
            fontweight='bold', color=DARK)
    ax.plot([x, x], [top_y - bh/2, bottom_y], linestyle='--', color=GRAY, linewidth=0.8)


def draw_message(ax, x1, x2, y, label, style='->', dashed=False):
    """Draw a message arrow between lifelines."""
    ls = '--' if dashed else '-'
    arrow_style = '->' if '->' in style else '->'
    if x2 > x1:
        ax.annotate('', xy=(x2 - 0.1, y), xytext=(x1 + 0.1, y),
                    arrowprops=dict(arrowstyle='->', color=DARK, lw=1.2, linestyle=ls))
    else:
        ax.annotate('', xy=(x2 + 0.1, y), xytext=(x1 - 0.1, y),
                    arrowprops=dict(arrowstyle='->', color=DARK, lw=1.2, linestyle='--'))
    tx = (x1 + x2) / 2
    ax.text(tx, y + 0.12, label, ha='center', va='bottom', fontsize=6.5, color=DARK)


def generate_sequence_auth():
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(-0.5, 14)
    ax.set_ylim(-10.5, 1.5)
    ax.set_aspect('equal')
    ax.axis('off')

    ax.text(7, 1.2, 'Diagramme de Sequence : Authentification', ha='center',
            fontsize=14, fontweight='bold', color=BLUE)

    # Lifelines
    ll = {'Client': 1, 'Nginx': 4, 'FastAPI': 7, 'bcrypt': 10, 'JWT': 13}
    for name, x in ll.items():
        draw_lifeline(ax, x, 0.5, -10, f':{name}')

    # Activation boxes
    for x, y1, y2 in [(7, -0.8, -4.5), (7, -5.8, -8.5)]:
        rect = FancyBboxPatch((x - 0.15, y2), 0.3, y1 - y2,
                              boxstyle="square,pad=0", facecolor=VERY_LIGHT_BLUE,
                              edgecolor=BLUE, linewidth=1)
        ax.add_patch(rect)

    # Messages - Login phase
    y = -0.5
    draw_message(ax, 1, 4, y, '1: POST /api/auth/login {user, pass}')
    y -= 0.7
    draw_message(ax, 4, 7, y, '2: forward request')
    y -= 0.7
    draw_message(ax, 7, 7.8, y, '3: check rate limit')
    ax.plot([7.8, 7.8], [y - 0.3, y + 0.1], color=BLUE, linewidth=1)
    y -= 0.7
    draw_message(ax, 7, 10, y, '4: verify(password, hash)')
    y -= 0.7
    draw_message(ax, 10, 7, y, '5: true', dashed=True)
    y -= 0.7
    draw_message(ax, 7, 13, y, '6: encode({sub, role, exp})')
    y -= 0.7
    draw_message(ax, 13, 7, y, '7: token JWT (HS256)', dashed=True)
    y -= 0.7
    draw_message(ax, 7, 4, y, '8: {access_token}', dashed=True)
    draw_message(ax, 4, 1, y - 0.15, '', dashed=True)

    # Separator
    y -= 0.8
    ax.plot([0, 14], [y, y], color=BLUE, linewidth=1, linestyle='-.')
    ax.text(7, y + 0.15, 'Requetes Authentifiees', ha='center', fontsize=8,
            color=BLUE, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.2', facecolor=WHITE, edgecolor=BLUE))

    # Messages - Authenticated requests
    y -= 0.7
    draw_message(ax, 1, 4, y, '9: GET /api/experts [Bearer token]')
    y -= 0.7
    draw_message(ax, 4, 7, y, '10: forward')
    y -= 0.7
    draw_message(ax, 7, 13, y, '11: decode(token)')
    y -= 0.7
    draw_message(ax, 13, 7, y, '12: {sub, role}', dashed=True)
    y -= 0.7
    draw_message(ax, 7, 1, y, '13: 200 OK {data}', dashed=True)

    save_fig(fig, 'sequence_auth')


# ═══════════════════════════════════════════════════════════════════
# 4. SEQUENCE DIAGRAM: Recommendation
# ═══════════════════════════════════════════════════════════════════
def generate_sequence_recommend():
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(-0.5, 14)
    ax.set_ylim(-10.5, 1.5)
    ax.set_aspect('equal')
    ax.axis('off')

    ax.text(7, 1.2, "Diagramme de Sequence : Recommandation d'Expert", ha='center',
            fontsize=14, fontweight='bold', color=BLUE)

    ll = {'Client': 1, 'FastAPI': 4, 'Recommender': 7.5, 'TF-IDF': 11, 'JSONL': 13.5}
    for name, x in ll.items():
        draw_lifeline(ax, x, 0.5, -10, f':{name}')

    # Activation box
    rect = FancyBboxPatch((7.5 - 0.15, -8.5), 0.3, 7.5,
                          boxstyle="square,pad=0", facecolor=VERY_LIGHT_BLUE,
                          edgecolor=BLUE, linewidth=1)
    ax.add_patch(rect)

    y = -0.5
    draw_message(ax, 1, 4, y, '1: POST /api/ai/recommend {query}')
    y -= 0.7
    draw_message(ax, 4, 7.5, y, '2: recommend(query)')
    y -= 0.8

    # Alt fragment
    alt_y = y
    rect = FancyBboxPatch((6.5, y - 1.6), 8, 1.8,
                          boxstyle="square,pad=0", facecolor='#FFFFF0',
                          edgecolor=BLUE, linewidth=1, linestyle='--')
    ax.add_patch(rect)
    ax.text(6.7, alt_y + 0.05, '[if not trained]', fontsize=7, color=BLUE, fontstyle='italic')

    draw_message(ax, 7.5, 13.5, y, '3: load employees.jsonl')
    y -= 0.7
    draw_message(ax, 13.5, 7.5, y, '4: profiles[]', dashed=True)
    y -= 0.7
    draw_message(ax, 7.5, 11, y, '5: fit_transform(corpus)')
    y -= 0.7
    draw_message(ax, 11, 7.5, y, '6: tfidf_matrix', dashed=True)

    y -= 0.8
    draw_message(ax, 7.5, 11, y, '7: transform(query)')
    y -= 0.7
    draw_message(ax, 11, 7.5, y, '8: query_vector', dashed=True)
    y -= 0.7
    draw_message(ax, 7.5, 7.5 + 0.8, y, '9: cosine_similarity()')
    ax.plot([7.5 + 0.8, 7.5 + 0.8], [y - 0.2, y + 0.1], color=BLUE, linewidth=1)
    y -= 0.7
    draw_message(ax, 7.5, 7.5 + 0.8, y, '10: sort top K')
    ax.plot([7.5 + 0.8, 7.5 + 0.8], [y - 0.2, y + 0.1], color=BLUE, linewidth=1)
    y -= 0.7
    draw_message(ax, 7.5, 4, y, '11: results[]', dashed=True)
    y -= 0.7
    draw_message(ax, 4, 1, y, '12: [experts + scores]', dashed=True)

    save_fig(fig, 'sequence_recommend')


# ═══════════════════════════════════════════════════════════════════
# 5. SEQUENCE DIAGRAM: PageRank
# ═══════════════════════════════════════════════════════════════════
def generate_sequence_pagerank():
    fig, ax = plt.subplots(1, 1, figsize=(13, 9))
    ax.set_xlim(-0.5, 13)
    ax.set_ylim(-9.5, 1.5)
    ax.set_aspect('equal')
    ax.axis('off')

    ax.text(6.5, 1.2, 'Diagramme de Sequence : PageRank des Experts', ha='center',
            fontsize=14, fontweight='bold', color=BLUE)

    ll = {'Client': 1, 'FastAPI': 4, 'PageRank': 7.5, 'JSONL': 11}
    for name, x in ll.items():
        draw_lifeline(ax, x, 0.5, -9, f':{name}')

    rect = FancyBboxPatch((7.5 - 0.15, -8.0), 0.3, 7,
                          boxstyle="square,pad=0", facecolor=VERY_LIGHT_BLUE,
                          edgecolor=BLUE, linewidth=1)
    ax.add_patch(rect)

    y = -0.5
    draw_message(ax, 1, 4, y, '1: GET /api/ai/expert-rank')
    y -= 0.7
    draw_message(ax, 4, 7.5, y, '2: rank()')
    y -= 0.7
    draw_message(ax, 7.5, 11, y, '3: load employees, projects, documents')
    y -= 0.7
    draw_message(ax, 11, 7.5, y, '4: data[]', dashed=True)
    y -= 0.8
    draw_message(ax, 7.5, 7.5 + 0.8, y, '5: build bipartite graph')
    ax.plot([7.5 + 0.8, 7.5 + 0.8], [y - 0.2, y + 0.1], color=BLUE, linewidth=1)
    ax.text(8.8, y, '(Expert <-> Skill <-> Project)', fontsize=6, color=GRAY, style='italic')
    y -= 0.8
    draw_message(ax, 7.5, 7.5 + 0.8, y, '6: compute base scores')
    ax.plot([7.5 + 0.8, 7.5 + 0.8], [y - 0.2, y + 0.1], color=BLUE, linewidth=1)

    # Loop fragment
    y -= 0.6
    rect_loop = FancyBboxPatch((6.8, y - 1.2), 2.5, 1.5,
                               boxstyle="square,pad=0", facecolor='#FFFFF5',
                               edgecolor=BLUE, linewidth=1, linestyle='--')
    ax.add_patch(rect_loop)
    ax.text(6.9, y + 0.2, 'loop [i = 1..20]', fontsize=7, color=BLUE, fontstyle='italic')
    y -= 0.3
    draw_message(ax, 7.5, 7.5 + 0.8, y, '7: iterate PageRank (d=0.85)')
    ax.plot([7.5 + 0.8, 7.5 + 0.8], [y - 0.2, y + 0.1], color=BLUE, linewidth=1)
    y -= 0.5
    draw_message(ax, 7.5, 7.5 + 0.8, y, '8: normalize scores')
    ax.plot([7.5 + 0.8, 7.5 + 0.8], [y - 0.2, y + 0.1], color=BLUE, linewidth=1)

    y -= 1.0
    draw_message(ax, 7.5, 7.5 + 0.8, y, '9: blend (60% PR + 40% base)')
    ax.plot([7.5 + 0.8, 7.5 + 0.8], [y - 0.2, y + 0.1], color=BLUE, linewidth=1)
    y -= 0.7
    draw_message(ax, 7.5, 4, y, '10: rankings[]', dashed=True)
    y -= 0.7
    draw_message(ax, 4, 1, y, '11: [ranked experts + scores]', dashed=True)

    save_fig(fig, 'sequence_pagerank')


# ═══════════════════════════════════════════════════════════════════
# 6. GRAPH SCHEMA (Neo4j)
# ═══════════════════════════════════════════════════════════════════
def draw_graph_node(ax, x, y, label, r=0.7, color=LIGHT_BLUE):
    circle = plt.Circle((x, y), r, facecolor=color, edgecolor=BLUE, linewidth=2)
    ax.add_patch(circle)
    ax.text(x, y, label, ha='center', va='center', fontsize=11, fontweight='bold', color=DARK)


def draw_graph_edge(ax, x1, y1, x2, y2, label, offset=0.15, color=DARK):
    dx = x2 - x1
    dy = y2 - y1
    dist = np.sqrt(dx**2 + dy**2)
    nx, ny = dx/dist, dy/dist
    sx, sy = x1 + nx * 0.75, y1 + ny * 0.75
    ex, ey = x2 - nx * 0.75, y2 - ny * 0.75

    ax.annotate('', xy=(ex, ey), xytext=(sx, sy),
                arrowprops=dict(arrowstyle='->', color=color, lw=1.5))

    mx = (sx + ex) / 2
    my = (sy + ey) / 2
    angle = np.degrees(np.arctan2(dy, dx))
    perp_x = -ny * offset
    perp_y = nx * offset
    ax.text(mx + perp_x, my + perp_y, label, ha='center', va='center',
            fontsize=8, color=BLUE, fontweight='bold', style='italic', rotation=angle,
            bbox=dict(boxstyle='round,pad=0.15', facecolor=WHITE, edgecolor='none', alpha=0.95))


def generate_graph_schema():
    fig, ax = plt.subplots(1, 1, figsize=(12, 9))
    ax.set_xlim(-2, 12)
    ax.set_ylim(-2, 9)
    ax.set_aspect('equal')
    ax.axis('off')

    ax.text(5, 8.5, 'Modele de Donnees -- Graphe Neo4j', ha='center', fontsize=16,
            fontweight='bold', color=BLUE)

    # Nodes
    draw_graph_node(ax, 5, 4, 'Expert', r=0.9, color=LIGHT_BLUE)
    draw_graph_node(ax, 0.5, 4, 'Skill', r=0.8, color=LIGHT_CYAN)
    draw_graph_node(ax, 9.5, 4, 'Project', r=0.8, color='#FEFCBF')
    draw_graph_node(ax, 5, 7.3, 'Document', r=0.8, color='#FED7D7')
    draw_graph_node(ax, 9.5, 7.3, 'Topic', r=0.7, color='#E9D8FD')
    draw_graph_node(ax, 5, 0.8, 'Expert', r=0.6, color='#BEE3F8')

    # Edges
    draw_graph_edge(ax, 5, 4, 0.5, 4, 'HAS_SKILL', offset=0.3)
    draw_graph_edge(ax, 5, 4, 9.5, 4, 'WORKS_ON', offset=0.3)
    draw_graph_edge(ax, 5, 4, 5, 7.3, 'AUTHORED', offset=0.4)
    draw_graph_edge(ax, 5, 7.3, 9.5, 7.3, 'COVERS_TOPIC', offset=0.3)
    draw_graph_edge(ax, 9.5, 4, 0.5, 4, 'REQUIRES_SKILL', offset=-0.5)
    draw_graph_edge(ax, 5, 4, 5, 0.8, 'KNOWS', offset=0.4)

    # Cardinalities
    ax.text(2.5, 4.55, 'N : M', fontsize=8, color=GRAY)
    ax.text(7.2, 4.55, 'N : M', fontsize=8, color=GRAY)
    ax.text(5.7, 5.8, '1 : N', fontsize=8, color=GRAY)
    ax.text(5, 3.3, 'N : M', fontsize=8, color=GRAY, ha='center')

    save_fig(fig, 'graph_schema')


# ═══════════════════════════════════════════════════════════════════
# 7. ARCHITECTURE DIAGRAM
# ═══════════════════════════════════════════════════════════════════
def generate_architecture():
    fig, ax = plt.subplots(1, 1, figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 11)
    ax.set_aspect('equal')
    ax.axis('off')

    ax.text(7, 10.5, 'Architecture 3-Tiers -- Nexora', ha='center', fontsize=16,
            fontweight='bold', color=BLUE)

    # ── Layer 1: Frontend ──
    rect1 = FancyBboxPatch((1, 8), 12, 2, boxstyle="round,pad=0.2",
                           facecolor='#EBF8FF', edgecolor=BLUE, linewidth=2)
    ax.add_patch(rect1)
    ax.text(7, 9.5, 'Couche Presentation (Frontend)', ha='center', fontsize=12,
            fontweight='bold', color=BLUE)
    ax.text(7, 8.9, 'React 18 + TypeScript + Material UI + Vite', ha='center',
            fontsize=9, color=DARK)
    ax.text(7, 8.4, 'react-force-graph-3d (WebGL / Three.js)', ha='center',
            fontsize=9, color=GRAY)

    # Arrow down
    ax.annotate('', xy=(7, 7.7), xytext=(7, 7.95),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=2))
    ax.text(8.5, 7.75, 'HTTP REST / WebSocket', fontsize=8, color=GRAY, style='italic')

    # ── Layer 2: Backend ──
    rect2 = FancyBboxPatch((1, 4), 12, 3.5, boxstyle="round,pad=0.2",
                           facecolor='#FFFFF0', edgecolor=BLUE, linewidth=2)
    ax.add_patch(rect2)
    ax.text(7, 7.1, 'Couche Metier (Backend)', ha='center', fontsize=12,
            fontweight='bold', color=BLUE)
    ax.text(7, 6.5, 'FastAPI + Uvicorn (API REST + WebSocket)', ha='center',
            fontsize=9, color=DARK)

    # Sub-boxes
    ml_box = FancyBboxPatch((1.8, 4.5), 3.5, 1.6, boxstyle="round,pad=0.15",
                            facecolor=LIGHT_CYAN, edgecolor=BLUE, linewidth=1)
    ax.add_patch(ml_box)
    ax.text(3.55, 5.8, 'Moteur ML', ha='center', fontsize=9, fontweight='bold', color=DARK)
    ax.text(3.55, 5.35, 'PageRank | TF-IDF', ha='center', fontsize=7.5, color=DARK)
    ax.text(3.55, 4.95, 'Collab. Filtering', ha='center', fontsize=7.5, color=DARK)

    auth_box = FancyBboxPatch((5.8, 4.5), 3, 1.6, boxstyle="round,pad=0.15",
                              facecolor='#FED7D7', edgecolor=BLUE, linewidth=1)
    ax.add_patch(auth_box)
    ax.text(7.3, 5.8, 'Auth + RBAC', ha='center', fontsize=9, fontweight='bold', color=DARK)
    ax.text(7.3, 5.35, 'JWT (HS256)', ha='center', fontsize=7.5, color=DARK)
    ax.text(7.3, 4.95, 'bcrypt + Rate Limit', ha='center', fontsize=7.5, color=DARK)

    bd_box = FancyBboxPatch((9.3, 4.5), 3.5, 1.6, boxstyle="round,pad=0.15",
                            facecolor='#E9D8FD', edgecolor=BLUE, linewidth=1)
    ax.add_patch(bd_box)
    ax.text(11.05, 5.8, 'Big Data', ha='center', fontsize=9, fontweight='bold', color=DARK)
    ax.text(11.05, 5.35, 'Kafka Simulator', ha='center', fontsize=7.5, color=DARK)
    ax.text(11.05, 4.95, 'PySpark Batch', ha='center', fontsize=7.5, color=DARK)

    # Arrow down
    ax.annotate('', xy=(7, 3.7), xytext=(7, 3.95),
                arrowprops=dict(arrowstyle='->', color=DARK, lw=2))
    ax.text(8.5, 3.75, 'Bolt (Cypher) / File I/O', fontsize=8, color=GRAY, style='italic')

    # ── Layer 3: Data ──
    rect3 = FancyBboxPatch((1, 1.5), 12, 2, boxstyle="round,pad=0.2",
                           facecolor='#F0FFF4', edgecolor=BLUE, linewidth=2)
    ax.add_patch(rect3)
    ax.text(7, 3.1, 'Couche Donnees', ha='center', fontsize=12,
            fontweight='bold', color=BLUE)

    neo_box = FancyBboxPatch((2, 1.8), 4.5, 1, boxstyle="round,pad=0.15",
                             facecolor=LIGHT_BLUE, edgecolor=BLUE, linewidth=1)
    ax.add_patch(neo_box)
    ax.text(4.25, 2.3, 'Neo4j 5 (Graph DB)', ha='center', fontsize=9, fontweight='bold', color=DARK)

    json_box = FancyBboxPatch((7.5, 1.8), 4.5, 1, boxstyle="round,pad=0.15",
                              facecolor='#FEFCBF', edgecolor=BLUE, linewidth=1)
    ax.add_patch(json_box)
    ax.text(9.75, 2.3, 'Fichiers JSONL', ha='center', fontsize=9, fontweight='bold', color=DARK)

    save_fig(fig, 'architecture_diagram')


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print("Generating Nexora UML diagrams...")
    generate_usecase_diagram()
    generate_class_diagram()
    generate_sequence_auth()
    generate_sequence_recommend()
    generate_sequence_pagerank()
    generate_graph_schema()
    generate_architecture()
    print("\nAll diagrams generated successfully!")
