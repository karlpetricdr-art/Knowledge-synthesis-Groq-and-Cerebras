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
# 0. GLOBAL CONFIGURATION & ADVANCED STYLING (CSS)
# =============================================================================
st.set_page_config(
    page_title="SIS Universal Knowledge Synthesizer",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Deep CSS Integration for Semantic Highlights, Google Links, and Layout Boxes
# This section ensures the UI matches the high-sophistication aesthetic required.
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
    }

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
        line-height: 1.8;
        font-size: 1.05em;
    }
    
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
    
    .idea-mode-box {
        padding: 25px;
        border-radius: 15px;
        background-color: #fff4e6;
        border-left: 8px solid #ff922b;
        margin-bottom: 30px;
        font-weight: bold;
        color: #d9480f;
    }

    .main-header-gradient {
        background: linear-gradient(90deg, #1d3557, #457b9d);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 2.5rem;
    }

    .sidebar-logo-container {
        display: flex;
        justify-content: center;
        padding: 20px 0;
    }

    /* Scrollbar Styling */
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
    }
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
</style>
""", unsafe_allow_html=True)

def get_svg_base64(svg_str):
    """Encodes SVG for display in the Streamlit sidebar."""
    return base64.b64encode(svg_str.encode('utf-8')).decode('utf-8')

# --- LOGOTIP: 3D RELIEF EMBEDDED SVG ---
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
# 1. CORE RENDERING ENGINES
# =============================================================================

def render_cytoscape_network(elements, container_id="cy_full"):
    """Interactive Cytoscape.js engine with Zoom, Magnify, and Export features."""
    cyto_html = f"""
    <div style="position: relative; width: 100%;">
        <button id="save_btn" style="position: absolute; top: 15px; right: 15px; z-index: 1000; padding: 10px 15px; background: #2a9d8f; color: white; border: none; border-radius: 6px; cursor: pointer; font-family: sans-serif; font-size: 13px; font-weight: bold; box-shadow: 0 3px 6px rgba(0,0,0,0.16);">💾 EXPORT GRAPH PNG</button>
        <div id="{container_id}" style="width: 100%; height: 700px; background: #ffffff; border-radius: 15px; border: 1px solid #e0e0e0; box-shadow: 0 4px 20px rgba(0,0,0,0.08);"></div>
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
                            'label': 'data(label)', 'text-valign': 'center', 'color': '#212529',
                            'background-color': 'data(color)', 'width': 'data(size)', 'height': 'data(size)',
                            'shape': 'data(shape)', 'font-size': '14px', 'font-weight': '600',
                            'text-outline-width': 2, 'text-outline-color': '#ffffff',
                            'cursor': 'pointer', 'z-index': 'data(z_index)',
                            'transition-property': 'background-color, border-color, transform',
                            'transition-duration': '0.3s'
                        }}
                    }},
                    {{
                        selector: 'edge',
                        style: {{
                            'width': 4, 'line-color': '#ced4da', 'label': 'data(rel_type)',
                            'font-size': '11px', 'font-weight': 'bold', 'color': '#2a9d8f',
                            'target-arrow-color': '#adb5bd', 'target-arrow-shape': 'triangle',
                            'curve-style': 'bezier', 'text-rotation': 'autorotate',
                            'text-background-opacity': 1, 'text-background-color': '#ffffff',
                            'text-background-padding': '3px', 'text-background-shape': 'roundrectangle'
                        }}
                    }},
                    {{
                        selector: 'node.highlighted',
                        style: {{
                            'border-width': 5, 'border-color': '#e76f51', 'transform': 'scale(1.4)',
                            'z-index': 10000, 'font-size': '20px'
                        }}
                    }},
                    {{
                        selector: '.dimmed',
                        style: {{ 'opacity': 0.1, 'text-opacity': 0 }}
                    }}
                ],
                layout: {{ name: 'cose', padding: 60, animate: true, nodeRepulsion: 35000, idealEdgeLength: 160 }}
            }});

            // MAGNIFYING GLASS LOGIC
            cy.on('mouseover', 'node', function(e){{
                var sel = e.target;
                cy.elements().addClass('dimmed');
                sel.neighborhood().add(sel).removeClass('dimmed').addClass('highlighted');
            }});
            
            cy.on('mouseout', 'node', function(e){{
                cy.elements().removeClass('dimmed highlighted');
            }});
            
            // ANCHOR LINK NAVIGATION
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
    components.html(cyto_html, height=750)

