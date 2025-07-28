// src/components/SimulationDashboard.tsx - Updated with professor's features
import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import { 
  PatientData, 
  SimulationResult, 
  ExtendedSimulationResult,
  SimulationParams, 
  MealSchedule, 
  DrugSchedule 
} from '../types/diabetes';
import { simulationAPI } from '../utils/api';
import './SimulationDashboard.css';

interface SimulationDashboardProps {
  patientData: PatientData;
  mealSchedule?: MealSchedule;
  drugSchedule?: DrugSchedule;
}

interface ComparisonResult {
  state: string;
  result: ExtendedSimulationResult;
}

const SimulationDashboard: React.FC<SimulationDashboardProps> = ({ 
  patientData, 
  mealSchedule: initialMealSchedule,
  drugSchedule 
}) => {
  const [simulationResult, setSimulationResult] = useState<ExtendedSimulationResult | null>(null);
  const [comparisonResults, setComparisonResults] = useState<ComparisonResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showExtendedMetrics, setShowExtendedMetrics] = useState(false);
  const [simulationDays, setSimulationDays] = useState<number | null>(null);
  const [comparisonMode, setComparisonMode] = useState(false);
  
  // Professor's default meal dosing pattern
  const [mealDosing, setMealDosing] = useState({
    breakfast: initialMealSchedule?.breakfast_factor || 0.4,
    lunch: initialMealSchedule?.lunch_factor || 0.4,
    dinner: initialMealSchedule?.dinner_factor || 0.8
  });

  const [mealSchedule, setMealSchedule] = useState<MealSchedule>({
    breakfast_time: initialMealSchedule?.breakfast_time || 0,
    breakfast_factor: mealDosing.breakfast,
    lunch_time: initialMealSchedule?.lunch_time || 6,
    lunch_factor: mealDosing.lunch,
    dinner_time: initialMealSchedule?.dinner_time || 12,
    dinner_factor: mealDosing.dinner,
  });
  
  const [selectedMetrics, setSelectedMetrics] = useState({
    glucose: true,
    insulin: true,
    glucagon: false,
    glp1: false,
    // Extended metrics
    alpha_cells: false,
    beta_cells: false,
    glut2: false,
    glut4: false,
    stored_glucose: false,
    oleic_acid: false,
    palmitic_acid: false,
    tnf_alpha: false,
  });
  
  const [simulationParams, setSimulationParams] = useState<SimulationParams>({
    patient_data: patientData,
    simulation_hours: 24,
    simulation_days: simulationDays || undefined,
    meal_schedule: mealSchedule,
    food_factor: 1.0,
    palmitic_factor: 1.0,
    drug_dosage: drugSchedule ? drugSchedule.initial_dose : 0.0,
    drug_schedule: drugSchedule,
    show_optimal: true,
    include_all_variables: true,
  });

  useEffect(() => {
    if (comparisonMode) {
      runComparisonSimulations();
    } else {
      runSimulation();
    }
  }, []);

  const runSimulation = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await simulationAPI.runExtendedSimulation({
        ...simulationParams,
        meal_schedule: mealSchedule
      });
      setSimulationResult(result);
    } catch (error: any) {
      setError(error.message);
      console.error('Simulation failed:', error);
    }
    setLoading(false);
  };

  const runComparisonSimulations = async () => {
    setLoading(true);
    setError(null);
    try {
      const states = ['normal', 'prediabetic', 'diabetic'];
      const results: ComparisonResult[] = [];
      
      for (const state of states) {
        const modifiedPatient = { ...patientData, diabetes_type: state };
        const params = {
          ...simulationParams,
          patient_data: modifiedPatient,
          meal_schedule: mealSchedule
        };
        const result = await simulationAPI.runExtendedSimulation(params);
        results.push({ state, result });
      }
      
      setComparisonResults(results);
    } catch (error: any) {
      setError(error.message);
      console.error('Comparison simulation failed:', error);
    }
    setLoading(false);
  };

  const handleParameterChange = (key: keyof SimulationParams, value: any) => {
    const newParams = { ...simulationParams, [key]: value };
    setSimulationParams(newParams);
  };

  const handleMealDosingChange = (meal: 'breakfast' | 'lunch' | 'dinner', value: number) => {
    const newDosing = { ...mealDosing, [meal]: value };
    setMealDosing(newDosing);
    
    const newSchedule = {
      ...mealSchedule,
      breakfast_factor: newDosing.breakfast,
      lunch_factor: newDosing.lunch,
      dinner_factor: newDosing.dinner
    };
    setMealSchedule(newSchedule);
    
    debouncedSimulation();
  };

  const handleSimulationTypeChange = (type: 'hours' | 'days') => {
    if (type === 'days') {
      setSimulationDays(7);
      handleParameterChange('simulation_days', 7);
      handleParameterChange('simulation_hours', 168);
    } else {
      setSimulationDays(null);
      handleParameterChange('simulation_days', undefined);
      handleParameterChange('simulation_hours', 24);
    }
    debouncedSimulation();
  };

  const toggleComparisonMode = () => {
    const newMode = !comparisonMode;
    setComparisonMode(newMode);
    if (newMode) {
      runComparisonSimulations();
    } else {
      runSimulation();
    }
  };

  const debouncedSimulation = () => {
    setTimeout(() => {
      if (comparisonMode) {
        runComparisonSimulations();
      } else {
        runSimulation();
      }
    }, 300);
  };

  const calculateBMI = () => {
    const heightM = patientData.height / 100;
    return (patientData.weight / (heightM * heightM)).toFixed(1);
  };

  const createPlotData = () => {
    if (comparisonMode && comparisonResults.length > 0) {
      return createComparisonPlotData();
    }
    
    if (!simulationResult) return [];

    const traces: any[] = [];
    const { 
      time_points, glucose, insulin, glucagon, glp1, optimal_glucose,
      alpha_cells, beta_cells, glut2, glut4, stored_glucose,
      oleic_acid, palmitic_acid, tnf_alpha
    } = simulationResult;

    // Convert time to days if multi-day simulation
    const timeInDays = simulationDays ? time_points.map(t => t / 24) : time_points;
    const timeLabel = simulationDays ? 'Time (days)' : 'Time (hours)';

    // Primary metrics
    if (selectedMetrics.glucose) {
      traces.push({
        x: timeInDays,
        y: glucose,
        type: 'scatter',
        mode: 'lines',
        name: 'Blood Glucose',
        line: { color: 'var(--rit-red)', width: 3 },
        hovertemplate: `${timeLabel}: %{x:.1f}<br>Glucose: %{y:.1f} mg/dL<extra></extra>`,
      });

      if (optimal_glucose && simulationParams.show_optimal) {
        traces.push({
          x: timeInDays,
          y: optimal_glucose,
          type: 'scatter',
          mode: 'lines',
          name: 'Optimal Glucose',
          line: { color: 'var(--rit-green)', width: 2, dash: 'dot' },
          hovertemplate: `${timeLabel}: %{x:.1f}<br>Optimal: %{y:.1f} mg/dL<extra></extra>`,
        });
      }
    }

    if (selectedMetrics.insulin) {
      traces.push({
        x: timeInDays,
        y: insulin,
        type: 'scatter',
        mode: 'lines',
        name: 'Insulin',
        line: { color: 'var(--rit-blue)', width: 3 },
        yaxis: 'y2',
        hovertemplate: `${timeLabel}: %{x:.1f}<br>Insulin: %{y:.1f} pmol/L<extra></extra>`,
      });
    }

    if (selectedMetrics.glucagon) {
      traces.push({
        x: timeInDays,
        y: glucagon,
        type: 'scatter',
        mode: 'lines',
        name: 'Glucagon',
        line: { color: 'var(--rit-purple)', width: 2 },
        yaxis: 'y3',
        hovertemplate: `${timeLabel}: %{x:.1f}<br>Glucagon: %{y:.1f} pg/mL<extra></extra>`,
      });
    }

    if (selectedMetrics.glp1) {
      traces.push({
        x: timeInDays,
        y: glp1,
        type: 'scatter',
        mode: 'lines',
        name: 'GLP-1',
        line: { color: 'var(--rit-yellow)', width: 2 },
        yaxis: 'y4',
        hovertemplate: `${timeLabel}: %{x:.1f}<br>GLP-1: %{y:.1f} pmol/L<extra></extra>`,
      });
    }

    // Extended metrics
    if (showExtendedMetrics) {
      if (selectedMetrics.beta_cells && beta_cells) {
        traces.push({
          x: timeInDays,
          y: beta_cells,
          type: 'scatter',
          mode: 'lines',
          name: 'β-cells',
          line: { color: 'var(--rit-lime)', width: 2 },
          visible: 'legendonly',
        });
      }

      if (selectedMetrics.stored_glucose && stored_glucose) {
        traces.push({
          x: timeInDays,
          y: stored_glucose,
          type: 'scatter',
          mode: 'lines',
          name: 'Stored Glucose',
          line: { color: 'var(--rit-warm-gray-dark)', width: 2 },
          visible: 'legendonly',
        });
      }

      if (selectedMetrics.tnf_alpha && tnf_alpha) {
        traces.push({
          x: timeInDays,
          y: tnf_alpha,
          type: 'scatter',
          mode: 'lines',
          name: 'TNF-α',
          line: { color: 'var(--rit-gray-dark)', width: 2 },
          visible: 'legendonly',
        });
      }
    }

    return traces;
  };

  const createComparisonPlotData = () => {
    const traces: any[] = [];
    const colors = {
      normal: 'var(--rit-green)',
      prediabetic: 'var(--rit-yellow)',
      diabetic: 'var(--rit-red)'
    };

    comparisonResults.forEach(({ state, result }) => {
      const timeInDays = simulationDays ? result.time_points.map(t => t / 24) : result.time_points;
      const timeLabel = simulationDays ? 'Time (days)' : 'Time (hours)';

      traces.push({
        x: timeInDays,
        y: result.glucose,
        type: 'scatter',
        mode: 'lines',
        name: `${state.charAt(0).toUpperCase() + state.slice(1)} Glucose`,
        line: { color: colors[state as keyof typeof colors], width: 3 },
        hovertemplate: `${timeLabel}: %{x:.1f}<br>${state} Glucose: %{y:.1f} mg/dL<extra></extra>`,
      });
    });

    return traces;
  };

  const getPlotLayout = () => {
    const yAxes: any = {};
    let axisCount = 0;
    const timeLabel = simulationDays ? 'Time (days)' : 'Time (hours)';
    const maxTime = simulationDays ? simulationParams.simulation_days! : simulationParams.simulation_hours;

    if (selectedMetrics.glucose || comparisonMode) {
      axisCount++;
      yAxes.yaxis = {
        title: 'Glucose (mg/dL)',
        side: 'left',
        color: comparisonMode ? 'var(--rit-black)' : 'var(--rit-red)',
        showgrid: true,
        gridcolor: 'var(--rit-gray-light)',
      };
    }

    if (selectedMetrics.insulin && !comparisonMode) {
      axisCount++;
      yAxes.yaxis2 = {
        title: 'Insulin (pmol/L)',
        side: 'right',
        overlaying: 'y',
        color: 'var(--rit-blue)',
        showgrid: false,
      };
    }

    if (selectedMetrics.glucagon && !comparisonMode) {
      axisCount++;
      yAxes.yaxis3 = {
        title: 'Glucagon (pg/mL)',
        side: 'right',
        overlaying: 'y',
        position: 0.85,
        color: 'var(--rit-purple)',
        showgrid: false,
      };
    }

    if (selectedMetrics.glp1 && !comparisonMode) {
      axisCount++;
      yAxes.yaxis4 = {
        title: 'GLP-1 (pmol/L)',
        side: 'right',
        overlaying: 'y',
        position: 0.9,
        color: 'var(--rit-yellow)',
        showgrid: false,
      };
    }

    // Add meal time annotations
    const mealTimes = [];
    const meals = [
      { time: mealSchedule.breakfast_time, label: '🍳', factor: mealDosing.breakfast },
      { time: mealSchedule.lunch_time, label: '🥗', factor: mealDosing.lunch },
      { time: mealSchedule.dinner_time, label: '🍽️', factor: mealDosing.dinner }
    ];

    for (const meal of meals) {
      // Add annotations for each day if multi-day simulation
      if (simulationDays) {
        for (let day = 0; day < simulationDays; day++) {
          mealTimes.push({
            x: (meal.time + day * 24) / 24,
            y: 0,
            xref: 'x',
            yref: 'paper',
            text: `${meal.label} ${meal.factor.toFixed(1)}x`,
            showarrow: true,
            arrowhead: 2,
            arrowsize: 1,
            arrowwidth: 2,
            arrowcolor: 'var(--rit-orange)',
            ax: 0,
            ay: -30,
            font: { size: 14 }
          });
        }
      } else {
        mealTimes.push({
          x: meal.time,
          y: 0,
          xref: 'x',
          yref: 'paper',
          text: `${meal.label} ${meal.factor.toFixed(1)}x`,
          showarrow: true,
          arrowhead: 2,
          arrowsize: 1,
          arrowwidth: 2,
          arrowcolor: 'var(--rit-orange)',
          ax: 0,
          ay: -30,
          font: { size: 14 }
        });
      }
    }

    return {
      title: {
        text: comparisonMode 
          ? `Glucose Dynamics Comparison - ${patientData.name}`
          : `Glucose Dynamics - ${patientData.name}`,
        font: { size: 20, color: 'var(--rit-black)' },
      },
      xaxis: {
        title: timeLabel,
        showgrid: true,
        gridcolor: 'var(--rit-gray-light)',
        range: [0, maxTime],
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
          x1: maxTime,
          y0: 70,
          y1: 140,
          fillcolor: 'rgba(132, 189, 0, 0.1)',
          line: { width: 0 },
          layer: 'below',
        },
        // Prediabetic range
        comparisonMode ? {
          type: 'rect',
          xref: 'x',
          yref: 'y',
          x0: 0,
          x1: maxTime,
          y0: 100,
          y1: 125,
          fillcolor: 'rgba(246, 190, 0, 0.1)',
          line: { width: 0 },
          layer: 'below',
        } : {},
        // Diabetic threshold line
        comparisonMode ? {
          type: 'line',
          xref: 'x',
          yref: 'y',
          x0: 0,
          x1: maxTime,
          y0: 126,
          y1: 126,
          line: {
            color: 'var(--rit-red)',
            width: 2,
            dash: 'dash',
          },
        } : {}
      ].filter(shape => Object.keys(shape).length > 0),
    };
  };

  const downloadData = () => {
    if (!simulationResult && comparisonResults.length === 0) return;
    
    let csvContent = '';
    
    if (comparisonMode && comparisonResults.length > 0) {
      // Comparison mode CSV
      const headers = ['Time (hours)', ...comparisonResults.map(r => `${r.state} Glucose (mg/dL)`)];
      const rows = comparisonResults[0].result.time_points.map((time, i) => {
        return [
          time.toFixed(2),
          ...comparisonResults.map(r => r.result.glucose[i].toFixed(2))
        ];
      });
      csvContent = [headers, ...rows].map(row => row.join(',')).join('\n');
    } else if (simulationResult) {
      // Single simulation CSV
      const headers = ['Time (hours)', 'Glucose (mg/dL)', 'Insulin (pmol/L)', 'Glucagon (pg/mL)', 'GLP-1 (pmol/L)'];
      const extendedHeaders = showExtendedMetrics ? [
        'Alpha Cells', 'Beta Cells', 'GLUT-2', 'GLUT-4', 
        'Stored Glucose', 'Oleic Acid', 'Palmitic Acid', 'TNF-α'
      ] : [];
      
      csvContent = [
        [...headers, ...extendedHeaders],
        ...simulationResult.time_points.map((time, i) => {
          const baseData = [
            time.toFixed(2),
            simulationResult.glucose[i].toFixed(2),
            simulationResult.insulin[i].toFixed(2),
            simulationResult.glucagon[i].toFixed(2),
            simulationResult.glp1[i].toFixed(2),
          ];
          
          const extendedData = showExtendedMetrics ? [
            simulationResult.alpha_cells?.[i]?.toFixed(2) || '',
            simulationResult.beta_cells?.[i]?.toFixed(2) || '',
            simulationResult.glut2?.[i]?.toFixed(2) || '',
            simulationResult.glut4?.[i]?.toFixed(2) || '',
            simulationResult.stored_glucose?.[i]?.toFixed(2) || '',
            simulationResult.oleic_acid?.[i]?.toFixed(2) || '',
            simulationResult.palmitic_acid?.[i]?.toFixed(2) || '',
            simulationResult.tnf_alpha?.[i]?.toFixed(2) || '',
          ] : [];
          
          return [...baseData, ...extendedData];
        })
      ].map(row => row.join(',')).join('\n');
    }

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `diabetes_simulation_${patientData.name.replace(/\s+/g, '_')}_${comparisonMode ? 'comparison' : 'extended'}.csv`;
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
            {simulationResult && !comparisonMode && (
              <>
                <span>A1C: {simulationResult.a1c_estimate}%</span>
                <span>Avg Glucose: {simulationResult.avg_glucose.toFixed(1)} mg/dL</span>
                <span>Time in Range: {simulationResult.time_in_range.toFixed(1)}%</span>
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
            onClick={toggleComparisonMode}
          >
            {comparisonMode ? '📊 Single View' : '📈 Compare States'}
          </button>
          <button className="btn-secondary" onClick={downloadData} disabled={!simulationResult && comparisonResults.length === 0}>
            💾 Download Data
          </button>
          <button className="btn-primary" onClick={comparisonMode ? runComparisonSimulations : runSimulation} disabled={loading}>
            {loading ? 'Running...' : '🔄 Refresh'}
          </button>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="parameter-panel">
          <h3>Simulation Parameters</h3>
          
          {/* Simulation Duration Toggle */}
          <div className="parameter-group">
            <label>Simulation Type</label>
            <div style={{ display: 'flex', gap: '1rem', marginBottom: '1rem' }}>
              <button 
                className={`btn-secondary ${!simulationDays ? 'active' : ''}`}
                onClick={() => handleSimulationTypeChange('hours')}
                style={{ 
                  flex: 1, 
                  background: !simulationDays ? 'var(--rit-orange)' : 'white',
                  color: !simulationDays ? 'white' : 'var(--rit-orange)'
                }}
              >
                Hours
              </button>
              <button 
                className={`btn-secondary ${simulationDays ? 'active' : ''}`}
                onClick={() => handleSimulationTypeChange('days')}
                style={{ 
                  flex: 1,
                  background: simulationDays ? 'var(--rit-orange)' : 'white',
                  color: simulationDays ? 'white' : 'var(--rit-orange)'
                }}
              >
                Days
              </button>
            </div>
          </div>

          <div className="parameter-group">
            <label>
              {simulationDays 
                ? `Simulation Days: ${simulationDays}` 
                : `Simulation Hours: ${simulationParams.simulation_hours}`}
            </label>
            <input
              type="range"
              min={simulationDays ? 1 : 6}
              max={simulationDays ? 30 : 72}
              step={simulationDays ? 1 : 6}
              value={simulationDays || simulationParams.simulation_hours}
              onChange={(e) => {
                const value = parseInt(e.target.value);
                if (simulationDays) {
                  setSimulationDays(value);
                  handleParameterChange('simulation_days', value);
                  handleParameterChange('simulation_hours', value * 24);
                } else {
                  handleParameterChange('simulation_hours', value);
                }
                debouncedSimulation();
              }}
            />
          </div>

          {/* Meal Dosing Pattern - Professor's Implementation */}
          <div className="parameter-group">
            <h4 style={{ color: 'var(--rit-orange)', fontSize: '16px', marginBottom: '0.5rem' }}>
              Meal Dosing Pattern
            </h4>
            <div className="meal-dosing-grid">
              <div className="dose-input">
                <label>Breakfast: {mealDosing.breakfast.toFixed(1)}x</label>
                <input
                  type="range"
                  min="0.1"
                  max="1.0"
                  step="0.1"
                  value={mealDosing.breakfast}
                  onChange={(e) => handleMealDosingChange('breakfast', parseFloat(e.target.value))}
                />
              </div>
              <div className="dose-input">
                <label>Lunch: {mealDosing.lunch.toFixed(1)}x</label>
                <input
                  type="range"
                  min="0.1"
                  max="1.0"
                  step="0.1"
                  value={mealDosing.lunch}
                  onChange={(e) => handleMealDosingChange('lunch', parseFloat(e.target.value))}
                />
              </div>
              <div className="dose-input">
                <label>Dinner: {mealDosing.dinner.toFixed(1)}x</label>
                <input
                  type="range"
                  min="0.1"
                  max="2.0"
                  step="0.1"
                  value={mealDosing.dinner}
                  onChange={(e) => handleMealDosingChange('dinner', parseFloat(e.target.value))}
                />
              </div>
            </div>
            <small style={{ color: 'var(--rit-gray-dark)', fontSize: '12px', marginTop: '0.25rem', display: 'block' }}>
              Professor's default: Breakfast 0.4, Lunch 0.4, Dinner 0.8
            </small>
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
            <small>
              {drugSchedule 
                ? `${drugSchedule.drug_type} therapy` 
                : '0 = no medication, 1.0+ = GLP-1 agonist'}
            </small>
          </div>

          {!comparisonMode && (
            <div className="metric-selector">
              <h4>Display Metrics</h4>
              <div className="metric-checkboxes">
                <h5 style={{ color: 'var(--rit-gray-dark)', fontSize: '14px', marginBottom: '0.5rem' }}>
                  Primary Metrics
                </h5>
                {Object.entries({
                  glucose: 'Glucose',
                  insulin: 'Insulin', 
                  glucagon: 'Glucagon',
                  glp1: 'GLP-1'
                }).map(([key, label]) => (
                  <label key={key} className="metric-checkbox">
                    <input
                      type="checkbox"
                      checked={selectedMetrics[key as keyof typeof selectedMetrics]}
                      onChange={(e) =>
                        setSelectedMetrics(prev => ({
                          ...prev,
                          [key]: e.target.checked
                        }))
                      }
                    />
                    <span className={`metric-label ${key}`}>
                      {label}
                    </span>
                  </label>
                ))}
                
                {/* Extended Metrics Toggle */}
                <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid var(--rit-gray-light)' }}>
                  <label className="metric-checkbox">
                    <input
                      type="checkbox"
                      checked={showExtendedMetrics}
                      onChange={(e) => setShowExtendedMetrics(e.target.checked)}
                    />
                    <span style={{ fontWeight: 600 }}>Show Extended Metrics</span>
                  </label>
                </div>
                
                {showExtendedMetrics && (
                  <>
                    <h5 style={{ color: 'var(--rit-gray-dark)', fontSize: '14px', margin: '0.5rem 0' }}>
                      Cell Populations
                    </h5>
                    {Object.entries({
                      alpha_cells: 'α-cells',
                      beta_cells: 'β-cells'
                    }).map(([key, label]) => (
                      <label key={key} className="metric-checkbox">
                        <input
                          type="checkbox"
                          checked={selectedMetrics[key as keyof typeof selectedMetrics]}
                          onChange={(e) =>
                            setSelectedMetrics(prev => ({
                              ...prev,
                              [key]: e.target.checked
                            }))
                          }
                        />
                        <span className="metric-label">{label}</span>
                      </label>
                    ))}
                    
                    <h5 style={{ color: 'var(--rit-gray-dark)', fontSize: '14px', margin: '0.5rem 0' }}>
                      Transport & Storage
                    </h5>
                    {Object.entries({
                      glut2: 'GLUT-2',
                      glut4: 'GLUT-4',
                      stored_glucose: 'Stored Glucose'
                    }).map(([key, label]) => (
                      <label key={key} className="metric-checkbox">
                        <input
                          type="checkbox"
                          checked={selectedMetrics[key as keyof typeof selectedMetrics]}
                          onChange={(e) =>
                            setSelectedMetrics(prev => ({
                              ...prev,
                              [key]: e.target.checked
                            }))
                          }
                        />
                        <span className="metric-label">{label}</span>
                      </label>
                    ))}
                    
                    <h5 style={{ color: 'var(--rit-gray-dark)', fontSize: '14px', margin: '0.5rem 0' }}>
                      Inflammatory Markers
                    </h5>
                    {Object.entries({
                      oleic_acid: 'Oleic Acid',
                      palmitic_acid: 'Palmitic Acid',
                      tnf_alpha: 'TNF-α'
                    }).map(([key, label]) => (
                      <label key={key} className="metric-checkbox">
                        <input
                          type="checkbox"
                          checked={selectedMetrics[key as keyof typeof selectedMetrics]}
                          onChange={(e) =>
                            setSelectedMetrics(prev => ({
                              ...prev,
                              [key]: e.target.checked
                            }))
                          }
                        />
                        <span className="metric-label">{label}</span>
                      </label>
                    ))}
                  </>
                )}
              </div>
            </div>
          )}

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
              <button onClick={comparisonMode ? runComparisonSimulations : runSimulation} className="btn-primary">
                Try Again
              </button>
            </div>
          ) : (simulationResult || comparisonResults.length > 0) ? (
            <Plot
              data={createPlotData()}
              layout={getPlotLayout()}
              config={{
                displayModeBar: true,
                displaylogo: false,
                modeBarButtonsToRemove: ['pan2d', 'lasso2d', 'select2d'],
                toImageButtonOptions: {
                  format: 'png',
                  filename: `diabetes_simulation_${patientData.name}_${comparisonMode ? 'comparison' : 'single'}`,
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

      {simulationResult && !comparisonMode && (
        <div className="simulation-summary">
          <div className="summary-card">
            <h3>Simulation Summary</h3>
            <div className="summary-grid">
              <div className="summary-item">
                <label>Average Glucose:</label>
                <span>{simulationResult.avg_glucose.toFixed(1)} mg/dL</span>
              </div>
              <div className="summary-item">
                <label>Peak Glucose:</label>
                <span>{Math.max(...simulationResult.glucose).toFixed(1)} mg/dL</span>
              </div>
              <div className="summary-item">
                <label>Minimum Glucose:</label>
                <span>{Math.min(...simulationResult.glucose).toFixed(1)} mg/dL</span>
              </div>
              <div className="summary-item">
                <label>Glucose Variability:</label>
                <span>{simulationResult.glucose_variability.toFixed(1)} mg/dL</span>
              </div>
              <div className="summary-item">
                <label>Time in Range (70-140):</label>
                <span>{simulationResult.time_in_range.toFixed(1)}%</span>
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
              <div className="summary-item">
                <label>Simulation Duration:</label>
                <span>
                  {simulationDays 
                    ? `${simulationDays} days` 
                    : `${simulationParams.simulation_hours} hours`}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {comparisonMode && comparisonResults.length > 0 && (
        <div className="simulation-summary">
          <div className="summary-card">
            <h3>Comparison Summary</h3>
            <div className="summary-grid">
              {comparisonResults.map(({ state, result }) => (
                <React.Fragment key={state}>
                  <div className="summary-item" style={{ gridColumn: '1 / -1', marginTop: '1rem' }}>
                    <h4 style={{ color: 'var(--rit-orange)', marginBottom: '0.5rem' }}>
                      {state.charAt(0).toUpperCase() + state.slice(1)} State
                    </h4>
                  </div>
                  <div className="summary-item">
                    <label>Average Glucose:</label>
                    <span>{result.avg_glucose.toFixed(1)} mg/dL</span>
                  </div>
                  <div className="summary-item">
                    <label>A1C Estimate:</label>
                    <span className={`diagnosis ${result.diagnosis.toLowerCase()}`}>
                      {result.a1c_estimate}%
                    </span>
                  </div>
                  <div className="summary-item">
                    <label>Time in Range:</label>
                    <span>{result.time_in_range.toFixed(1)}%</span>
                  </div>
                </React.Fragment>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SimulationDashboard;