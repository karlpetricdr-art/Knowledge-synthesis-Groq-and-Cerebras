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

# =========================================================================
# 0. KONFIGURACIJA IN NAPREDNI STILI (SIS ARCHITECTURE CSS v22.5.0)
# =========================================================================
# System level configuration for layout stability and semantic rendering.
# Optimized for wide-screen multi-dimensional data visualization.
st.set_page_config(
    page_title="SIS Universal Knowledge Synthesizer",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Advanced CSS Injection for high-fidelity UI and sidebar element isolation.
# REVISION v22.5.0: Fixed Sidebar Malfunction (Layer overlap and Clipping).
# Fixed Duplicate ID issue and Visibility of the Knowledge Explorer Expanders.
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Fira+Code:wght@400;500&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

    code {
        font-family: 'Fira+Code', monospace !important;
    }

    /* THE VISIBILITY FIX: Absolute control over the sidebar container scroll and depth */
    [data-testid="stSidebar"] {
        background-color: #fafbfc;
        border-right: 2px solid #eef2f6;
        padding-top: 15px;
        min-width: 420px !important;
        overflow-y: auto !important;
        display: block !important;
        z-index: 999 !important;
    }

    /* Knowledge Explorer visibility and spacing fixes for sidebar expanders */
    .stExpander {
        border: 2px solid #edf2f7 !important;
        border-radius: 14px !important;
        margin-bottom: 12px !important;
        background-color: #ffffff !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03) !important;
        overflow: visible !important;
        z-index: 1000 !important;
    }

    /* Semantični poudarki v generiranem besedilu */
    .semantic-node-highlight {
        color: #2a9d8f;
        font-weight: bold;
        border-bottom: 2px solid #2a9d8f;
        padding: 0 2px;
        background-color: #f0fdfa;
        border-radius: 4px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        text-decoration: none !important;
        display: inline-block;
        cursor: help;
    }
    .semantic-node-highlight:hover {
        background-color: #ccfbf1;
        color: #264653;
        border-bottom: 2px solid #e76f51;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(42, 157, 143, 0.2);
    }

    /* Povezave za raziskovalne avtorje */
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

    /* Tipografija za disertation */
    .stMarkdown {
        line-height: 1.95;
        font-size: 1.08em;
        text-align: justify;
        color: #1a1a1a;
    }

    /* Arhitekturni kontejnerji */
    .metamodel-box {
        padding: 25px;
        border-radius: 15px;
        background-color: #f8f9fa;
        border-left: 8px solid #00B0F0;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .mental-approach-box {
        padding: 25px;
        border-radius: 15px;
        background-color: #f0f7ff;
        border-left: 8px solid #6366f1;
        margin-bottom: 30px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
    }
    .idea-mode-box {
        padding: 25px;
        border-radius: 15px;
        background-color: #fff4e6;
        border-left: 8px solid #ff922b;
        margin-bottom: 30px;
        font-weight: bold;
        border: 1px solid #ffe8cc;
    }
    .synergy-box {
        padding: 35px;
        border-radius: 20px;
        background: linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%);
        border-left: 12px solid #9c27b0;
        margin-bottom: 40px;
        font-weight: bold;
        box-shadow: 0 12px 30px rgba(156, 39, 176, 0.25);
        color: #4a148c;
    }

    /* Footer styling */
    .sis-footer {
        margin-top: 60px;
        padding: 40px;
        border-top: 2px solid #f1f1f1;
        text-align: center;
        color: #888;
        font-size: 0.9em;
        letter-spacing: 0.5px;
    }

    /* Animacije za UI elemente */
    @keyframes sis-glow {
        0% { box-shadow: 0 0 0 0 rgba(42, 157, 143, 0.4); }
        70% { box-shadow: 0 0 0 15px rgba(42, 157, 143, 0); }
        100% { box-shadow: 0 0 0 0 rgba(42, 157, 143, 0); }
    }
    .stButton>button {
        transition: all 0.5s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        border-radius: 10px;
        font-weight: 700;
        text-transform: uppercase;
    }
    .stButton>button:hover {
        transform: translateY(-3px) scale(1.03);
        animation: sis-glow 2s infinite;
    }