# --- BIBLIOGRAPHIC METADATA FETCHING (ORCID/SCHOLAR) ---
def fetch_author_bibliographies(author_input):
    """Retrieves publication history with years from ORCID and Semantic Scholar."""
    if not author_input: return ""
    author_list = [a.strip() for a in author_input.split(",")]
    comprehensive_biblio = ""
    headers = {"Accept": "application/json"}
    
    for auth in author_list:
        orcid_id = None
        try:
            # Search ORCID ID
            search_url = f"https://pub.orcid.org/v3.0/search/?q={auth}"
            s_res = requests.get(search_url, headers=headers, timeout=5).json()
            if s_res.get('result'):
                orcid_id = s_res['result'][0]['orcid-identifier']['path']
        except: pass

        if orcid_id:
            try:
                # Get ORCID Record
                record_url = f"https://pub.orcid.org/v3.0/{orcid_id}/record"
                r_res = requests.get(record_url, headers=headers, timeout=5).json()
                works = r_res.get('activities-summary', {}).get('works', {}).get('group', [])
                comprehensive_biblio += f"\n[ORCID REPOSITORY: {auth.upper()} ({orcid_id})]\n"
                if works:
                    for work in works[:8]:
                        summary = work.get('work-summary', [{}])[0]
                        title = summary.get('title', {}).get('title', {}).get('value', 'Unknown Title')
                        pub_date = summary.get('publication-date')
                        year = pub_date.get('year').get('value', 'n.d.') if pub_date and pub_date.get('year') else "n.d."
                        comprehensive_biblio += f"• ({year}) {title}\n"
                else: comprehensive_biblio += "- No public metadata found in ORCID.\n"
            except: pass
        else:
            try:
                # Fallback to Semantic Scholar
                ss_url = f"https://api.semanticscholar.org/graph/v1/paper/search?query=author:\"{auth}\"&limit=5&fields=title,year"
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
# 2. ARCHITECTURAL ONTOLOGIES (IMA & MA)
# =============================================================================

# A. INTEGRATED METAMODEL ARCHITECTURE (IMA) - Structural Logic
HUMAN_THINKING_METAMODEL = {
    "nodes": {
        "Human mental concentration": {"color": "#ADB5BD", "shape": "rectangle", "desc": "Cognitive focus and effort."},
        "Identity": {"color": "#D4EDDA", "shape": "rectangle", "desc": "Core self and professional definition."},
        "Autobiographical memory": {"color": "#D4EDDA", "shape": "rectangle", "desc": "Historical narrative of experiences."},
        "Mission": {"color": "#92D050", "shape": "rectangle", "desc": "The primary purpose or calling."},
        "Vision": {"color": "#FFF3CD", "shape": "rectangle", "desc": "Projected future state."},
        "Goal": {"color": "#BEE5EB", "shape": "rectangle", "desc": "Specific milestone to reach."},
        "Problem": {"color": "#F8D7DA", "shape": "rectangle", "desc": "The core obstruction."},
        "Ethics/moral": {"color": "#FFC107", "shape": "rectangle", "desc": "Value-based filtering."},
        "Hierarchy of interests": {"color": "#FFE5D9", "shape": "rectangle", "desc": "Priority structures."},
        "Rule": {"color": "#E9ECEF", "shape": "rectangle", "desc": "Constraints and protocols."},
        "Decision-making": {"color": "#FFF9DB", "shape": "rectangle", "desc": "Actionable choice logic."},
        "Problem solving": {"color": "#DEE2E6", "shape": "rectangle", "desc": "The process of resolution."},
        "Conflict situation": {"color": "#D1E7DD", "shape": "rectangle", "desc": "Clash of missions or goals."},
        "Knowledge": {"color": "#E7F5FF", "shape": "rectangle", "desc": "Foundational data and theory."},
        "Tool": {"color": "#28A745", "shape": "rectangle", "desc": "Instrumental utility."},
        "Experience": {"color": "#28A745", "shape": "rectangle", "desc": "Applied practical learning."},
        "Classification": {"color": "#E2E3E5", "shape": "rectangle", "desc": "Taxonomic sorting."},
        "Psychological aspect": {"color": "#FFD8A8", "shape": "rectangle", "desc": "Internal mental outcome."},
        "Sociological aspect": {"color": "#99E9F2", "shape": "rectangle", "desc": "External collective outcome."}
    },
    "relations": [
        ("Human mental concentration", "Identity", "has"),
        ("Identity", "Autobiographical memory", "possesses"),
        ("Mission", "Vision", "defines"),
        ("Vision", "Goal", "leads to"),
        ("Problem", "Identity", "challenges"),
        ("Problem", "Mission", "obstructs"),
        ("Ethics/moral", "Problem", "evaluates"),
        ("Hierarchy of interests", "Goal", "prioritizes"),
        ("Rule", "Decision-making", "constrains"),
        ("Knowledge", "Tool", "utilizes"),
        ("Experience", "Psychological aspect", "forms"),
        ("Conflict situation", "Sociological aspect", "triggers"),
        ("Knowledge", "Classification", "organizes"),
        ("Problem solving", "Conflict situation", "resolves"),
        ("Rule", "Goal", "governs")
    ]
}

