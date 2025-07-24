// src/components/EnhancedSimulationDashboard.tsx
import React, { useState, useEffect, useRef } from 'react';
import Plot from 'react-plotly.js';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { PatientData, SimulationResult } from '../types/diabetes';
import { simulationAPI } from '../utils/api';
import './SimulationDashboard.css';

interface SimulationParams {
  patient_data: PatientData;
  simulation_hours: number;
  food_factor: number;
  palmitic_factor: number;
  drug_dosage: number;
  show_optimal: boolean;
  meal_times: number[];
  meal_factors: number[];
}

interface EnhancedSimulationDashboardProps {
  patientData: PatientData;
}

const EnhancedSimulationDashboard: React.FC<EnhancedSimulationDashboardProps> = ({ patientData }) => {
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null);
  const [comparisonResults, setComparisonResults] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exportingPDF, setExportingPDF] = useState(false);
  const [activeAnalysis, setActiveAnalysis] = useState<'basic' | 'meals' | 'progression' | 'treatment'>('basic');
  const plotRef = useRef<any>(null);
  
  const [selectedMetrics, setSelectedMetrics] = useState({
    glucose: true,
    insulin: true,
    glucagon: false,
    glp1: false,
    beta_cells: false,
    alpha_cells: false,
  });
  
  const [simulationParams, setSimulationParams] = useState<SimulationParams>({
    patient_data: patientData,
    simulation_hours: 24,
    food_factor: 1.0,
    palmitic_factor: 1.0,
    drug_dosage: 0.0,
    show_optimal: true,
    meal_times: [0, 6, 12, 18],
    meal_factors: [1.0, 1.0, 2.0, 0.0], // breakfast, lunch, dinner, snack
  });

  useEffect(() => {
    runBasicSimulation();
  }, []);

  const runBasicSimulation = async () => {
    setLoading(true);
    setError(null);
    setActiveAnalysis('basic');
    try {
      const result = await simulationAPI.runSimulation(simulationParams);
      setSimulationResult(result);
      setComparisonResults(null);
    } catch (error: any) {
      setError(error.message);
      console.error('Simulation failed:', error);
    }
    setLoading(false);
  };

  const runMealComparison = async () => {
    setLoading(true);
    setError(null);
    setActiveAnalysis('meals');
    try {
      const result = await simulationAPI.compareMealPatterns(simulationParams);
      setComparisonResults(result);
      setSimulationResult(null);
    } catch (error: any) {
      setError(error.message);
      console.error('Meal comparison failed:', error);
    }
    setLoading(false);
  };

  const runObesityProgression = async () => {
    setLoading(true);
    setError(null);
    setActiveAnalysis('progression');
    try {
      const result = await simulationAPI.simulateObesityProgression(simulationParams);
      setComparisonResults(result);
      setSimulationResult(null);
    } catch (error: any) {
      setError(error.message);
      console.error('Obesity progression simulation failed:', error);
    }
    setLoading(false);
  };

  const runTreatmentAnalysis = async () => {
    setLoading(true);
    setError(null);
    setActiveAnalysis('treatment');
    try {
      const result = await simulationAPI.analyzeDrugTreatment(simulationParams);
      setComparisonResults(result);
      setSimulationResult(null);
    } catch (error: any) {
      setError(error.message);
      console.error('Treatment analysis failed:', error);
    }
    setLoading(false);
  };

  const handleParameterChange = (key: keyof SimulationParams, value: any) => {
    setSimulationParams(prev => ({ ...prev, [key]: value }));
  };

  const handleMealFactorChange = (index: number, value: number) => {
    const newMealFactors = [...simulationParams.meal_factors];
    newMealFactors[index] = value;
    setSimulationParams(prev => ({ ...prev, meal_factors: newMealFactors }));
  };

  const setMealPattern = (pattern: 'balanced' | 'light-heavy' | 'heavy-light' | 'small-frequent') => {
    const patterns = {
      'balanced': [1.0, 1.0, 1.0, 0.0],
      'light-heavy': [0.5, 1.0, 2.0, 0.0],
      'heavy-light': [2.0, 1.0, 0.5, 0.0],
      'small-frequent': [0.8, 0.8, 0.8, 0.6]
    };
    setSimulationParams(prev => ({ ...prev, meal_factors: patterns[pattern] }));
  };

  const setScenario = (scenario: 'normal' | 'high-risk' | 'treatment' | 'optimal') => {
    const scenarios = {
      'normal': { food_factor: 1.0, palmitic_factor: 1.0, drug_dosage: 0.0 },
      'high-risk': { food_factor: 2.0, palmitic_factor: 2.5, drug_dosage: 0.0 },
      'treatment': { food_factor: 1.2, palmitic_factor: 1.5, drug_dosage: 1.0 },
      'optimal': { food_factor: 0.8, palmitic_factor: 0.7, drug_dosage: 0.5 }
    };
    const params = scenarios[scenario];
    setSimulationParams(prev => ({ ...prev, ...params }));
  };

  const calculateBMI = () => {
    const heightM = patientData.height / 100;
    return (patientData.weight / (heightM * heightM)).toFixed(1);
  };

  const createPlotData = () => {
    if (!simulationResult) return [];

    const traces: any[] = [];
    const { time_points, glucose, insulin, glucagon, glp1, beta_cells, alpha_cells, optimal_glucose } = simulationResult;

    // Enhanced glucose trace with reference ranges
    if (selectedMetrics.glucose) {
      traces.push({
        x: time_points,
        y: glucose,
        type: 'scatter',
        mode: 'lines',
        name: 'Blood Glucose',
        line: { color: '#f76902', width: 3 }, // RIT Orange
        hovertemplate: 'Time: %{x:.1f}h<br>Glucose: %{y:.1f} mg/dL<extra></extra>',
      });

      if (optimal_glucose && simulationParams.show_optimal) {
        traces.push({
          x: time_points,
          y: optimal_glucose,
          type: 'scatter',
          mode: 'lines',
          name: 'Optimal Glucose',
          line: { color: '#27ae60', width: 2, dash: 'dot' },
          hovertemplate: 'Time: %{x:.1f}h<br>Optimal: %{y:.1f} mg/dL<extra></extra>',
        });
      }
    }

    // Enhanced hormone traces with secondary axes
    if (selectedMetrics.insulin) {
      traces.push({
        x: time_points,
        y: insulin,
        type: 'scatter',
        mode: 'lines',
        name: 'Insulin',
        line: { color: '#58595b', width: 3 }, // RIT Gray
        yaxis: 'y2',
        hovertemplate: 'Time: %{x:.1f}h<br>Insulin: %{y:.1f} pmol/L<extra></extra>',
      });
    }

    if (selectedMetrics.glucagon) {
      traces.push({
        x: time_points,
        y: glucagon,
        type: 'scatter',
        mode: 'lines',
        name: 'Glucagon',
        line: { color: '#9b59b6', width: 2 },
        yaxis: 'y3',
        hovertemplate: 'Time: %{x:.1f}h<br>Glucagon: %{y:.1f} pg/mL<extra></extra>',
      });
    }

    if (selectedMetrics.glp1) {
      traces.push({
        x: time_points,
        y: glp1,
        type: 'scatter',
        mode: 'lines',
        name: 'GLP-1',
        line: { color: '#e74c3c', width: 2 },
        yaxis: 'y4',
        hovertemplate: 'Time: %{x:.1f}h<br>GLP-1: %{y:.1f} pmol/L<extra></extra>',
      });
    }

    if (selectedMetrics.beta_cells) {
      traces.push({
        x: time_points,
        y: beta_cells,
        type: 'scatter',
        mode: 'lines',
        name: 'β-cells',
        line: { color: '#1abc9c', width: 2 },
        yaxis: 'y5',
        hovertemplate: 'Time: %{x:.1f}h<br>β-cells: %{y:.1f}<extra></extra>',
      });
    }

    if (selectedMetrics.alpha_cells) {
      traces.push({
        x: time_points,
        y: alpha_cells,
        type: 'scatter',
        mode: 'lines',
        name: 'α-cells',
        line: { color: '#ff8c00', width: 2 }, // RIT Secondary Orange
        yaxis: 'y6',
        hovertemplate: 'Time: %{x:.1f}h<br>α-cells: %{y:.1f}<extra></extra>',
      });
    }

    return traces;
  };

  const getPlotLayout = () => {
    const yAxes: any = {};
    let rightPosition = 0.85;

    if (selectedMetrics.glucose) {
      yAxes.yaxis = {
        title: 'Glucose (mg/dL)',
        side: 'left',
        color: '#f76902', // RIT Orange
        showgrid: true,
        gridcolor: '#f0f0f0',
      };
    }

    if (selectedMetrics.insulin) {
      yAxes.yaxis2 = {
        title: 'Insulin (pmol/L)',
        side: 'right',
        overlaying: 'y',
        color: '#58595b', // RIT Gray
        showgrid: false,
        position: rightPosition,
      };
      rightPosition -= 0.05;
    }

    if (selectedMetrics.glucagon) {
      yAxes.yaxis3 = {
        title: 'Glucagon (pg/mL)',
        side: 'right',
        overlaying: 'y',
        position: rightPosition,
        color: '#9b59b6',
        showgrid: false,
      };
      rightPosition -= 0.05;
    }

    if (selectedMetrics.glp1) {
      yAxes.yaxis4 = {
        title: 'GLP-1 (pmol/L)',
        side: 'right',
        overlaying: 'y',
        position: rightPosition,
        color: '#e74c3c',
        showgrid: false,
      };
      rightPosition -= 0.05;
    }

    if (selectedMetrics.beta_cells) {
      yAxes.yaxis5 = {
        title: 'β-cells',
        side: 'right',
        overlaying: 'y',
        position: rightPosition,
        color: '#1abc9c',
        showgrid: false,
      };
      rightPosition -= 0.05;
    }

    if (selectedMetrics.alpha_cells) {
      yAxes.yaxis6 = {
        title: 'α-cells',
        side: 'right',
        overlaying: 'y',
        position: rightPosition,
        color: '#ff8c00',
        showgrid: false,
      };
    }

    // Enhanced meal annotations with RIT branding
    const mealLabels = ['🥞', '🍽️', '🍖', '🍪'];
    const mealTimes = simulationParams.meal_times?.map((mealTime, index) => ({
      x: mealTime,
      y: 0,
      xref: 'x',
      yref: 'paper',
      text: `${mealLabels[index] || '🍽️'}<br>${simulationParams.meal_factors[index]?.toFixed(1)}x`,
      showarrow: true,
      arrowhead: 2,
      arrowsize: 1,
      arrowwidth: 2,
      arrowcolor: '#f76902', // RIT Orange
      ax: 0,
      ay: -40,
      font: { size: 12, color: '#58595b' }
    })) || [];

    return {
      title: {
        text: `RIT Enhanced Glucose Dynamics - ${patientData.name} (${activeAnalysis.toUpperCase()})`,
        font: { size: 20, color: '#58595b', family: 'Arial, sans-serif' }, // RIT Gray
      },
      xaxis: {
        title: 'Time (hours)',
        showgrid: true,
        gridcolor: '#f0f0f0',
        range: [0, simulationParams.simulation_hours],
        color: '#58595b',
      },
      ...yAxes,
      legend: {
        orientation: 'h',
        y: -0.2,
        x: 0.5,
        xanchor: 'center',
        font: { color: '#58595b' }
      },
      margin: { l: 60, r: 140, t: 80, b: 120 },
      height: 600,
      showlegend: true,
      hovermode: 'x unified',
      plot_bgcolor: 'white',
      paper_bgcolor: 'white',
      annotations: mealTimes,
      shapes: [
        // Normal glucose range (RIT-themed)
        {
          type: 'rect',
          xref: 'x',
          yref: 'y',
          x0: 0,
          x1: simulationParams.simulation_hours,
          y0: 70,
          y1: 140,
          fillcolor: 'rgba(39, 174, 96, 0.1)',
          line: { width: 0 },
          layer: 'below',
        },
        // Prediabetic range
        {
          type: 'rect',
          xref: 'x',
          yref: 'y',
          x0: 0,
          x1: simulationParams.simulation_hours,
          y0: 140,
          y1: 200,
          fillcolor: 'rgba(247, 105, 2, 0.1)', // RIT Orange tint
          line: { width: 0 },
          layer: 'below',
        }
      ],
    };
  };

  const generateEnhancedPDFReport = async () => {
    if (!simulationResult && !comparisonResults) return;

    setExportingPDF(true);
    try {
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pageWidth = pdf.internal.pageSize.getWidth();
      let yPosition = 20;

      // RIT Header
      pdf.setFontSize(24);
      pdf.setFont('helvetica', 'bold');
      pdf.setTextColor(247, 105, 2); // RIT Orange
      pdf.text('RIT Diabetes Simulation Report', pageWidth / 2, yPosition, { align: 'center' });
      yPosition += 8;
      
      pdf.setFontSize(12);
      pdf.setFont('helvetica', 'normal');
      pdf.setTextColor(88, 89, 91); // RIT Gray
      pdf.text('Rochester Institute of Technology', pageWidth / 2, yPosition, { align: 'center' });
      yPosition += 4;
      
      pdf.setTextColor(0, 0, 0);
      pdf.text(`Analysis Type: ${activeAnalysis.toUpperCase()} | Generated: ${new Date().toLocaleDateString()}`, pageWidth / 2, yPosition, { align: 'center' });
      yPosition += 20;

      // Patient Information
      pdf.setFontSize(16);
      pdf.setFont('helvetica', 'bold');
      pdf.setTextColor(247, 105, 2); // RIT Orange
      pdf.text('Patient Profile', 20, yPosition);
      yPosition += 10;

      pdf.setFontSize(12);
      pdf.setFont('helvetica', 'normal');
      pdf.setTextColor(0, 0, 0);
      const patientInfo = [
        `Name: ${patientData.name}`,
        `Age: ${patientData.age} years | Gender: ${patientData.gender}`,
        `BMI: ${calculateBMI()} kg/m² | Activity: ${patientData.activity_level}`,
        `Diabetes Status: ${patientData.diabetes_type || 'Auto-detected'}`,
        `Medications: ${patientData.medications.join(', ') || 'None'}`,
        `Family History: ${patientData.family_history ? 'Yes' : 'No'} | Smoking: ${patientData.smoking_status}`
      ];

      patientInfo.forEach(info => {
        pdf.text(info, 20, yPosition);
        yPosition += 6;
      });

      yPosition += 15;

      // Analysis-specific content
      if (simulationResult) {
        // Basic simulation results
        pdf.setFontSize(16);
        pdf.setFont('helvetica', 'bold');
        pdf.setTextColor(247, 105, 2); // RIT Orange
        pdf.text('Simulation Results', 20, yPosition);
        yPosition += 10;

        const results = [
          `A1C Estimate: ${simulationResult.a1c_estimate}% (${simulationResult.diagnosis})`,
          `Average Glucose: ${simulationResult.simulation_summary.average_glucose} mg/dL`,
          `Glucose Variability: ${simulationResult.simulation_summary.glucose_variability} mg/dL`,
          `Time in Range (70-180): ${simulationResult.simulation_summary.time_in_range}%`,
          `Dawn Phenomenon: ${simulationResult.glucose_metrics?.dawn_phenomenon || 'N/A'} mg/dL`,
          `Glucose Stability Score: ${simulationResult.glucose_metrics?.glucose_stability?.stability_score || 'N/A'}/100`
        ];

        pdf.setFontSize(12);
        pdf.setFont('helvetica', 'normal');
        pdf.setTextColor(0, 0, 0);
        results.forEach(result => {
          pdf.text(result, 20, yPosition);
          yPosition += 6;
        });

      } else if (comparisonResults) {
        // Comparison results
        pdf.setFontSize(16);
        pdf.setFont('helvetica', 'bold');
        pdf.setTextColor(247, 105, 2); // RIT Orange
        pdf.text(`${activeAnalysis.charAt(0).toUpperCase() + activeAnalysis.slice(1)} Analysis Results`, 20, yPosition);
        yPosition += 10;

        if (comparisonResults.comparison_metrics) {
          pdf.setFontSize(12);
          pdf.setFont('helvetica', 'normal');
          pdf.setTextColor(0, 0, 0);
          comparisonResults.comparison_metrics.forEach((metric: any, index: number) => {
            pdf.text(`${index + 1}. ${metric.scenario}: A1C ${metric.a1c_estimate}% (${metric.a1c_change >= 0 ? '+' : ''}${metric.a1c_change})`, 20, yPosition);
            yPosition += 6;
          });
        }
      }

      // Add chart on new page
      pdf.addPage();
      yPosition = 20;

      pdf.setFontSize(16);
      pdf.setFont('helvetica', 'bold');
      pdf.setTextColor(247, 105, 2); // RIT Orange
      pdf.text('Glucose Dynamics Visualization', pageWidth / 2, yPosition, { align: 'center' });
      yPosition += 15;

      if (plotRef.current) {
        const chartElement = plotRef.current.el;
        const canvas = await html2canvas(chartElement, {
          scale: 2,
          backgroundColor: '#ffffff'
        });

        const imgData = canvas.toDataURL('image/png');
        const imgWidth = pageWidth - 40;
        const imgHeight = (canvas.height * imgWidth) / canvas.width;

        pdf.addImage(imgData, 'PNG', 20, yPosition, imgWidth, Math.min(imgHeight, 160));
      }

      // Save PDF
      const fileName = `RIT_diabetes_simulation_${patientData.name.replace(/\s+/g, '_')}_${activeAnalysis}_${new Date().toISOString().split('T')[0]}.pdf`;
      pdf.save(fileName);

    } catch (error) {
      console.error('Enhanced PDF generation failed:', error);
      alert('Failed to generate enhanced PDF report. Please try again.');
    } finally {
      setExportingPDF(false);
    }
  };

  const getMealSizeLabel = (factor: number): string => {
    if (factor === 0) return 'Skip';
    if (factor <= 0.5) return 'Light';
    if (factor <= 1.0) return 'Normal';
    if (factor <= 1.5) return 'Large';
    return 'Extra Large';
  };

  return (
    <div className="enhanced-simulation-dashboard rit-dashboard">
      <div className="dashboard-header rit-header">
        <div className="patient-info">
          <div className="rit-branding-header">
            <span className="rit-logo-header">🎓</span>
            <div>
              <h2>{patientData.name} - Enhanced Simulation</h2>
              <span className="rit-subtitle-header">Rochester Institute of Technology</span>
            </div>
          </div>
          <div className="patient-stats">
            <span>Age: {patientData.age}</span>
            <span>BMI: {calculateBMI()}</span>
            <span>Activity: {patientData.activity_level}</span>
            {simulationResult && (
              <>
                <span>A1C: {simulationResult.a1c_estimate}%</span>
                <span className={`diagnosis ${simulationResult.diagnosis.toLowerCase()}`}>
                  {simulationResult.diagnosis}
                </span>
              </>
            )}
          </div>
        </div>
        <div className="dashboard-actions">
          <button 
            className="btn-secondary rit-secondary" 
            onClick={generateEnhancedPDFReport} 
            disabled={(!simulationResult && !comparisonResults) || exportingPDF}
          >
            {exportingPDF ? '📄 Generating...' : '📄 RIT Report'}
          </button>
          <button className="btn-primary rit-primary" onClick={runBasicSimulation} disabled={loading}>
            {loading ? 'Running...' : '🔄 Refresh'}
          </button>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="parameter-panel rit-panel">
          <h3>🎛️ Enhanced Controls</h3>
          
          {/* Analysis Type Selection */}
          <div className="parameter-group">
            <h4>Analysis Type</h4>
            <div className="analysis-buttons">
              <button 
                className={`btn-analysis rit-analysis ${activeAnalysis === 'basic' ? 'active' : ''}`}
                onClick={runBasicSimulation}
                disabled={loading}
              >
                Basic Simulation
              </button>
              <button 
                className={`btn-analysis rit-analysis ${activeAnalysis === 'meals' ? 'active' : ''}`}
                onClick={runMealComparison}
                disabled={loading}
              >
                Meal Patterns
              </button>
              <button 
                className={`btn-analysis rit-analysis ${activeAnalysis === 'progression' ? 'active' : ''}`}
                onClick={runObesityProgression}
                disabled={loading}
              >
                Obesity Progression
              </button>
              <button 
                className={`btn-analysis rit-analysis ${activeAnalysis === 'treatment' ? 'active' : ''}`}
                onClick={runTreatmentAnalysis}
                disabled={loading}
              >
                Drug Treatment
              </button>
            </div>
          </div>

          {/* Basic Parameters */}
          <div className="parameter-group">
            <h4>Simulation Parameters</h4>
            
            <label>Duration: {simulationParams.simulation_hours}h</label>
            <input
              type="range"
              min="6"
              max="72"
              step="6"
              value={simulationParams.simulation_hours}
              onChange={(e) => handleParameterChange('simulation_hours', parseInt(e.target.value))}
              className="rit-slider"
            />

            <label>Food Factor: {simulationParams.food_factor.toFixed(1)}x</label>
            <input
              type="range"
              min="0.5"
              max="3.0"
              step="0.1"
              value={simulationParams.food_factor}
              onChange={(e) => handleParameterChange('food_factor', parseFloat(e.target.value))}
              className="rit-slider"
            />
            <small>Represents overall food intake (1.0 = normal, 2.0+ = overeating)</small>

            <label>Palmitic Factor: {simulationParams.palmitic_factor.toFixed(1)}x</label>
            <input
              type="range"
              min="0.5"
              max="4.0"
              step="0.1"
              value={simulationParams.palmitic_factor}
              onChange={(e) => handleParameterChange('palmitic_factor', parseFloat(e.target.value))}
              className="rit-slider"
            />
            <small>Obesity-related inflammatory marker (1.0 = normal, 3.0+ = obese)</small>

            <label>Drug Dosage: {simulationParams.drug_dosage.toFixed(1)}</label>
            <input
              type="range"
              min="0"
              max="2.0"
              step="0.1"
              value={simulationParams.drug_dosage}
              onChange={(e) => handleParameterChange('drug_dosage', parseFloat(e.target.value))}
              className="rit-slider"
            />
            <small>GLP-1 agonist equivalent (0 = none, 1.0+ = therapeutic dose)</small>
          </div>

          {/* Enhanced Meal Controls */}
          <div className="parameter-group">
            <h4>Individual Meal Factors</h4>
            <div className="meal-controls">
              {['Breakfast', 'Lunch', 'Dinner', 'Snack'].map((meal, index) => (
                <div key={meal} className="meal-factor-control">
                  <label>{meal}: {simulationParams.meal_factors[index]?.toFixed(1)}x ({getMealSizeLabel(simulationParams.meal_factors[index] || 0)})</label>
                  <input
                    type="range"
                    min="0"
                    max="3.0"
                    step="0.1"
                    value={simulationParams.meal_factors[index] || 0}
                    onChange={(e) => handleMealFactorChange(index, parseFloat(e.target.value))}
                    className="rit-slider"
                  />
                </div>
              ))}
            </div>
            
            <div className="meal-pattern-buttons">
              <button 
                className="btn-pattern rit-pattern"
                onClick={() => setMealPattern('balanced')}
              >
                Balanced Meals
              </button>
              <button 
                className="btn-pattern rit-pattern"
                onClick={() => setMealPattern('light-heavy')}
              >
                Light → Heavy
              </button>
              <button 
                className="btn-pattern rit-pattern"
                onClick={() => setMealPattern('heavy-light')}
              >
                Heavy → Light
              </button>
              <button 
                className="btn-pattern rit-pattern"
                onClick={() => setMealPattern('small-frequent')}
              >
                Small Frequent
              </button>
            </div>
          </div>

          {/* Quick Scenarios */}
          <div className="parameter-group">
            <h4>Quick Scenarios</h4>
            <div className="scenario-buttons">
              <button 
                className="btn-scenario rit-scenario"
                onClick={() => setScenario('normal')}
              >
                Normal Health
              </button>
              <button 
                className="btn-scenario rit-scenario"
                onClick={() => setScenario('high-risk')}
              >
                High Risk
              </button>
              <button 
                className="btn-scenario rit-scenario"
                onClick={() => setScenario('treatment')}
              >
                With Treatment
              </button>
              <button 
                className="btn-scenario rit-scenario"
                onClick={() => setScenario('optimal')}
              >
                Optimal Control
              </button>
            </div>
          </div>

          {/* Metric Selection */}
          <div className="metric-selector">
            <h4>Display Variables</h4>
            <div className="metric-checkboxes">
              {Object.entries(selectedMetrics).map(([metric, selected]) => (
                <label key={metric} className="metric-checkbox rit-checkbox">
                  <input
                    type="checkbox"
                    checked={selected}
                    onChange={(e) =>
                      setSelectedMetrics(prev => ({
                        ...prev,
                        [metric]: e.target.checked
                      }))
                    }
                  />
                  <span className={`metric-label ${metric.replace('_', '-')}`}>
                    {metric.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </span>
                </label>
              ))}
            </div>
          </div>
        </div>

        <div className="results-panel rit-results">
          {loading ? (
            <div className="loading-spinner rit-loading">
              <div className="spinner rit-spinner"></div>
              <p>Running {activeAnalysis} analysis...</p>
            </div>
          ) : error ? (
            <div className="error-message rit-error">
              <h3>Analysis Error</h3>
              <p>{error}</p>
              <button onClick={runBasicSimulation} className="btn-primary rit-primary">Try Again</button>
            </div>
          ) : simulationResult ? (
            <div className="plot-container">
              <Plot
                ref={plotRef}
                data={createPlotData()}
                layout={getPlotLayout()}
                config={{
                  displayModeBar: true,
                  displaylogo: false,
                  modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
                  toImageButtonOptions: {
                    format: 'png',
                    filename: `RIT_diabetes_${activeAnalysis}_${patientData.name}`,
                    height: 600,
                    width: 1200,
                    scale: 2
                  }
                }}
                style={{ width: '100%', height: '600px' }}
              />
            </div>
          ) : comparisonResults ? (
            <div className="comparison-results">
              <div className="comparison-card rit-card">
                <h3>{activeAnalysis.charAt(0).toUpperCase() + activeAnalysis.slice(1)} Analysis Results</h3>
                
                {comparisonResults.comparison_metrics && (
                  <div className="comparison-table">
                    <table className="rit-table">
                      <thead>
                        <tr>
                          <th>Scenario</th>
                          <th>A1C (%)</th>
                          <th>Change</th>
                          <th>Avg Glucose</th>
                          <th>Time in Range</th>
                          <th>Variability</th>
                        </tr>
                      </thead>
                      <tbody>
                        {comparisonResults.comparison_metrics.map((metric: any, index: number) => (
                          <tr key={index}>
                            <td><strong>{metric.scenario}</strong></td>
                            <td>{metric.a1c_estimate}%</td>
                            <td className={metric.a1c_change < 0 ? 'improvement' : metric.a1c_change > 0 ? 'worsening' : 'neutral'}>
                              {metric.a1c_change >= 0 ? '+' : ''}{metric.a1c_change}%
                            </td>
                            <td>{metric.average_glucose} mg/dL</td>
                            <td>{metric.time_in_range}%</td>
                            <td>{metric.glucose_variability} mg/dL</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}

                {comparisonResults.recommendations && (
                  <div className="recommendations rit-recommendations">
                    <h4>Analysis Recommendations</h4>
                    <ul>
                      {comparisonResults.recommendations.map((rec: string, index: number) => (
                        <li key={index}>{rec}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {comparisonResults.clinical_outcomes && (
                  <div className="clinical-outcomes rit-outcomes">
                    <h4>Clinical Outcomes</h4>
                    <ul>
                      {comparisonResults.clinical_outcomes.map((outcome: string, index: number) => (
                        <li key={index}>{outcome}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="no-data rit-no-data">
              <p>Select an analysis type to view results</p>
            </div>
          )}
        </div>
      </div>

      {/* Enhanced Summary Section */}
      {simulationResult && (
        <div className="simulation-summary">
          <div className="summary-card rit-summary">
            <div className="rit-summary-header">
              <h3>📊 Enhanced Simulation Summary</h3>
              <div className="rit-logo-small">🎓</div>
            </div>
            <div className="summary-grid">
              <div className="summary-item rit-summary-item">
                <label>Average Glucose:</label>
                <span>{simulationResult.simulation_summary.average_glucose} mg/dL</span>
              </div>
              <div className="summary-item rit-summary-item">
                <label>Peak Glucose:</label>
                <span>{simulationResult.simulation_summary.max_glucose} mg/dL</span>
              </div>
              <div className="summary-item rit-summary-item">
                <label>Glucose Variability:</label>
                <span>{simulationResult.simulation_summary.glucose_variability} mg/dL</span>
              </div>
              <div className="summary-item rit-summary-item">
                <label>Time in Range:</label>
                <span>{simulationResult.simulation_summary.time_in_range}%</span>
              </div>
              <div className="summary-item rit-summary-item">
                <label>Time in Tight Range:</label>
                <span>{simulationResult.simulation_summary.time_in_tight_range || 'N/A'}%</span>
              </div>
              <div className="summary-item rit-summary-item">
                <label>A1C Estimate:</label>
                <span className={`diagnosis ${simulationResult.diagnosis.toLowerCase()}`}>
                  {simulationResult.a1c_estimate}%
                </span>
              </div>
            </div>

            {/* Enhanced Glucose Metrics */}
            {simulationResult.glucose_metrics && (
              <div className="meal-analysis rit-analysis-section">
                <h4>🔬 Advanced Glucose Analysis</h4>
                <div className="meal-breakdown">
                  <div className="meal-item rit-metric-item">
                    <div className="meal-name">Dawn Phenomenon</div>
                    <div className="meal-factor">{simulationResult.glucose_metrics.dawn_phenomenon || 0} mg/dL</div>
                    <div className="meal-size">Early morning rise</div>
                  </div>
                  <div className="meal-item rit-metric-item">
                    <div className="meal-name">Stability Score</div>
                    <div className="meal-factor">{simulationResult.glucose_metrics.glucose_stability?.stability_score || 0}/100</div>
                    <div className="meal-size">Higher = more stable</div>
                  </div>
                  <div className="meal-item rit-metric-item">
                    <div className="meal-name">Mean Excursion</div>
                    <div className="meal-factor">{simulationResult.glucose_metrics.glucose_stability?.mean_rate_of_change || 0}</div>
                    <div className="meal-size">mg/dL per 5min</div>
                  </div>
                  <div className="meal-item rit-metric-item">
                    <div className="meal-name">MAGE</div>
                    <div className="meal-factor">{simulationResult.glucose_metrics.glucose_stability?.mage || 0}</div>
                    <div className="meal-size">Mean amplitude</div>
                  </div>
                </div>
              </div>
            )}

            {/* Current Meal Configuration */}
            <div className="meal-analysis rit-analysis-section">
              <h4>🍽️ Current Meal Configuration</h4>
              <div className="meal-breakdown">
                {['Breakfast', 'Lunch', 'Dinner', 'Snack'].map((meal, index) => (
                  <div key={meal} className="meal-item rit-metric-item">
                    <div className="meal-name">{meal} ({simulationParams.meal_times[index]}:00)</div>
                    <div className="meal-factor">{simulationParams.meal_factors[index]?.toFixed(1)}x</div>
                    <div className="meal-size">{getMealSizeLabel(simulationParams.meal_factors[index] || 0)}</div>
                  </div>
                ))}
              </div>
            </div>

            {/* Recommendations */}
            {simulationResult.recommendations && simulationResult.recommendations.length > 0 && (
              <div className="recommendations rit-recommendations">
                <h4>💡 Personalized Recommendations</h4>
                <ul>
                  {simulationResult.recommendations.map((rec, index) => (
                    <li key={index}>{rec}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default EnhancedSimulationDashboard;