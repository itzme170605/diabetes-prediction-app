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
                <label>BMI & Category</label>
                <div className="bmi-display">
                  {calculateBMI()} kg/m² ({getBMICategory()})
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
                <label htmlFor="activity_level">Activity Level</label>
                <select
                  id="activity_level"
                  name="activity_level"
                  value={formData.activity_level || 'moderate'}
                  onChange={handleInputChange}
                >
                  <option value="sedentary">Sedentary (little to no exercise)</option>
                  <option value="light">Light (1-3 days/week)</option>
                  <option value="moderate">Moderate (3-5 days/week)</option>
                  <option value="active">Very Active (6-7 days/week)</option>
                </select>
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
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="family_history" className="checkbox-label">
                <input
                  type="checkbox"
                  id="family_history"
                  name="family_history"
                  checked={formData.family_history || false}
                  onChange={handleInputChange}
                />
                Family history of diabetes
              </label>
            </div>
          </div>

          <div className="form-section">
            <h3>Medications</h3>
            <div className="medication-input">
              <input
                type="text"
                value={currentMedication}
                onChange={(e) => setCurrentMedication(e.target.value)}
                placeholder="Enter medication name"
                onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addMedication())}
              />
              <button type="button" onClick={addMedication} className="btn-secondary">
                Add
              </button>
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
              <p>Common diabetes medications:</p>
              <div className="medication-suggestions">
                {['Metformin', 'Insulin', 'GLP-1 agonist', 'Semaglutide', 'Ozempic'].map(med => (
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