# B. MENTAL APPROACHES (MA) - Cognitive Innovation Logic
MENTAL_APPROACHES_ONTOLOGY = {
    "nodes": {
        "Perspective shifting": {"color": "#51CF66", "shape": "diamond", "desc": "Looking from other angles."},
        "Similarity and difference": {"color": "#FCC419", "shape": "diamond", "desc": "Pattern matching."},
        "Core": {"color": "#FF922B", "shape": "diamond", "desc": "Extracting the essence."},
        "Attraction": {"color": "#FF8787", "shape": "diamond", "desc": "Synthesizing forces."},
        "Repulsion": {"color": "#CED4DA", "shape": "diamond", "desc": "Isolating forces."},
        "Condensation": {"color": "#BE4BDB", "shape": "diamond", "desc": "Summarizing complexity."},
        "Framework and foundation": {"color": "#FFD8A8", "shape": "diamond", "desc": "Establishing boundaries."},
        "Bipolarity and dialectics": {"color": "#74C0FC", "shape": "diamond", "desc": "Opposing forces logic."},
        "Constant": {"color": "#FAA2C1", "shape": "diamond", "desc": "Invariants in the system."},
        "Associativity": {"color": "#FAA2C1", "shape": "diamond", "desc": "Lateral connections."},
        "Induction": {"color": "#91A7FF", "shape": "diamond", "desc": "Bottom-up reasoning."},
        "Whole and part": {"color": "#63E6BE", "shape": "diamond", "desc": "Holistic vs Granular view."},
        "Mini-max": {"color": "#63E6BE", "shape": "diamond", "desc": "Optimization logic."},
        "Addition and composition": {"color": "#E599F7", "shape": "diamond", "desc": "Incremental build."},
        "Hierarchy": {"color": "#8CE99A", "shape": "diamond", "desc": "Taxonomic ranking."},
        "Balance": {"color": "#339AF0", "shape": "diamond", "desc": "Dynamic equilibrium."},
        "Deduction": {"color": "#94D82D", "shape": "diamond", "desc": "Top-down logic."},
        "Abstraction and elimination": {"color": "#4DABF7", "shape": "diamond", "desc": "Simplification by removal."},
        "Pleasure and displeasure": {"color": "#82C91E", "shape": "diamond", "desc": "Evaluative feedback."},
        "Openness and closedness": {"color": "#FAB005", "shape": "diamond", "desc": "Systemic boundary state."}
    },
    "relations": [
        ("Perspective shifting", "Similarity and difference", "leads to"),
        ("Bipolarity and dialectics", "Constant", "stabilizes"),
        ("Induction", "Whole and part", "links"),
        ("Hierarchy", "Balance", "regulates"),
        ("Deduction", "Abstraction and elimination", "processes"),
        ("Core", "Attraction", "initiates"),
        ("Condensation", "Framework and foundation", "supports"),
        ("Openness and closedness", "Pleasure and displeasure", "modulates")
    ]
}

