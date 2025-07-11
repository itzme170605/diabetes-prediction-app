// src/pages/ResearchPage.tsx
import React, { useState } from 'react';
import './ResearchPage.css';

const ResearchPage: React.FC = () => {
  const [activeEquation, setActiveEquation] = useState<number | null>(null);
  const [currentAnimation, setCurrentAnimation] = useState<number>(0);

  const equations = [
    {
      id: 1,
      name: "GLP-1 Dynamics",
      equation: "dL/dt = λL(t) - μLB·B·L - μLA·A·L",
      description: "Models the glucagon-like peptide-1 hormone that stimulates insulin release after meals",
      variables: ["L: GLP-1 concentration", "B: β-cell density", "A: α-cell density"],
      parameters: ["λL: GLP-1 secretion rate", "μLB: GLP-1 absorption by β-cells", "μLA: GLP-1 absorption by α-cells"]
    },
    {
      id: 2,
      name: "β-cell Dynamics",
      equation: "dB/dt = λ̃B·(L-L0)/(KL+(L-L0)) - μ̃B·B·(1+ξ1·G+ξ2·P)",
      description: "Insulin-producing cells that are activated by GLP-1 and impaired by glucose toxicity",
      variables: ["B: β-cell density", "L: GLP-1 concentration", "G: glucose", "P: palmitic acid"],
      parameters: ["λ̃B: activation rate", "μ̃B: deactivation rate", "ξ1, ξ2: impairment factors"]
    },
    {
      id: 3,
      name: "α-cell Dynamics", 
      equation: "dA/dt = λ̃A·(Ihypo-I)/(KI+(Ihypo-I))·1/(1+L/K̂L) - μ̃A·A",
      description: "Glucagon-producing cells activated during hypoglycemia, suppressed by GLP-1",
      variables: ["A: α-cell density", "I: insulin", "L: GLP-1"],
      parameters: ["λ̃A: activation rate", "Ihypo: hypoglycemia threshold", "K̂L: GLP-1 inhibition"]
    },
    {
      id: 4,
      name: "Insulin Dynamics",
      equation: "dI/dt = λIB·B - μI·I - μIG·G·I",
      description: "Primary hormone for glucose regulation, secreted by β-cells",
      variables: ["I: insulin concentration", "B: β-cell density", "G: glucose"],
      parameters: ["λIB: insulin secretion rate", "μI: insulin decay", "μIG: glucose-dependent decay"]
    },
    {
      id: 5,
      name: "GLUT-4 Dynamics",
      equation: "dU4/dt = λU4I·I·1/(1+ηTα·Tα) - μU4·U4",
      description: "Glucose transporter from blood to cells, activated by insulin, inhibited by inflammation",
      variables: ["U4: GLUT-4 density", "I: insulin", "Tα: TNF-α"],
      parameters: ["λU4I: activation by insulin", "ηTα: TNF-α inhibition", "μU4: decay rate"]
    },
    {
      id: 6,
      name: "Blood Glucose",
      equation: "dG/dt = λG(t) - λG*(t)·G + λG*U2·G*·U2/(KU2+U2) - λGU4·G·U4/(KU4+U4)",
      description: "Central variable representing blood glucose concentration",
      variables: ["G: blood glucose", "G*: stored glucose", "U2: GLUT-2", "U4: GLUT-4"],
      parameters: ["λG: glucose input", "λG*: glucose elimination", "Transport coefficients"]
    }
  ];

  const parameterTable = [
    { param: "KL", description: "Half-saturation of GLP-1", value: "1.7×10⁻¹⁴", unit: "g/cm³", source: "Estimated" },
    { param: "KU2", description: "Half-saturation of GLUT-2", value: "9.45×10⁻⁶", unit: "g/cm³", source: "Wolfsdorf (2012)" },
    { param: "KU4", description: "Half-saturation of GLUT-4", value: "2.78×10⁻⁶", unit: "g/cm³", source: "Gorovits (2003)" },
    { param: "λIB", description: "Insulin secretion by β-cells", value: "1.26×10⁻⁸", unit: "d⁻¹", source: "Estimated" },
    { param: "μI", description: "Insulin decay rate", value: "198.04", unit: "d⁻¹", source: "Morishima (1992)" },
    { param: "γG", description: "Baseline glucose secretion", value: "0.017", unit: "g/cm³·d⁻¹", source: "Estimated" },
    { param: "λTα", description: "TNF-α secretion rate", value: "1.19×10⁻⁹", unit: "g/cm³·d⁻¹", source: "Estimated" },
    { param: "μTα", description: "TNF-α decay rate", value: "199", unit: "d⁻¹", source: "Simo (2012)" }
  ];

  return (
    <div className="research-page">
      {/* Hero Section */}
      <section className="research-hero">
        <div className="container">
          <h1>Mathematical Model of Diabetes</h1>
          <p className="hero-subtitle">
            Understanding obesity-induced type 2 diabetes through mathematical modeling
          </p>
          
          <div className="paper-citation">
            <div className="citation-box">
              <h3>📄 Research Paper</h3>
              <p className="citation-text">
                <strong>Siewe, N., & Friedman, A.</strong> (2024). A mathematical model of obesity-induced 
                type 2 diabetes and efficacy of anti-diabetic weight reducing drug. 
                <em>Journal of Theoretical Biology</em>, 581, 111756.
              </p>
              <div className="citation-links">
                <a href="https://doi.org/10.1016/j.jtbi.2024.111756" 
                   target="_blank" 
                   rel="noopener noreferrer"
                   className="btn-secondary">
                  📖 Read Paper
                </a>
                <button className="btn-primary">📋 Copy Citation</button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Model Overview */}
      <section className="model-overview">
        <div className="container">
          <h2>Model Overview</h2>
          <div className="overview-grid">
            <div className="overview-card">
              <div className="card-icon">🔬</div>
              <h3>12 Variables</h3>
              <p>Complete physiological system including hormones, cells, and metabolites</p>
            </div>
            <div className="overview-card">
              <div className="card-icon">📊</div>
              <h3>50+ Parameters</h3>
              <p>Carefully calibrated constants based on experimental literature</p>
            </div>
            <div className="overview-card">
              <div className="card-icon">🧮</div>
              <h3>ODE System</h3>
              <p>Differential equations modeling dynamic interactions over time</p>
            </div>
            <div className="overview-card">
              <div className="card-icon">💊</div>
              <h3>Treatment Effects</h3>
              <p>Includes modeling of GLP-1 agonist drugs like Mounjaro and Ozempic</p>
            </div>
          </div>
        </div>
      </section>

      {/* Variables Section */}
      <section className="variables-section">
        <div className="container">
          <h2>Model Variables</h2>
          <div className="variables-grid">
            <div className="variable-card">
              <h3>L - GLP-1</h3>
              <p>Glucagon-like peptide-1 hormone concentration</p>
              <div className="variable-role">Stimulates insulin release after meals</div>
            </div>
            <div className="variable-card">
              <h3>A - α-cells</h3>
              <p>Pancreatic α-cell density</p>
              <div className="variable-role">Secrete glucagon to raise blood glucose</div>
            </div>
            <div className="variable-card">
              <h3>B - β-cells</h3>
              <p>Pancreatic β-cell density</p>
              <div className="variable-role">Secrete insulin to lower blood glucose</div>
            </div>
            <div className="variable-card">
              <h3>I - Insulin</h3>
              <p>Insulin hormone concentration</p>
              <div className="variable-role">Primary glucose-lowering hormone</div>
            </div>
            <div className="variable-card">
              <h3>G - Glucose</h3>
              <p>Blood glucose concentration</p>
              <div className="variable-role">Central variable for diabetes diagnosis</div>
            </div>
            <div className="variable-card">
              <h3>U4 - GLUT-4</h3>
              <p>Glucose transporter type 4</p>
              <div className="variable-role">Transports glucose from blood to cells</div>
            </div>
            <div className="variable-card">
              <h3>P - Palmitic Acid</h3>
              <p>Pro-inflammatory fatty acid</p>
              <div className="variable-role">Causes insulin resistance in obesity</div>
            </div>
            <div className="variable-card">
              <h3>Tα - TNF-α</h3>
              <p>Tumor necrosis factor alpha</p>
              <div className="variable-role">Inflammatory marker that impairs insulin</div>
            </div>
          </div>
        </div>
      </section>

      {/* Equations Section */}
      <section className="equations-section">
        <div className="container">
          <h2>Mathematical Equations</h2>
          <p className="section-subtitle">
            The core differential equations that govern glucose dynamics
          </p>
          
          <div className="equations-container">
            {equations.map((eq) => (
              <div 
                key={eq.id}
                className={`equation-card ${activeEquation === eq.id ? 'active' : ''}`}
                onClick={() => setActiveEquation(activeEquation === eq.id ? null : eq.id)}
              >
                <div className="equation-header">
                  <h3>{eq.name}</h3>
                  <div className="equation-formula">
                    {eq.equation}
                  </div>
                </div>
                
                {activeEquation === eq.id && (
                  <div className="equation-details">
                    <p className="equation-description">{eq.description}</p>
                    
                    <div className="equation-info">
                      <div className="info-section">
                        <h4>Variables:</h4>
                        <ul>
                          {eq.variables.map((variable, idx) => (
                            <li key={idx}>{variable}</li>
                          ))}
                        </ul>
                      </div>
                      
                      <div className="info-section">
                        <h4>Parameters:</h4>
                        <ul>
                          {eq.parameters.map((param, idx) => (
                            <li key={idx}>{param}</li>
                          ))}
                        </ul>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Parameters Table */}
      <section className="parameters-section">
        <div className="container">
          <h2>Key Parameters</h2>
          <p className="section-subtitle">
            Selected physiological constants from Table 2 of the research paper
          </p>
          
          <div className="parameters-table-container">
            <table className="parameters-table">
              <thead>
                <tr>
                  <th>Parameter</th>
                  <th>Description</th>
                  <th>Value</th>
                  <th>Unit</th>
                  <th>Source</th>
                </tr>
              </thead>
              <tbody>
                {parameterTable.map((param, idx) => (
                  <tr key={idx}>
                    <td><code>{param.param}</code></td>
                    <td>{param.description}</td>
                    <td>{param.value}</td>
                    <td>{param.unit}</td>
                    <td>{param.source}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          <div className="parameters-note">
            <p>
              <strong>Note:</strong> Complete parameter table with 50+ constants is available in the full research paper.
              Values marked as "Estimated" were derived through model fitting and literature synthesis.
            </p>
          </div>
        </div>
      </section>

      {/* Pathophysiology Flowchart Section */}
      <section className="pathophysiology-section">
        <div className="container">
          <h2>Diabetes Pathophysiology</h2>
          <p className="section-subtitle">
            Complete network interactions showing how obesity leads to type 2 diabetes
          </p>
          
          <div className="pathophysiology-container">
            <div className="scenario-tabs">
              <button 
                className={`tab ${currentAnimation === 0 ? 'active' : ''}`}
                onClick={() => setCurrentAnimation(0)}
              >
                Normal Physiology
              </button>
              <button 
                className={`tab ${currentAnimation === 1 ? 'active' : ''}`}
                onClick={() => setCurrentAnimation(1)}
              >
                Obesity & NEFA Effects
              </button>
              <button 
                className={`tab ${currentAnimation === 2 ? 'active' : ''}`}
                onClick={() => setCurrentAnimation(2)}
              >
                Treatment with GLP-1 Agonists
              </button>
            </div>

            <div className="flowchart-container">
              {currentAnimation === 0 && (
                <div className="flowchart normal-pathway">
                  <div className="flowchart-title">Normal Glucose Regulation Network</div>
                  
                  {/* Food Intake */}
                  <div className="component food-intake" data-component="food-intake">
                    <div className="component-icon">🍽️</div>
                    <div className="component-label">Food Intake</div>
                  </div>

                  {/* GLP-1 */}
                  <div className="component hormone glp1" data-component="glp1">
                    <div className="component-icon">💊</div>
                    <div className="component-label">GLP-1</div>
                  </div>

                  {/* Beta Cells */}
                  <div className="component cell beta-cell" data-component="beta-cell">
                    <div className="component-icon">🔵</div>
                    <div className="component-label">β-cells</div>
                  </div>

                  {/* Insulin */}
                  <div className="component hormone insulin" data-component="insulin">
                    <div className="component-icon">💉</div>
                    <div className="component-label">Insulin</div>
                  </div>

                  {/* GLUT-4 */}
                  <div className="component transporter glut4" data-component="glut4">
                    <div className="component-icon">🚪</div>
                    <div className="component-label">GLUT-4</div>
                  </div>

                  {/* Glucose */}
                  <div className="component metabolite glucose" data-component="glucose">
                    <div className="component-icon">🍯</div>
                    <div className="component-label">Blood Glucose</div>
                  </div>

                  {/* Liver */}
                  <div className="component organ liver" data-component="liver">
                    <div className="component-icon">🫀</div>
                    <div className="component-label">Liver</div>
                    <div className="sub-component">
                      <div className="component-label">Stored Glucose</div>
                      <div className="component-label">Glycogen</div>
                    </div>
                  </div>

                  {/* Alpha Cells */}
                  <div className="component cell alpha-cell" data-component="alpha-cell">
                    <div className="component-icon">🔴</div>
                    <div className="component-label">α-cells</div>
                  </div>

                  {/* Glucagon */}
                  <div className="component hormone glucagon" data-component="glucagon">
                    <div className="component-icon">⚡</div>
                    <div className="component-label">Glucagon</div>
                  </div>

                  {/* GLUT-2 */}
                  <div className="component transporter glut2" data-component="glut2">
                    <div className="component-icon">🚪</div>
                    <div className="component-label">GLUT-2</div>
                  </div>

                  {/* SVG Arrows */}
                  <svg className="connection-svg" viewBox="0 0 1200 600">
                    {/* Food to GLP-1 */}
                    <path d="M 190 120 L 270 120" stroke="#e67e22" strokeWidth="3" fill="none" markerEnd="url(#arrowhead)"/>
                    
                    {/* GLP-1 to Beta cells */}
                    <path d="M 410 120 L 490 120" stroke="#e67e22" strokeWidth="3" fill="none" markerEnd="url(#arrowhead)"/>
                    
                    {/* Beta cells to Insulin */}
                    <path d="M 630 120 L 710 120" stroke="#e67e22" strokeWidth="3" fill="none" markerEnd="url(#arrowhead)"/>
                    
                    {/* Insulin to GLUT-4 */}
                    <path d="M 850 120 L 930 120" stroke="#e67e22" strokeWidth="3" fill="none" markerEnd="url(#arrowhead)"/>
                    
                    {/* GLUT-4 to Glucose */}
                    <path d="M 1000 180 L 1000 250" stroke="#e67e22" strokeWidth="3" fill="none" markerEnd="url(#arrowhead)"/>
                    
                    {/* Glucose to Liver */}
                    <path d="M 1000 350 L 1000 420" stroke="#e67e22" strokeWidth="3" fill="none" markerEnd="url(#arrowhead)"/>
                    
                    {/* Alpha cells to Glucagon */}
                    <path d="M 630 480 L 710 480" stroke="#e67e22" strokeWidth="3" fill="none" markerEnd="url(#arrowhead)"/>
                    
                    {/* Glucagon to GLUT-2 */}
                    <path d="M 850 480 L 930 480" stroke="#e67e22" strokeWidth="3" fill="none" markerEnd="url(#arrowhead)"/>
                    
                    {/* GLUT-2 to Glucose (reverse) */}
                    <path d="M 1000 430 C 1050 430 1050 300 1000 300" stroke="#e67e22" strokeWidth="3" fill="none" markerEnd="url(#arrowhead)"/>
                    
                    {/* GLP-1 inhibits Alpha cells */}
                    <path d="M 340 180 C 340 350 490 350 490 430" stroke="#3498db" strokeWidth="3" fill="none" markerEnd="url(#inhibition)" strokeDasharray="5,5"/>
                    
                    {/* Define arrow markers */}
                    <defs>
                      <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                        <polygon points="0 0, 10 3.5, 0 7" fill="#e67e22"/>
                      </marker>
                      <marker id="inhibition" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
                        <circle cx="5" cy="5" r="3" fill="none" stroke="#3498db" strokeWidth="2"/>
                        <line x1="2" y1="5" x2="8" y2="5" stroke="#3498db" strokeWidth="2"/>
                      </marker>
                    </defs>
                  </svg>
                </div>
              )}

              {currentAnimation === 1 && (
                <div className="flowchart obesity-pathway">
                  <div className="flowchart-title">Obesity-Induced NEFA Effects Network</div>
                  
                  {/* Food Intake Enhanced */}
                  <div className="component food-intake enhanced" data-component="food-intake">
                    <div className="component-icon">🍽️</div>
                    <div className="component-label">Excessive Food Intake</div>
                    <div className="component-note">Increased caloric intake</div>
                  </div>

                  {/* Obesity */}
                  <div className="component condition obesity" data-component="obesity">
                    <div className="component-icon">⚖️</div>
                    <div className="component-label">Obesity</div>
                    <div className="component-note">Adipose tissue accumulation</div>
                  </div>

                  {/* NEFA */}
                  <div className="component metabolite nefa" data-component="nefa">
                    <div className="component-icon">🧈</div>
                    <div className="component-label">NEFA</div>
                    <div className="component-note">Non-esterified fatty acids</div>
                  </div>

                  {/* Palmitic Acid */}
                  <div className="component metabolite palmitic" data-component="palmitic">
                    <div className="component-icon">🔶</div>
                    <div className="component-label">Palmitic Acid</div>
                    <div className="component-note">Pro-inflammatory</div>
                  </div>

                  {/* Oleic Acid */}
                  <div className="component metabolite oleic" data-component="oleic">
                    <div className="component-icon">🟢</div>
                    <div className="component-label">Oleic Acid</div>
                    <div className="component-note">Anti-inflammatory</div>
                  </div>

                  {/* TNF-α */}
                  <div className="component inflammatory tnf" data-component="tnf">
                    <div className="component-icon">🔥</div>
                    <div className="component-label">TNF-α</div>
                    <div className="component-note">Inflammatory cytokine</div>
                  </div>

                  {/* GLP-1 */}
                  <div className="component hormone glp1" data-component="glp1">
                    <div className="component-icon">💊</div>
                    <div className="component-label">GLP-1</div>
                  </div>

                  {/* Impaired Beta Cells */}
                  <div className="component cell beta-cell impaired" data-component="beta-cell">
                    <div className="component-icon">🔵</div>
                    <div className="component-label">β-cells (Impaired)</div>
                    <div className="component-note">Glucose & palmitic acid toxicity</div>
                  </div>

                  {/* Insulin */}
                  <div className="component hormone insulin" data-component="insulin">
                    <div className="component-icon">💉</div>
                    <div className="component-label">Insulin</div>
                  </div>

                  {/* Impaired GLUT-4 */}
                  <div className="component transporter glut4 impaired" data-component="glut4">
                    <div className="component-icon">🚪</div>
                    <div className="component-label">GLUT-4 (Impaired)</div>
                    <div className="component-note">TNF-α inhibition</div>
                  </div>

                  {/* Elevated Glucose */}
                  <div className="component metabolite glucose elevated" data-component="glucose">
                    <div className="component-icon">🍯</div>
                    <div className="component-label">Blood Glucose (Elevated)</div>
                    <div className="component-note">Hyperglycemia</div>
                  </div>

                  {/* SVG Arrows for Obesity Pathway */}
                  <svg className="connection-svg" viewBox="0 0 1200 600">
                    {/* Food to Obesity */}
                    <path d="M 190 120 L 270 120" stroke="#f39c12" strokeWidth="3" fill="none" markerEnd="url(#arrowhead-warning)"/>
                    
                    {/* Obesity to NEFA */}
                    <path d="M 410 120 L 490 120" stroke="#e74c3c" strokeWidth="3" fill="none" markerEnd="url(#arrowhead-danger)"/>
                    
                    {/* NEFA to Palmitic */}
                    <path d="M 630 120 L 710 120" stroke="#e74c3c" strokeWidth="3" fill="none" markerEnd="url(#arrowhead-danger)"/>
                    
                    {/* NEFA to Oleic */}
                    <path d="M 560 180 L 560 250" stroke="#27ae60" strokeWidth="3" fill="none" markerEnd="url(#arrowhead-success)"/>
                    
                    {/* Palmitic to TNF-α */}
                    <path d="M 850 120 L 930 120" stroke="#e74c3c" strokeWidth="3" fill="none" markerEnd="url(#arrowhead-danger)"/>
                    
                    {/* TNF-α to GLUT-4 (inhibition) */}
                    <path d="M 1000 180 C 1050 200 1050 380 850 400" stroke="#e74c3c" strokeWidth="3" fill="none" markerEnd="url(#inhibition-danger)" strokeDasharray="5,5"/>
                    
                    {/* Food to GLP-1 */}
                    <path d="M 120 180 L 120 300" stroke="#3498db" strokeWidth="3" fill="none" markerEnd="url(#arrowhead)"/>
                    
                    {/* GLP-1 to Beta cells */}
                    <path d="M 190 340 L 270 340" stroke="#3498db" strokeWidth="3" fill="none" markerEnd="url(#arrowhead)"/>
                    
                    {/* Palmitic to Beta cells (toxicity) */}
                    <path d="M 780 180 C 780 260 340 260 340 300" stroke="#e74c3c" strokeWidth="3" fill="none" markerEnd="url(#inhibition-danger)" strokeDasharray="5,5"/>
                    
                    {/* Beta cells to Insulin */}
                    <path d="M 410 340 L 490 340" stroke="#3498db" strokeWidth="3" fill="none" markerEnd="url(#arrowhead)"/>
                    
                    {/* Insulin to GLUT-4 */}
                    <path d="M 630 340 L 710 340" stroke="#3498db" strokeWidth="3" fill="none" markerEnd="url(#arrowhead)"/>
                    
                    {/* GLUT-4 to Glucose (impaired) */}
                    <path d="M 780 400 L 850 400" stroke="#f39c12" strokeWidth="3" fill="none" markerEnd="url(#arrowhead-warning)" strokeDasharray="5,5"/>
                    
                    {/* Oleic to TNF-α (inhibition) */}
                    <path d="M 630 280 C 780 280 780 180 930 180" stroke="#27ae60" strokeWidth="3" fill="none" markerEnd="url(#inhibition-success)" strokeDasharray="5,5"/>
                    
                    {/* Define arrow markers */}
                    <defs>
                      <marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                        <polygon points="0 0, 10 3.5, 0 7" fill="#3498db"/>
                      </marker>
                      <marker id="arrowhead-warning" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                        <polygon points="0 0, 10 3.5, 0 7" fill="#f39c12"/>
                      </marker>
                      <marker id="arrowhead-danger" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                        <polygon points="0 0, 10 3.5, 0 7" fill="#e74c3c"/>
                      </marker>
                      <marker id="arrowhead-success" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                        <polygon points="0 0, 10 3.5, 0 7" fill="#27ae60"/>
                      </marker>
                      <marker id="inhibition-danger" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
                        <circle cx="5" cy="5" r="3" fill="none" stroke="#e74c3c" strokeWidth="2"/>
                        <line x1="2" y1="5" x2="8" y2="5" stroke="#e74c3c" strokeWidth="2"/>
                      </marker>
                      <marker id="inhibition-success" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
                        <circle cx="5" cy="5" r="3" fill="none" stroke="#27ae60" strokeWidth="2"/>
                        <line x1="2" y1="5" x2="8" y2="5" stroke="#27ae60" strokeWidth="2"/>
                      </marker>
                    </defs>
                  </svg>
                </div>
              )}

              {currentAnimation === 2 && (
                <div className="flowchart treatment-pathway">
                  <div className="flowchart-title">GLP-1 Agonist Treatment Network</div>
                  
                  {/* Mounjaro/Ozempic */}
                  <div className="component drug mounjaro" data-component="mounjaro">
                    <div className="component-icon">💊</div>
                    <div className="component-label">Mounjaro/Ozempic</div>
                    <div className="component-note">GLP-1 receptor agonist</div>
                  </div>

                  {/* Enhanced GLP-1 */}
                  <div className="component hormone glp1 enhanced" data-component="glp1">
                    <div className="component-icon">💊</div>
                    <div className="component-label">GLP-1 (Enhanced)</div>
                    <div className="component-note">Drug-enhanced activity</div>
                  </div>

                  {/* Reduced Food Intake */}
                  <div className="component food-intake reduced" data-component="food-intake">
                    <div className="component-icon">🍽️</div>
                    <div className="component-label">Food Intake (Reduced)</div>
                    <div className="component-note">Gastric emptying delay</div>
                  </div>

                  {/* Restored Beta Cell Function */}
                  <div className="component cell beta-cell restored" data-component="beta-cell">
                    <div className="component-icon">🔵</div>
                    <div className="component-label">β-cells (Restored)</div>
                    <div className="component-note">Improved insulin secretion</div>
                  </div>

                  {/* Enhanced Insulin */}
                  <div className="component hormone insulin enhanced" data-component="insulin">
                    <div className="component-icon">💉</div>
                    <div className="component-label">Insulin (Enhanced)</div>
                    <div className="component-note">Improved secretion</div>
                  </div>

                  {/* Weight Loss */}
                  <div className="component condition weight-loss" data-component="weight-loss">
                    <div className="component-icon">⚖️</div>
                    <div className="component-label">Weight Loss</div>
                    <div className="component-note">12-22% body weight reduction</div>
                  </div>

                  {/* Reduced NEFA */}
                  <div className="component metabolite nefa reduced" data-component="nefa">
                    <div className="component-icon">🧈</div>
                    <div className="component-label">NEFA (Reduced)</div>
                    <div className="component-note">Less adipose tissue</div>
                  </div>

                  {/* Reduced Palmitic Acid */}
                  <div className="component metabolite palmitic reduced" data-component="palmitic">
                    <div className="component-icon">🔶</div>
                    <div className="component-label">Palmitic Acid (Reduced)</div>
                    <div className="component-note">Less inflammation</div>
                  </div>

                  {/* Reduced Inflammation */}
                  <div className="component inflammatory tnf reduced" data-component="tnf">
                    <div className="component-icon">🔥</div>
                    <div className="component-label">TNF-α (Reduced)</div>
                    <div className="component-note">Decreased inflammation</div>
                  </div>

                  {/* Restored GLUT-4 */}
                  <div className="component transporter glut4 restored" data-component="glut4">
                    <div className="component-icon">🚪</div>
                    <div className="component-label">GLUT-4 (Restored)</div>
                    <div className="component-note">Improved function</div>
                  </div>

                  {/* Improved Glucose Control */}
                  <div className="component metabolite glucose improved" data-component="glucose">
                    <div className="component-icon">🍯</div>
                    <div className="component-label">Blood Glucose (Improved)</div>
                    <div className="component-note">A1C reduction: 1.8-2.4%</div>
                  </div>

                  {/* Suppressed Glucagon */}
                  <div className="component hormone glucagon suppressed" data-component="glucagon">
                    <div className="component-icon">⚡</div>
                    <div className="component-label">Glucagon (Suppressed)</div>
                    <div className="component-note">Reduced glucose production</div>
                  </div>

                  {/* SVG Arrows for Treatment Pathway */}
                  <svg className="connection-svg" viewBox="0 0 1200 600">
                    {/* Drug to GLP-1 */}
                    <path d="M 190 120 L 270 120" stroke="#1abc9c" strokeWidth="4" fill="none" markerEnd="url(#arrowhead-treatment)"/>
                    
                    {/* Drug to Food Intake (reduction) */}
                    <path d="M 120 180 L 120 250" stroke="#1abc9c" strokeWidth="3" fill="none" markerEnd="url(#inhibition-treatment)" strokeDasharray="5,5"/>
                    
                    {/* Enhanced GLP-1 to Beta cells */}
                    <path d="M 410 120 L 490 120" stroke="#2ecc71" strokeWidth="4" fill="none" markerEnd="url(#arrowhead-success)"/>
                    
                    {/* Beta cells to Insulin */}
                    <path d="M 630 120 L 710 120" stroke="#2ecc71" strokeWidth="4" fill="none" markerEnd="url(#arrowhead-success)"/>
                    
                    {/* Insulin to GLUT-4 */}
                    <path d="M 850 120 L 930 120" stroke="#2ecc71" strokeWidth="4" fill="none" markerEnd="url(#arrowhead-success)"/>
                    
                    {/* GLUT-4 to Glucose */}
                    <path d="M 1000 180 L 1000 250" stroke="#2ecc71" strokeWidth="4" fill="none" markerEnd="url(#arrowhead-success)"/>
                    
                    {/* Reduced Food to Weight Loss */}
                    <path d="M 190 300 L 270 300" stroke="#2ecc71" strokeWidth="3" fill="none" markerEnd="url(#arrowhead-success)"/>
                    
                    {/* Weight Loss to Reduced NEFA */}
                    <path d="M 410 300 L 490 300" stroke="#2ecc71" strokeWidth="3" fill="none" markerEnd="url(#arrowhead-success)"/>
                    
                    {/* Reduced NEFA to Reduced Palmitic */}
                    <path d="M 630 300 L 710 300" stroke="#2ecc71" strokeWidth="3" fill="none" markerEnd="url(#arrowhead-success)"/>
                    
                    {/* Reduced Palmitic to Reduced TNF-α */}
                    <path d="M 850 300 L 930 300" stroke="#2ecc71" strokeWidth="3" fill="none" markerEnd="url(#arrowhead-success)"/>
                    
                    {/* Reduced TNF-α to Restored GLUT-4 */}
                    <path d="M 1000 250 C 1050 200 1050 160 1000 160" stroke="#2ecc71" strokeWidth="3" fill="none" markerEnd="url(#arrowhead-success)"/>
                    
                    {/* Enhanced GLP-1 to Suppressed Glucagon */}
                    <path d="M 340 180 C 340 480 490 480 490 450" stroke="#1abc9c" strokeWidth="3" fill="none" markerEnd="url(#inhibition-treatment)" strokeDasharray="5,5"/>
                    
                    {/* Define treatment arrow markers */}
                    <defs>
                      <marker id="arrowhead-treatment" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                        <polygon points="0 0, 10 3.5, 0 7" fill="#1abc9c"/>
                      </marker>
                      <marker id="arrowhead-success" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
                        <polygon points="0 0, 10 3.5, 0 7" fill="#2ecc71"/>
                      </marker>
                      <marker id="inhibition-treatment" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
                        <circle cx="5" cy="5" r="3" fill="none" stroke="#1abc9c" strokeWidth="2"/>
                        <line x1="2" y1="5" x2="8" y2="5" stroke="#1abc9c" strokeWidth="2"/>
                      </marker>
                    </defs>
                  </svg>
                </div>
              )}
            </div>

            <div className="pathway-description">
              {currentAnimation === 0 && (
                <div className="description-card normal">
                  <h3>🟢 Normal Glucose Regulation</h3>
                  <ul>
                    <li><strong>Food Intake:</strong> Triggers GLP-1 release from gut enteroendocrine cells</li>
                    <li><strong>GLP-1 Action:</strong> Stimulates pancreatic β-cells to secrete insulin</li>
                    <li><strong>Insulin Signaling:</strong> Activates GLUT-4 via IRS-1-PI3K-Akt pathway</li>
                    <li><strong>Glucose Transport:</strong> GLUT-4 transports glucose from blood to liver cells</li>
                    <li><strong>Glucose Storage:</strong> Stored as glycogen in liver</li>
                    <li><strong>Hypoglycemia Response:</strong> α-cells secrete glucagon, activating GLUT-2</li>
                    <li><strong>Glucose Release:</strong> GLUT-2 transports glucose from liver to blood</li>
                    <li><strong>GLP-1 Regulation:</strong> Suppresses glucagon when glucose is high</li>
                  </ul>
                </div>
              )}
              {currentAnimation === 1 && (
                <div className="description-card warning">
                  <h3>🟡 Obesity-Induced Pathological Changes</h3>
                  <ul>
                    <li><strong>Excessive Food Intake:</strong> Leads to obesity and adipose tissue accumulation</li>
                    <li><strong>NEFA Release:</strong> Adipose tissue releases inflammatory fatty acids during meals</li>
                    <li><strong>Palmitic Acid:</strong> Pro-inflammatory acid causes β-cell dysfunction and apoptosis</li>
                    <li><strong>TNF-α Production:</strong> Palmitic acid promotes inflammatory cytokine release</li>
                    <li><strong>Insulin Resistance:</strong> TNF-α impairs GLUT-4 translocation via PTEN/Akt pathway</li>
                    <li><strong>β-cell Toxicity:</strong> Chronic glucose and palmitic acid exposure damages β-cells</li>
                    <li><strong>Oleic Acid Protection:</strong> Anti-inflammatory fatty acid can reduce TNF-α effects</li>
                    <li><strong>Compensatory Mechanisms:</strong> Initially β-cells increase insulin production</li>
                  </ul>
                </div>
              )}
              {currentAnimation === 2 && (
                <div className="description-card success">
                  <h3>🟢 GLP-1 Agonist Treatment Effects</h3>
                  <ul>
                    <li><strong>Drug Action:</strong> Mounjaro/Ozempic activate GLP-1 receptors</li>
                    <li><strong>Enhanced GLP-1:</strong> Increased insulin secretion and β-cell activation</li>
                    <li><strong>Reduced Food Intake:</strong> Gastric emptying delay leads to satiety</li>
                    <li><strong>Weight Loss:</strong> 12-22% body weight reduction with high-dose treatment</li>
                    <li><strong>Reduced Inflammation:</strong> Weight loss decreases adipose tissue and NEFA release</li>
                    <li><strong>Improved Insulin Sensitivity:</strong> Reduced TNF-α restores GLUT-4 function</li>
                    <li><strong>β-cell Recovery:</strong> Reduced glucose and palmitic acid toxicity</li>
                    <li><strong>Clinical Outcomes:</strong> A1C reduction of 1.8-2.4% in clinical trials</li>
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Model Assumptions */}
      <section className="assumptions-section">
        <div className="container">
          <h2>Model Assumptions</h2>
          <div className="assumptions-grid">
            <div className="assumption-card">
              <h3>🔬 Physiological Assumptions</h3>
              <ul>
                <li>Michaelis-Menten kinetics for enzyme reactions</li>
                <li>Well-mixed compartments for hormones and metabolites</li>
                <li>Steady-state approximation for rapid reactions</li>
                <li>Linear dose-response for drug effects</li>
              </ul>
            </div>
            <div className="assumption-card">
              <h3>📊 Mathematical Assumptions</h3>
              <ul>
                <li>Continuous time differential equations</li>
                <li>Deterministic (non-stochastic) model</li>
                <li>Parameters constant within simulation</li>
                <li>Initial conditions based on patient status</li>
              </ul>
            </div>
            <div className="assumption-card">
              <h3>🏥 Clinical Assumptions</h3>
              <ul>
                <li>Meal timing affects hormone release</li>
                <li>Obesity increases inflammatory markers</li>
                <li>Age-related β-cell function decline</li>
                <li>Drug compliance assumed perfect</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Authors Section */}
      <section className="authors-section">
        <div className="container">
          <h2>Research Authors</h2>
          <div className="authors-grid">
            <div className="author-card">
              <div className="author-photo">
                <div className="photo-placeholder">N.S.</div>
              </div>
              <h3>Nourridine Siewe</h3>
              <p className="author-affiliation">
                School of Mathematics and Statistics<br/>
                Rochester Institute of Technology
              </p>
              <p className="author-bio">
                Specialized in mathematical modeling of biological systems 
                and differential equations applications in medicine.
              </p>
            </div>
            <div className="author-card">
              <div className="author-photo">
                <div className="photo-placeholder">A.F.</div>
              </div>
              <h3>Avner Friedman</h3>
              <p className="author-affiliation">
                Department of Mathematics<br/>
                The Ohio State University
              </p>
              <p className="author-bio">
                Distinguished mathematician known for work in mathematical biology 
                and medical applications of differential equations.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default ResearchPage;