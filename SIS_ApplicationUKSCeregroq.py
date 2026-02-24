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
# 0. GLOBAL CONFIGURATION & SYSTEM TIMESTAMP (FEBRUARY 24, 2026)
# =============================================================================
SYSTEM_DATE = "February 24, 2026"
VERSION_ID = "v22.5.0 Sequential-Synergy-Final-850"

st.set_page_config(
    page_title=f"SIS Universal Knowledge Synthesizer - {SYSTEM_DATE}",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Deep CSS Integration to fix Sidebar visibility, text contrast, and icon artifacts.
# Aggressively removes 'keyboard_double_arrow_right' and forces high-contrast Explorer readability.
st.markdown("""
<style>
  /* 1. OBLITERATE THE KEYBOARD ARROW ARTIFACT */
    /* This hides the specific text and icon containers that glitch in the sidebar */
    [data-testid="stSidebar"] [data-testid="stIcon"], 
    [data-testid="stSidebar"] span[data-testid="stExpanderIcon"],
    [data-testid="stSidebar"] .st-emotion-cache-16idsys {
        display: none !important;
        visibility: hidden !important;
        width: 0 !important;
    }

    /* 2. FIX KNOWLEDGE EXPLORER VISIBILITY */
    /* This forces the text to be deep navy/black so it is no longer "badly visible" */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] .stMarkdown li,
    [data-testid="stSidebar"] label {
        color: #001219 !important; /* Deep high-contrast navy */
        font-size: 1rem !important;
        font-weight: 500 !important;
        opacity: 1 !important;
    }

    /* 3. ENSURE EXPANDER HEADERS ARE READABLE */
    .stExpander details summary p {
        color: #1d3557 !important;
        font-weight: 700 !important;
    }
    
    /* Forcing high-contrast text in Knowledge Explorer for perfect readability */
    [data-testid="stSidebar"] .stMarkdown p, 
    [data-testid="stSidebar"] .stMarkdown li,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stExpander p {
        color: #001219 !important;
        font-size: 0.98em !important;
        font-weight: 500 !important;
        line-height: 1.6;
        opacity: 1 !important;
    }

    /* Re-styling Expander for deep contrast and clear hierarchy */
    .st-emotion-cache-p3y65y, .stExpander {
        background-color: #ffffff !important;
        border: 1px solid #d8e2dc !important;
        border-radius: 12px !important;
        margin-bottom: 10px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.04);
    }
    
    .stExpander details summary p {
        color: #1d3557 !important;
        font-weight: 700 !important;
        font-size: 1.05em !important;
    }

    /* --- SYNTHESIS CONTENT & HIGHLIGHTING --- */
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

    /* --- ARCHITECTURAL FOCUS BOXES --- */
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
        padding: 10px 18px;
        border-radius: 50px;
        font-size: 0.95em;
        font-weight: 700;
        margin-bottom: 30px;
        display: block;
        text-align: center;
        box-shadow: 0 4px 12px rgba(29, 53, 87, 0.25);
        letter-spacing: 1px;
    }

    .sidebar-logo-container {
        display: flex;
        justify-content: center;
        padding: 10px 0;
        margin-bottom: 10px;
    }

    .stButton>button {
        width: 100%;
        border-radius: 10px;
        font-weight: 700;
        text-transform: uppercase;
        transition: all 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

def get_svg_base64(svg_str):
    """Utility to encode SVG for display in the Streamlit sidebar."""
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

# --- LOGOTIP: 3D RELIEF (ORIGINAL RESTORED: PYRAMID & TREE) ---
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
# 1. CORE RENDERING ENGINES & DATA FETCHING
# =============================================================================

def render_cytoscape_network(elements, container_id="cy_synergy_full_pipeline"):
    """Interactive Cytoscape.js engine for high-density 18D graphs."""
    cyto_html = f"""
    <div style="position: relative; width: 100%;">
        <button id="save_btn" style="position: absolute; top: 15px; right: 15px; z-index: 1000; padding: 10px 15px; background: #2a9d8f; color: white; border: none; border-radius: 6px; cursor: pointer; font-family: sans-serif; font-size: 13px; font-weight: bold; box-shadow: 0 3px 6px rgba(0,0,0,0.16);">💾 EXPORT GRAPH PNG</button>
        <div id="{container_id}" style="width: 100%; height: 750px; background: #ffffff; border-radius: 15px; border: 1px solid #e0e0e0; box-shadow: 0 4px 20px rgba(0,0,0,0.08);"></div>
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
                            'font-weight': '600',
                            'text-outline-width': 2, 
                            'text-outline-color': '#ffffff',
                            'cursor': 'pointer', 
                            'z-index': 'data(z_index)'
                        }}
                    }},
                    {{
                        selector: 'edge',
                        style: {{
                            'width': 4, 
                            'line-color': '#ced4da', 
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
                            'text-background-padding': '3px',
                            'text-background-shape': 'roundrectangle'
                        }}
                    }},
                    {{
                        selector: 'node.highlighted',
                        style: {{
                            'border-width': 5,
                            'border-color': '#e76f51',
                            'transform': 'scale(1.4)',
                            'z-index': 10000,
                            'font-size': '20px'
                        }}
                    }},
                    {{
                        selector: '.dimmed',
                        style: {{
                            'opacity': 0.1,
                            'text-opacity': 0
                        }}
                    }}
                ],
                layout: {{ 
                    name: 'cose', 
                    padding: 60, 
                    animate: true, 
                    nodeRepulsion: 45000, 
                    idealEdgeLength: 200 
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
                    setTimeout(function(){{ target.style.backgroundColor = "transparent"; }}, 3000);
                }}
            }});

            document.getElementById('save_btn').addEventListener('click', function() {{
                var png64 = cy.png({{full: true, bg: 'white', scale: 2}});
                var link = document.createElement('a');
                link.href = png64;
                link.download = 'sis_synergy_graph.png';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }});
        }});
    </script>
    """
    components.html(cyto_html, height=800)

def fetch_author_bibliographies(author_input):
    """Retrieves high-fidelity bibliographic data from ORCID and Semantic Scholar with years."""
    if not author_input: return ""
    author_list = [a.strip() for a in author_input.split(",")]
    comprehensive_biblio = ""
    headers = {"Accept": "application/json"}
    
    for auth in author_list:
        orcid_id = None
        try:
            s_res = requests.get(f"https://pub.orcid.org/v3.0/search/?q={auth}", headers=headers, timeout=5).json()
            if s_res.get('result'):
                orcid_id = s_res['result'][0]['orcid-identifier']['path']
        except: pass

        if orcid_id:
            try:
                r_res = requests.get(f"https://pub.orcid.org/v3.0/{orcid_id}/record", headers=headers, timeout=5).json()
                works = r_res.get('activities-summary', {}).get('works', {}).get('group', [])
                comprehensive_biblio += f"\n[ORCID REPOSITORY: {auth.upper()} ({orcid_id})]\n"
                if works:
                    for work in works[:12]:
                        summary = work.get('work-summary', [{}])[0]
                        title = summary.get('title', {}).get('title', {}).get('value', 'Unknown')
                        year = work.get('publication-date', {}).get('year', {}).get('value', 'n.d.')
                        comprehensive_biblio += f"• ({year}) {title}\n"
                else: comprehensive_biblio += "- No metadata found in ORCID.\n"
            except: pass
        else:
            try:
                ss_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query=author:\"{auth}\"&limit=8&fields=title,year"
                ss_res = requests.get(ss_url, timeout=5).json()
                papers = ss_res.get("data", [])
                if papers:
                    comprehensive_biblio += f"\n[SCHOLAR DATA: {auth.upper()}]\n"
                    for p in papers:
                        comprehensive_biblio += f"• ({p.get('year','n.d.')}) {p['title']}\n"
                else: comprehensive_biblio += f"- No record found for {auth}.\n"
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
            "desc": "The high-level existential imperative driving the direction of inquiry."
        },
        "Vision": {
            "color": "#FFFF00", "shape": "rectangle", 
            "desc": "Mental simulation of a desired future outcome acting as a magnetic pull."
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
            "desc": " Wisdom gained through direct application of knowledge."
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
        ("Human mental concentration", "Identity", "has"), ("Identity", "Autobiographical memory", "possesses"),
        ("Mission", "Vision", "defines"), ("Vision", "Goal", "leads to"), ("Problem", "Identity", "challenges"),
        ("Rule", "Decision-making", "constrains"), ("Knowledge", "Classification", "organizes")
    ]
}

MENTAL_APPROACHES_ONTOLOGY = {
    "nodes": {
        "Perspective shifting": {
            "color": "#00FF00", "shape": "diamond", 
            "desc": "Rotating problem space through disparate stakeholders."
        },
        "Similarity and difference": {
            "color": "#FFFF00", "shape": "diamond", 
            "desc": "Pattern recognition act identifying anomalies."
        },
        "Core": {
            "color": "#FFC000", "shape": "diamond", 
            "desc": "Distillation of a problem into fundamental essence."
        },
        "Attraction": {
            "color": "#F2A6A2", "shape": "diamond", 
            "desc": "Force drawing disparate concepts into synthesis."
        },
        "Repulsion": {
            "color": "#D9D9D9", "shape": "diamond", 
            "desc": "Isolation of incompatible solutions or noise."
        },
        "Condensation": {
            "color": "#CCC0DA", "shape": "diamond", 
            "desc": "Reduction of vast complexity into strategic insight."
        },
        "Framework and foundation": {
            "color": "#F8CBAD", "shape": "diamond", 
            "desc": "Establishing boundaries for innovation logic."
        },
        "Bipolarity and dialectics": {
            "color": "#DDEBF7", "shape": "diamond", 
            "desc": "Synthesis through opposing tension tension."
        },
        "Constant": {
            "color": "#E1C1D1", "shape": "diamond", 
            "desc": "Identifying stable system invariants."
        },
        "Associativity": {
            "color": "#E1C1D1", "shape": "diamond", 
            "desc": "Non-linear, lateral knowledge linking."
        },
        "Induction": {
            "color": "#B4C6E7", "shape": "diamond", 
            "desc": "Building broad theory from field observations."
        },
        "Whole and part": {
            "color": "#00FF00", "shape": "diamond", 
            "desc": "Holistic vs Granular logic navigation."
        },
        "Mini-max": {
            "color": "#00FF00", "shape": "diamond", 
            "desc": "Maximum utility with minimum friction search."
        },
        "Addition and composition": {
            "color": "#FF00FF", "shape": "diamond", 
            "desc": "Building complexity through layering building blocks."
        },
        "Hierarchy": {
            "color": "#C6EFCE", "shape": "diamond", 
            "desc": "Vertical taxonomic ranking by systemic priority."
        },
        "Balance": {
            "color": "#00B0F0", "shape": "diamond", 
            "desc": "Search for dynamic equilibrium between variables."
        },
        "Deduction": {
            "color": "#92D050", "shape": "diamond", 
            "desc": "Applying broad laws to solve specifics."
        },
        "Abstraction and elimination": {
            "color": "#00B0F0", "shape": "diamond", 
            "desc": "Removing noise to reach a generic model."
        },
        "Pleasure and displeasure": {
            "color": "#00FF00", "shape": "diamond", 
            "desc": "Evaluative feedback on solution elegance."
        },
        "Openness and closedness": {
            "color": "#FFC000", "shape": "diamond", 
            "desc": "Systemic boundary state governing external data nodes."
        }
    }
}

# =============================================================================
# 3. KNOWLEDGE BASE (EXHAUSTIVE 18D SCIENCE FIELDS)
# =============================================================================

KNOWLEDGE_BASE = {
    "User profiles": {
        "Adventurers": {"description": "Explorers of hidden interdisciplinary patterns and high-risk hypotheses."},
        "Applicators": {"description": "Focused on practical efficiency, rapid deployment, and tangible execution."},
        "Know-it-alls": {"description": "Seekers of systemic absolute clarity, comprehensive taxonomy, and complete data."},
        "Observers": {"description": "Passive monitors of systemic dynamics and trend watchers without direct intervention."}
    },
    "Scientific paradigms": {
        "Empiricism": "Focus on sensory experience, experimental evidence, and observation-driven data.",
        "Rationalism": "Reliance on deductive logic, a priori reasoning, and mathematical certainty.",
        "Constructivism": "Knowledge as a social and cognitive build, dependent on context and perception.",
        "Positivism": "Strict adherence to verifiable facts and rejection of metaphysical speculation.",
        "Pragmatism": "Evaluation based on practical consequences, utility, and real-world application."
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
        "Mathematics": {"cat": "Formal", "methods": ["Axiomatization", "Formal Proof", "Stochastic Modeling"], "tools": ["MATLAB", "LaTeX", "WolframAlpha"], "facets": ["Topology", "Algebra", "Calculus"]},
        "Physics": {"cat": "Natural", "methods": ["Quantum Modeling", "Particle Tracking"], "tools": ["Accelerator", "Spectrometer"], "facets": ["Relativity", "Quantum Mechanics"]},
        "Chemistry": {"cat": "Natural", "methods": ["Synthesis", "Titration"], "tools": ["NMR", "Mass Spec"], "facets": ["Organic", "Physical", "Biochem"]},
        "Biology": {"cat": "Natural", "methods": ["Gene Sequencing", "CRISPR"], "tools": ["Microscope", "PCR"], "facets": ["Genetics", "Ecology", "Cell"]},
        "Neuroscience": {"cat": "Natural", "methods": ["Neuroimaging", "Optogenetics"], "tools": ["fMRI", "EEG"], "facets": ["Plasticity", "Synaptic Physiology"]},
        "Psychology": {"cat": "Social", "methods": ["Double-Blind Trials", "Psychometrics"], "tools": ["Surveys", "Biofeedback"], "facets": ["Behavioral", "Clinical"]},
        "Sociology": {"cat": "Social", "methods": ["Ethnography", "Network Analysis"], "tools": ["NVivo", "SPSS"], "facets": ["Demography", "Stratification"]},
        "Computer Science": {"cat": "Formal", "methods": ["Algorithm Design", "Verification"], "tools": ["GPU Clusters", "Docker"], "facets": ["AI", "Cybersecurity", "Cloud"]},
        "Medicine": {"cat": "Applied", "methods": ["Clinical Trials", "Epidemiology"], "tools": ["MRI", "CT"], "facets": ["Genomics", "Immunology"]},
        "Engineering": {"cat": "Applied", "methods": ["Finite Element Analysis", "Prototyping"], "tools": ["CAD", "3D Printers"], "facets": ["Robotics", "Nanotech"]},
        "Legal science": {"cat": "Social", "methods": ["Legal Hermeneutics", "Comparative Law"], "tools": ["Legislative DB", "Westlaw"], "facets": ["Jurisprudence", "Criminal Law"]},
        "Economics": {"cat": "Social", "methods": ["Econometrics", "Game Theory"], "tools": ["Bloomberg", "Stata"], "facets": ["Macroeconomics", "Finance"]},
        "Philosophy": {"cat": "Humanities", "methods": ["Socratic Method", "Dialectics"], "tools": ["Logic Mapping"], "facets": ["Epistemology", "Ethics"]},
        "Linguistics": {"cat": "Humanities", "methods": ["Corpus Analysis", "Syntactic Parsing"], "tools": ["Praat", "NLTK"], "facets": ["Semantics", "Phonology"]},
        "Ecology": {"cat": "Natural", "methods": ["Remote Sensing", "Trophic Modeling"], "tools": ["GIS", "Biosensors"], "facets": ["Biodiversity", "Biogeochemistry"]},
        "History": {"cat": "Humanities", "methods": ["Archival Research", "Prosopography"], "tools": ["Radiocarbon Dating"], "facets": ["Military History", "Diplomacy"]},
        "Politics": {"cat": "Social", "methods": ["Policy Analysis", "Comparative Politics"], "tools": ["Polls", "Legislative DB"], "facets": ["Governance", "IR"]},
        "Forensic sciences": {"cat": "Applied", "methods": ["DNA Profiling", "Ballistics"], "tools": ["Luminol", "Mass Spec"], "facets": ["Digital Forensics", "Pathology"]},
        "Geology": {"cat": "Natural", "methods": ["Stratigraphy", "Mineralogy"], "tools": ["Seismograph", "GIS"], "facets": ["Tectonics", "Petrology"]},
        "Architecture": {"cat": "Applied", "methods": ["Parametric Design"], "tools": ["Revit", "Rhino 3D"], "facets": ["Urban Design", "Sustainability"]},
        "Pedagogy": {"cat": "Social", "methods": ["Instructional Design"], "tools": ["LMS"], "facets": ["Curriculum Dev", "Educational Psych"]}
    }
}

# =============================================================================
# 4. INTERFACE CONSTRUCTION (STREAMLIT SIDEBAR & MAIN)
# =============================================================================

if 'show_user_guide' not in st.session_state: st.session_state.show_user_guide = False

# --- EXPANDED LEFT SIDEBAR: LOGO & VISIBILITY FIXES ---
with st.sidebar:
    # Original 3D Relief Logo
    st.markdown(f'<div class="sidebar-logo-container"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    
    # Hardcoded Date Badge
    st.markdown(f'<div class="date-badge">FEBRUARY 24, 2026</div>', unsafe_allow_html=True)
    
    st.header("⚙️ SYSTEM CONTROL")
    
    st.subheader("🔑 Dual API Access")
    groq_api_key = st.text_input("Groq Key (Phase 1 Synthesis):", type="password", help="Builds structural research foundation using IMA logic.")
    cerebras_api_key = st.text_input("Cerebras Key (Phase 2 Ideas):", type="password", help="Generates innovations and mapping using MA logic.")
    
    st.divider()
    col_reset, col_guide = st.columns(2)
    with col_reset:
        if st.button("♻️ RESET"):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()
    with col_guide:
        if st.button("📖 GUIDE"):
            st.session_state.show_user_guide = not st.session_state.show_user_guide
            st.rerun()
            
    st.divider()
    st.subheader("🌐 EXTERNAL CONNECTORS")
    # RESTORED LINK BUTTONS
    st.link_button("📂 GitHub Repository", "https://github.com/", use_container_width=True)
    st.link_button("🆔 ORCID Registry", "https://orcid.org/", use_container_width=True)
    st.link_button("🎓 Google Scholar", "https://scholar.google.com/", use_container_width=True)
    
    st.divider()
    st.subheader("📚 KNOWLEDGE EXPLORER")
    # Clean high-contrast expanders
    with st.expander("👤 User Profile Ontologies", expanded=False):
        for p, d in KNOWLEDGE_BASE["User profiles"].items(): st.markdown(f"**{p}**: {d['description']}")
    with st.expander("🧠 Mental Approach (MA) Map", expanded=False):
        for m, d in MENTAL_APPROACHES_ONTOLOGY["nodes"].items(): st.markdown(f"• **{m}**: {d['desc']}")
    with st.expander("🏛️ Metamodel (IMA) Structures", expanded=False):
        for n, d in HUMAN_THINKING_METAMODEL["nodes"].items(): st.markdown(f"• **{n}**: {d['desc']}")
    with st.expander("🔬 Science Taxonomy", expanded=False):
        for s in sorted(KNOWLEDGE_BASE["Science fields"].keys()): st.markdown(f"• **{s}**")
    with st.expander("🏗️ Structural Model Context", expanded=False):
        for m, d in KNOWLEDGE_BASE["Structural models"].items(): st.markdown(f"**{m}**: {d}")

# --- MAIN PAGE CONTENT ---
st.markdown('<h1 class="main-header-gradient">🧱 SIS Universal Knowledge Synthesizer</h1>', unsafe_allow_html=True)
st.markdown(f"**Advanced Sequential Synergy Pipeline** | Current Date: **{SYSTEM_DATE}**")

if st.session_state.show_user_guide:
    st.info(f"""
    **Sequential Synergy Pipeline Workflow:**
    1. **Key Input**: Provide both Groq (Phase 1) and Cerebras (Phase 2) keys.
    2. **Research Foundation (Step 1)**: Groq performs structural synthesis using IMA logic (Identity, Mission, Goal).
    3. **Innovation Prompt (Step 2)**: Cerebras takes Groq's work and generates 'Useful Innovative Ideas' using MA logic (Dialectics, Core).
    4. **Visualization**: The interactive graph maps structural facts against produced ideas.
    """)

col_ref1, col_ref2 = st.columns(2)
with col_ref1:
    st.markdown("""<div class="metamodel-box"><b>🏛️ Phase 1: Groq (IMA Architecture)</b><br>Structural reasoning building the factual foundation. Focus: Identity, Mission, Problem.</div>""", unsafe_allow_html=True)
with col_ref2:
    st.markdown("""<div class="mental-approach-box"><b>🧠 Phase 2: Cerebras (MA Architecture)</b><br>Cognitive transformation generating innovative solutions. Focus: Dialectics, Perspective, Induction.</div>""", unsafe_allow_html=True)

st.markdown("### 🛠️ CONFIGURE SYNERGY PIPELINE")

# Config Rows
r1c1, r1c2, r1c3 = st.columns([1.5, 2, 1])
with r1c1: target_authors = st.text_input("👤 Authors for ORCID Analysis:", placeholder="Karl Petrič, Samo Kralj, Teodor Petrič")
with r1c2: sel_sciences = st.multiselect("2. Select Science Fields:", sorted(list(KNOWLEDGE_BASE["Science fields"].keys())), default=["Physics", "Psychology", "Sociology"])
with r1c3: expertise = st.select_slider("3. Expertise Level:", ["Novice", "Intermediate", "Expert"], value="Expert")

r2c1, r2c2, r2c3 = st.columns(3)
with r2c1: sel_paradigms = st.multiselect("4. Scientific Paradigms:", list(KNOWLEDGE_BASE["Scientific paradigms"].keys()), default=["Rationalism"])
with r2c2: sel_models = st.multiselect("5. Structural Models:", list(KNOWLEDGE_BASE["Structural models"].keys()), default=["Concepts"])
with r2c3: goal_context = st.selectbox("6. Strategic Project Goal:", ["Scientific Research", "Problem Solving", "Educational", "Policy Making"])

st.divider()

# Inquiry Area
col_inq1, col_inq2, col_inq3 = st.columns([2, 2, 1])
with col_inq1: user_query = st.text_area("❓ STEP 1: Research Inquiry (for GROQ):", placeholder="Fact-based foundational inquiry...", height=200)
with col_inq2: idea_query = st.text_area("💡 STEP 2: Innovation Prompt (for CEREBRAS):", placeholder="Innovation targets based on synthesis...", height=200)
with col_inq3:
    uploaded_file = st.file_uploader("📂 ATTACH DATA (.txt only):", type=['txt'], help="Context for AI engines.")
    file_content = ""
    if uploaded_file: 
        file_content = uploaded_file.read().decode("utf-8")
        st.success("File integrated.")

# =============================================================================
# 5. SYNERGY EXECUTION ENGINE (GROQ -> CEREBRAS)
# =============================================================================

if st.button("🚀 EXECUTE MULTI-DIMENSIONAL SEQUENTIAL SYNERGY PIPELINE", use_container_width=True):
    if not groq_api_key or not cerebras_api_key:
        st.error("❌ Dual-Model synergy requires both Groq and Cerebras keys.")
    elif not user_query:
        st.warning("⚠️ Phase 1 Research Inquiry is required.")
    else:
        try:
            # Init Clients
            groq_client = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
            cerebras_client = OpenAI(api_key=cerebras_api_key, base_url="https://api.cerebras.ai/v1")
            biblio = fetch_author_bibliographies(target_authors) if target_authors else ""

            # --- PHASE 1: GROQ ---
            with st.spinner('PHASE 1: Groq synthesizing structural foundation (IMA Logic)...'):
                groq_sys = f"""
                You are the SIS Research Synthesizer (Phase 1).
                SESSION DATE: {SYSTEM_DATE}
                STRICT IMA ARCHITECTURE FOCUS: {json.dumps(HUMAN_THINKING_METAMODEL)}
                DATA CONTEXT: Sciences: {sel_sciences}. Authors: {biblio}. Attachment: {file_content}
                TASK: Provide a factual interdisciplinary dissertation foundation (approx 1500 words).
                """
                groq_resp = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": groq_sys}, {"role": "user", "content": user_query}],
                    temperature=0.4
                )
                groq_synthesis = groq_resp.choices[0].message.content

            # --- PHASE 2: CEREBRAS ---
            with st.spinner('PHASE 2: Cerebras producing innovative ideas and semantic mapping (MA Logic)...'):
                cerebras_sys = f"""
                You are the SIS Innovation Engine (Phase 2).
                SESSION DATE: {SYSTEM_DATE}
                STRICT MENTAL APPROACHES (MA) FOCUS: {json.dumps(MENTAL_APPROACHES_ONTOLOGY)}
                TASK: Use Groq's foundation to generate 'Useful Innovative Ideas' for: {idea_query}.
                End with '### SEMANTIC_GRAPH_JSON' and JSON network (40-60 nodes).
                Schema: {{"nodes": [{{"id": "n1", "label": "Text", "type": "Root|Branch", "color": "#hex", "shape": "rectangle|diamond"}}], "edges": [{{"source": "n1", "target": "n2", "rel_type": "AS|BT"}}]}}
                """
                cerebras_prompt = f"GROQ FOUNDATION:\n{groq_synthesis}\n\nUSER TARGET:\n{idea_query}"
                cerebras_resp = cerebras_client.chat.completions.create(
                    model="llama3.1-70b",
                    messages=[{"role": "system", "content": cerebras_sys}, {"role": "user", "content": cerebras_prompt}],
                    temperature=0.85
                )
                cerebras_innovation = cerebras_resp.choices[0].message.content

            # --- COMBINING AND RENDERING ---
            combined_content = f"## 📚 Phase 1: Research Foundation (Groq)\n{groq_synthesis}\n\n---\n## 💡 Phase 2: Useful Innovative Ideas (Cerebras)\n{cerebras_innovation}"
            parts = combined_content.split("### SEMANTIC_GRAPH_JSON")
            main_markdown = parts[0]
            
            if len(parts) > 1:
                try:
                    g_json = json.loads(re.search(r'\{.*\}', parts[1], re.DOTALL).group())
                    for n in g_json.get("nodes", []):
                        lbl, nid = n["label"], n["id"]
                        g_url = urllib.parse.quote(lbl)
                        repl = f'<span id="{nid}"><a href="https://www.google.com/search?q={g_url}" target="_blank" class="semantic-node-highlight">{lbl}<i class="google-icon">↗</i></a></span>'
                        main_markdown = main_markdown.replace(lbl, repl, 1)
                except: pass

            st.subheader("📊 INTEGRATED PIPELINE RESULTS")
            st.markdown(main_markdown, unsafe_allow_html=True)

            if len(parts) > 1:
                try:
                    g_json = json.loads(re.search(r'\{.*\}', parts[1], re.DOTALL).group())
                    st.subheader("🕸️ INTEGRATED SEQUENTIAL SEMANTIC NETWORK")
                    st.caption(f"Visual Mapping by Cerebras on {SYSTEM_DATE}.")
                    elements = []
                    for n in g_json.get("nodes", []):
                        level = n.get("type", "Branch")
                        size = 110 if level == "Root" else 85
                        elements.append({"data": {"id": n["id"], "label": n["label"], "color": n.get("color", "#2a9d8f"), "size": size, "shape": n.get("shape", "rectangle"), "z_index": 1}})
                    for e in g_json.get("edges", []):
                        elements.append({"data": {"source": e["source"], "target": e["target"], "rel_type": e.get("rel_type", "AS")}})
                    render_cytoscape_network(elements, "viz_synergy_final_850")
                except: st.warning("⚠️ Error parsing Semantic Graph JSON.")

            if biblio:
                with st.expander("📚 EXTENDED BIBLIOGRAPHIC DATA"): st.text(biblio)

        except Exception as e:
            st.error(f"❌ Pipeline Failure: {e}")

# =============================================================================
# 6. FOOTER
# =============================================================================
st.divider()
st.caption(f"SIS Universal Knowledge Synthesizer | {VERSION_ID} | Operating Date: {SYSTEM_DATE}")
st.write("")


