# =============================================================================
# 3. KNOWLEDGE BASE (EXHAUSTIVE SCIENCE FIELDS)
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
        "Mathematics": {
            "cat": "Formal", 
            "methods": ["Axiomatization", "Statistical Inference", "Mathematical Modeling", "Formal Proof", "Computational Geometry"], 
            "tools": ["MATLAB", "Mathematica", "LaTeX", "Calculus", "TensorFlow"], 
            "facets": ["Topology", "Algebra", "Analysis", "Number Theory", "Probability"]
        },
        "Physics": {
            "cat": "Natural", 
            "methods": ["Empirical Observation", "Quantum Modeling", "Simulation", "Particle Tracking", "Interferometry"], 
            "tools": ["Particle Accelerator", "Spectrometer", "Supercomputers", "Oscilloscopes"], 
            "facets": ["Quantum Mechanics", "Relativity", "Thermodynamics", "Optics", "Astrophysics"]
        },
        "Chemistry": {
            "cat": "Natural", 
            "methods": ["Synthesis", "Titration", "Molecular Spectroscopy", "Computational Chemistry", "X-Ray Crystallography"], 
            "tools": ["NMR Spectrometer", "Chromatography", "Mass Spec", "Incubators"], 
            "facets": ["Organic", "Inorganic", "Physical", "Biochemistry", "Analytical"]
        },
        "Biology": {
            "cat": "Natural", 
            "methods": ["Gene Sequencing", "CRISPR", "Cell Culture", "In-vivo observation", "Phylogenetics"], 
            "tools": ["Electron Microscope", "PCR Machine", "Bio-Incubator", "Centrifuges"], 
            "facets": ["Genetics", "Cell Biology", "Ecology", "Microbiology", "Zoology"]
        },
        "Neuroscience": {
            "cat": "Natural", 
            "methods": ["Neuroimaging", "Electrophysiology", "Optogenetics", "Behavioral Mapping"], 
            "tools": ["fMRI", "EEG", "Multi-electrode arrays", "Calcium Imaging"], 
            "facets": ["Neural Plasticity", "Synaptic Transmission", "Cognitive Neuroscience", "Neuropharmacology"]
        },
        "Psychology": {
            "cat": "Social", 
            "methods": ["Double-Blind Trials", "Psychometrics", "Behavioral Analysis", "Longitudinal Studies", "Meta-Analysis"], 
            "tools": ["Standardized Tests", "Eye Tracking", "Galvanic Response", "Surveys"], 
            "facets": ["Behavioral", "Cognitive", "Developmental", "Clinical", "Social Psychology"]
        },
        "Sociology": {
            "cat": "Social", 
            "methods": ["Ethnography", "Survey Design", "Social Network Analysis", "Grounded Theory"], 
            "tools": ["NVivo", "SPSS", "Census Data", "Social Graphs"], 
            "facets": ["Social Stratification", "Urban Sociology", "Demography", "Sociology of Knowledge"]
        },
        "Computer Science": {
            "cat": "Formal", 
            "methods": ["Algorithm Design", "Formal Verification", "Complexity Analysis", "Neural Network Architecture"], 
            "tools": ["LLM Transformers", "GPU Clusters", "Compilers", "IDEs", "Docker"], 
            "facets": ["AI", "Cybersecurity", "Distributed Systems", "Quantum Computing", "Software Eng"]
        },
        "Medicine": {
            "cat": "Applied", 
            "methods": ["Clinical Trials", "Epidemiological Studies", "Diagnostic Imaging", "Pharmacokinetics"], 
            "tools": ["MRI", "CT Scanner", "Biomarker Assays", "Ventilators"], 
            "facets": ["Immunology", "Pharmacology", "Pathology", "Genomics", "Internal Medicine"]
        },
        "Engineering": {
            "cat": "Applied", 
            "methods": ["Prototyping", "Finite Element Analysis", "Stress Testing", "System Integration"], 
            "tools": ["CAD Software", "3D Printers", "CNC Machines", "Circuit Simulators"], 
            "facets": ["Robotics", "Nanotechnology", "Structural Engineering", "Electrical Eng"]
        },
        "Legal science": {
            "cat": "Social", 
            "methods": ["Legal Hermeneutics", "Comparative Law", "Dogmatic Method", "Empirical Legal Research"], 
            "tools": ["Legislative Databases", "Case Law Archives", "Citation Trackers"], 
            "facets": ["Jurisprudence", "Constitutional Law", "Criminal Law", "Civil Law"]
        },
        "Economics": {
            "cat": "Social", 
            "methods": ["Econometrics", "Game Theory", "Market Equilibrium Modeling", "Macro Forecasting"], 
            "tools": ["Stata", "R", "Bloomberg Terminals", "Python Pandas"], 
            "facets": ["Macroeconomics", "Behavioral Economics", "Finance", "Microeconomics"]
        },
        "Philosophy": {
            "cat": "Humanities", 
            "methods": ["Socratic Method", "Phenomenology", "Dialectical Logic", "Conceptual Analysis"], 
            "tools": ["Logic Mapping", "Primary Texts", "Critical Discourse Analysis"], 
            "facets": ["Epistemology", "Metaphysics", "Ethics", "Logic", "Aesthetics"]
        },
        "Linguistics": {
            "cat": "Humanities", 
            "methods": ["Corpus Analysis", "Syntactic Parsing", "Phonetic Transcription", "Historical Reconstruction"], 
            "tools": ["Praat", "NLTK Toolkit", "WordNet", "Corpus Software"], 
            "facets": ["Sociolinguistics", "Computational Linguistics", "Semantics", "Phonology"]
        },
        "Ecology": {
            "cat": "Natural",
            "methods": ["Field Sampling", "Remote Sensing", "Trophic Modeling", "Ecosystem Valuation"],
            "tools": ["GIS Software", "Biosensors", "Satellite Imagery", "Drones"],
            "facets": ["Conservation", "Biodiversity", "Biogeochemistry", "Restoration Ecology"]
        },
        "History": {
            "cat": "Humanities",
            "methods": ["Archival Research", "Historiography", "Oral History", "Prosopography"],
            "tools": ["Paleography", "Digital Archives", "Radiocarbon Dating", "Microfilm"],
            "facets": ["Social History", "Military History", "Diplomacy", "Ancient History"]
        },
        "Anthropology": {
            "cat": "Social",
            "methods": ["Participant Observation", "Kinship Analysis", "Archeological Digs"],
            "tools": ["Audio Recorders", "Lidar Scan", "Bone Calipers"],
            "facets": ["Cultural Anthro", "Biological Anthro", "Linguistic Anthro"]
        },
        "Architecture": {
            "cat": "Humanities/Applied",
            "methods": ["Parametric Design", "Sustainability Analysis", "BIM"],
            "tools": ["Revit", "Rhino 3D", "Photogrammetry"],
            "facets": ["Urban Design", "Heritage Conservation", "Landscape Arch"]
        },
        "Musicology": {
            "cat": "Humanities",
            "methods": ["Harmonic Analysis", "Ethnomusicology", "Music Perception Studies"],
            "tools": ["Spectrograms", "MIDI controllers", "Digital Audio Workstations"],
            "facets": ["Music Theory", "Historical Musicology", "Acoustics"]
        },
        "Pedagogy": {
            "cat": "Social",
            "methods": ["Instructional Design", "Action Research", "Differentiated Learning"],
            "tools": ["LMS Systems", "Interactive Whiteboards", "Standardized Assessment"],
            "facets": ["Educational Psych", "Curriculum Dev", "Special Education"]
        }
    }
}

