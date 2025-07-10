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
          <h2>Development Team</h2>
          
          <div className="team-grid">
            {/* Professor */}
            <div className="team-member-card featured">
              <div className="member-photo">
                <div className="photo-placeholder">
                  <img src="/api/placeholder/200/200" alt="Professor" className="member-image" />
                </div>
              </div>
              <div className="member-info">
                <h3>Dr. [Professor Name]</h3>
                <p className="member-role">Project Supervisor & Research Mentor</p>
                <p className="member-affiliation">
                  Department of [Department]<br/>
                  [University Name]
                </p>
                <p className="member-bio">
                  Leading researcher in computational biology and mathematical modeling 
                  of biological systems. Specializes in diabetes research and 
                  differential equation applications in medicine.
                </p>
                <div className="member-links">
                  <a href="#" className="link-btn">📧 Email</a>
                  <a href="#" className="link-btn">🏫 Faculty Page</a>
                  <a href="#" className="link-btn">📚 Research</a>
                </div>
              </div>
            </div>

            {/* Student Developer */}
            <div className="team-member-card">
              <div className="member-photo">
                <div className="photo-placeholder">
                  <img src="/api/placeholder/200/200" alt="Jatin" className="member-image" />
                </div>
              </div>
              <div className="member-info">
                <h3>Jatin Zain</h3>
                <p className="member-role">Lead Developer & Project Manager</p>
                <p className="member-affiliation">
                  Computer Science Student<br/>
                  [University Name]
                </p>
                <p className="member-bio">
                  Full-stack developer with expertise in React, Python, and scientific computing. 
                  Passionate about applying technology to solve healthcare challenges and 
                  making complex medical research accessible through interactive applications.
                </p>
                <div className="member-links">
                  <a href="https://github.com/itzme170605" className="link-btn">💻 GitHub</a>
                  <a href="https://linkedin.com/in/jatin-zain" className="link-btn">💼 LinkedIn</a>
                  <a href="#" className="link-btn">📧 Email</a>
                </div>
              </div>
            </div>

            {/* Team Member 2 */}
            <div className="team-member-card">
              <div className="member-photo">
                <div className="photo-placeholder">
                  <img src="/api/placeholder/200/200" alt="Team Member" className="member-image" />
                </div>
              </div>
              <div className="member-info">
                <h3>[Team Member Name]</h3>
                <p className="member-role">Research Assistant & Data Analyst</p>
                <p className="member-affiliation">
                  [Department/Program]<br/>
                  [University Name]
                </p>
                <p className="member-bio">
                  Specializes in data analysis and validation of mathematical models. 
                  Contributed to parameter estimation and clinical validation of 
                  the diabetes simulation model.
                </p>
                <div className="member-links">
                  <a href="#" className="link-btn">🔬 Research Project</a>
                  <a href="#" className="link-btn">💼 LinkedIn</a>
                  <a href="#" className="link-btn">📧 Email</a>
                </div>
              </div>
            </div>

            {/* Team Member 3 */}
            <div className="team-member-card">
              <div className="member-photo">
                <div className="photo-placeholder">
                  <img src="/api/placeholder/200/200" alt="Team Member" className="member-image" />
                </div>
              </div>
              <div className="member-info">
                <h3>[Team Member Name]</h3>
                <p className="member-role">UI/UX Designer & Frontend Developer</p>
                <p className="member-affiliation">
                  [Department/Program]<br/>
                  [University Name]
                </p>
                <p className="member-bio">
                  Focuses on user experience design and medical interface development. 
                  Responsible for creating intuitive visualizations and ensuring 
                  the application meets healthcare professional needs.
                </p>
                <div className="member-links">
                  <a href="#" className="link-btn">🎨 Portfolio</a>
                  <a href="#" className="link-btn">💼 LinkedIn</a>
                  <a href="#" className="link-btn">📧 Email</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Research Collaboration */}
      <section className="collaboration-section">
        <div className="container">
          <h2>Research Collaboration</h2>
          <div className="collaboration-content">
            <div className="collaboration-text">
              <h3>Building on Academic Excellence</h3>
              <p>
                This project is built upon the foundational research by 
                <strong> Dr. Nourridine Siewe</strong> and <strong>Dr. Avner Friedman</strong>, 
                whose mathematical model provides the scientific backbone for our interactive simulation.
              </p>
              <p>
                Our team has worked to translate complex mathematical concepts into 
                an accessible, user-friendly application that serves both educational 
                and research purposes in the diabetes community.
              </p>
              
              <div className="collaboration-highlights">
                <div className="highlight-item">
                  <div className="highlight-icon">🔬</div>
                  <h4>Scientific Rigor</h4>
                  <p>Faithful implementation of peer-reviewed research</p>
                </div>
                <div className="highlight-item">
                  <div className="highlight-icon">💻</div>
                  <h4>Technical Innovation</h4>
                  <p>Modern web technologies for interactive simulation</p>
                </div>
                <div className="highlight-item">
                  <div className="highlight-icon">🏥</div>
                  <h4>Clinical Relevance</h4>
                  <p>Practical applications for healthcare professionals</p>
                </div>
              </div>
            </div>
            
            <div className="collaboration-visual">
              <div className="collaboration-diagram">
                <div className="diagram-node research">
                  <div className="node-icon">📄</div>
                  <div className="node-label">Research Paper</div>
                </div>
                <div className="diagram-arrow">→</div>
                <div className="diagram-node implementation">
                  <div className="node-icon">⚙️</div>
                  <div className="node-label">Mathematical Model</div>
                </div>
                <div className="diagram-arrow">→</div>
                <div className="diagram-node application">
                  <div className="node-icon">🖥️</div>
                  <div className="node-label">Web Application</div>
                </div>
                <div className="diagram-arrow">→</div>
                <div className="diagram-node impact">
                  <div className="node-icon">🌍</div>
                  <div className="node-label">Community Impact</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Project Timeline */}
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
            <div className="timeline-item current">
              <div className="timeline-marker"></div>
              <div className="timeline-content">
                <h3>Sprint 4: Refinement & Validation</h3>
                <p className="timeline-date">Week 7</p>
                <p>Model validation, performance optimization, and documentation</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Technology Stack */}
      <section className="tech-section">
        <div className="container">
          <h2>Technology Stack</h2>
          <div className="tech-grid">
            <div className="tech-category">
              <h3>Backend</h3>
              <div className="tech-items">
                <div className="tech-item">
                  <div className="tech-icon">🐍</div>
                  <span>Python</span>
                </div>
                <div className="tech-item">
                  <div className="tech-icon">⚡</div>
                  <span>FastAPI</span>
                </div>
                <div className="tech-item">
                  <div className="tech-icon">🧮</div>
                  <span>NumPy/SciPy</span>
                </div>
                <div className="tech-item">
                  <div className="tech-icon">📊</div>
                  <span>Matplotlib</span>
                </div>
              </div>
            </div>
            
            <div className="tech-category">
              <h3>Frontend</h3>
              <div className="tech-items">
                <div className="tech-item">
                  <div className="tech-icon">⚛️</div>
                  <span>React</span>
                </div>
                <div className="tech-item">
                  <div className="tech-icon">📘</div>
                  <span>TypeScript</span>
                </div>
                <div className="tech-item">
                  <div className="tech-icon">📈</div>
                  <span>Plotly.js</span>
                </div>
                <div className="tech-item">
                  <div className="tech-icon">🎨</div>
                  <span>CSS3</span>
                </div>
              </div>
            </div>
            
            <div className="tech-category">
              <h3>Tools & Deployment</h3>
              <div className="tech-items">
                <div className="tech-item">
                  <div className="tech-icon">🐙</div>
                  <span>Git/GitHub</span>
                </div>
                <div className="tech-item">
                  <div className="tech-icon">🔧</div>
                  <span>Node.js</span>
                </div>
                <div className="tech-item">
                  <div className="tech-icon">📦</div>
                  <span>Docker</span>
                </div>
                <div className="tech-item">
                  <div className="tech-icon">☁️</div>
                  <span>Cloud Ready</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Contact Section */}
      <section className="contact-section">
        <div className="container">
          <h2>Get in Touch</h2>
          <div className="contact-content">
            <div className="contact-text">
              <h3>Questions or Feedback?</h3>
              <p>
                We'd love to hear from you! Whether you're a healthcare professional, 
                researcher, or student interested in diabetes modeling, feel free to reach out.
              </p>
              <div className="contact-methods">
                <div className="contact-method">
                  <div className="method-icon">📧</div>
                  <div className="method-info">
                    <h4>Email</h4>
                    <p>diabetesscope@university.edu</p>
                  </div>
                </div>
                <div className="contact-method">
                  <div className="method-icon">🏫</div>
                  <div className="method-info">
                    <h4>Institution</h4>
                    <p>[University Name]<br/>[Department]</p>
                  </div>
                </div>
                <div className="contact-method">
                  <div className="method-icon">💻</div>
                  <div className="method-info">
                    <h4>GitHub</h4>
                    <p>github.com/itzme170605/diabetes-prediction-app</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="contact-form">
              <h3>Send us a message</h3>
              <form className="feedback-form">
                <div className="form-group">
                  <label>Name</label>
                  <input type="text" placeholder="Your name" />
                </div>
                <div className="form-group">
                  <label>Email</label>
                  <input type="email" placeholder="Your email" />
                </div>
                <div className="form-group">
                  <label>Subject</label>
                  <select>
                    <option>General Inquiry</option>
                    <option>Research Collaboration</option>
                    <option>Technical Support</option>
                    <option>Feature Request</option>
                  </select>
                </div>
                <div className="form-group">
                  <label>Message</label>
                  <textarea placeholder="Your message" rows={5}></textarea>
                </div>
                <button type="submit" className="btn-primary">Send Message</button>
              </form>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default AboutPage;