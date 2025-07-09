// src/components/SimulationDashboard.tsx
import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import { PatientData, SimulationResult, SimulationParams } from '../types/diabetes';
import { simulationAPI } from '../utils/api';
import './SimulationDashboard.css';

interface SimulationDashboardProps {
  patientData: PatientData;
}

const SimulationDashboard: React.FC<SimulationDashboardProps> = ({ patientData }) => {
  const [simulationResult, setSimulationResult] = useState<SimulationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedMetrics, setSelectedMetrics] = useState({
    glucose: true,
    insulin: true,
    glucagon: false,
    glp1: false,
  });
  
  const [simulationParams, setSimulationParams] = useState<SimulationParams>({
    patient_data: patientData,
    simulation_hours: 24,
    food_factor: 1.0,
    palmitic_factor: 1.0,
    drug_dosage: 0.0,
    show_optimal: true,
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
    const { time_points, glucose, insulin, glucagon, glp1, optimal_glucose } = simulationResult;

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

    return traces;
  };

  const getPlotLayout = () => {
    const yAxes: any = {};
    let axisCount = 0;

    if (selectedMetrics.glucose) {
      axisCount++;
      yAxes.yaxis = {
        title: 'Glucose (mg/dL)',
        side: 'left',
        color: '#e74c3c',
        showgrid: true,
        gridcolor: '#f0f0f0',
      };
    }

    if (selectedMetrics.insulin) {
      axisCount++;
      yAxes.yaxis2 = {
        title: 'Insulin (pmol/L)',
        side: 'right',
        overlaying: 'y',
        color: '#3498db',
        showgrid: false,
      };
    }

    if (selectedMetrics.glucagon) {
      axisCount++;
      yAxes.yaxis3 = {
        title: 'Glucagon (pg/mL)',
        side: 'right',
        overlaying: 'y',
        position: 0.85,
        color: '#9b59b6',
        showgrid: false,
      };
    }

    if (selectedMetrics.glp1) {
      axisCount++;
      yAxes.yaxis4 = {
        title: 'GLP-1 (pmol/L)',
        side: 'right',
        overlaying: 'y',
        position: 0.9,
        color: '#f39c12',
        showgrid: false,
      };
    }

    // Add meal time annotations
    const mealTimes = [];
    for (let i = 0; i < simulationParams.simulation_hours; i += 6) {
      if (i < simulationParams.simulation_hours) {
        mealTimes.push({
          x: i,
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
        });
      }
    }

    return {
      title: {
        text: `Glucose Dynamics - ${patientData.name}`,
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
      margin: { l: 60, r: 60, t: 80, b: 100 },
      height: 500,
      showlegend: true,
      hovermode: 'x unified',
      plot_bgcolor: 'white',
      paper_bgcolor: 'white',
      annotations: mealTimes,
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

  const downloadData = () => {
    if (!simulationResult) return;
    
    const csvContent = [
      ['Time (hours)', 'Glucose (mg/dL)', 'Insulin (pmol/L)', 'Glucagon (pg/mL)', 'GLP-1 (pmol/L)'],
      ...simulationResult.time_points.map((time, i) => [
        time.toFixed(2),
        simulationResult.glucose[i].toFixed(2),
        simulationResult.insulin[i].toFixed(2),
        simulationResult.glucagon[i].toFixed(2),
        simulationResult.glp1[i].toFixed(2),
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `diabetes_simulation_${patientData.name.replace(/\s+/g, '_')}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
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
          <button className="btn-secondary" onClick={downloadData} disabled={!simulationResult}>
            📊 Download Data
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
                    {metric.charAt(0).toUpperCase() + metric.slice(1)}
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
                <span>{(simulationResult.glucose.reduce((a, b) => a + b, 0) / simulationResult.glucose.length).toFixed(1)} mg/dL</span>
              </div>
              <div className="summary-item">
                <label>Peak Glucose:</label>
                <span>{Math.max(...simulationResult.glucose).toFixed(1)} mg/dL</span>
              </div>
              <div className="summary-item">
                <label>Glucose Variability:</label>
                <span>{Math.sqrt(simulationResult.glucose.reduce((sum, val, _, arr) => {
                  const mean = arr.reduce((a, b) => a + b) / arr.length;
                  return sum + Math.pow(val - mean, 2);
                }, 0) / simulationResult.glucose.length).toFixed(1)} mg/dL</span>
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
              <div className="summary-item">
                <label>Data Points:</label>
                <span>{simulationResult.time_points.length}</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SimulationDashboard;