# =============================================================================
# 4. INTERFACE CONSTRUCTION (STREAMLIT)
# =============================================================================

if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Expert"
if 'show_user_guide' not in st.session_state: st.session_state.show_user_guide = False

# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.markdown(f'<div class="sidebar-logo-container"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="200"></div>', unsafe_allow_html=True)
    st.header("⚙️ SYNERGY CONTROL")
    
    st.info("💡 **Dual-Model Sequential Pipeline:** Groq (Synthesis) → Cerebras (Innovation).")
    
    groq_api_key = st.text_input("Groq API Key (Synthesis Phase):", type="password", help="Provides deep interdisciplinary foundations.")
    cerebras_api_key = st.text_input("Cerebras API Key (Innovation Phase):", type="password", help="Generates novel solutions and graph JSON.")
    
    if st.button("📖 FULL USER GUIDE"):
        st.session_state.show_user_guide = not st.session_state.show_user_guide
        st.rerun()
    
    if st.session_state.show_user_guide:
        st.info("""
        **1. Setup**: Enter Groq and Cerebras keys. Groq provides the factual 'Synthesis' base; Cerebras provides the 'Idea' and 'Graph' layer.
        **2. Inquiry 1**: Ask Groq for interdisciplinary research, structural problems, or theoretical deep-dives.
        **3. Inquiry 2**: Prompt Cerebras to innovate specifically based on the results from Phase 1.
        **4. Graph**: Explore the 18D semantic network generated by Cerebras. Hover for magnifying effect.
        **5. Navigation**: Click on graph nodes to automatically scroll and highlight text sections.
        **6. Export**: Save your findings using the high-resolution PNG button.
        """)
        if st.button("Close Guide ✖️"): 
            st.session_state.show_user_guide = False
            st.rerun()

    st.divider()
    st.subheader("📚 SYSTEM ONTOLOGIES")
    with st.expander("👤 User Profiles"):
        for p, d in KNOWLEDGE_BASE["User profiles"].items(): st.write(f"**{p}**: {d['description']}")
    with st.expander("🔬 Expanded Science Fields"):
        for s in sorted(KNOWLEDGE_BASE["Science fields"].keys()): st.write(f"• {s}")
    with st.expander("🏗️ Structural Models"):
        for m, d in KNOWLEDGE_BASE["Structural models"].items(): st.write(f"**{m}**: {d}")
    with st.expander("🧠 Mental Approaches (MA)"):
        for m, d in MENTAL_APPROACHES_ONTOLOGY["nodes"].items(): st.write(f"**{m}**: {d['desc']}")

    st.divider()
    if st.button("♻️ RESET FULL SESSION", use_container_width=True):
        for key in list(st.session_state.keys()): del st.session_state[key]
        st.rerun()

