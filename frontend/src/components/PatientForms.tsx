// src/components/PatientForm.tsx
import React, { useState } from 'react';
import { PatientData } from '../types/diabetes';
import './PatientForm.css';

interface PatientFormProps {
  onSubmit: (data: PatientData) => void;
}

const PatientForm: React.FC<PatientFormProps> = ({ onSubmit }) => {
  const [formData, setFormData] = useState<PatientData>({
    name: '',
    age: 30,
    weight: 70,
    height: 170,
    gender: 'male',
    diabetes_type: null,
    obesity_level: null,
    meal_frequency: 3,
    sugar_intake: null,
    exercise_level: 'moderate',
    medications: [],
    fasting_glucose: null,
    a1c_level: null,
    activity_level: 'moderate',
    smoking_status: 'non_smoker',
    family_history: false,
    // Derived fields (calculated automatically)
    bmi: null,
    bmi_category: null,
    diabetes_risk: null,
  });

  const [showModal, setShowModal] = useState(true);
  const [currentMedication, setCurrentMedication] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
    setShowModal(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    
    if (type === 'checkbox') {
      const checkbox = e.target as HTMLInputElement;
      setFormData(prev => ({
        ...prev,
        [name]: checkbox.checked
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [name]: type === 'number' ? parseFloat(value) || 0 : value
      }));
    }
  };

  const addMedication = () => {
    if (currentMedication.trim() && !formData.medications.includes(currentMedication.trim())) {
      setFormData(prev => ({
        ...prev,
        medications: [...prev.medications, currentMedication.trim()]
      }));
      setCurrentMedication('');
    }
  };

  const removeMedication = (medication: string) => {
    setFormData(prev => ({
      ...prev,
      medications: prev.medications.filter(med => med !== medication)
    }));
  };

  const calculateBMI = () => {
    const heightM = formData.height / 100;
    return (formData.weight / (heightM * heightM)).toFixed(1);
  };

  const getBMICategory = () => {
    const bmi = parseFloat(calculateBMI());
    if (bmi < 18.5) return 'Underweight';
    if (bmi < 25) return 'Normal';
    if (bmi < 30) return 'Overweight';
    return 'Obese';
  };

  if (!showModal) return null;

  return (
    <div className="modal-overlay">
      <div className="patient-form-modal">
        <div className="form-header">
          <div className="rit-branding">
            <div className="rit-logo">🎓</div>
            <div className="rit-title">
              <h2>Enhanced Diabetes Simulation</h2>
              <p className="rit-subtitle">Rochester Institute of Technology</p>
            </div>
          </div>
        </div>
        
        <p className="form-description">
          Enter comprehensive patient details for personalized diabetes simulation using our enhanced 12-variable ODE model based on peer-reviewed research.
        </p>
        
        <form onSubmit={handleSubmit} className="patient-form">
          <div className="form-section">
            <h3>📋 Basic Information</h3>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="name">Full Name *</label>
                <input
                  type="text"
                  id="name"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                  placeholder="Enter patient name"
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="age">Age *</label>
                <input
                  type="number"
                  id="age"
                  name="age"
                  value={formData.age}
                  onChange={handleInputChange}
                  min="1"
                  max="120"
                  required
                />
                <small>Age affects β-cell function and insulin sensitivity</small>
              </div>
              
              <div className="form-group">
                <label htmlFor="gender">Gender *</label>
                <select
                  id="gender"
                  name="gender"
                  value={formData.gender}
                  onChange={handleInputChange}
                  required
                >
                  <option value="male">Male</option>
                  <option value="female">Female</option>
                </select>
                <small>Affects metabolic parameters and hormone sensitivity</small>
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>⚖️ Physical Measurements</h3>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="weight">Weight (kg) *</label>
                <input
                  type="number"
                  id="weight"
                  name="weight"
                  value={formData.weight}
                  onChange={handleInputChange}
                  min="20"
                  max="300"
                  step="0.1"
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="height">Height (cm) *</label>
                <input
                  type="number"
                  id="height"
                  name="height"
                  value={formData.height}
                  onChange={handleInputChange}
                  min="100"
                  max="250"
                  required
                />
              </div>
              
              <div className="form-group">
                <label>BMI & Category</label>
                <div className="bmi-display rit-accent">
                  {calculateBMI()} kg/m² ({getBMICategory()})
                </div>
                <small>BMI directly affects obesity factor and TNF-α levels in the model</small>
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>🩺 Medical Information</h3>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="diabetes_type">Diabetes Status</label>
                <select
                  id="diabetes_type"
                  name="diabetes_type"
                  value={formData.diabetes_type || ''}
                  onChange={handleInputChange}
                >
                  <option value="">Auto-detect from glucose/A1C</option>
                  <option value="normal">Normal glucose tolerance</option>
                  <option value="prediabetic">Prediabetes</option>
                  <option value="diabetic">Type 2 Diabetes</option>
                </select>
                <small>Affects β-cell function and insulin resistance parameters</small>
              </div>
              
              <div className="form-group">
                <label htmlFor="fasting_glucose">Fasting Glucose (mg/dL)</label>
                <input
                  type="number"
                  id="fasting_glucose"
                  name="fasting_glucose"
                  value={formData.fasting_glucose || ''}
                  onChange={handleInputChange}
                  min="50"
                  max="400"
                  placeholder="Normal: 70-99 mg/dL"
                />
                <small>Used for diabetes status classification and model calibration</small>
              </div>
              
              <div className="form-group">
                <label htmlFor="a1c_level">A1C Level (%)</label>
                <input
                  type="number"
                  id="a1c_level"
                  name="a1c_level"
                  value={formData.a1c_level || ''}
                  onChange={handleInputChange}
                  min="3"
                  max="15"
                  step="0.1"
                  placeholder="Normal: <5.7%"
                />
                <small>Key diagnostic marker for diabetes management</small>
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>🏃‍♂️ Lifestyle Factors</h3>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="activity_level">Physical Activity Level</label>
                <select
                  id="activity_level"
                  name="activity_level"
                  value={formData.activity_level || 'moderate'}
                  onChange={handleInputChange}
                >
                  <option value="sedentary">Sedentary (little to no exercise)</option>
                  <option value="light">Light activity (1-3 days/week)</option>
                  <option value="moderate">Moderate activity (3-5 days/week)</option>
                  <option value="active">Very active (6-7 days/week)</option>
                </select>
                <small>Significantly affects insulin sensitivity and GLUT-4 function</small>
              </div>
              
              <div className="form-group">
                <label htmlFor="smoking_status">Smoking Status</label>
                <select
                  id="smoking_status"
                  name="smoking_status"
                  value={formData.smoking_status || 'non_smoker'}
                  onChange={handleInputChange}
                >
                  <option value="non_smoker">Non-smoker</option>
                  <option value="former_smoker">Former smoker</option>
                  <option value="smoker">Current smoker</option>
                </select>
                <small>Smoking increases inflammation (TNF-α) and insulin resistance</small>
              </div>

              <div className="form-group">
                <label htmlFor="meal_frequency">Meals per Day</label>
                <input
                  type="number"
                  id="meal_frequency"
                  name="meal_frequency"
                  value={formData.meal_frequency}
                  onChange={handleInputChange}
                  min="1"
                  max="10"
                />
                <small>Affects glucose variability and meal timing optimization</small>
              </div>
            </div>

            <div className="form-group">
              <label className="checkbox-wrapper">
                <input
                  type="checkbox"
                  id="family_history"
                  name="family_history"
                  checked={formData.family_history || false}
                  onChange={handleInputChange}
                />
                <span className="checkmark"></span>
                Family history of diabetes
              </label>
              <small>Increases genetic predisposition and diabetes risk scoring</small>
            </div>
          </div>

          <div className="form-section">
            <h3>💊 Current Medications</h3>
            <div className="medication-input-wrapper">
              <div className="medication-input">
                <input
                  type="text"
                  value={currentMedication}
                  onChange={(e) => setCurrentMedication(e.target.value)}
                  placeholder="Enter medication name"
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addMedication())}
                />
                <button type="button" onClick={addMedication} className="btn-add-med">
                  Add
                </button>
              </div>
              <small>Medications directly affect model parameters (insulin sensitivity, GLP-1 levels, etc.)</small>
            </div>
            
            <div className="medication-list">
              {formData.medications.map((medication, index) => (
                <span key={index} className="medication-tag">
                  {medication}
                  <button
                    type="button"
                    onClick={() => removeMedication(medication)}
                    className="remove-medication"
                  >
                    ×
                  </button>
                </span>
              ))}
            </div>

            <div className="common-medications">
              <p><strong>Common diabetes medications:</strong></p>
              <div className="medication-suggestions">
                {['Metformin', 'Insulin', 'Semaglutide (Ozempic)', 'Tirzepatide (Mounjaro)', 'Liraglutide', 'SGLT2 inhibitor'].map(med => (
                  <button
                    key={med}
                    type="button"
                    className="btn-suggestion"
                    onClick={() => {
                      if (!formData.medications.includes(med)) {
                        setFormData(prev => ({
                          ...prev,
                          medications: [...prev.medications, med]
                        }));
                      }
                    }}
                  >
                    {med}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="form-section enhanced-features rit-section">
            <h3>🔬 Enhanced Simulation Features</h3>
            <div className="feature-highlights">
              <div className="feature-item">
                <span className="feature-icon">📊</span>
                <div className="feature-content">
                  <strong>12-Variable ODE Model</strong>
                  <p>Advanced mathematical model including GLP-1, glucagon, GLUT transporters, and inflammatory markers</p>
                </div>
              </div>
              <div className="feature-item">
                <span className="feature-icon">🍽️</span>
                <div className="feature-content">
                  <strong>Meal Pattern Analysis</strong>
                  <p>Customize individual meals (breakfast, lunch, dinner, snacks) and compare eating patterns</p>
                </div>
              </div>
              <div className="feature-item">
                <span className="feature-icon">💊</span>
                <div className="feature-content">
                  <strong>Drug Treatment Modeling</strong>
                  <p>Simulate GLP-1 agonist effects with personalized dosing and lifestyle modifications</p>
                </div>
              </div>
              <div className="feature-item">
                <span className="feature-icon">📈</span>
                <div className="feature-content">
                  <strong>Advanced Analytics</strong>
                  <p>Dawn phenomenon, post-meal response, glucose stability, and metabolic age assessment</p>
                </div>
              </div>
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary rit-primary">
              🚀 Start Enhanced Simulation
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PatientForm;