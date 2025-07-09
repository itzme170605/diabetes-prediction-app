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
  });

  const [showModal, setShowModal] = useState(true);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
    setShowModal(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? parseFloat(value) || 0 : value
    }));
  };

  const calculateBMI = () => {
    const heightM = formData.height / 100;
    return (formData.weight / (heightM * heightM)).toFixed(1);
  };

  if (!showModal) return null;

  return (
    <div className="modal-overlay">
      <div className="patient-form-modal">
        <h2>Patient Information</h2>
        <p className="form-description">
          Enter patient details to personalize the diabetes simulation model
        </p>
        
        <form onSubmit={handleSubmit} className="patient-form">
          <div className="form-section">
            <h3>Basic Information</h3>
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
                  <option value="other">Other</option>
                </select>
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>Physical Measurements</h3>
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
                <label>BMI</label>
                <div className="bmi-display">
                  {calculateBMI()} kg/m²
                </div>
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>Medical Information</h3>
            <div className="form-grid">
              <div className="form-group">
                <label htmlFor="diabetes_type">Diabetes Status</label>
                <select
                  id="diabetes_type"
                  name="diabetes_type"
                  value={formData.diabetes_type || ''}
                  onChange={handleInputChange}
                >
                  <option value="">Auto-detect from glucose</option>
                  <option value="normal">Normal</option>
                  <option value="prediabetic">Prediabetic</option>
                  <option value="diabetic">Type 2 Diabetic</option>
                </select>
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
                  placeholder="70-100 normal"
                />
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
                  placeholder="<5.7% normal"
                />
              </div>
            </div>
          </div>

          <div className="form-section">
            <h3>Lifestyle Factors</h3>
            <div className="form-grid">
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
              </div>
              
              <div className="form-group">
                <label htmlFor="exercise_level">Exercise Level</label>
                <select
                  id="exercise_level"
                  name="exercise_level"
                  value={formData.exercise_level || 'moderate'}
                  onChange={handleInputChange}
                >
                  <option value="sedentary">Sedentary</option>
                  <option value="light">Light</option>
                  <option value="moderate">Moderate</option>
                  <option value="vigorous">Vigorous</option>
                </select>
              </div>
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary">
              Start Simulation
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PatientForm;