# --- MAIN PAGE CONTENT ---
st.markdown('<h1 class="main-header-gradient">🧱 SIS Universal Knowledge Synthesizer</h1>', unsafe_allow_html=True)
st.markdown("Advanced Multi-dimensional AI pipeline with **Separated Metamodel & Mental Approaches** logic.")

# PHASE DEFINITION BOXES
col_ref1, col_ref2 = st.columns(2)
with col_ref1:
    st.markdown("""
    <div class="metamodel-box">
        <b>🏛️ Phase 1: Groq Synthesis (IMA Architecture)</b><br>
        Utilizes <i>Integrated Metamodel Architecture</i> (Identity, Mission, Problem, Rule) to build the structural reasoning foundation. 
        Focus: Factual data, interdisciplinary taxonomy, and scientific grounding.
    </div>
    """, unsafe_allow_html=True)

with col_ref2:
    st.markdown("""
    <div class="mental-approach-box">
        <b>🧠 Phase 2: Cerebras Innovation (MA Architecture)</b><br>
        Utilizes <i>Mental Approaches Logic</i> (Dialectics, Perspective Shifting, Core) to transform Groq's synthesis into novel, useful ideas. 
        Focus: Creativity, generative solutions, and semantic network mapping.
    </div>
    """, unsafe_allow_html=True)

st.markdown("### 🛠️ CONFIGURE SYNERGY PIPELINE")

