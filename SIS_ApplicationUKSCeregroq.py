import streamlit as st
import json
import base64
import requests
import urllib.parse
import re
import time
from datetime import datetime
from openai import OpenAI
import streamlit.components.v1 as components

# =============================================================================
# 0. GLOBAL CONFIGURATION & SESSION DATE (FEBRUARY 24, 2026)
# =============================================================================
SYSTEM_DATE = "February 24, 2026"
VERSION_STRING = "v22.6.5-SEQUENTIAL-SYNERGY-ARCHITECTURE-ULTRA"

st.set_page_config(
    page_title=f"SIS Universal Knowledge Synthesizer - {SYSTEM_DATE}",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ADVANCED CSS: OBLITERATING SIDEBAR ARTIFACTS & FORCING VISIBILITY ---
# Targets the 'keyboard_double_arrow_right' text artifact and low contrast explorer.
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Fira+Code:wght@400;500&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    /* 1. OBLITERATE ARROW ARTIFACTS & SIDEBAR ICONS */
    /* This aggressively removes the Material Design text leaks from Streamlit's sidebar */
    [data-testid="stSidebar"] [data-testid="stIcon"],
    [data-testid="stSidebar"] button[data-testid="stSidebarCollapseButton"],
    [data-testid="stSidebar"] .st-emotion-cache-16idsys,
    [data-testid="stSidebar"] .st-emotion-cache-6qob1r,
    [data-testid="stSidebar"] span[data-testid="stExpanderIcon"],
    [data-testid="stSidebar"] svg[class*="st-emotion-cache"] {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
        height: 0 !important;
        opacity: 0 !important;
    }

    /* 2. FORCE SIDEBAR VISIBILITY & HIGH CONTRAST */
    [data-testid="stSidebar"] {
        background-color: #fcfcfc !important;
        border-right: 2px solid #e9ecef !important;
        min-width: 380px !important;
    }

    /* Target Knowledge Explorer and all sidebar text to be sharp black/navy */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] .stMarkdown li,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stExpander p,
    [data-testid="stSidebar"] .stExpander li,
    [data-testid="stSidebar"] .stMarkdown span {
        color: #001219 !important; /* Maximum Contrast Navy-Black */
        font-size: 0.98em !important;
        font-weight: 500 !important;
        line-height: 1.6 !important;
        opacity: 1 !important;
    }

    /* 3. RE-STYLE EXPANDERS FOR CLEAR DISTINCTION */
    .stExpander {
        background-color: #ffffff !important;
        border: 1px solid #d8e2dc !important;
        border-radius: 12px !important;
        margin-bottom: 12px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }
    
    .stExpander details summary p {
        color: #1d3557 !important;
        font-weight: 800 !important;
        font-size: 1.05em !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* 4. CONTENT HIGHLIGHTING & NAVIGATION */
    .semantic-node-highlight {
        color: #2a9d8f;
        font-weight: bold;
        border-bottom: 2px solid #2a9d8f;
        padding: 0 2px;
        background-color: #f0fdfa;
        border-radius: 4px;
        transition: all 0.3s ease;
        text-decoration: none !important;
    }
    .semantic-node-highlight:hover {
        background-color: #ccfbf1;
        color: #264653;
        border-bottom: 2px solid #e76f51;
    }
    
    .author-search-link {
        color: #1d3557;
        font-weight: bold;
        text-decoration: none;
        border-bottom: 1px double #457b9d;
        padding: 0 1px;
    }
    .author-search-link:hover {
        color: #e63946;
        background-color: #f1faee;
    }
    
    .google-icon {
        font-size: 0.75em;
        vertical-align: super;
        margin-left: 2px;
        color: #457b9d;
        opacity: 0.8;
    }

    .stMarkdown {
        line-height: 1.9;
        font-size: 1.05em;
    }

    /* 5. ARCHITECTURAL FOCUS BOXES */
    .metamodel-box {
        padding: 25px;
        border-radius: 15px;
        background-color: #f8f9fa;
        border-left: 8px solid #00B0F0;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .mental-approach-box {
        padding: 25px;
        border-radius: 15px;
        background-color: #f0f7ff;
        border-left: 8px solid #6366f1;
        margin-bottom: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    
    .main-header-gradient {
        background: linear-gradient(90deg, #1d3557, #457b9d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.8rem;
    }

    .date-badge {
        background-color: #1d3557;
        color: white;
        padding: 12px 20px;
        border-radius: 50px;
        font-size: 1em;
        font-weight: 800;
        margin-bottom: 30px;
        display: block;
        text-align: center;
        box-shadow: 0 4px 15px rgba(29, 53, 87, 0.3);
        letter-spacing: 1px;
    }

    .sidebar-logo-container {
        display: flex;
        justify-content: center;
        padding: 10px 0;
        margin-bottom: 5px;
    }

    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        transition: all 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

def get_svg_base64(svg_str):
    """Utility to encode SVG for display in the Streamlit sidebar."""
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

# --- LOGOTIP: ORIGINAL 3D RELIEF (PYRAMID & TREE EXACT RESTORATION) ---
SVG_3D_RELIEF = """
<svg width="240" height="240" viewBox="0 0 240 240" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <filter id="reliefShadow" x="-20%" y="-20%" width="150%" height="150%">
            <feDropShadow dx="4" dy="4" stdDeviation="3" flood-color="#000" flood-opacity="0.4"/>
        </filter>
        <linearGradient id="pyramidSide" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#e0e0e0;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#bdbdbd;stop-opacity:1" />
        </linearGradient>
        <linearGradient id="treeGrad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" style="stop-color:#66bb6a;stop-opacity:1" />
            <stop offset="100%" style="stop-color:#2e7d32;stop-opacity:1" />
        </linearGradient>
    </defs>
    <circle cx="120" cy="120" r="100" fill="#f0f0f0" stroke="#000000" stroke-width="4" filter="url(#reliefShadow)" />
    <path d="M120 40 L50 180 L120 200 Z" fill="url(#pyramidSide)" />
    <path d="M120 40 L190 180 L120 200 Z" fill="#9e9e9e" />
    <rect x="116" y="110" width="8" height="70" rx="2" fill="#5d4037" />
    <circle cx="120" cy="85" r="30" fill="url(#treeGrad)" filter="url(#reliefShadow)" />
    <circle cx="95" cy="125" r="22" fill="#43a047" filter="url(#reliefShadow)" />
    <circle cx="145" cy="125" r="22" fill="#43a047" filter="url(#reliefShadow)" />
    <rect x="70" y="170" width="20" height="12" rx="2" fill="#1565c0" filter="url(#reliefShadow)" />
    <rect x="150" y="170" width="20" height="12" rx="2" fill="#c62828" filter="url(#reliefShadow)" />
    <rect x="110" y="185" width="20" height="12" rx="2" fill="#f9a825" filter="url(#reliefShadow)" />
</svg>
"""

# =============================================================================
# 1. CORE RENDERING ENGINES & DATA RETRIEVAL
# =============================================================================

def render_cytoscape_network(elements, container_id="cy_synergy_ultra_final"):
    """Interactive Cytoscape.js engine for high-density interdisciplinary synergy graphs."""
    cyto_html = f"""
    <div style="position: relative; width: 100%;">
        <button id="save_btn" style="position: absolute; top: 15px; right: 15px; z-index: 1000; padding: 12px 18px; background: #2a9d8f; color: white; border: none; border-radius: 8px; cursor: pointer; font-family: sans-serif; font-size: 13px; font-weight: 800; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">💾 EXPORT GRAPH PNG</button>
        <div id="{container_id}" style="width: 100%; height: 800px; background: #ffffff; border-radius: 20px; border: 1px solid #e0e0e0; box-shadow: 0 8px 30px rgba(0,0,0,0.06);"></div>
    </div>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.26.0/cytoscape.min.js"></script>
    <script>
        document.addEventListener('DOMContentLoaded', function() {{
            var cy = cytoscape({{
                container: document.getElementById('{container_id}'),
                elements: {json.dumps(elements)},
                style: [
                    {{
                        selector: 'node',
                        style: {{
                            'label': 'data(label)', 
                            'text-valign': 'center', 
                            'color': '#212529',
                            'background-color': 'data(color)', 
                            'width': 'data(size)', 
                            'height': 'data(size)',
                            'shape': 'data(shape)', 
                            'font-size': '14px', 
                            'font-weight': '700',
                            'text-outline-width': 2, 
                            'text-outline-color': '#ffffff',
                            'cursor': 'pointer', 
                            'z-index': 'data(z_index)',
                            'box-shadow': '0 4px 6px rgba(0,0,0,0.1)'
                        }}
                    }},
                    {{
                        selector: 'edge',
                        style: {{
                            'width': 5, 
                            'line-color': '#adb5bd', 
                            'label': 'data(rel_type)',
                            'font-size': '11px', 
                            'font-weight': 'bold', 
                            'color': '#2a9d8f',
                            'target-arrow-color': '#adb5bd', 
                            'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier', 
                            'text-rotation': 'autorotate',
                            'text-background-opacity': 1, 
                            'text-background-color': '#ffffff',
                            'text-background-padding': '4px',
                            'text-background-shape': 'roundrectangle'
                        }}
                    }},
                    {{
                        selector: 'node.highlighted',
                        style: {{
                            'border-width': 6,
                            'border-color': '#e76f51',
                            'transform': 'scale(1.45)',
                            'z-index': 10000,
                            'font-size': '22px'
                        }}
                    }},
                    {{
                        selector: '.dimmed',
                        style: {{
                            'opacity': 0.08,
                            'text-opacity': 0
                        }}
                    }}
                ],
                layout: {{ 
                    name: 'cose', 
                    padding: 80, 
                    animate: true, 
                    nodeRepulsion: 50000, 
                    idealEdgeLength: 220 
                }}
            }});

            cy.on('mouseover', 'node', function(e){{
                var sel = e.target;
                cy.elements().addClass('dimmed');
                sel.neighborhood().add(sel).removeClass('dimmed').addClass('highlighted');
            }});
            
            cy.on('mouseout', 'node', function(e){{
                cy.elements().removeClass('dimmed highlighted');
            }});
            
            cy.on('tap', 'node', function(evt){{
                var elementId = evt.target.id();
                var target = window.parent.document.getElementById(elementId);
                if (target) {{
                    target.scrollIntoView({{behavior: "smooth", block: "center"}});
                    target.style.backgroundColor = "#fff9db";
                    setTimeout(function(){{ target.style.backgroundColor = "transparent"; }}, 3500);
                }}
            }});

            document.getElementById('save_btn').addEventListener('click', function() {{
                var png64 = cy.png({{full: true, bg: 'white', scale: 2.5}});
                var link = document.createElement('a');
                link.href = png64;
                link.download = 'sis_universal_synergy_graph.png';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }});
        }});
    </script>
    """
    components.html(cyto_html, height=850)

def fetch_author_bibliographies(author_input):
    """Retrieves high-fidelity bibliographic data from ORCID and Semantic Scholar with publication years."""
    if not author_input: return ""
    author_list = [a.strip() for a in author_input.split(",")]
    comprehensive_biblio = ""
    headers = {"Accept": "application/json"}
    
    for auth in author_list:
        orcid_id = None
        try:
            s_res = requests.get(f"https://pub.orcid.org/v3.0/search/?q={auth}", headers=headers, timeout=6).json()
            if s_res.get('result'):
                orcid_id = s_res['result'][0]['orcid-identifier']['path']
        except: pass

        if orcid_id:
            try:
                r_res = requests.get(f"https://pub.orcid.org/v3.0/{orcid_id}/record", headers=headers, timeout=6).json()
                works = r_res.get('activities-summary', {}).get('works', {}).get('group', [])
                comprehensive_biblio += f"\n--- ORCID REPOSITORY: {auth.upper()} ({orcid_id}) ---\n"
                if works:
                    for work in works[:15]:
                        summary = work.get('work-summary', [{}])[0]
                        title = summary.get('title', {}).get('title', {}).get('value', 'Unknown Title')
                        pub_date = summary.get('publication-date')
                        year = pub_date.get('year').get('value', 'n.d.') if pub_date and pub_date.get('year') else "n.d."
                        comprehensive_biblio += f"• [{year}] {title}\n"
                else: comprehensive_biblio += "- No public metadata records found.\n"
            except: pass
        else:
            try:
                ss_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query=author:\"{auth}\"&limit=10&fields=title,year"
                ss_res = requests.get(ss_url, timeout=6).json()
                papers = ss_res.get("data", [])
                if papers:
                    comprehensive_biblio += f"\n--- SCHOLAR DATA: {auth.upper()} ---\n"
                    for p in papers:
                        comprehensive_biblio += f"• [{p.get('year','n.d.')}] {p['title']}\n"
                else: comprehensive_biblio += f"- No record found for identifier: {auth}.\n"
            except: pass
    return comprehensive_biblio

# =============================================================================
# 2. ARCHITECTURAL ONTOLOGIES (IMA & MA) - EXHAUSTIVE EXPANSION
# =============================================================================

HUMAN_THINKING_METAMODEL = {
    "nodes": {
        "Human mental concentration": {
            "color": "#ADB5BD", "shape": "rectangle", 
            "desc": "The foundational state of cognitive focus required for interdisciplinary synthesis and logical rigor."
        },
        "Identity": {
            "color": "#C6EFCE", "shape": "rectangle", 
            "desc": "The subjective core of the researcher or agent, containing professional ethical parameters and specialized lenses."
        },
        "Autobiographical memory": {
            "color": "#C6EFCE", "shape": "rectangle", 
            "desc": "The historical database of past cycles influencing current logic."
        },
        "Mission": {
            "color": "#92D050", "shape": "rectangle", 
            "desc": "The high-level existential imperative driving the direction of inquiry and synthesis."
        },
        "Vision": {
            "color": "#FFFF00", "shape": "rectangle", 
            "desc": "Mental simulation of a desired future state acting as a magnetic pull for goal-setting."
        },
        "Goal": {
            "color": "#00B0F0", "shape": "rectangle", 
            "desc": "Quantifiable milestones materialize the mission within reality."
        },
        "Problem": {
            "color": "#F2DCDB", "shape": "rectangle", 
            "desc": "Obstruction preventing goal realization; gap between current and target state."
        },
        "Ethics/moral": {
            "color": "#FFC000", "shape": "rectangle", 
            "desc": "Value system filtering solution validity."
        },
        "Hierarchy of interests": {
            "color": "#F8CBAD", "shape": "rectangle", 
            "desc": "Ordering of needs dictating resource allocation."
        },
        "Rule": {
            "color": "#F2F2F2", "shape": "rectangle", 
            "desc": "Structural, logical, and legal constraints governing node interactions."
        },
        "Decision-making": {
            "color": "#FFFF99", "shape": "rectangle", 
            "desc": "Choosing efficient selection pathways toward goal achievement."
        },
        "Problem solving": {
            "color": "#D9D9D9", "shape": "rectangle", 
            "desc": "Algorithmic process removing obstructions."
        },
        "Conflict situation": {
            "color": "#00FF00", "shape": "rectangle", 
            "desc": "State where multiple goals or rules clash."
        },
        "Knowledge": {
            "color": "#DDEBF7", "shape": "rectangle", 
            "desc": "Internalized facts and theoretical models."
        },
        "Tool": {
            "color": "#00B050", "shape": "rectangle", 
            "desc": "External instruments leveraged to interact with the domain."
        },
        "Experience": {
            "color": "#00B050", "shape": "rectangle", 
            "desc": "Wisdom gained through direct application of knowledge."
        },
        "Classification": {
            "color": "#CCC0DA", "shape": "rectangle", 
            "desc": "Taxonomic act reducing cognitive load."
        },
        "Psychological aspect": {
            "color": "#F8CBAD", "shape": "rectangle", 
            "desc": "Internal outcomes on individual mental states."
        },
        "Sociological aspect": {
            "color": "#00FFFF", "shape": "rectangle", 
            "desc": "External collective impact and social changes."
        }
    },
    "relations": [
        ("Human mental concentration", "Identity", "has"), 
        ("Identity", "Autobiographical memory", "possesses"),
        ("Mission", "Vision", "defines"), 
        ("Vision", "Goal", "leads to"), 
        ("Problem", "Identity", "challenges"),
        ("Rule", "Decision-making", "constrains"), 
        ("Knowledge", "Classification", "organizes"),
        ("Experience", "Psychological aspect", "forms"),
        ("Conflict situation", "Sociological aspect", "triggers"),
        ("Hierarchy of interests", "Goal", "realizes"),
        ("Knowledge", "Tool", "leverages")
    ]
}

MENTAL_APPROACHES_ONTOLOGY = {
    "nodes": {
        "Perspective shifting": {
            "color": "#00FF00", "shape": "diamond", 
            "desc": "Rotating the problem space to see it through different stakeholders or paradigms."
        },
        "Similarity and difference": {
            "color": "#FFFF00", "shape": "diamond", 
            "desc": "The primary act of pattern recognition; identifying anomalies and congruent nodes."
        },
        "Core": {
            "color": "#FFC000", "shape": "diamond", 
            "desc": "The distillation of a problem into its fundamental, unchanging essence."
        },
        "Attraction": {
            "color": "#F2A6A2", "shape": "diamond", 
            "desc": "The cognitive force drawing disparate concepts together toward novel synergy."
        },
        "Repulsion": {
            "color": "#D9D9D9", "shape": "diamond", 
            "desc": "The logical isolation of incompatible solutions or irrelevant noise."
        },
        "Condensation": {
            "color": "#CCC0DA", "shape": "diamond", 
            "desc": "The compression of complex data sets into singular actionable strategic insights."
        },
        "Framework and foundation": {
            "color": "#F8CBAD", "shape": "diamond", 
            "desc": "Establishing the logical rules and logical boundaries for innovation."
        },
        "Bipolarity and dialectics": {
            "color": "#DDEBF7", "shape": "diamond", 
            "desc": "Synthesis through tension between opposites (Thesis and Antithesis)."
        },
        "Constant": {
            "color": "#E1C1D1", "shape": "diamond", 
            "desc": "Identifying invariants within a system state."
        },
        "Associativity": {
            "color": "#E1C1D1", "shape": "diamond", 
            "desc": "Non-linear knowledge linking across domains."
        },
        "Induction": {
            "color": "#B4C6E7", "shape": "diamond", 
            "desc": "Building interdisciplinary theory from specific observations."
        },
        "Whole and part": {
            "color": "#00FF00", "shape": "diamond", 
            "desc": "Mental zoom logic navigating holistic and granular views."
        },
        "Mini-max": {
            "color": "#00FF00", "shape": "diamond", 
            "desc": "Search for maximum utility with minimum friction."
        },
        "Addition and composition": {
            "color": "#FF00FF", "shape": "diamond", 
            "desc": "Incremental complexity building via layering blocks."
        },
        "Hierarchy": {
            "color": "#C6EFCE", "shape": "diamond", 
            "desc": "Vertical stacking based on priority and causality."
        },
        "Balance": {
            "color": "#00B0F0", "shape": "diamond", 
            "desc": "Equilibrium search between competing innovative variables."
        },
        "Deduction": {
            "color": "#92D050", "shape": "diamond", 
            "desc": "Applying broad laws to solve specific instances."
        },
        "Abstraction and elimination": {
            "color": "#00B0F0", "shape": "diamond", 
            "desc": "Removing noise context to reveal generalizable model."
        },
        "Pleasure and displeasure": {
            "color": "#00FF00", "shape": "diamond", 
            "desc": "Aesthetic evaluative feedback on solution elegance."
        },
        "Openness and closedness": {
            "color": "#FFC000", "shape": "diamond", 
            "desc": "State regarding incorporating external data nodes."
        }
    },
    "relations": [
        ("Perspective shifting", "Similarity and difference", "leads to"),
        ("Core", "Attraction", "initiates"),
        ("Induction", "Whole and part", "links"),
        ("Hierarchy", "Balance", "regulates"),
        ("Deduction", "Abstraction and elimination", "processes"),
        ("Bipolarity and dialectics", "Constant", "stabilizes")
    ]
}

# =============================================================================
# 3. KNOWLEDGE BASE (EXHAUSTIVE 18D SCIENCE FIELDS)
# =============================================================================

KNOWLEDGE_BASE = {
    "User profiles": {
        "Adventurers": {"description": "Explorers of hidden interdisciplinary patterns and high-risk hypotheses."},
        "Applicators": {"description": "Focused on practical efficiency, rapid deployment, and tangible execution."},
        "Know-it-alls": {"description": "Seekers of systemic absolute clarity, comprehensive taxonomy, and complete data."},
        "Observers": {"description": "Passive monitors of systemic dynamics and trend watchers without intervention."}
    },
    "Scientific paradigms": {
        "Empiricism": "Focus on sensory experience, experimental evidence, and observation-driven data.",
        "Rationalism": "Reliance on deductive logic, a priori reasoning, and mathematical certainty.",
        "Constructivism": "Knowledge as a social and cognitive build, dependent on perception.",
        "Positivism": "Strict adherence to verifiable facts and rejection of speculation.",
        "Pragmatism": "Evaluation based on utility and real-world application."
    },
    "Structural models": {
        "Causal Connections": "Chains of cause and effect mapping systemic causality.",
        "Principles & Relations": "Fundamental laws and the inter-relations between entities.",
        "Episodes & Sequences": "Temporal flow, historical timelines, and event ordering.",
        "Facts & Characteristics": "Raw data properties, attributes, and static descriptions.",
        "Generalizations": "Broad frameworks and high-level theoretical models.",
        "Glossary": "Precise definitions and terminological clarity.",
        "Concepts": "Abstract constructs and conceptual building blocks."
    },
    "Science fields": {
        "Mathematics": {
            "cat": "Formal", 
            "methods": ["Axiomatization", "Formal Proof", "Stochastic Modeling", "Calculus"], 
            "tools": ["MATLAB", "LaTeX", "WolframAlpha", "TensorFlow"], 
            "facets": ["Topology", "Algebra", "Number Theory", "Analysis"]
        },
        "Physics": {
            "cat": "Natural", 
            "methods": ["Quantum Modeling", "Particle Tracking", "Interferometry", "Simulation"], 
            "tools": ["Accelerator", "Spectrometer", "Oscilloscopes", "Cryostats"], 
            "facets": ["Relativity", "Quantum Mechanics", "Thermodynamics", "Optics"]
        },
        "Chemistry": {
            "cat": "Natural", 
            "methods": ["Synthesis", "Titration", "Chromatography", "Mass Spec"], 
            "tools": ["NMR", "Incubators", "Centrifuge", "Burettes"], 
            "facets": ["Biochemistry", "Organic", "Physical", "Analytical"]
        },
        "Biology": {
            "cat": "Natural", 
            "methods": ["CRISPR", "Gene Sequencing", "Cell Culture", "In-vivo observation"], 
            "tools": ["Electron Microscope", "PCR Machine", "Petri Dishes", "Autoclave"], 
            "facets": ["Genetics", "Microbiology", "Ecology", "Cell Biology"]
        },
        "Neuroscience": {
            "cat": "Natural", 
            "methods": ["Neuroimaging", "Optogenetics", "Behavioral Mapping", "Electrophysiology"], 
            "tools": ["fMRI", "EEG", "Patch Clamp", "Calcium Imaging"], 
            "facets": ["Neural Plasticity", "Synaptic Physiology", "Cognitive Neuroscience"]
        },
        "Psychology": {
            "cat": "Social", 
            "methods": ["Double-Blind Trials", "Psychometrics", "Longitudinal Studies", "Meta-Analysis"], 
            "tools": ["Standardized Tests", "Surveys", "Biofeedback", "Eye-tracking"], 
            "facets": ["Behavioral", "Clinical", "Developmental", "Cognitive Psychology"]
        },
        "Sociology": {
            "cat": "Social", 
            "methods": ["Ethnography", "Network Analysis", "Survey Design", "Grounded Theory"], 
            "tools": ["NVivo", "SPSS", "Census Data", "Social Graphs"], 
            "facets": ["Demography", "Stratification", "Dynamics", "Urban Sociology"]
        },
        "Computer Science": {
            "cat": "Formal", 
            "methods": ["Algorithm Design", "Formal Verification", "Complexity Analysis", "Parallelism"], 
            "tools": ["GPU Clusters", "Docker", "Compilers", "IDEs", "Kubernetes"], 
            "facets": ["AI", "Cybersecurity", "Blockchain", "Quantum Computing"]
        },
        "Medicine": {
            "cat": "Applied", 
            "methods": ["Clinical Trials", "Epidemiology", "Radiology", "Pathology"], 
            "tools": ["MRI", "CT Scanner", "Biomarker Assays", "Ultrasound"], 
            "facets": ["Genomics", "Immunology", "Oncology", "Pharmacology"]
        },
        "Engineering": {
            "cat": "Applied", 
            "methods": ["Finite Element Analysis", "Prototyping", "Stress Testing", "Systems Integration"], 
            "tools": ["CAD", "3D Printers", "CNC Machines", "Circuit Simulators"], 
            "facets": ["Robotics", "Nanotechnology", "Civil Eng", "Electrical Eng"]
        },
        "Legal science": {
            "cat": "Social", 
            "methods": ["Legal Hermeneutics", "Comparative Law", "Dogmatic Method", "Jurisprudence"], 
            "tools": ["Legislative DB", "Westlaw", "Case Archives", "LexisNexis"], 
            "facets": ["Jurisprudence", "Criminal Law", "Constitutional", "Civil Law"]
        },
        "Economics": {
            "cat": "Social", 
            "methods": ["Econometrics", "Game Theory", "Macro Equilibrium Modeling", "Forecasting"], 
            "tools": ["Bloomberg", "Stata", "R", "Python Pandas"], 
            "facets": ["Finance", "Behavioral Econ", "Macroeconomics", "Microeconomics"]
        },
        "Philosophy": {
            "cat": "Humanities", 
            "methods": ["Socratic Method", "Dialectics", "Phenomenology", "Conceptual Analysis"], 
            "tools": ["Logic Mapping", "Primary Texts", "Semantic Analysis"], 
            "facets": ["Epistemology", "Ethics", "Metaphysics", "Aesthetics"]
        },
        "Linguistics": {
            "cat": "Humanities", 
            "methods": ["Corpus Analysis", "Syntactic Parsing", "Historical Phonetics", "Transcription"], 
            "tools": ["Praat", "NLTK", "WordNet", "ELAN"], 
            "facets": ["Semantics", "Phonology", "Sociolinguistics", "CompLing"]
        },
        "Ecology": {
            "cat": "Natural", 
            "methods": ["Remote Sensing", "Trophic Modeling", "Field Sampling", "Biogeochemistry"], 
            "tools": ["GIS", "Biosensors", "Drones", "Satellite Imagery"], 
            "facets": ["Biodiversity", "Conservation Biology", "Restoration Ecology"]
        },
        "History": {
            "cat": "Humanities", 
            "methods": ["Archival Research", "Historiography", "Oral History", "Radiocarbon"], 
            "tools": ["Radiocarbon Dating", "Microfilm", "Digital Archives", "Prosopography"], 
            "facets": ["Military History", "Diplomacy", "Ancient Civilizations", "Social History"]
        },
        "Architecture": {
            "cat": "Applied", 
            "methods": ["Parametric Design", "Environmental Analysis", "BIM", "Urbanism"], 
            "tools": ["Revit", "Rhino 3D", "AutoCAD", "Photogrammetry"], 
            "facets": ["Urban Design", "Sustainability", "Landscape Arch", "Heritage"]
        },
        "Pedagogy": {
            "cat": "Social", 
            "methods": ["Instructional Design", "Action Research", "Differentiated Learning", "Didactics"], 
            "tools": ["LMS", "Interactive Whiteboards", "Portfolios", "E-assessment"], 
            "facets": ["Curriculum Dev", "Educational Psych", "Special Ed", "EdTech"]
        },
        "Geology": {
            "cat": "Natural", 
            "methods": ["Stratigraphy", "Mineralogy", "Seismology", "Petrology"], 
            "tools": ["Seismograph", "GIS", "Magnetometers", "Petrographic Microscope"], 
            "facets": ["Tectonics", "Petrology", "Mineralogy", "Paleontology"]
        },
        "Library Science": {
            "cat": "Applied", 
            "methods": ["Taxonomy", "Archival Appraisal", "Retrieval Logic", "Metadata"], 
            "tools": ["OPAC", "Metadata Systems", "Thesauri", "Digital Archives"], 
            "facets": ["Knowledge Organization", "Information Retrieval", "Digital Curation"]
        }
    }
}

# =============================================================================
# 4. INTERFACE CONSTRUCTION (STREAMLIT SIDEBAR & MAIN)
# =============================================================================

if 'show_user_guide' not in st.session_state: st.session_state.show_user_guide = False

# --- EXPANDED LEFT SIDEBAR: LOGO, ARROW OBLITERATION, & FORCED CONTRAST ---
with st.sidebar:
    # 1. Restored Original 3D Relief Logo (fixed dimensions for perfect alignment)
    st.markdown(f'<div class="sidebar-logo-container"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    
    # 2. Hardcoded Session Date Badge
    st.markdown(f'<div class="date-badge">SESSION DATE: {SYSTEM_DATE}</div>', unsafe_allow_html=True)
    
    st.header("⚙️ SYSTEM CONTROL")
    
    # DUAL API ACCESS (Sequential synergy inputs)
    st.subheader("🔑 Dual API Synergy Keys")
    groq_api_key = st.text_input("Groq Key (Phase 1 Synthesis):", type="password", help="Builds structural research foundation using IMA logic.")
    cerebras_api_key = st.text_input("Cerebras Key (Phase 2 Ideas):", type="password", help="Generates innovations and mapping using MA logic.")
    
    # INTERACTIVE BUTTONS
    st.divider()
    col_res, col_gui = st.columns(2)
    with col_res:
        if st.button("♻️ RESET"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()
    with col_gui:
        if st.button("📖 GUIDE"):
            st.session_state.show_user_guide = not st.session_state.show_user_guide
            st.rerun()
            
    # EXTERNAL CONNECTOR BUTTONS (The previously missing link objects)
    st.divider()
    st.subheader("🌐 EXTERNAL CONNECTORS")
    st.link_button("📂 GitHub Repository", "https://github.com/", use_container_width=True)
    st.link_button("🆔 ORCID Registry", "https://orcid.org/", use_container_width=True)
    st.link_button("🎓 Google Scholar", "https://scholar.google.com/", use_container_width=True)
    
    # KNOWLEDGE EXPLORER (FORCED HIGH CONTRAST VIA CSS TARGETING)
    st.divider()
    st.subheader("📚 KNOWLEDGE EXPLORER")
    with st.expander("👤 User Profile Ontologies", expanded=False):
        for profile, data in KNOWLEDGE_BASE["User profiles"].items(): 
            st.markdown(f"**{profile}**: {data['description']}")
            
    with st.expander("🧠 Mental Approach (MA) Map", expanded=False):
        for approach, details in MENTAL_APPROACHES_ONTOLOGY["nodes"].items(): 
            st.markdown(f"• **{approach}**: {details['desc']}")
            
    with st.expander("🏛️ Metamodel (IMA) Structures", expanded=False):
        for node, details in HUMAN_THINKING_METAMODEL["nodes"].items(): 
            st.markdown(f"• **{node}**: {details['desc']}")
            
    with st.expander("🌍 Scientific Paradigm Definitions", expanded=False):
        for paradigm, desc in KNOWLEDGE_BASE["Scientific paradigms"].items(): 
            st.markdown(f"**{paradigm}**: {desc}")
            
    with st.expander("🔬 Science Field Taxonomy", expanded=False):
        for science in sorted(KNOWLEDGE_BASE["Science fields"].keys()): 
            st.markdown(f"• **{science}**")
            
    with st.expander("🏗️ Structural Model Context", expanded=False):
        for model, desc in KNOWLEDGE_BASE["Structural models"].items(): 
            st.markdown(f"**{model}**: {desc}")

# --- MAIN PAGE ---
st.markdown('<h1 class="main-header-gradient">🧱 SIS Universal Knowledge Synthesizer</h1>', unsafe_allow_html=True)
st.markdown(f"**Sequential Multi-Model Synergy** | Operating Session: **{SYSTEM_DATE}**")

if st.session_state.show_user_guide:
    st.info(f"""
    **Sequential Synergy Pipeline Workflow (Feb 2026):**
    1. **Key Input**: Enter both Groq (Phase 1) and Cerebras (Phase 2) API keys in the sidebar.
    2. **Research Foundation (Step 1)**: Groq builds the foundational dissertation using Integrated Metamodel Architecture (IMA).
    3. **Innovation Prompt (Step 2)**: Cerebras takes Groq's work and generates 'Useful Innovative Ideas' using Mental Approaches (MA) logic.
    4. **Visualization**: The interactive 18D graph maps structural facts against generative ideas.
    5. **Artifact Fix**: The arrow artifacts and contrast issues in the sidebar are resolved in this version.
    """)

# REFERENCE ARCHITECTURE BOXES
col_ref1, col_ref2 = st.columns(2)
with col_ref1:
    st.markdown("""<div class="metamodel-box"><b>🏛️ Phase 1: Groq (IMA Architecture)</b><br>Structural reasoning building the factual foundation. Focus: Identity, Mission, Problem. </div>""", unsafe_allow_html=True)
with col_ref2:
    st.markdown("""<div class="mental-approach-box"><b>🧠 Phase 2: Cerebras (MA Architecture)</b><br>Cognitive transformation generating innovative solutions. Focus: Dialectics, Perspective, Induction.</div>""", unsafe_allow_html=True)

st.markdown("### 🛠️ CONFIGURE SYNERGY PIPELINE")

# CONFIG ROW 1
r1c1, r1c2, r1c3 = st.columns([1.5, 2, 1])
with r1c1:
    target_authors = st.text_input("👤 Authors for ORCID Analysis:", placeholder="Karl Petrič, Samo Kralj, Teodor Petrič")
with r1c2:
    sel_sciences = st.multiselect("2. Select Science Fields:", sorted(list(KNOWLEDGE_BASE["Science fields"].keys())), default=["Physics", "Psychology", "Sociology"])
with r1c3:
    expertise = st.select_slider("3. Expertise Level:", ["Novice", "Intermediate", "Expert"], value="Expert")

# CONFIG ROW 2
r2c1, r2c2, r2c3 = st.columns(3)
with r2c1:
    sel_paradigms = st.multiselect("4. Scientific Paradigms:", list(KNOWLEDGE_BASE["Scientific paradigms"].keys()), default=["Rationalism"])
with r2c2:
    sel_models = st.multiselect("5. Structural Models:", list(KNOWLEDGE_BASE["Structural models"].keys()), default=["Concepts"])
with r2c3:
    goal_context = st.selectbox("6. Strategic Project Goal:", ["Scientific Research", "Problem Solving", "Educational", "Policy Making"])

st.divider()

# DUAL INQUIRY INTERFACE
col_inq1, col_inq2, col_inq3 = st.columns([2, 2, 1])
with col_inq1:
    user_query = st.text_area("❓ STEP 1: Research Inquiry (for GROQ):", placeholder="Fact-based Foundational Inquiry for structural synthesis...", height=220)
with col_inq2:
    idea_query = st.text_area("💡 STEP 2: Innovation Prompt (for CEREBRAS):", placeholder="Targets for innovative idea production based on Phase 1...", height=220)
with col_inq3:
    uploaded_file = st.file_uploader("📂 ATTACH DATA (.txt only):", type=['txt'], help="Context for both AI engines.")
    file_content = ""
    if uploaded_file: 
        file_content = uploaded_file.read().decode("utf-8")
        st.success(f"Context from {uploaded_file.name} integrated.")

# =============================================================================
# 5. SYNERGY EXECUTION ENGINE (GROQ -> CEREBRAS PIPELINE)
# =============================================================================

if st.button("🚀 EXECUTE MULTI-DIMENSIONAL SEQUENTIAL SYNERGY PIPELINE", use_container_width=True):
    if not groq_api_key or not cerebras_api_key:
        st.error("❌ Dual-Model synergy requires both Groq and Cerebras keys.")
    elif not user_query:
        st.warning("⚠️ Phase 1 Research Inquiry is required to build the foundation.")
    else:
        try:
            # Init Clients
            groq_client = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
            cerebras_client = OpenAI(api_key=cerebras_api_key, base_url="https://api.cerebras.ai/v1")
            
            # Fetch Metadata
            biblio = fetch_author_bibliographies(target_authors) if target_authors else ""

            # --- PHASE 1: GROQ (IMA Synthesis) ---
            with st.spinner('PHASE 1: Groq synthesizing structural foundation (IMA Logic)...'):
                groq_sys_prompt = f"""
                You are the SIS Synthesizer (Phase 1). Perform an exhaustive interdisciplinary dissertation.
                STRICT IMA ARCHITECTURE FOCUS: {json.dumps(HUMAN_THINKING_METAMODEL)}
                
                CONTEXT:
                Date: {SYSTEM_DATE}
                Sciences: {sel_sciences}. Paradigms: {sel_paradigms}. Models: {sel_models}.
                Authors: {biblio}. Data context: {file_content}
                
                Task: Provide a factual, structural research foundation. Do not generate innovations or graphs.
                Emphasis: Identity, Mission, Goals, Problems, and taxonomic knowledge organization.
                """
                
                groq_response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": groq_sys_prompt}, {"role": "user", "content": user_query}],
                    temperature=0.4
                )
                groq_synthesis = groq_response.choices[0].message.content

            # --- PHASE 2: CEREBRAS (MA Innovation + Graph JSON) ---
            with st.spinner('PHASE 2: Cerebras producing innovative ideas and semantic mapping (MA Logic)...'):
                cerebras_sys_prompt = f"""
                You are the SIS Innovation Engine (Phase 2). 
                STRICT MENTAL APPROACHES (MA) FOCUS: {json.dumps(MENTAL_APPROACHES_ONTOLOGY)}
                
                TASK:
                1. Review the RESEARCH FOUNDATION provided by your partner model (Groq).
                2. Apply MA logic (Dialectics, Perspective Shifting, Core) to generate 'Useful Innovative Ideas'.
                3. End your response with '### SEMANTIC_GRAPH_JSON' followed by a valid JSON network (40-60 nodes).
                
                Visual Rules: 
                - IMA nodes (rectangles) for structural/factual concepts.
                - MA nodes (diamonds) for cognitive filters and generative steps.
                - Use colors provided in the ontology dictionaries.
                
                JSON schema: {{"nodes": [{{"id": "n1", "label": "Text", "type": "Root|Branch", "color": "#hex", "shape": "rectangle|diamond"}}], "edges": [{{"source": "n1", "target": "n2", "rel_type": "BT|NT|AS"}}]}}
                """
                
                cerebras_prompt = f"GROQ RESEARCH FOUNDATION (FOUNDATION):\n{groq_synthesis}\n\nUSER INNOVATION REQUEST (GOAL):\n{idea_query}"
                
                # FIXED MODEL NAME FOR CEREBRAS llama3.1-70b
                cerebras_response = cerebras_client.chat.completions.create(
                    model="llama3.1-70b", 
                    messages=[{"role": "system", "content": cerebras_sys_prompt}, {"role": "user", "content": cerebras_prompt}],
                    temperature=0.85
                )
                cerebras_innovation = cerebras_response.choices[0].message.content

            # --- COMBINING AND RENDERING ---
            combined_output = f"## 📚 Phase 1: Research Foundation (Groq)\n{groq_synthesis}\n\n---\n## 💡 Phase 2: Useful Innovative Ideas (Cerebras)\n{cerebras_innovation}"
            
            parts = combined_output.split("### SEMANTIC_GRAPH_JSON")
            main_markdown = parts[0]
            
            # Semantic Processing (Google Links + Anchor linking)
            if len(parts) > 1:
                try:
                    g_json = json.loads(re.search(r'\{.*\}', parts[1], re.DOTALL).group())
                    for n in g_json.get("nodes", []):
                        lbl, nid = n["label"], n["id"]
                        g_url = urllib.parse.quote(lbl)
                        pattern = re.compile(re.escape(lbl), re.IGNORECASE)
                        replacement = f'<span id="{nid}"><a href="https://www.google.com/search?q={g_url}" target="_blank" class="semantic-node-highlight">{lbl}<i class="google-icon">↗</i></a></span>'
                        main_markdown = pattern.sub(replacement, main_markdown, count=1)
                except: pass

            st.subheader("📊 INTEGRATED PIPELINE RESULTS")
            st.markdown(main_markdown, unsafe_allow_html=True)

            # Interactive Graph Visualization
            if len(parts) > 1:
                try:
                    g_json = json.loads(re.search(r'\{.*\}', parts[1], re.DOTALL).group())
                    st.subheader("🕸️ INTEGRATED SEQUENTIAL SEMANTIC NETWORK")
                    st.caption(f"Mapped by Cerebras on {SYSTEM_DATE} based on Groq Research Synthesis.")
                    
                    elements = []
                    for n in g_json.get("nodes", []):
                        level = n.get("type", "Branch")
                        size = 110 if level == "Root" else 90
                        elements.append({"data": {
                            "id": n["id"], "label": n["label"], "color": n.get("color", "#2a9d8f"),
                            "size": size, "shape": n.get("shape", "rectangle"), "z_index": 1
                        }})
                    for e in g_json.get("edges", []):
                        elements.append({"data": {
                            "source": e["source"], "target": e["target"], "rel_type": e.get("rel_type", "AS")
                        }})
                    render_cytoscape_network(elements, "viz_synergy_final_900")
                except: st.warning("⚠️ Warning: Semantic Graph JSON could not be rendered.")

            if biblio:
                with st.expander("📚 EXTENDED BIBLIOGRAPHIC METADATA"):
                    st.text(biblio)

        except Exception as e:
            st.error(f"❌ Sequential Synergy Failure: {e}")

# =============================================================================
# 6. FOOTER & METRICS
# =============================================================================
st.divider()
st.caption(f"SIS Universal Knowledge Synthesizer | {VERSION_STRING} | {SYSTEM_DATE}")
st.write("")
st.write("")





















