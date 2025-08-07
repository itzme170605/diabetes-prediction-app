// src/pages/AboutPage.tsx
import React from 'react';
import './AboutPage.css';

const AboutPage: React.FC = () => {
  return (
    <div className="about-page">
      {/* Hero Section */}
      <section className="about-hero">
        <div className="container">
          <h1>About Our Team</h1>
          <p className="hero-subtitle">
            Meet the researchers and developers behind DiabetesScope
          </p>
        </div>
      </section>

      {/* Team Section */}
      <section className="team-section">
        <div className="container">
          <h2>NourLabians</h2>
          
          <div className="team-grid">
            {/* Professor */}
            <div className="team-member-card featured">
              <div className="member-photo">
                <div className="photo-placeholder">
                  <img src="/Nourridine_.jpeg" alt="Professor" className="member-image" />
                </div>
              </div>
              <div className="member-info">
                <h3>Dr. Nourridine Siewe</h3>
                <p className="member-role">Project Supervisor & Research Mentor</p>
                <p className="member-affiliation">
                  School of Mathematics and Statistics<br/>
                  Rochester Institute of Technology
                </p>
                <p className="member-bio">
                  Leading researcher in computational biology and mathematical modeling 
                  of biological systems. Specializes in diabetes research and 
                  differential equation applications in medicine.
                </p>
                <div className="member-links">
                  <a href="https://www.linkedin.com/in/nourridine-siewe-56284325/" className="link-btn">🔗 LinkedIn</a>
                  <a href="https://www.rit.edu/directory/nxssma-nourridine-siewe" className="link-btn">🏫 Faculty Page</a>
                  <a href="https://scholar.google.com/citations?user=twyTEFMAAAAJ&hl=en" className="link-btn">📚 Research</a>
                </div>
              </div>
            </div>

            {/* Jatin Jain */}
            <div className="team-member-card">
              <div className="member-photo">
                <div className="photo-placeholder">
                  <img src="/Jatin_.jpeg" alt="Jatin Jain" className="member-image" />
                </div>
              </div>
              <div className="member-info">
                <h3>Jatin Jain</h3>
                <p className="member-role">Lead Developer & Project Manager</p>
                <p className="member-affiliation">
                  BSc Computer Science<br/>
                  Rochester Institute of Technology
                </p>
                <p className="member-bio">
                  Passionate full-stack developer experimenting across domains. Focused on combining 
                  research, mathematics, and healthcare to build impactful, data-driven applications.
                </p>
                <div className="member-links">
                  <a href="https://github.com/itzme170605" className="link-btn">💻 GitHub</a>
                  <a href="https://www.linkedin.com/in/jatin-jain2106/" className="link-btn">💼 LinkedIn</a>
                </div>
              </div>
            </div>

            {/* Mercy Kioko */}
            <div className="team-member-card">
              <div className="member-photo">
                <div className="photo-placeholder">
                  <img src="Mercy_.jpg" alt="Mercy Kioko" className="member-image" />
                </div>
              </div>
              <div className="member-info">
                <h3>Mercy Kioko</h3>
                <p className="member-role">Graduate Research Assistant & Data Analyst</p>
                <p className="member-affiliation">
                  Applied Statistics<br/>
                  Rochester Institute of Technology
                </p>
                <p className="member-bio">
                  Mercy extends the diabetes model framework by formulating new biological equations, 
                  estimating parameters, simulating models, and analyzing sensitivities in metabolic pathways.
                </p>
                <div className="member-links">
                  <a href="https://www.linkedin.com/in/mercy-kioko-b1a22b309" className="link-btn">💼 LinkedIn</a>
                  <a href="mailto:mnk5928@rit.edu" className="link-btn">📧 Email</a>
                </div>
              </div>
            </div>

            {/* Zach Zhao */}
            <div className="team-member-card">
              <div className="member-photo">
                <div className="photo-placeholder">
                  <img src="/Zach_Zhao.jpg" alt="Zach Zhao" className="member-image" />
                </div>
              </div>
              <div className="member-info">
                <h3>Zach Zhao</h3>
                <p className="member-role">Mathematical Modeler</p>
                <p className="member-affiliation">
                  Applied Statistics & Mathematics<br/>
                  Rochester Institute of Technology
                </p>
                <p className="member-bio">
                  Developed mathematical models for agricultural applications. Focuses on translating 
                  research into analytical simulations to support data-driven solutions.
                </p>
                <div className="member-links">
                  <a href="https://www.linkedin.com/in/zzachzhao" className="link-btn">💼 LinkedIn</a>
                  <a href="mailto:zz1769@rit.edu" className="link-btn">📧 Email</a>
                </div>
              </div>
            </div>

            {/* Neha Rajtiya */}
            <div className="team-member-card">
              <div className="member-photo">
                <div className="photo-placeholder">
                  <img src="/api/placeholder/200/200" alt="Neha Rajtiya" className="member-image" />
                </div>
              </div>
              <div className="member-info">
                <h3>Neha Rajtiya</h3>
                <p className="member-role">PhD Student Researcher</p>
                <p className="member-affiliation">
                  --<br/>
                  --
                </p>
                <p className="member-bio">
                  --
                </p>
                <div className="member-links">
                  {/* No links available */}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Research Collaboration and Timeline kept same */}

      <section className="timeline-section">
        <div className="container">
          <h2>Project Timeline</h2>
          <div className="timeline">
            <div className="timeline-item">
              <div className="timeline-marker"></div>
              <div className="timeline-content">
                <h3>Sprint 0: Research & Analysis</h3>
                <p className="timeline-date">Week 1</p>
                <p>Literature review, paper analysis, and requirement gathering</p>
              </div>
            </div>
            <div className="timeline-item">
              <div className="timeline-marker"></div>
              <div className="timeline-content">
                <h3>Sprint 1: Architecture & Foundation</h3>
                <p className="timeline-date">Week 2</p>
                <p>Technology stack selection and project structure design</p>
              </div>
            </div>
            <div className="timeline-item">
              <div className="timeline-marker"></div>
              <div className="timeline-content">
                <h3>Sprint 2: Core Implementation</h3>
                <p className="timeline-date">Week 3-4</p>
                <p>Mathematical model implementation and backend development</p>
              </div>
            </div>
            <div className="timeline-item">
              <div className="timeline-marker"></div>
              <div className="timeline-content">
                <h3>Sprint 3: Frontend & Integration</h3>
                <p className="timeline-date">Week 5-6</p>
                <p>User interface development and system integration</p>
              </div>
            </div>
            <div className="timeline-item">
              <div className="timeline-marker"></div>
              <div className="timeline-content">
                <h3>Sprint 4: Refinement & Validation</h3>
                <p className="timeline-date">Week 7</p>
                <p>Model validation, performance optimization, and documentation</p>
              </div>
            </div>
            <div className="timeline-item current">
              <div className="timeline-marker"></div>
              <div className="timeline-content">
                <h3>Sprint 5: Deployment & Feedback</h3>
                <p className="timeline-date">Week 8+</p>
                <p>Public deployment, feedback collection, and feature enhancements</p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default AboutPage;