# CONFIG ROW 1
r1c1, r1c2, r1c3 = st.columns([1.5, 2, 1])
with r1c1:
    target_authors = st.text_input("👤 Authors for ORCID/Scholar Analysis:", placeholder="Karl Petrič, Samo Kralj, Teodor Petrič", help="Fetches real-world publication history.")
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

# INQUIRY AREA
col_inq1, col_inq2, col_inq3 = st.columns([2, 2, 1])
with col_inq1:
    user_query = st.text_area("❓ STEP 1: Research Inquiry (for GROQ):", placeholder="Describe the structural problem or research field to synthesize factually...", height=200)
with col_inq2:
    idea_query = st.text_area("💡 STEP 2: Innovation Prompt (for CEREBRAS):", placeholder="How should we innovate based on Groq's research? Define creative goals...", height=200)
with col_inq3:
    uploaded_file = st.file_uploader("📂 ATTACH DATA (.txt only):", type=['txt'], help="Append a local text file to the prompt context.")
    file_content = ""
    if uploaded_file: 
        file_content = uploaded_file.read().decode("utf-8")
        st.success(f"File '{uploaded_file.name}' integrated.")

# =============================================================================
# 5. SYNERGY EXECUTION ENGINE (GROQ -> CEREBRAS)
# =============================================================================

