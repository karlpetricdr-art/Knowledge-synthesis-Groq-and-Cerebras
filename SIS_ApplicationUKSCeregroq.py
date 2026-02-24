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
# The application date is hardcoded to reflect the specific session requirements.
SYSTEM_DATE = "February 24, 2026"

st.set_page_config(
    page_title=f"SIS Universal Knowledge Synthesizer - {SYSTEM_DATE}",
    page_icon="🌳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Deep CSS Integration for Semantic Highlights, Google Links, and Layout Boxes
# This section ensures the UI matches the high-sophistication aesthetic required.
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&family=Fira+Code:wght@400;500&display=swap');
    
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
        font-size: 2.8rem;
    }

    .sidebar-logo-container {
        display: flex;
        justify-content: center;
        padding: 15px 0;
    }
    
    .date-badge {
        background-color: #1d3557;
        color: white;
        padding: 4px 12px;
        border-radius: 50px;
        font-size: 0.85em;
        font-weight: 600;
        margin-bottom: 10px;
        display: inline-block;
    }

    /* Code block refinements */
    code {
        font-family: 'Fira Code', monospace !important;
    }
    
    /* Custom Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #fcfcfc;
        border-right: 1px solid #eee;
    }
    
    .stButton>button {
        border-radius: 8px;
        transition: all 0.2s ease;
    }
</style>
""", unsafe_allow_html=True)

def get_svg_base64(svg_str):
    """Utility to encode SVG for Streamlit components."""
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
# 1. CORE RENDERING & DATA FETCHING
# =============================================================================

def render_cytoscape_network(elements, container_id="cy_synergy_full"):
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
                    idealEdgeLength: 180 
                }}
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
    components.html(cyto_html, height=800)

def fetch_author_bibliographies(author_input):
    """Retrieves high-fidelity bibliographic data from ORCID and Semantic Scholar."""
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
                    for work in works[:12]:
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
# 2. ARCHITECTURAL ONTOLOGIES (IMA & MA) - EXPANDED
# =============================================================================

# A. INTEGRATED METAMODEL ARCHITECTURE (IMA) - Structural Logic
HUMAN_THINKING_METAMODEL = {
    "nodes": {
        "Human mental concentration": {
            "color": "#ADB5BD", 
            "shape": "rectangle", 
            "desc": "The foundational state of cognitive focus required for interdisciplinary synthesis and logical rigor."
        },
        "Identity": {
            "color": "#C6EFCE", 
            "shape": "rectangle", 
            "desc": "The subjective core of the cognitive actor, including values, professional background, and systemic position."
        },
        "Autobiographical memory": {
            "color": "#C6EFCE", 
            "shape": "rectangle", 
            "desc": "The repository of personal and professional experiences that color logical interpretations and mission setting."
        },
        "Mission": {
            "color": "#92D050", 
            "shape": "rectangle", 
            "desc": "The high-level existential or professional purpose driving the current inquiry or problem-solving cycle."
        },
        "Vision": {
            "color": "#FFFF00", 
            "shape": "rectangle", 
            "desc": "A mental simulation of the desired future state, serving as the blueprint for long-term goal setting."
        },
        "Goal": {
            "color": "#00B0F0", 
            "shape": "rectangle", 
            "desc": "Specific, quantifiable, and time-bound targets that materialize the mission within the constraints of reality."
        },
        "Problem": {
            "color": "#F2DCDB", 
            "shape": "rectangle", 
            "desc": "A perceived gap or obstruction between the current state and the goal/vision state."
        },
        "Ethics/moral": {
            "color": "#FFC000", 
            "shape": "rectangle", 
            "desc": "The internal filtration system used to determine the validity and acceptability of proposed solutions."
        },
        "Hierarchy of interests": {
            "color": "#F8CBAD", 
            "shape": "rectangle", 
            "desc": "The ordering of desires and needs that dictates where cognitive resources are allocated during conflict."
        },
        "Rule": {
            "color": "#F2F2F2", 
            "shape": "rectangle", 
            "desc": "Formal or informal constraints (laws, scientific principles, protocols) that govern the search for solutions."
        },
        "Decision-making": {
            "color": "#FFFF99", 
            "shape": "rectangle", 
            "desc": "The actual act of choosing between alternative pathways to resolve a identified problem."
        },
        "Problem solving": {
            "color": "#D9D9D9", 
            "shape": "rectangle", 
            "desc": "The algorithmic application of tools and knowledge to remove obstructions and reach goals."
        },
        "Conflict situation": {
            "color": "#00FF00", 
            "shape": "rectangle", 
            "desc": "A state where two or more goals, missions, or rules clash, requiring high-level synthesis."
        },
        "Knowledge": {
            "color": "#DDEBF7", 
            "shape": "rectangle", 
            "desc": "The internalized collection of facts, theories, and models leveraged for reasoning."
        },
        "Tool": {
            "color": "#00B050", 
            "shape": "rectangle", 
            "desc": "External instruments (software, hardware, methodologies) used to interact with the problem domain."
        },
        "Experience": {
            "color": "#00B050", 
            "shape": "rectangle", 
            "desc": "The practical skill and wisdom gained through the repetitive cycle of decision-making and problem-solving."
        },
        "Classification": {
            "color": "#CCC0DA", 
            "shape": "rectangle", 
            "desc": "The taxonomic act of grouping knowledge or problems into structured categories for better retrieval."
        },
        "Psychological aspect": {
            "color": "#F8CBAD", 
            "shape": "rectangle", 
            "desc": "The internal cognitive and emotional outcomes resulting from the success or failure of the synthesis."
        },
        "Sociological aspect": {
            "color": "#00FFFF", 
            "shape": "rectangle", 
            "desc": "The external collective impact and systemic changes triggered by the produced ideas."
        }
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
        ("Problem solving", "Conflict situation", "resolves"),
        ("Knowledge", "Classification", "organizes")
    ]
}

# B. MENTAL APPROACHES (MA) - Cognitive Transformation Logic
MENTAL_APPROACHES_ONTOLOGY = {
    "nodes": {
        "Perspective shifting": {
            "color": "#00FF00", 
            "shape": "diamond", 
            "desc": "The ability to rotate the problem space and view it through disparate scientific and stakeholder lenses."
        },
        "Similarity and difference": {
            "color": "#FFFF00", 
            "shape": "diamond", 
            "desc": "The fundamental pattern-recognition act of comparing current data against existing mental models."
        },
        "Core": {
            "color": "#FFC000", 
            "shape": "diamond", 
            "desc": "The distillation process of isolating the most critical, unchangeable essence of a complex problem."
        },
        "Attraction": {
            "color": "#F2A6A2", 
            "shape": "diamond", 
            "desc": "The force that draws disparate knowledge nodes together to form a novel synthesis."
        },
        "Repulsion": {
            "color": "#D9D9D9", 
            "shape": "diamond", 
            "desc": "The logic of isolating incompatible theories or separating non-essential noise from the core."
        },
        "Condensation": {
            "color": "#CCC0DA", 
            "shape": "diamond", 
            "desc": "The reduction of vast informational complexity into a singular, actionable strategic insight."
        },
        "Framework and foundation": {
            "color": "#F8CBAD", 
            "shape": "diamond", 
            "desc": "Establishing the ground rules and logical boundaries within which innovation must occur."
        },
        "Bipolarity and dialectics": {
            "color": "#DDEBF7", 
            "shape": "diamond", 
            "desc": "The synthesis of truth through the tension of opposing forces (Thesis and Antithesis)."
        },
        "Constant": {
            "color": "#E1C1D1", 
            "shape": "diamond", 
            "desc": "Identifying invariants within a system that remain stable regardless of environmental flux."
        },
        "Associativity": {
            "color": "#E1C1D1", 
            "shape": "diamond", 
            "desc": "The lateral linking of knowledge nodes that do not share a direct causal or taxonomic path."
        },
        "Induction": {
            "color": "#B4C6E7", 
            "shape": "diamond", 
            "desc": "Building broad interdisciplinary theory from specific experimental or field observations."
        },
        "Whole and part": {
            "color": "#00FF00", 
            "shape": "diamond", 
            "desc": "The mental zoom logic of navigating between holistic system views and granular component detail."
        },
        "Mini-max": {
            "color": "#00FF00", 
            "shape": "diamond", 
            "desc": "The optimization filter focused on achieving maximum innovative utility with minimum cognitive friction."
        },
        "Addition and composition": {
            "color": "#FF00FF", 
            "shape": "diamond", 
            "desc": "Building complexity through the incremental layering of simpler conceptual building blocks."
        },
        "Hierarchy": {
            "color": "#C6EFCE", 
            "shape": "diamond", 
            "desc": "Organizing ideas into vertical priority stacks based on their foundational importance."
        },
        "Balance": {
            "color": "#00B0F0", 
            "shape": "diamond", 
            "desc": "The search for dynamic equilibrium in systems with multiple competing variables."
        },
        "Deduction": {
            "color": "#92D050", 
            "shape": "diamond", 
            "desc": "Applying broad scientific laws or axioms to solve a specific problematic instance."
        },
        "Abstraction and elimination": {
            "color": "#00B0F0", 
            "shape": "diamond", 
            "desc": "The removal of specific real-world noise to reach a generic, re-usable innovative model."
        },
        "Pleasure and displeasure": {
            "color": "#00FF00", 
            "shape": "diamond", 
            "desc": "The aesthetic and emotional feedback loop evaluating the elegance of a solution."
        },
        "Openness and closedness": {
            "color": "#FFC000", 
            "shape": "diamond", 
            "desc": "Determining whether a system should incorporate new external data or protect its current internal state."
        }
    },
    "relations": [
        ("Perspective shifting", "Similarity and difference", "leads to"),
        ("Core", "Attraction", "initiates"),
        ("Induction", "Whole and part", "links"),
        ("Hierarchy", "Balance", "regulates"),
        ("Deduction", "Abstraction and elimination", "processes")
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
            "methods": ["Axiomatization", "Formal Proof", "Computational Geometry", "Stochastic Modeling"], 
            "tools": ["MATLAB", "LaTeX", "WolframAlpha", "NumPy"], 
            "facets": ["Topology", "Algebra", "Number Theory", "Calculus"]
        },
        "Physics": {
            "cat": "Natural", 
            "methods": ["Quantum Modeling", "Particle Tracking", "Simulation", "Interferometry"], 
            "tools": ["Accelerator", "Spectrometer", "Oscilloscopes", "Cryostats"], 
            "facets": ["Relativity", "Thermodynamics", "Quantum Mechanics", "Astro-physics"]
        },
        "Chemistry": {
            "cat": "Natural", 
            "methods": ["Titration", "Molecular Spectroscopy", "Organic Synthesis", "Chromatography"], 
            "tools": ["NMR", "Gas Chromatography", "Mass Spec", "Burettes"], 
            "facets": ["Organic", "Physical", "Biochemistry", "Analytical"]
        },
        "Biology": {
            "cat": "Natural", 
            "methods": ["Gene Sequencing", "CRISPR", "Cell Culture", "Taxonomy"], 
            "tools": ["Electron Microscope", "PCR Machine", "Petri Dishes", "Centrifuge"], 
            "facets": ["Genetics", "Microbiology", "Ecology", "Neurobiology"]
        },
        "Neuroscience": {
            "cat": "Natural", 
            "methods": ["Neuroimaging", "Optogenetics", "Behavioral Mapping"], 
            "tools": ["fMRI", "EEG", "Electrodes", "Patch Clamp"], 
            "facets": ["Cognitive Neuroscience", "Neural Plasticity", "Synaptic Physiology"]
        },
        "Psychology": {
            "cat": "Social", 
            "methods": ["Double-Blind Trials", "Psychometrics", "Longitudinal Studies"], 
            "tools": ["Standardized Tests", "Eye Tracking", "Surveys", "Biofeedback"], 
            "facets": ["Behavioral", "Clinical", "Developmental", "Cognitive"]
        },
        "Sociology": {
            "cat": "Social", 
            "methods": ["Ethnography", "Survey Design", "Social Network Analysis"], 
            "tools": ["NVivo", "SPSS", "Stata", "Census Data"], 
            "facets": ["Demography", "Stratification", "Social Dynamics"]
        },
        "Computer Science": {
            "cat": "Formal", 
            "methods": ["Algorithm Design", "Formal Verification", "Parallel Computing"], 
            "tools": ["GPU Clusters", "Docker", "Compilers", "VS Code"], 
            "facets": ["AI", "Cybersecurity", "Blockchain", "Quantum Computing"]
        },
        "Medicine": {
            "cat": "Applied", 
            "methods": ["Clinical Trials", "Epidemiology", "Radiology"], 
            "tools": ["MRI", "CT", "Biomarker Assays", "Ultrasound"], 
            "facets": ["Genomics", "Immunology", "Pathology", "Oncology"]
        },
        "Engineering": {
            "cat": "Applied", 
            "methods": ["Finite Element Analysis", "Prototyping", "Stress Testing"], 
            "tools": ["CAD", "3D Printers", "Load Cells", "Simulation Software"], 
            "facets": ["Robotics", "Nanotech", "Civil Eng", "Electrical Eng"]
        },
        "Legal science": {
            "cat": "Social", 
            "methods": ["Legal Hermeneutics", "Comparative Law", "Dogmatic Method"], 
            "tools": ["Case Law Archives", "Legislative Databases", "Westlaw"], 
            "facets": ["Jurisprudence", "Constitutional Law", "Criminal Law"]
        },
        "Economics": {
            "cat": "Social", 
            "methods": ["Econometrics", "Game Theory", "Macro Modeling"], 
            "tools": ["Stata", "Bloomberg", "R", "Python"], 
            "facets": ["Macroeconomics", "Finance", "Behavioral Econ"]
        },
        "Philosophy": {
            "cat": "Humanities", 
            "methods": ["Socratic Method", "Dialectics", "Phenomenology"], 
            "tools": ["Logic Mapping", "Critical Discourse Analysis"], 
            "facets": ["Epistemology", "Ethics", "Metaphysics", "Logic"]
        },
        "Linguistics": {
            "cat": "Humanities", 
            "methods": ["Corpus Analysis", "Syntactic Parsing", "Historical Phonetics"], 
            "tools": ["Praat", "NLTK", "WordNet", "ELAN"], 
            "facets": ["Semantics", "Phonology", "Sociolinguistics"]
        },
        "Ecology": {
            "cat": "Natural", 
            "methods": ["Remote Sensing", "Trophic Modeling", "Field Sampling"], 
            "tools": ["GIS", "Biosensors", "Lidar", "Drones"], 
            "facets": ["Biodiversity", "Biogeochemistry", "Conservation"]
        },
        "History": {
            "cat": "Humanities", 
            "methods": ["Archival Research", "Historiography", "Oral History"], 
            "tools": ["Radiocarbon Dating", "Microfilm", "Digital Archives"], 
            "facets": ["Military History", "Diplomacy", "Ancient Civilizations"]
        },
        "Criminology": {
            "cat": "Social", 
            "methods": ["Profiling", "Case Studies", "Victimology"], 
            "tools": ["Crime Mapping", "AFIS", "CODIS"], 
            "facets": ["Penology", "Forensic Psych", "Criminal Justice"]
        },
        "Forensic sciences": {
            "cat": "Natural", 
            "methods": ["Trace Analysis", "DNA Profiling", "Ballistics"], 
            "tools": ["Luminol", "Mass Spec", "Gas Chromatography"], 
            "facets": ["Digital Forensics", "Pathology", "Odontology"]
        },
        "Architecture": {
            "cat": "Humanities/Applied",
            "methods": ["Parametric Design", "Sustainability Analysis", "BIM"],
            "tools": ["Revit", "Rhino 3D", "Photogrammetry"],
            "facets": ["Urban Design", "Heritage Conservation", "Landscape Arch"]
        },
        "Pedagogy": {
            "cat": "Social",
            "methods": ["Instructional Design", "Action Research", "Differentiated Learning"],
            "tools": ["LMS Systems", "Interactive Whiteboards"],
            "facets": ["Educational Psych", "Curriculum Dev", "Special Education"]
        },
        "Library Science": {
            "cat": "Applied",
            "methods": ["Taxonomy", "Archival Appraisal", "Information Retrieval"],
            "tools": ["OPAC", "Metadata Systems", "Thesauri"],
            "facets": ["Knowledge Org", "Digital Curation", "Bibliometrics"]
        }
    }
}

# =============================================================================
# 4. INTERFACE CONSTRUCTION (STREAMLIT SIDEBAR & MAIN)
# =============================================================================

if 'expertise_val' not in st.session_state: st.session_state.expertise_val = "Expert"
if 'show_user_guide' not in st.session_state: st.session_state.show_user_guide = False

# --- EXPANDED LEFT SIDEBAR ---
with st.sidebar:
    st.markdown(f'<div class="sidebar-logo-container"><img src="data:image/svg+xml;base64,{get_svg_base64(SVG_3D_RELIEF)}" width="200"></div>', unsafe_allow_html=True)
    st.header("⚙️ SYSTEM CONTROL")
    st.markdown(f'<div class="date-badge">DATE: {SYSTEM_DATE}</div>', unsafe_allow_html=True)
    
    # API INPUT SECTION
    st.subheader("🔑 Access Credentials")
    groq_api_key = st.text_input("Groq API Key (Phase 1 Synthesis):", type="password", help="Provides structural foundation via IMA.")
    cerebras_api_key = st.text_input("Cerebras API Key (Phase 2 Ideas):", type="password", help="Generates innovations and graph via MA.")
    
    # INTERACTIVE BUTTONS & UTILITIES
    st.divider()
    col_reset, col_guide = st.columns(2)
    with col_reset:
        if st.button("♻️ RESET", use_container_width=True):
            for key in list(st.session_state.keys()): del st.session_state[key]
            st.rerun()
    with col_guide:
        if st.button("📖 GUIDE", use_container_width=True):
            st.session_state.show_user_guide = not st.session_state.show_user_guide
            st.rerun()
            
    # EXTERNAL CONNECTOR BUTTONS (THE MISSING LINKS)
    st.divider()
    st.subheader("🌐 EXTERNAL CONNECTORS")
    st.link_button("📂 GitHub Repository", "https://github.com/", use_container_width=True)
    st.link_button("🆔 ORCID Registry", "https://orcid.org/", use_container_width=True)
    st.link_button("🎓 Google Scholar", "https://scholar.google.com/", use_container_width=True)
    
    # ONTOLOGY EXPLORERS (EXPANDERS)
    st.divider()
    st.subheader("📚 KNOWLEDGE EXPLORER")
    with st.expander("👤 User Profiles"):
        for p, d in KNOWLEDGE_BASE["User profiles"].items(): st.write(f"**{p}**: {d['description']}")
    with st.expander("🧠 Mental Approaches (MA)"):
        for m, d in MENTAL_APPROACHES_ONTOLOGY["nodes"].items(): st.write(f"• **{m}**: {d['desc']}")
    with st.expander("🏛️ Metamodel Nodes (IMA)"):
        for n, d in HUMAN_THINKING_METAMODEL["nodes"].items(): st.write(f"• **{n}**: {d['desc']}")
    with st.expander("🌍 Scientific Paradigms"):
        for p, d in KNOWLEDGE_BASE["Scientific paradigms"].items(): st.write(f"**{p}**: {d}")
    with st.expander("🔬 Science Fields (Detailed)"):
        for s in sorted(KNOWLEDGE_BASE["Science fields"].keys()): st.write(f"• **{s}**")
    with st.expander("🏗️ Structural Models"):
        for m, d in KNOWLEDGE_BASE["Structural models"].items(): st.write(f"**{m}**: {d}")

# --- MAIN PAGE CONTENT ---
st.markdown('<h1 class="main-header-gradient">🧱 SIS Universal Knowledge Synthesizer</h1>', unsafe_allow_html=True)
st.markdown(f"Advanced Multi-dimensional interdisciplinary pipeline | **{SYSTEM_DATE}**")

if st.session_state.show_user_guide:
    st.info(f"""
    **Sequential Synergy Pipeline Guide (Updated {SYSTEM_DATE}):**
    1. **Dual Engines**: Enter your Groq and Cerebras keys. Groq handles logical synthesis; Cerebras handles creative production.
    2. **Research Inquiry (Step 1)**: Groq builds a foundation (approx 1500 words) using Integrated Metamodel Architecture (IMA).
    3. **Innovation Prompt (Step 2)**: Cerebras takes Groq's research foundation and applies Mental Approaches (MA) logic to generate novel ideas.
    4. **Semantic Network**: The final interactive graph is produced by Cerebras, mapping the interconnections between IMA and MA concepts.
    5. **Interaction**: Hover over nodes to see a magnifying effect on their neighbors. Click on nodes to auto-scroll and highlight specific text segments.
    """)

# REFERENCE BOXES
col_ref1, col_ref2 = st.columns(2)
with col_ref1:
    st.markdown("""
    <div class="metamodel-box">
        <b>🏛️ Phase 1: Groq (IMA Architecture)</b><br>
        Structural reasoning using Identity, Mission, Problem, and Rule. Provides the interdisciplinary factual foundation.
    </div>
    """, unsafe_allow_html=True)

with col_ref2:
    st.markdown("""
    <div class="mental-approach-box">
        <b>🧠 Phase 2: Cerebras (MA Architecture)</b><br>
        Cognitive transformation using Dialectics, Perspective Shifting, and Essence. Produces innovative solutions and high-density mapping.
    </div>
    """, unsafe_allow_html=True)

st.markdown("### 🛠️ CONFIGURE SYNERGY PIPELINE")

# CONFIG ROW 1
r1c1, r1c2, r1c3 = st.columns([1.5, 2, 1])
with r1c1:
    target_authors = st.text_input("👤 Authors for Metadata Analysis:", placeholder="Karl Petrič, Samo Kralj, Teodor Petrič", help="Fetches real ORCID publication history.")
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
    user_query = st.text_area("❓ STEP 1: Research Inquiry (for GROQ):", placeholder="Describe the problem factually for structural synthesis...", height=200)
with col_inq2:
    idea_query = st.text_area("💡 STEP 2: Innovation Prompt (for CEREBRAS):", placeholder="Define the targets for innovative idea production based on Phase 1...", height=200)
with col_inq3:
    uploaded_file = st.file_uploader("📂 ATTACH DATA (.txt only):", type=['txt'], help="Attach local documents to provide further context to the AI engines.")
    file_content = ""
    if uploaded_file: 
        file_content = uploaded_file.read().decode("utf-8")
        st.success(f"Attached: {uploaded_file.name}")

# =============================================================================
# 5. SYNERGY EXECUTION ENGINE (GROQ -> CEREBRAS)
# =============================================================================

if st.button("🚀 EXECUTE MULTI-DIMENSIONAL SEQUENTIAL SYNERGY PIPELINE", use_container_width=True):
    if not groq_api_key or not cerebras_api_key:
        st.error("❌ Dual-Model synergy requires both Groq and Cerebras keys in the sidebar.")
    elif not user_query:
        st.warning("⚠️ Phase 1 Research Inquiry is required to establish the foundation.")
    else:
        try:
            # Init Clients
            groq_client = OpenAI(api_key=groq_api_key, base_url="https://api.groq.com/openai/v1")
            cerebras_client = OpenAI(api_key=cerebras_api_key, base_url="https://api.cerebras.ai/v1")
            
            # Metadata fetch
            biblio = fetch_author_bibliographies(target_authors) if target_authors else ""

            # --- PHASE 1: GROQ (IMA Synthesis) ---
            with st.spinner('PHASE 1: Groq synthesizing structural foundation (IMA Logic)...'):
                groq_sys = f"""
                You are the SIS Research Synthesizer (Phase 1).
                DATE OF OPERATION: {SYSTEM_DATE}
                STRICT IMA ARCHITECTURE FOCUS: {json.dumps(HUMAN_THINKING_METAMODEL)}
                
                DATA CONTEXT:
                Sciences: {sel_sciences}. 
                Paradigms: {sel_paradigms}. 
                Expertise: {expertise}. 
                Goal: {goal_context}.
                Authors: {biblio}. 
                Data Context: {file_content}

                TASK:
                Provide a factual, structurally-sound interdisciplinary dissertation (approx 1500 words).
                Focus strictly on mapping the problem structure, identifying mission-critical rules, and taxonomic organization.
                DO NOT generate innovative ideas or graph JSON yet. Only provide the deep research foundation.
                """
                
                groq_resp = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": groq_sys}, {"role": "user", "content": user_query}],
                    temperature=0.4
                )
                groq_synthesis = groq_resp.choices[0].message.content

            # --- PHASE 2: CEREBRAS (MA Innovation + Graph JSON) ---
            with st.spinner('PHASE 2: Cerebras producing innovative ideas and semantic mapping (MA Logic)...'):
                cerebras_sys = f"""
                You are the SIS Innovation Engine (Phase 2).
                DATE OF OPERATION: {SYSTEM_DATE}
                
                STRICT MENTAL APPROACHES (MA) FOCUS: {json.dumps(MENTAL_APPROACHES_ONTOLOGY)}
                
                TASK:
                1. Review the RESEARCH FOUNDATION generated by your partner (Groq).
                2. Apply MA logic (Dialectics, Core, Perspective Shifting) to generate radical 'Useful Innovative Ideas'.
                3. Propose generative solutions that don't exist in existing literature.
                4. End your response with '### SEMANTIC_GRAPH_JSON' followed by a valid JSON network (40-50 nodes).
                
                VISUAL RULES: 
                - Use IMA colors/shapes (rectangles) for factual foundation concepts.
                - Use MA colors/shapes (diamonds) for innovative transformation concepts.
                - Ensure dense interconnection using BT (Broader), NT (Narrower), and AS (Associative) links.
                
                JSON schema: {{"nodes": [{{"id": "n1", "label": "Text", "type": "Root|Branch", "color": "#hex", "shape": "rectangle|diamond"}}], "edges": [{{"source": "n1", "target": "n2", "rel_type": "AS|BT|outcome_of"}}]}}
                """
                
                cerebras_prompt = f"[RESEARCH FOUNDATION GENERATED BY GROQ]:\n{groq_synthesis}\n\n[USER INNOVATION REQUEST]:\n{idea_query}"
                
                cerebras_resp = cerebras_client.chat.completions.create(
                    model="llama3.1-70b",
                    messages=[{"role": "system", "content": cerebras_sys}, {"role": "user", "content": cerebras_prompt}],
                    temperature=0.85
                )
                cerebras_innovation = cerebras_resp.choices[0].message.content

            # --- POST-PROCESSING & RENDERING ---
            combined_content = f"## 📚 Phase 1: Research Foundation (Groq)\n{groq_synthesis}\n\n---\n## 💡 Phase 2: Useful Innovative Ideas (Cerebras)\n{cerebras_innovation}"
            
            parts = combined_content.split("### SEMANTIC_GRAPH_JSON")
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
                    st.caption(f"Mapped by Cerebras on {SYSTEM_DATE} based on the Groq-generated Research Foundation.")
                    
                    elements = []
                    for n in g_json.get("nodes", []):
                        level = n.get("type", "Branch")
                        size = 110 if level == "Root" else (85 if level == "Branch" else 65)
                        elements.append({"data": {
                            "id": n["id"], "label": n["label"], "color": n.get("color", "#2a9d8f"),
                            "size": size, "shape": n.get("shape", "rectangle"), "z_index": 1
                        }})
                    for e in g_json.get("edges", []):
                        elements.append({"data": {
                            "source": e["source"], "target": e["target"], "rel_type": e.get("rel_type", "AS")
                        }})
                    render_cytoscape_network(elements, "viz_synergy_final_800")
                except: st.warning("⚠️ Error: Could not parse Semantic Graph JSON from Cerebras innovation results.")

            if biblio:
                with st.expander("📚 EXTENDED BIBLIOGRAPHIC METADATA"):
                    st.text(biblio)

        except Exception as e:
            st.error(f"❌ Sequential Synergy Failure: {e}")

# =============================================================================
# 6. FOOTER & METRICS
# =============================================================================
st.divider()
st.caption(f"SIS Universal Knowledge Synthesizer | v22.4 Sequential Synergy | Groq & Cerebras Pipeline | {SYSTEM_DATE}")
st.write("")
st.write("")