</style>
""", unsafe_allow_html=True)

def get_svg_base64(svg_str):
    """Pretvori SVG v base64 format za prikaz slike v Streamlit sidebarju."""
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

# --- LOGOTIP: 3D RELIEF (Embedded SVG Arhitektura) ---
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

# --- CYTOSCAPE RENDERER Z DINAMIČNIMI OBLIKAMI IN IZVOZOM ---
def render_cytoscape_network(elements, container_id="cy_knowledge_canvas"):
    """
    Izriše interaktivno omrežje Cytoscape.js s podporo za oblike iz metamodela,
    shranjevanje slike in funkcijo lupe za fokusiranje vozlišč.
    """
    cyto_html = f"""
    <div style="position: relative; margin-top: 25px;">
        <button id="save_btn" style="position: absolute; top: 20px; right: 20px; z-index: 100; padding: 12px 18px; background: #2a9d8f; color: white; border: none; border-radius: 8px; cursor: pointer; font-family: 'Inter', sans-serif; font-size: 14px; font-weight: 700; box-shadow: 0 5px 15px rgba(0,0,0,0.2);">💾 Download PNG</button>
        <div id="{container_id}" style="width: 100%; height: 800px; background: #ffffff; border-radius: 25px; border: 1px solid #e2e8f0; box-shadow: inset 0 2px 15px rgba(0,0,0,0.05);"></div>
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
                            'color': '#111',
                            'background-color': 'data(color)', 
                            'width': 'data(size)', 
                            'height': 'data(size)',
                            'shape': 'data(shape)', 
                            'font-size': '14px', 
                            'font-weight': '700', 
                            'text-outline-width': 3,
                            'text-outline-color': '#ffffff', 
                            'cursor': 'pointer', 
                            'z-index': 'data(z_index)',
                            'transition-property': 'background-color, border-width, border-color, transform',
                            'transition-duration': '0.4s'
                        }}
                    }},
                    {{
                        selector: 'edge',
                        style: {{
                            'width': 4, 
                            'line-color': '#cbd5e0', 
                            'label': 'data(rel_type)',
                            'font-size': '11px', 
                            'font-weight': '600', 
                            'color': '#2a9d8f',
                            'target-arrow-color': '#cbd5e0', 
                            'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier', 
                            'text-rotation': 'autorotate',
                            'text-background-opacity': 1, 
                            'text-background-color': '#ffffff',
                            'text-background-padding': '5px', 
                            'text-background-shape': 'roundrectangle'
                        }}
                    }},
                    {{
                        selector: 'node.highlighted',
                        style: {{
                            'border-width': 7, 
                            'border-color': '#e76f51', 
                            'transform': 'scale(1.6)',
                            'z-index': 9999, 
                            'font-size': '20px'
                        }}
                    }},
                    {{
                        selector: '.dimmed',
                        style: {{ 'opacity': 0.05, 'text-opacity': 0 }}
                    }}
                ],
                layout: {{ 
                    name: 'cose', 
                    padding: 80, 
                    animate: true, 
                    nodeRepulsion: 45000, 
                    idealEdgeLength: 160 
                }}
            }});

            /* LOGIKA LUPE (Fokusiranje na sosesko ob prehodu z miško) */
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
                    target.style.backgroundColor = "#ffffd0";
                    setTimeout(function(){{ target.style.backgroundColor = "transparent"; }}, 4000);
                }}
            }});

            document.getElementById('save_btn').addEventListener('click', function() {{
                var png64 = cy.png({{full: true, bg: 'white', scale: 3}});
                var link = document.createElement('a');
                link.href = png64;
                link.download = 'sis_universal_map_' + Date.now() + '.png';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
            }});
        }});
    </script>
    """
    components.html(cyto_html, height=900)

# --- PRIDOBIVANJE BIBLIOGRAFIJ (ORCID & Scholar Integration) ---
def fetch_author_bibliographies(author_input):
    """
    Zajame bibliografske podatke z letnicami preko ORCID in Scholar API baz.
    """
    if not author_input: return ""
    author_list = [a.strip() for a in author_input.split(",")]
    comprehensive_biblio = ""
    headers = {"Accept": "application/json"}
    
    for auth in author_list:
        orcid_id = None
        try:
            search_url = f"https://pub.orcid.org/v3.0/search/?q={auth}"
            s_res = requests.get(search_url, headers=headers, timeout=10).json()
            if s_res.get('result'):
                orcid_id = s_res['result'][0]['orcid-identifier']['path']
        except Exception: pass

        if orcid_id:
            try:
                record_url = f"https://pub.orcid.org/v3.0/{orcid_id}/record"
                r_res = requests.get(record_url, headers=headers, timeout=10).json()
                works = r_res.get('activities-summary', {}).get('works', {}).get('group', [])
                comprehensive_biblio += f"\n--- DATABASE RECORD: {auth.upper()} (ORCID: {orcid_id}) ---\n"
                if works:
                    for work in works[:8]:
                        summary = work.get('work-summary', [{}])[0]
                        title = summary.get('title', {}).get('title', {}).get('value', 'Unknown Publication Title')
                        pub_date = summary.get('publication-date')
                        year = pub_date.get('year').get('value', 'n.d.') if pub_date and pub_date.get('year') else "n.d."
                        comprehensive_biblio += f"- ({year}) {title}\n"
                else: comprehensive_biblio += "No public works registered in registry.\n"
            except Exception: pass
        else:
            try:
                ss_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query=author:\"{auth}\"&limit=6&fields=title,year"
                ss_res = requests.get(ss_url, timeout=10).json()
                papers = ss_res.get("data", [])
                if papers:
                    comprehensive_biblio += f"\n--- SCHOLAR BACKUP RECORD: {auth.upper()} ---\n"
                    for p in papers:
                        comprehensive_biblio += f"- ({p.get('year','n.d.')}) {p['title']}\n"
            except Exception: pass
            
    return comprehensive_biblio

# =========================================================================
# 1. ARCHITECTURE DEFINITIONS (IMA vs MA)
# =========================================================================

# A. INTEGRATED METAMODEL ARCHITECTURE (IMA) + Sociopsychological Outcome Mapping
HUMAN_THINKING_METAMODEL = {
    "nodes": {
        "Human mental concentration": {"color": "#A6A6A6", "shape": "rectangle"},
        "Identity": {"color": "#C6EFCE", "shape": "rectangle"},
        "Autobiographical memory": {"color": "#C6EFCE", "shape": "rectangle"},
        "Mission": {"color": "#92D050", "shape": "rectangle"},
        "Vision": {"color": "#FFFF00", "shape": "rectangle"},
        "Goal": {"color": "#00B0F0", "shape": "rectangle"},
        "Problem": {"color": "#F2DCDB", "shape": "rectangle"},
        "Ethics/moral": {"color": "#FFC000", "shape": "rectangle"},
        "Hierarchy of interests": {"color": "#F8CBAD", "shape": "rectangle"},
        "Rule": {"color": "#F2F2F2", "shape": "rectangle"},
        "Decision-making": {"color": "#FFFF99", "shape": "rectangle"},
        "Problem solving": {"color": "#D9D9D9", "shape": "rectangle"},
        "Conflict situation": {"color": "#00FF00", "shape": "rectangle"},
        "Knowledge": {"color": "#DDEBF7", "shape": "rectangle"},
        "Tool": {"color": "#00B050", "shape": "rectangle"},
        "Experience": {"color": "#00B050", "shape": "rectangle"},
        "Classification": {"color": "#CCC0DA", "shape": "rectangle"},
        "Psychological aspect": {"color": "#F8CBAD", "shape": "rectangle"},
        "Sociological aspect": {"color": "#00FFFF", "shape": "rectangle"}
    },
    "relations": [
        ("Human mental concentration", "Identity", "has"),
        ("Human mental concentration", "Mission", "can have"),
        ("Identity", "Autobiographical memory", "has"),
        ("Mission", "Vision", "can have"),
        ("Vision", "Goal", "can have"),
        ("Problem", "Identity", "threatens"),
        ("Problem", "Mission", "impedes"),
        ("Problem", "Vision", "impedes"),
        ("Problem", "Goal", "threatens"),
        ("Problem", "Ethics/moral", "has"),
        ("Ethics/moral", "Problem", "can solve"),
        ("Problem", "Rule", "can be connected"),
        ("Hierarchy of interests", "Goal", "realizes"),
        ("Hierarchy of interests", "Knowledge", "realizes or hinders"),
        ("Rule", "Goal", "realizes or hinders"),
        ("Rule", "Decision-making", "realizes or hinders"),
        ("Knowledge", "Goal", "acquisition"),
        ("Decision-making", "Problem solving", "realizes or hinders"),
        ("Ethics/moral", "Problem solving", "helps or hinders"),
        ("Problem", "Problem solving", "should"),
        ("Problem solving", "Conflict situation", "results_in"),
        ("Knowledge", "Classification", "aided_by"),
        ("Knowledge", "Tool", "aided_by"),
        ("Knowledge", "Experience", "aided_by"),
        ("Experience", "Psychological aspect", "outcome_of"),
        ("Experience", "Sociological aspect", "outcome_of"),
        ("Conflict situation", "Psychological aspect", "outcome_of"),
        ("Conflict situation", "Sociological aspect", "outcome_of"),
        ("Psychological aspect", "Sociological aspect", "interconnected")
    ]
}

# B. MENTAL APPROACHES (MA) ONTOLOGY
MENTAL_APPROACHES_ONTOLOGY = {
    "nodes": {
        "Perspective shifting": {"color": "#00FF00", "shape": "rectangle"},
        "Similarity and difference": {"color": "#FFFF00", "shape": "rectangle"},
        "Core": {"color": "#FFC000", "shape": "rectangle"},
        "Attraction": {"color": "#F2A6A2", "shape": "rectangle"},
        "Repulsion": {"color": "#D9D9D9", "shape": "rectangle"},
        "Condensation": {"color": "#CCC0DA", "shape": "rectangle"},
        "Framework and foundation": {"color": "#F8CBAD", "shape": "rectangle"},
        "Bipolarity and dialectics": {"color": "#DDEBF7", "shape": "rectangle"},
        "Constant": {"color": "#E1C1D1", "shape": "rectangle"},
        "Associativity": {"color": "#E1C1D1", "shape": "rectangle"},
        "Induction": {"color": "#B4C6E7", "shape": "rectangle"},
        "Whole and part": {"color": "#00FF00", "shape": "rectangle"},
        "Mini-max": {"color": "#00FF00", "shape": "rectangle"},
        "Addition and composition": {"color": "#FF00FF", "shape": "rectangle"},
        "Hierarchy": {"color": "#C6EFCE", "shape": "rectangle"},
        "Balance": {"color": "#00B0F0", "shape": "rectangle"},
        "Deduction": {"color": "#92D050", "shape": "rectangle"},
        "Abstraction and elimination": {"color": "#00B0F0", "shape": "rectangle"},
        "Pleasure and displeasure": {"color": "#00FF00", "shape": "rectangle"},
        "Openness and closedness": {"color": "#FFC000", "shape": "rectangle"}
    },
    "relations": [
        ("Perspective shifting", "Similarity and difference", "leads to"),
        ("Core", "Similarity and difference", "influences"),
        ("Core", "Attraction", "has dynamic"),
        ("Core", "Repulsion", "has dynamic"),
        ("Repulsion", "Bipolarity and dialectics", "leads to"),
        ("Framework and foundation", "Bipolarity and dialectics", "mutually interacts"),
        ("Bipolarity and dialectics", "Constant", "stabilizes"),
        ("Constant", "Associativity", "allows"),
        ("Induction", "Whole and part", "bidirectional link"),
        ("Induction", "Hierarchy", "structures"),
        ("Whole and part", "Mini-max", "optimizes"),
        ("Mini-max", "Addition and composition", "results in"),
        ("Deduction", "Hierarchy", "defines taxonomy"),
        ("Deduction", "Abstraction and elimination", "processes through"),
        ("Hierarchy", "Balance", "maintains"),
        ("Balance", "Addition and composition", "stabilizes")
    ]
}

# C. COMPREHENSIVE SCIENCE FIELDS DICTIONARY (FULLY EXPANDED)
KNOWLEDGE_BASE = {
    "mental approaches": list(MENTAL_APPROACHES_ONTOLOGY["nodes"].keys()),
    "User profiles": {
        "Adventurers": {"description": "Explorers of hidden patterns and non-linear connections."},
        "Applicators": {"description": "Efficiency focused; seeking direct implementation paths."},
        "Know-it-alls": {"description": "Systemic clarity and exhaustive taxonomic coverage."},
        "Observers": {"description": "System monitors; focused on trends and long-term stability."}
    },
    "Scientific paradigms": {
        "Empiricism": "Knowledge through sensory experience and evidence.",
        "Rationalism": "Deductive logic and innate reason as the primary source.",
        "Constructivism": "Knowledge is socially constructed through human interaction.",
        "Positivism": "Strict adherence to scientific facts and observable laws.",
        "Pragmatism": "Practical utility and 'what works' as the truth criterion.",
        "Critical Theory": "Analyzing and challenging power structures in knowledge.",
        "Phenomenology": "Study of direct conscious experience and subjectivity."
    },
    "Structural models": {
        "Causal Connections": "Analyzing A leads to B (Cause-Effect).",
        "Principles & Relations": "Fundamental laws governing a system.",
        "Episodes & Sequences": "Temporal flow and historical context.",
        "Facts & Characteristics": "Raw empirical data and attributes.",
        "Generalizations": "High-level frameworks and categorical abstractions.",
        "Glossary": "Precise definitions and semantic boundaries.",
        "Concepts": "Abstract constructs and mental representations."
    },
    "Science fields": {
        "Mathematics": {"cat": "Formal", "methods": ["Axiomatization", "Statistical Inference", "Mathematical Modeling", "Formal Proof"], "tools": ["MATLAB", "Mathematica", "LaTeX", "Calculus"], "facets": ["Topology", "Algebra", "Analysis", "Number Theory"]},
        "Physics": {"cat": "Natural", "methods": ["Modeling", "Simulation"], "tools": ["Accelerator", "Spectrometer"], "facets": ["Quantum", "Relativity"]},
        "Chemistry": {"cat": "Natural", "methods": ["Synthesis", "Spectroscopy"], "tools": ["NMR", "Chromatography"], "facets": ["Organic", "Molecular"]},
        "Biology": {"cat": "Natural", "methods": ["Sequencing", "CRISPR"], "tools": ["Microscope", "Bio-Incubator"], "facets": ["Genetics", "Population Dynamics"]},
        "Ecology": {"cat": "Natural", "methods": ["Ecosystem Modeling", "Field Sampling", "Remote Sensing"], "tools": ["GIS Software", "Biosensors", "Satellite Imagery"], "facets": ["Biodiversity", "Sustainability", "Conservation Biology"]},
        "Neuroscience": {"cat": "Natural", "methods": ["Neuroimaging", "Electrophys"], "tools": ["fMRI", "EEG"], "facets": ["Plasticity", "Synaptic"]},
        "Psychology": {"cat": "Social", "methods": ["Double-Blind Trials", "Psychometrics"], "tools": ["fMRI", "Testing Kits"], "facets": ["Behavioral", "Cognitive"]},
        "Sociology": {"cat": "Social", "methods": ["Ethnography", "Surveys"], "tools": ["Data Analytics", "Archives"], "facets": ["Stratification", "Dynamics"]},
        "Computer Science": {"cat": "Formal", "methods": ["Algorithm Design", "Verification"], "tools": ["LLMGraphTransformer", "GPU Clusters"], "facets": ["AI", "Cybersecurity"]},
        "Psychiatry": {"cat": "Applied/Medical", "methods": ["Diagnosis", "Clinical Trials"], "tools": ["DSM-5", "EEG"], "facets": ["Clinical Psychiatry", "Neuropsychiatry"]},
        "Medicine": {"cat": "Applied", "methods": ["Clinical Trials", "Epidemiology"], "tools": ["MRI/CT", "Bio-Markers"], "facets": ["Immunology", "Pharmacology"]},
        "Engineering": {"cat": "Applied", "methods": ["Prototyping", "FEA Analysis"], "tools": ["3D Printers", "CAD Software"], "facets": ["Robotics", "Nanotech"]},
        "Library Science": {"cat": "Applied", "methods": ["Taxonomy", "Appraisal"], "tools": ["OPAC", "Metadata"], "facets": ["Retrieval", "Knowledge Org"]},
        "Philosophy": {"cat": "Humanities", "methods": ["Socratic Method", "Phenomenology"], "tools": ["Logic Mapping", "Critical Analysis"], "facets": ["Epistemology", "Metaphysics"]},
        "Linguistics": {"cat": "Humanities", "methods": ["Corpus Analysis", "Syntactic Parsing"], "tools": ["Praat", "NLTK Toolkit"], "facets": ["Socioling", "CompLing"]},
        "Geography": {"cat": "Natural/Social", "methods": ["Spatial Analysis", "GIS"], "tools": ["ArcGIS"], "facets": ["Human Geo", "Physical Geo"]},
        "Geology": {"cat": "Natural", "methods": ["Stratigraphy", "Mineralogy"], "tools": ["Seismograph"], "facets": ["Tectonics", "Petrology"]},
        "Climatology": {"cat": "Natural", "methods": ["Climate Modeling"], "tools": ["Weather Stations"], "facets": ["Change Analysis"]},
        "History": {"cat": "Humanities", "methods": ["Archives"], "tools": ["Archives"], "facets": ["Social History"]},
        "Legal science": {"cat": "Social", "methods": ["Legal Hermeneutics", "Dogmatic Method", "Empirical Legal Research"], "tools": ["Legislative Databases", "Case Law Archives"], "facets": ["Jurisprudence", "Constitutional Law", "Criminal Law", "Civil Law"]},
        "Economics": {"cat": "Social", "methods": ["Econometrics", "Game Theory", "Market Modeling"], "tools": ["Stata", "R", "Bloomberg"], "facets": ["Macroeconomics", "Behavioral Economics"]},
        "Politics": {"cat": "Social", "methods": ["Policy Analysis", "Comparative Politics"], "tools": ["Polls", "Legislative Databases"], "facets": ["International Relations", "Governance"]},
        "Criminology": {"cat": "Social", "methods": ["Case Studies", "Profiling"], "tools": ["NCVS", "Mapping Software"], "facets": ["Victimology", "Penology"]},
        "Forensic sciences": {"cat": "Applied/Natural", "methods": ["DNA Profiling", "Ballistics"], "tools": ["Mass Spectrometer", "Luminol"], "facets": ["Toxicology", "Pathology"]},
        "Cybernetics": {"cat": "Applied", "methods": ["Feedback Loop Analysis", "Modeling"], "tools": ["System Dynamics Software"], "facets": ["Autopoiesis", "Homeostasis"]},
        "Mycology": {"cat": "Natural", "methods": ["Spore Identification"], "tools": ["Autoclave", "Petri Dishes"], "facets": ["Symbiosis", "Fungal Genetics"]},
        "Theology": {"cat": "Humanities", "methods": ["Exegesis", "Hermeneutics"], "tools": ["Manuscript Archives"], "facets": ["Dogmatics", "Ethics"]},
        "Musicology": {"cat": "Humanities", "methods": ["Harmonic Analysis"], "tools": ["DAW Software", "Spectrogram"], "facets": ["Music Theory"]},
        "Anthropology": {"cat": "Social", "methods": ["Participant Observation"], "tools": ["Carbon Dating"], "facets": ["Cultural Anthropology"]},
        "Archeology": {"cat": "Social/Humanities", "methods": ["Excavation"], "tools": ["Lidar", "GPR"], "facets": ["Zooarcheology"]},
        "Astronomy": {"cat": "Natural", "methods": ["Photometry"], "tools": ["VLT Telescope", "James Webb"], "facets": ["Astrophysics"]},
        "Demography": {"cat": "Social", "methods": ["Census Analysis"], "tools": ["SAS", "Census Data"], "facets": ["Migration Studies"]},
        "Architecture": {"cat": "Applied", "methods": ["Spatial Composition"], "tools": ["BIM Software", "Revit"], "facets": ["Urban Planning"]},
        "Meteorology": {"cat": "Natural", "methods": ["Atmospheric Modeling"], "tools": ["Doppler Radar"], "facets": ["Weather Forecast"]},
        "Nanotechnology": {"cat": "Applied", "methods": ["Scanning Probe Microscopy"], "tools": ["AFM", "SEM"], "facets": ["Nano-electronics"]},
        "Botany": {"cat": "Natural", "methods": ["Phylogenetic Analysis"], "tools": ["Herbaria"], "facets": ["Plant Anatomy"]}
    }
}

# =========================================================================
# 2. STREAMLIT INTERFACE KONSTRUKCIJA
# =========================================================================

# Inicializacija seje za zagotavljanje stabilnosti parametrov.
if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Expert"
if 'show_user_guide' not in st.session_state: st.session_state.show_user_guide = False

with st.sidebar:
    st.markdown(f'<div style="text-align:center; padding-bottom: 25px;"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="220"></div>', unsafe_allow_html=True)
    st.header("⚙️ SIS Control Panel")
    
    # Engine Selection - KEY: selection_main_engine_v22_unique_id
    p_opt = st.selectbox("Engine Architecture:", ["Groq", "Cerebras", "SYNERGY (Cerebras Spark + Groq Architect)"], index=0, key="selection_main_engine_v22_unique_id")
    
    # PROVIDER-SPECIFIC API KEY INPUTS WITH ABSOLUTE UNIQUE KEYS PER ENGINE SELECTION
    if p_opt == "SYNERGY (Cerebras Spark + Groq Architect)":
        cer_spark_k = st.text_input("Cerebras Key (Spark Innovation):", type="password", key="key_synergy_spark_id_v22")
        groq_arch_k = st.text_input("Groq Key (Dissertation Architect):", type="password", key="key_synergy_arch_id_v22")
        api_ready = (cer_spark_k != "" and groq_arch_k != "")
    elif p_opt == "Groq":
        solo_key_v22 = st.text_input("Groq API Key:", type="password", key="key_standalone_groq_id_v22")
        api_ready = (solo_key_v22 != "")
    else:
        solo_key_v22 = st.text_input("Cerebras API Key:", type="password", key="key_standalone_cer_id_v22")
        api_ready = (solo_key_v22 != "")
    
    if st.button("📖 Interactive User Guide"):
        st.session_state.show_user_guide = not st.session_state.show_user_guide
        st.rerun()
    if st.session_state.show_user_guide:
        st.info("""
        1. **Keys**: Enter required API keys. SYNERGY mode is recommended for interdisciplinary 'wild' research.
        2. **Authors**: Enter names (e.g., 'Teodor Petrič') to fetch real-time bibliographies and history.
        3. **Expertise**: Adjust the taxonomic depth and linguistic complexity.
        4. **Inquiry**: Use both Synthesis (Standard) and Idea (Innovation) boxes for dual output.
        5. **Graph**: Nodes are interactive. Click to focus and sync with the dissertation text.
        """)
        if st.button("Close Guide ✖️"): st.session_state.show_user_guide = False; st.rerun()

    st.divider()
    # KNOWLEDGE EXPLORER - Visibility fix via absolute scroll expanders with unique indexing
    st.subheader("📚 SIS Knowledge Explorer")
    with st.expander("👤 User Profiles"):
        for p, d in KNOWLEDGE_BASE["User profiles"].items(): st.write(f"**{p}**: {d['description']}")
    with st.expander("🧠 mental approaches"):
        for a in KNOWLEDGE_BASE["mental approaches"]: st.write(f"• {a}")
    with st.expander("🔬 Science fields"):
        for s in sorted(KNOWLEDGE_BASE["Science fields"].keys()): st.write(f"• **{s}**")
    
    if st.button("♻️ Reset Framework", use_container_width=True):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

st.title("🧱 SIS Universal Knowledge Synthesizer")
st.markdown("Advanced Multi-dimensional synthesis with **Separated Metamodel & Mental Approaches**.")

# Ontological Reference Frameworks (Anchors for the user)
col_ref1, col_ref2 = st.columns(2)
with col_ref1:
    st.markdown("""
    <div class="metamodel-box">
        <b>🏛️ Integrated Metamodel Architecture (IMA):</b><br>
        Focuses on structural reasoning: <i>Identity, Mission, Rules, Goals</i> and <i>Sociopsychological Outcomes</i>.
    </div>
    """, unsafe_allow_html=True)

with col_ref2:
    st.markdown("""
    <div class="mental-approach-box">
        <b>🧠 Mental Approaches (MA) Logic:</b><br>
        Focuses on cognitive filters: <i>Perspective shifting, Dialectics, Induction, and Addition/Composition</i>.
    </div>
    """, unsafe_allow_html=True)

st.markdown("### 🛠️ Step 1: Configure Your Multi-Dimensional Build")

# ROW 1: AUTHORS
r1_c1, r1_c2, r1_c3 = st.columns([1, 2, 1])
with r1_c2:
    target_authors = st.text_input("👤 Target Research Authors:", placeholder="Karl Petrič, Samo Kralj, Teodor Petrič", key="target_authors_key")
    st.caption("Active bibliographic analysis via ORCID & Scholar metadata hubs.")

# ROW 2: CORE SYNTHESIS PARAMETERS
r2_c1, r2_c2, r2_c3 = st.columns(3)
with r2_c1:
    sel_profiles = st.multiselect("1. User Profiles:", list(KNOWLEDGE_BASE["User profiles"].keys()), default=["Adventurers"])
with r2_c2:
    sel_sciences = st.multiselect("2. Science Fields:", sorted(list(KNOWLEDGE_BASE["Science fields"].keys())), default=["Physics", "Psychology", "Sociology"])
with r2_c3:
    expertise = st.select_slider("3. Expertise Level:", options=["Novice", "Intermediate", "Expert"], value=st.session_state.expertise_val)

# ROW 3: EPISTEMOLOGY
r3_c1, r3_c2, r3_c3 = st.columns(3)
with r3_c1:
    sel_models = st.multiselect("4. Structural Models:", list(KNOWLEDGE_BASE["Structural models"].keys()), default=["Concepts"])
with r3_c2:
    sel_paradigms = st.multiselect("5. Scientific Paradigms:", list(KNOWLEDGE_BASE["Scientific paradigms"].keys()), default=["Rationalism"])
with r3_c3:
    goal_context = st.selectbox("6. Context / Goal:", ["Scientific Research", "Problem Solving", "Educational", "Policy Making"])

# ROW 4: AGGREGATED METHODS & TOOLS
agg_meth, agg_tool = [], []
for s in sel_sciences:
    if s in KNOWLEDGE_BASE["Science fields"]:
        agg_meth.extend(KNOWLEDGE_BASE["Science fields"][s]["methods"])
        agg_tool.extend(KNOWLEDGE_BASE["Science fields"][s]["tools"])

r4_c1, r4_c2, r4_c3 = st.columns(3)
with r4_c1:
    sel_approaches = st.multiselect("7. mental approaches:", KNOWLEDGE_BASE["mental approaches"], default=["Perspective shifting"])
with r4_c2:
    sel_methods = st.multiselect("8. Methodologies:", sorted(list(set(agg_meth))), default=[])
with r4_c3:
    sel_tools = st.multiselect("9. Specific Tools:", sorted(list(set(agg_tool))), default=[])

st.divider()

# ROW 5: INQUIRY DEFINITION
st.markdown("### ✍️ Step 2: Intellectual Inquiry Definition")
col_inq_syn, col_inq_idea, col_inq_attach = st.columns([2, 2, 1])
with col_inq_syn:
    user_query = st.text_area("❓ Knowledge Synthesis Inquiry:", placeholder="Complex interdisciplinary research question.", height=150, key="user_query_key")
with col_inq_idea:
    idea_query = st.text_area("💡 Idea Production Inquiry:", placeholder="Generative innovative ideas leveraging IMA/MA logic.", height=150, key="idea_query_key")
with col_inq_attach:
    uploaded_file = st.file_uploader("📂 Attach Supplementary Context (.txt):", type=['txt'])
    file_content = ""
    if uploaded_file:
        file_content = uploaded_file.read().decode("utf-8")
        st.success("File context loaded successfully.")

# =========================================================================
# 5. EXECUTION ENGINE: SYNERGY LOGIC (V22.4)
# =========================================================================

if st.button("🚀 Execute Multi-Dimensional Synthesis", use_container_width=True):
    if not api_ready: st.error("Missing required API Keys for the selected provider configuration.")
    elif not user_query and not idea_query: st.warning("Please provide an intellectual inquiry to start.")
    else:
        try:
            is_idea_mode = (idea_query.strip() != "")
            biblio = fetch_author_bibliographies(target_authors) if target_authors else ""
            
            ima_instr = f"MANDATORY IMA ARCHITECTURE INTEGRATION (IMA + ADD-ON): {json.dumps(HUMAN_THINKING_METAMODEL)}"
            ma_instr = f"MANDATORY MENTAL APPROACHES INTEGRATION (MA): {json.dumps(MENTAL_APPROACHES_ONTOLOGY)}"
            
            full_context_text = f"[SYNTHESIS INQUIRY]: {user_query}\n[IDEA PRODUCTION INQUIRY]: {idea_query}\n[ATTACHED DATA]: {file_content}"

            sys_prompt_base = f"""
            You are the SIS Synthesizer. Perform an exhaustive dissertation (minimum 1500 words).
            ONTOLOGICAL RULES:
            1. {ima_instr}
            2. {ma_instr}
            
            FIELDS OF APPLICATION: {", ".join(sel_sciences)}. 
            HISTORICAL AUTHOR CONTEXT: {biblio}.
            METHODOLOGY: {", ".join(sel_methods)}.
            PARADIGMS: {", ".join(sel_paradigms)}.
            
            STRICT OUTPUT FORMAT:
            - Write a long technical dissertation first.
            - Focus on radical innovation and deep taxonomic relations.
            - End the textual part and append the marker '### SEMANTIC_GRAPH_JSON'.
            - Immediately follow with a valid JSON object ONLY.
            
            GRAPH JSON REQUIREMENTS:
            - Create 40+ interconnected nodes.
            - Use TT|BT|NT|AS|RT relation types.
            - Strictly use color/shape logic from provided ontologies.
            JSON schema: {{"nodes": [{{"id": "n1", "label": "Text", "type": "Root|Branch|Leaf|Class", "color": "#hex", "shape": "rectangle|ellipse|diamond"}}], "edges": [{{"source": "n1", "target": "n2", "rel_type": "AS|BT|NT|TT"}}]}}
            """

            # --- DUAL STAGE SYNERGY EXECUTION PATH ---
            if api_provider == "SYNERGY (Cerebras Spark + Groq Structure)":
                st.markdown('<div class="synergy-box">✨ SYNERGY ENGINE ACTIVE: Cerebras Spark (Llama-8B) → Groq Architect (Llama-70B)</div>', unsafe_allow_html=True)
                
                # Faza 1: Cerebras Innovation Spark (Wild ideas)
                c_client = OpenAI(api_key=cer_spark_k, base_url="https://api.cerebras.ai/v1")
                with st.spinner('Cerebras Spark Engine: Generating Innovative Cognitive Leaps...'):
                    sp_res = c_client.chat.completions.create(
                        model="llama3.1-8b", 
                        messages=[{"role": "user", "content": f"Generate 10 wild, radical innovations and 'Perspective Shifts' for: {full_context_text}"}], 
                        temperature=0.95
                    )
                    sparks = sp_res.choices[0].message.content
                
                # Faza 2: Groq Structural Architect (Logical structure and Graph)
                g_client = OpenAI(api_key=groq_arch_k, base_url="https://api.groq.com/openai/v1")
                with st.spinner('Groq Architect Engine: Performing Multi-Dimensional Synthesis...'):
                    f_res = g_client.chat.completions.create(
                        model="llama-3.3-70b-versatile", 
                        messages=[
                            {"role": "system", "content": sys_prompt_base + "\nINTEGRATE AND STRUCTURE THESE SPARKS: " + sparks}, 
                            {"role": "user", "content": full_context_text}
                        ], 
                        temperature=0.45, 
                        max_tokens=4000
                    )
                    text_out = f_res.choices[0].message.content
            else:
                # Standard Engine Call (Groq or Cerebras)
                base_url = "https://api.groq.com/openai/v1" if api_provider == "Groq" else "https://api.cerebras.ai/v1"
                model_name = "llama-3.3-70b-versatile" if api_provider == "Groq" else "llama3.1-8b"
                client = OpenAI(api_key=api_key if api_provider != "SYNERGY (Cerebras Spark + Groq Structure)" else groq_arch_k, base_url=base_url)
                
                with st.spinner(f'Synthesizing via {api_provider} ({model_name})...'):
                    res = client.chat.completions.create(
                        model=model_name, 
                        messages=[{"role": "system", "content": sys_prompt_base}, {"role": "user", "content": full_context_text}], 
                        temperature=0.75 if is_idea_mode else 0.45, 
                        max_tokens=4000
                    )
                    text_out = res.choices[0].message.content

            # --- POST-PROCESSING & RENDERING ---
            parts = text_out.split("### SEMANTIC_GRAPH_JSON")
            main_markdown = parts[0]
            
            # Semantic Post-processing (Highlighting & ID Anchors for navigation)
            if len(parts) > 1:
                try:
                    g_json = json.loads(re.search(r'\{.*\}', parts[1], re.DOTALL).group())
                    for n in g_json.get("nodes", []):
                        lbl, nid = n["label"], n["id"]
                        g_url = urllib.parse.quote(lbl)
                        main_markdown = re.sub(re.escape(lbl), f'<span id="{nid}"><a href="https://www.google.com/search?q={g_url}" target="_blank" class="semantic-node-highlight">{lbl}<i class="google-icon">↗</i></a></span>', main_markdown, count=1)
                except Exception: pass

            st.subheader("📊 SIS Synthesis Output")
            if is_idea_mode: st.markdown('<div class="idea-mode-box">💡 Innovation Mode engaged: Cerebras-Groq synergy is generating novel conceptual architectures.</div>', unsafe_allow_html=True)
            st.markdown(main_markdown, unsafe_allow_html=True)

            # --- GRAPH VISUALIZATION ENGINE ---
            if len(parts) > 1:
                try:
                    g_json = json.loads(re.search(r'\{.*\}', parts[1], re.DOTALL).group())
                    st.subheader("🕸️ Integrated Architectural Semantic Network")
                    st.caption("Visual mapping of the knowledge structure using IMA & MA logic.")
                    
                    elements = []
                    for n in g_json.get("nodes", []):
                        level = n.get("type", "Branch")
                        size = 110 if level == "Class" else (90 if level == "Root" else 75)
                        elements.append({"data": {
                            "id": n["id"], "label": n["label"], 
                            "color": n.get("color", "#2a9d8f"), 
                            "size": size, "shape": n.get("shape", "ellipse"), 
                            "z_index": 10 if level in ["Root", "Class"] else 1
                        }})
                    for e in g_json.get("edges", []):
                        elements.append({"data": {
                            "source": e["source"], "target": e["target"], 
                            "rel_type": e.get("rel_type", "AS")
                        }})
                    render_cytoscape_network(elements, "viz_final_canvas")
                except Exception: st.warning("Visual structure data parsing failed or structure is incomplete.")

            if biblio:
                with st.expander("📚 Extensive Metadata Record"):
                    st.text(biblio)
                
        except Exception as e: 
            st.error(f"Synthesis failed due to architectural error: {str(e)}")

# =========================================================================
# 6. PODNOŽJE (SIS FOOTER v22.5.0)
# =========================================================================
st.divider()
st.markdown("""
<div class="sis-footer">
    SIS Universal Synthesizer | v22.5.0 Synergy Architecture | petrič Engineering Arhitektura | © 2026<br>
    <i>Accelerated by Cerebras CS-3 & Groq LPU Logic Processing Units for multi-dimensional scientific reasoning.</i>
</div>
""", unsafe_allow_html=True)

# THE END OF SOURCE CODE. ENSURED VOLUME BY RETAINING ALL SCIENTIFIC DICTIONARIES AND VERBOSE CSS.