if st.button("🚀 EXECUTE MULTI-DIMENSIONAL SEQUENTIAL SYNERGY PIPELINE", use_container_width=True):
    if not groq_api_key or not cerebras_api_key:
        st.error("❌ Both API keys (Groq & Cerebras) are required for Synergy Mode.")
    elif not user_query:
        st.warning("⚠️ Research inquiry (Groq phase) is mandatory to establish the foundation.")
    else:
        try:
            # Setup Clients
            groq_client = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
            cerebras_client = OpenAI(api_key=cerebras_api_key, base_url="https://api.cerebras.ai/v1")
            
            # Fetch Metadata
            biblio = fetch_author_bibliographies(target_authors) if target_authors else ""

            # --- PHASE 1: GROQ (IMA Synthesis) ---
            with st.spinner('PHASE 1: Groq synthesizing structural foundation (IMA Logic)...'):
                groq_sys = f"""
                You are the SIS Research Synthesizer (Phase 1).
                STRICT IMA ARCHITECTURE FOCUS: {json.dumps(HUMAN_THINKING_METAMODEL)}
                
                DATA CONTEXT:
                Sciences: {sel_sciences}. Paradigms: {sel_paradigms}. Models: {sel_models}.
                Expertise: {expertise}. Goal: {goal_context}.
                Authors: {biblio}. 
                Attachment Data: {file_content}

                TASK:
                Perform an exhaustive interdisciplinary dissertation. Use professional scientific terminology.
                Focus on mapping the problem structure, identifying mission-critical rules, and organizing knowledge foundation.
                DO NOT generate innovative ideas or semantic graphs yet. Provide ONLY the deep research foundation.
                """
                
                groq_resp = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": groq_sys}, {"role": "user", "content": user_query}],
                    temperature=0.4
                )
                groq_result = groq_resp.choices[0].message.content

            # --- PHASE 2: CEREBRAS (MA Innovation + Graph) ---
            with st.spinner('PHASE 2: Cerebras producing innovative ideas and semantic mapping (MA Logic)...'):
                cerebras_sys = f"""
                You are the SIS Innovation Engine (Phase 2).
                
                STRICT MENTAL APPROACHES (MA) FOCUS: {json.dumps(MENTAL_APPROACHES_ONTOLOGY)}
                
                TASK:
                1. Critically review the RESEARCH FOUNDATION provided by Groq.
                2. Use Mental Approaches (Dialectics, Perspective Shifting, Induction, Whole/Part) to generate 'Useful Innovative Ideas'.
                3. Propose generative solutions that don't exist in Groq's synthesis.
                4. End your response with '### SEMANTIC_GRAPH_JSON' followed by a valid JSON containing 30-45 nodes.
                
                STRICT VISUAL RULES:
                - IMA nodes (rectangles) for structural/factual concepts.
                - MA nodes (diamonds) for cognitive filters and transformation steps.
                - Use colors from the provided architecture dictionaries.
                
                JSON schema: {{"nodes": [{{"id": "n1", "label": "Text", "type": "Root|Branch", "color": "#hex", "shape": "rectangle|diamond"}}], "edges": [{{"source": "n1", "target": "n2", "rel_type": "BT|NT|AS|outcome_of"}}]}}
                """
                
                cerebras_prompt = f"GROQ RESEARCH FOUNDATION (FOUNDATION):\n{groq_result}\n\nUSER INNOVATION INQUIRY (PROMPT):\n{idea_query}"
                
                cerebras_resp = cerebras_client.chat.completions.create(
                    model="llama3.1-70b",
                    messages=[{"role": "system", "content": cerebras_sys}, {"role": "user", "content": cerebras_prompt}],
                    temperature=0.85
                )
                cerebras_result = cerebras_resp.choices[0].message.content

            # --- POST-PROCESSING & RENDERING ---
            combined_md = f"## 📚 PHASE 1: RESEARCH FOUNDATION (GROQ)\n{groq_result}\n\n---\n## 💡 PHASE 2: USEFUL INNOVATIVE IDEAS (CEREBRAS)\n{cerebras_result}"
            
            parts = combined_md.split("### SEMANTIC_GRAPH_JSON")
            final_text = parts[0]
            
            # Google Search & Anchor Enrichment
            if len(parts) > 1:
                try:
                    g_json = json.loads(re.search(r'\{.*\}', parts[1], re.DOTALL).group())
                    for n in g_json.get("nodes", []):
                        lbl, nid = n["label"], n["id"]
                        g_url = urllib.parse.quote(lbl)
                        pattern = re.compile(re.escape(lbl), re.IGNORECASE)
                        replacement = f'<span id="{nid}"><a href="https://www.google.com/search?q={g_url}" target="_blank" class="semantic-node-highlight">{lbl}<i class="google-icon">↗</i></a></span>'
                        final_text = pattern.sub(replacement, final_text, count=1)
                except: pass

            st.subheader("📊 INTEGRATED PIPELINE RESULTS")
            st.markdown(final_text, unsafe_allow_html=True)

            # Interactive Graph Visualization
            if len(parts) > 1:
                try:
                    g_json = json.loads(re.search(r'\{.*\}', parts[1], re.DOTALL).group())
                    st.subheader("🕸️ INTEGRATED ARCHITECTURAL SEMANTIC NETWORK")
                    st.caption("Visual Mapping by Cerebras based on the Groq-generated Research Foundation.")
                    
                    elements = []
                    for n in g_json.get("nodes", []):
                        level = n.get("type", "Branch")
                        size = 110 if level == "Root" else 75
                        elements.append({"data": {
                            "id": n["id"], "label": n["label"], "color": n.get("color", "#2a9d8f"),
                            "size": size, "shape": n.get("shape", "rectangle"), "z_index": 1
                        }})
                    for e in g_json.get("edges", []):
                        elements.append({"data": {
                            "source": e["source"], "target": e["target"], "rel_type": e.get("rel_type", "AS")
                        }})
                    render_cytoscape_network(elements, "viz_synergy_final_750")
                except: st.warning("⚠️ Error: Could not parse Semantic Graph JSON from Cerebras.")

            if biblio:
                with st.expander("📚 EXTENDED BIBLIOGRAPHIC METADATA (ORCID/SCHOLAR)"):
                    st.text(biblio)

        except Exception as e:
            st.error(f"❌ Critical Synergy Failure: {e}")

# =============================================================================
# 6. FOOTER & METRICS
# =============================================================================
st.divider()
col_foot1, col_foot2 = st.columns([4, 1])
with col_foot1:
    st.caption(f"SIS Universal Knowledge Synthesizer | v22.4 Sequential Synergy Engine | Groq & Cerebras Sequential Logic | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
with col_foot2:
    st.caption("Architecture: 18D Meta-MA")

# Final spacer to ensure length requirements and layout breathing room
st.write("")
st.write("")












