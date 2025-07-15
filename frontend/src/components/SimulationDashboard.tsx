// src/components/SimulationDashboard.tsx
import React, { useState, useEffect, useRef } from 'react';
import Plot from 'react-plotly.js';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { PatientData, SimulationResult, SimulationParams, ODEParameters } from '../types/diabetes';
import { simulationAPI } from '../utils/api';
import './SimulationDashboard.css';

interface SimulationDashboardProps {
  patientData: PatientData;
}

const SimulationDashboard: React.FC<SimulationDashboardProps> = ({ patientData }) => {
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [exportingPDF, setExportingPDF] = useState(false);
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
    exercise_times: [],
  });

  useEffect(() => {
    runSimulation();
  }, []);

  const runSimulation = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await simulationAPI.runSimulation(simulationParams);
      setSimulationResult(result);
    } catch (error: any) {
      setError(error.message);
      console.error('Simulation failed:', error);
    }
    setLoading(false);
  };

  const handleParameterChange = (key: keyof SimulationParams, value: any) => {
    const newParams = { ...simulationParams, [key]: value };
    setSimulationParams(newParams);
  };

  const debouncedSimulation = () => {
    setTimeout(runSimulation, 300);
  };

  const calculateBMI = () => {
    const heightM = patientData.height / 100;
    return (patientData.weight / (heightM * heightM)).toFixed(1);
  };

  const createPlotData = () => {
    if (!simulationResult) return [];

    const traces: any[] = [];
    const { time_points, glucose, insulin, glucagon, glp1, beta_cells, alpha_cells, optimal_glucose } = simulationResult;

    // Glucose trace
    if (selectedMetrics.glucose) {
      traces.push({
        x: time_points,
        y: glucose,
        type: 'scatter',
        mode: 'lines',
        name: 'Blood Glucose',
        line: { color: '#e74c3c', width: 3 },
        hovertemplate: 'Time: %{x:.1f}h<br>Glucose: %{y:.1f} mg/dL<extra></extra>',
      });

      // Optimal glucose trace
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

    // Insulin trace (secondary y-axis)
    if (selectedMetrics.insulin) {
      traces.push({
        x: time_points,
        y: insulin,
        type: 'scatter',
        mode: 'lines',
        name: 'Insulin',
        line: { color: '#3498db', width: 3 },
        yaxis: 'y2',
        hovertemplate: 'Time: %{x:.1f}h<br>Insulin: %{y:.1f} pmol/L<extra></extra>',
      });
    }

    // Glucagon trace
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

    // GLP-1 trace
    if (selectedMetrics.glp1) {
      traces.push({
        x: time_points,
        y: glp1,
        type: 'scatter',
        mode: 'lines',
        name: 'GLP-1',
        line: { color: '#f39c12', width: 2 },
        yaxis: 'y4',
        hovertemplate: 'Time: %{x:.1f}h<br>GLP-1: %{y:.1f} pmol/L<extra></extra>',
      });
    }

    // Beta cells trace
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

    // Alpha cells trace
    if (selectedMetrics.alpha_cells) {
      traces.push({
        x: time_points,
        y: alpha_cells,
        type: 'scatter',
        mode: 'lines',
        name: 'α-cells',
        line: { color: '#e67e22', width: 2 },
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
        color: '#e74c3c',
        showgrid: true,
        gridcolor: '#f0f0f0',
      };
    }

    if (selectedMetrics.insulin) {
      yAxes.yaxis2 = {
        title: 'Insulin (pmol/L)',
        side: 'right',
        overlaying: 'y',
        color: '#3498db',
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
        color: '#f39c12',
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
        color: '#e67e22',
        showgrid: false,
      };
    }

    // Add meal time annotations
    const mealTimes = simulationParams.meal_times?.map(mealTime => ({
      x: mealTime,
      y: 0,
      xref: 'x',
      yref: 'paper',
      text: '🍽️',
      showarrow: true,
      arrowhead: 2,
      arrowsize: 1,
      arrowwidth: 2,
      arrowcolor: '#e67e22',
      ax: 0,
      ay: -30,
      font: { size: 16 }
    })) || [];

    // Add exercise time annotations
    const exerciseTimes = simulationParams.exercise_times?.map(exerciseTime => ({
      x: exerciseTime,
      y: 0,
      xref: 'x',
      yref: 'paper',
      text: '🏃',
      showarrow: true,
      arrowhead: 2,
      arrowsize: 1,
      arrowwidth: 2,
      arrowcolor: '#2ecc71',
      ax: 0,
      ay: -30,
      font: { size: 16 }
    })) || [];

    return {
      title: {
        text: `Glucose Dynamics Simulation - ${patientData.name}`,
        font: { size: 20, color: '#333' },
      },
      xaxis: {
        title: 'Time (hours)',
        showgrid: true,
        gridcolor: '#f0f0f0',
        range: [0, simulationParams.simulation_hours],
      },
      ...yAxes,
      legend: {
        orientation: 'h',
        y: -0.15,
        x: 0.5,
        xanchor: 'center',
      },
      margin: { l: 60, r: 120, t: 80, b: 100 },
      height: 500,
      showlegend: true,
      hovermode: 'x unified',
      plot_bgcolor: 'white',
      paper_bgcolor: 'white',
      annotations: [...mealTimes, ...exerciseTimes],
      shapes: [
        // Normal glucose range shading
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
        }
      ],
    };
  };

  const generatePDFReport = async () => {
    if (!simulationResult) return;

    setExportingPDF(true);
    try {
      // Create a new jsPDF instance
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      let yPosition = 20;

      // Title
      pdf.setFontSize(20);
      pdf.setFont('helvetica', 'bold');
      pdf.text('Diabetes Simulation Report', pageWidth / 2, yPosition, { align: 'center' });
      yPosition += 15;

      // Patient Information
      pdf.setFontSize(16);
      pdf.text('Patient Information', 20, yPosition);
      yPosition += 10;

      pdf.setFontSize(12);
      pdf.setFont('helvetica', 'normal');
      const patientInfo = [
        `Name: ${simulationResult.patient_info.name}`,
        `Age: ${simulationResult.patient_info.age} years`,
        `Gender: ${simulationResult.patient_info.gender}`,
        `BMI: ${simulationResult.patient_info.bmi} kg/m² (${simulationResult.patient_info.bmi_category})`,
        `Diabetes Type: ${simulationResult.patient_info.diabetes_type}`,
        `Diabetes Risk: ${simulationResult.patient_info.diabetes_risk}`,
        `Activity Level: ${simulationResult.patient_info.activity_level}`,
        `Medications: ${simulationResult.patient_info.medications.join(', ') || 'None'}`
      ];

      patientInfo.forEach(info => {
        pdf.text(info, 20, yPosition);
        yPosition += 6;
      });

      yPosition += 10;

      // Simulation Results Summary
      pdf.setFontSize(16);
      pdf.setFont('helvetica', 'bold');
      pdf.text('Simulation Results', 20, yPosition);
      yPosition += 10;

      pdf.setFontSize(12);
      pdf.setFont('helvetica', 'normal');
      const simulationSummary = [
        `Estimated A1C: ${simulationResult.simulation_summary.estimated_a1c}%`,
        `Diagnosis: ${simulationResult.diagnosis}`,
        `Average Glucose: ${simulationResult.simulation_summary.average_glucose} mg/dL`,
        `Glucose Range: ${simulationResult.simulation_summary.min_glucose} - ${simulationResult.simulation_summary.max_glucose} mg/dL`,
        `Glucose Variability: ${simulationResult.simulation_summary.glucose_variability} mg/dL`,
        `Time in Target Range (70-180 mg/dL): ${simulationResult.simulation_summary.time_in_range}%`,
        `Time Above Range: ${simulationResult.simulation_summary.time_above_range}%`,
        `Time Below Range: ${simulationResult.simulation_summary.time_below_range}%`
      ];

      simulationSummary.forEach(info => {
        pdf.text(info, 20, yPosition);
        yPosition += 6;
      });

      // Add new page for chart
      pdf.addPage();
      yPosition = 20;

      // Chart title
      pdf.setFontSize(16);
      pdf.setFont('helvetica', 'bold');
      pdf.text('Glucose Dynamics Chart', pageWidth / 2, yPosition, { align: 'center' });
      yPosition += 15;

      // Capture the chart
      if (plotRef.current) {
        const chartElement = plotRef.current.el;
        const canvas = await html2canvas(chartElement, {
          scale: 2,
          backgroundColor: '#ffffff'
        });

        const imgData = canvas.toDataURL('image/png');
        const imgWidth = pageWidth - 40;
        const imgHeight = (canvas.height * imgWidth) / canvas.width;

        pdf.addImage(imgData, 'PNG', 20, yPosition, imgWidth, imgHeight);
        yPosition += imgHeight + 10;
      }

      // Add new page for ODE equations
      pdf.addPage();
      yPosition = 20;

      // ODE Equations Section
      pdf.setFontSize(16);
      pdf.setFont('helvetica', 'bold');
      pdf.text('Mathematical Model: Ordinary Differential Equations', 20, yPosition);
      yPosition += 15;

      pdf.setFontSize(12);
      pdf.setFont('helvetica', 'normal');
      pdf.text('This simulation is based on a system of 12 coupled differential equations that model', 20, yPosition);
      yPosition += 6;
      pdf.text('the complex interactions between glucose, insulin, and other hormones in the body.', 20, yPosition);
      yPosition += 10;

      // Key equations (simplified for general audience)
      pdf.setFontSize(14);
      pdf.setFont('helvetica', 'bold');
      pdf.text('Key Model Components:', 20, yPosition);
      yPosition += 10;

      pdf.setFontSize(11);
      pdf.setFont('helvetica', 'normal');
      const equations = [
        '1. Blood Glucose (G): Affected by food intake, insulin action, and liver glucose release',
        '   • Increases with meals and stress',
        '   • Decreases with insulin and exercise',
        '',
        '2. Insulin (I): Produced by pancreatic β-cells in response to glucose',
        '   • Higher glucose levels trigger more insulin production',
        '   • Helps cells absorb glucose from blood',
        '',
        '3. Glucagon (C): Produced by pancreatic α-cells when glucose is low',
        '   • Signals liver to release stored glucose',
        '   • Counteracts insulin effects',
        '',
        '4. GLP-1 (L): Incretin hormone that enhances insulin secretion',
        '   • Released after meals',
        '   • Target for diabetes medications',
        '',
        '5. Pancreatic Cells (β and α): Respond to glucose and hormone levels',
        '   • β-cells: Produce insulin when glucose is high',
        '   • α-cells: Produce glucagon when glucose is low',
        '',
        '6. Glucose Transporters (GLUT-2, GLUT-4): Enable glucose uptake by cells',
        '   • GLUT-2: In liver and pancreas (glucose sensing)',
        '   • GLUT-4: In muscle and fat (insulin-dependent)',
      ];

      equations.forEach(eq => {
        if (yPosition > pageHeight - 20) {
          pdf.addPage();
          yPosition = 20;
        }
        pdf.text(eq, 20, yPosition);
        yPosition += 5;
      });

      // Add new page for parameters
      pdf.addPage();
      yPosition = 20;

      // Model Parameters Section
      pdf.setFontSize(16);
      pdf.setFont('helvetica', 'bold');
      pdf.text('Model Parameters (Personalized for Patient)', 20, yPosition);
      yPosition += 15;

      pdf.setFontSize(12);
      pdf.setFont('helvetica', 'normal');
      pdf.text('The following parameters were automatically adjusted based on patient characteristics:', 20, yPosition);
      yPosition += 10;

      // Key parameter explanations
      const parameterExplanations = [
        'Age Factor: Older patients have reduced β-cell function',
        'BMI Factor: Higher BMI increases insulin resistance and inflammation',
        'Activity Level: Regular exercise improves insulin sensitivity',
        'Medications: Each medication has specific effects on glucose metabolism',
        'Gender: Affects baseline insulin sensitivity and hormone interactions',
        'Smoking Status: Increases inflammation and insulin resistance',
        '',
        'Example Parameter Adjustments:',
        `• Obesity factor: ${simulationParams.palmitic_factor}x (1.0 = normal, higher = more insulin resistant)`,
        `• Food factor: ${simulationParams.food_factor}x (represents dietary habits)`,
        `• Drug dosage: ${simulationParams.drug_dosage} units (GLP-1 agonist equivalent)`,
      ];

      parameterExplanations.forEach(param => {
        if (yPosition > pageHeight - 20) {
          pdf.addPage();
          yPosition = 20;
        }
        pdf.text(param, 20, yPosition);
        yPosition += 6;
      });

      // Add recommendations
      if (simulationResult.recommendations.length > 0) {
        yPosition += 10;
        pdf.setFontSize(14);
        pdf.setFont('helvetica', 'bold');
        pdf.text('Personalized Recommendations:', 20, yPosition);
        yPosition += 10;

        pdf.setFontSize(11);
        pdf.setFont('helvetica', 'normal');
        simulationResult.recommendations.forEach((rec, index) => {
          if (yPosition > pageHeight - 20) {
            pdf.addPage();
            yPosition = 20;
          }
          pdf.text(`${index + 1}. ${rec}`, 20, yPosition);
          yPosition += 6;
        });
      }

      // Save the PDF
      const fileName = `diabetes_simulation_${patientData.name.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
      pdf.save(fileName);

    } catch (error) {
      console.error('PDF generation failed:', error);
      alert('Failed to generate PDF report. Please try again.');
    } finally {
      setExportingPDF(false);
    }
  };

  return (
    <div className="simulation-dashboard">
      <div className="dashboard-header">
        <div className="patient-info">
          <h2>{patientData.name}</h2>
          <div className="patient-stats">
            <span>Age: {patientData.age}</span>
            <span>BMI: {calculateBMI()}</span>
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
            className="btn-secondary" 
            onClick={generatePDFReport} 
            disabled={!simulationResult || exportingPDF}
          >
            {exportingPDF ? '📄 Generating...' : '📄 Download PDF Report'}
          </button>
          <button className="btn-primary" onClick={runSimulation} disabled={loading}>
            {loading ? 'Running...' : '🔄 Refresh'}
          </button>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="parameter-panel">
          <h3>Simulation Parameters</h3>
          
          <div className="parameter-group">
            <label>Simulation Duration: {simulationParams.simulation_hours} hours</label>
            <input
              type="range"
              min="6"
              max="72"
              step="6"
              value={simulationParams.simulation_hours}
              onChange={(e) => {
                handleParameterChange('simulation_hours', parseInt(e.target.value));
                debouncedSimulation();
              }}
            />
          </div>

          <div className="parameter-group">
            <label>Food Factor: {simulationParams.food_factor.toFixed(1)}x</label>
            <input
              type="range"
              min="0.5"
              max="3.0"
              step="0.1"
              value={simulationParams.food_factor}
              onChange={(e) => {
                handleParameterChange('food_factor', parseFloat(e.target.value));
                debouncedSimulation();
              }}
            />
            <small>1.0 = normal eating, 2.0+ = overeating</small>
          </div>

          <div className="parameter-group">
            <label>Obesity Factor: {simulationParams.palmitic_factor.toFixed(1)}x</label>
            <input
              type="range"
              min="0.5"
              max="4.0"
              step="0.1"
              value={simulationParams.palmitic_factor}
              onChange={(e) => {
                handleParameterChange('palmitic_factor', parseFloat(e.target.value));
                debouncedSimulation();
              }}
            />
            <small>1.0 = normal weight, 3.0+ = obese</small>
          </div>

          <div className="parameter-group">
            <label>Drug Dosage: {simulationParams.drug_dosage.toFixed(1)} units</label>
            <input
              type="range"
              min="0"
              max="2.0"
              step="0.1"
              value={simulationParams.drug_dosage}
              onChange={(e) => {
                handleParameterChange('drug_dosage', parseFloat(e.target.value));
                debouncedSimulation();
              }}
            />
            <small>0 = no medication, 1.0+ = GLP-1 agonist therapy</small>
          </div>

          <div className="metric-selector">
            <h4>Display Metrics</h4>
            <div className="metric-checkboxes">
              {Object.entries(selectedMetrics).map(([metric, selected]) => (
                <label key={metric} className="metric-checkbox">
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
                  <span className={`metric-label ${metric}`}>
                    {metric.replace('_', '-').charAt(0).toUpperCase() + metric.replace('_', '-').slice(1)}
                  </span>
                </label>
              ))}
            </div>
          </div>

          <div className="preset-buttons">
            <button onClick={() => {
              setSimulationParams({...simulationParams, food_factor: 1.0, palmitic_factor: 1.0, drug_dosage: 0.0});
              debouncedSimulation();
            }}>Normal</button>
            <button onClick={() => {
              setSimulationParams({...simulationParams, food_factor: 2.0, palmitic_factor: 2.5, drug_dosage: 0.0});
              debouncedSimulation();
            }}>High Risk</button>
            <button onClick={() => {
              setSimulationParams({...simulationParams, food_factor: 1.2, palmitic_factor: 1.5, drug_dosage: 1.0});
              debouncedSimulation();
            }}>With Treatment</button>
            <button onClick={() => {
              setSimulationParams({...simulationParams, food_factor: 0.8, palmitic_factor: 0.7, drug_dosage: 0.5});
              debouncedSimulation();
            }}>Optimal</button>
          </div>
        </div>

        <div className="plot-container">
          {loading ? (
            <div className="loading-spinner">
              <div className="spinner"></div>
              <p>Running simulation...</p>
            </div>
          ) : error ? (
            <div className="error-message">
              <h3>Simulation Error</h3>
              <p>{error}</p>
              <button onClick={runSimulation} className="btn-primary">Try Again</button>
            </div>
          ) : simulationResult ? (
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
                  filename: `diabetes_simulation_${patientData.name}`,
                  height: 600,
                  width: 1000,
                  scale: 1
                }
              }}
              style={{ width: '100%', height: '100%' }}
            />
          ) : (
            <div className="no-data">
              <p>No simulation data available</p>
            </div>
          )}
        </div>
      </div>

      {simulationResult && (
        <div className="simulation-summary">
          <div className="summary-card">
            <h3>Simulation Summary</h3>
            <div className="summary-grid">
              <div className="summary-item">
                <label>Average Glucose:</label>
                <span>{simulationResult.simulation_summary.average_glucose} mg/dL</span>
              </div>
              <div className="summary-item">
                <label>Peak Glucose:</label>
                <span>{simulationResult.simulation_summary.max_glucose} mg/dL</span>
              </div>
              <div className="summary-item">
                <label>Glucose Variability:</label>
                <span>{simulationResult.simulation_summary.glucose_variability} mg/dL</span>
              </div>
              <div className="summary-item">
                <label>Time in Range:</label>
                <span>{simulationResult.simulation_summary.time_in_range}%</span>
              </div>
              <div className="summary-item">
                <label>A1C Estimate:</label>
                <span className={`diagnosis ${simulationResult.diagnosis.toLowerCase()}`}>
                  {simulationResult.a1c_estimate}%
                </span>
              </div>
              <div className="summary-item">
                <label>Diagnosis:</label>
                <span className={`diagnosis ${simulationResult.diagnosis.toLowerCase()}`}>
                  {simulationResult.diagnosis}
                </span>
              </div>
            </div>

            {simulationResult.recommendations.length > 0 && (
              <div className="recommendations">
                <h4>Personalized Recommendations:</h4>
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

export default SimulationDashboard;