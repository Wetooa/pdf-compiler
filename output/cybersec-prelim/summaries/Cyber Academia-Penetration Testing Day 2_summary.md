# Learning Guide: Cyber Academia-Penetration Testing Day 2.pdf


*Generated on 2026-03-12 19:55:38*


*This is a simplified learning guide created from the original PDF. Use this for studying instead of reading the lengthy original text.*


---


## Pages 1-20


Here's a simplified, easy-to-read learning guide based on the provided text, designed for efficient study.

---

## Penetration Testing: Learning Guide

This guide condenses essential information about penetration testing, focusing on core concepts and practical steps.

---

### 1. Introduction to Penetration Testing

**Curriculum Overview:**
*   **Introduction:** Overview, Purpose, Importance, Types, Legal/Ethical considerations.
*   **Standards:** Overview, OWASP Top 10, Assessment techniques.
*   **Tools:** Overview, Common tools, Installation/Configuration.
*   **Phases:** Pre-engagement, Information Gathering, Vulnerability Analysis, Exploitation, Post-Exploitation, Reporting.

---

### 2. Penetration Testing Phases Overview

A penetration test (pentest) follows a structured approach, typically comprising these phases:

1.  **Pre-engagement Interactions:** Defining scope, rules, and logistics.
2.  **Information Gathering:** Collecting data about the target.
3.  **Vulnerability Analysis:** Identifying weaknesses.
4.  **Exploitation:** Gaining access using vulnerabilities.
5.  **Post-Exploitation:** Maintaining access and escalating privileges.
6.  **Reporting:** Documenting findings and recommendations.

---

### 3. Phase 1: Pre-Engagement Interactions

This initial phase sets the foundation for the entire penetration test.

**Key Activities:**
*   **Scoping:** Defining what will be tested.
*   **Establishing Lines of Communication:** Setting up contact methods.
*   **Rules of Communication:** Defining how and when to communicate.

#### 3.1. Scoping

**Importance of Scoping:**
*   **Crucial:** Arguably the most important component of a pentest.
*   **Focuses Assessment:** Ensures efficient testing on target systems.
*   **Avoids Disruption:** Allows the organization to prepare, minimizing downtime.
*   **Ensures Compliance:** Helps meet regulatory obligations and maintain security.
*   **Maximizes Resources:** Optimizes use of time, personnel, and budget.
*   **Facilitates Communication:** Prevents "scope creep" (testing expanding beyond initial objectives).

**Scoping Process:**
1.  **Set a Scoping Meeting:** Discuss initial requirements.
2.  **Send Scoping Questionnaire:** Gather detailed client needs.
3.  **Generate a Pentest Information Sheet:** Document final agreed-upon details.

**Scoping Questionnaires:**
*   **Purpose:** To understand client needs and properly estimate the scope.
*   **Variation:** Questions differ based on the type of application/system tested.
*   **Examples for Network Pentest:**
    *   Total IP addresses to be tested?
    *   Internal IP addresses?
    *   External IP addresses?
*   **Examples for Web Pentest:**
    *   Number of web applications?
    *   Approximate static pages?
    *   Approximate dynamic pages?
    *   Number of user roles?

**Pentest Information Sheet (Key Contents):**
*   **Target(s) to be tested:** Specific systems, applications, or networks.
*   **Schedule of the test:** Start and end dates.
*   **Test Credentials:** Any necessary login details.
*   **Specific Instructions:** How to access the application, important notes, reminders.
*   **Security Test Cases:** (If applicable) specific scenarios to test.

**What to Consider When Defining Scope:**
*   **System Types:** On-premise vs. cloud environments.
*   **Existing Defenses:** Security controls, gaps, vulnerabilities, attack responses, current security posture.
*   **Configurations:** System, network, and device settings.
*   **Tolerance Levels:** How systems, networks, and devices react to attacks.
*   **Attack Sophistication:** Depth and breadth of the attack.
*   **Risk Landscape:** Overall environment where a threat actor might gain access.

#### 3.2. Rules of Engagement (RoE)

The RoE defines the terms and conditions of the pentest.

**Key Elements of a Written Agreement (Signed by both parties):**
*   **Testing Methods & Techniques:** Specific approaches allowed.
*   **Scope & Limitations:** Explicitly states what is included and excluded.
*   **Testing Restrictions:** Prohibited actions or targets.
*   **Access Level:** How much access the testing team has to systems and data.
*   **Communication & Escalation:** Procedures for issues or incidents.
*   **Confidentiality & Data Protection:** Requirements for handling sensitive information.
*   **Roles & Responsibilities:** Clearly defines duties for both the testing team and the client organization.
*   **Specifics:** Client contact details, sensitive data handling, client IT team notifications, status meeting schedules, and reports.

---

### 4. Phase 2: Information Gathering

This phase is about collecting data to build a comprehensive picture of the target.

**Definition:**
*   The phase where publicly-available or internal information about the target is collected.

**Purpose & Benefits:**
*   **Identify Attack Vectors:** Helps pinpoint potential entry points for an attack.
*   **Assess Security Posture:** Provides insights into the target's overall security status.
*   **Collect Intelligence:** Gathers valuable data to inform subsequent testing phases.

---


---


## Pages 19-27


## Learning Guide: Information Gathering

This guide simplifies the process of **Information Gathering**, a crucial phase in penetration testing.

---

### 1. Information Gathering - Overview

**What it is:**
*   The initial phase of a penetration test (pentest) where information about the target is collected.
*   Information can be publicly available or internally sourced.

**Why it's important (Purpose):**
*   **Identify potential attack vectors:** Discover ways to exploit the target.
*   **Assess security posture:** Understand the target's current security strengths and weaknesses.
*   **Collect valuable intelligence:** Gather actionable data to plan further testing.

---

### 2. Open-Source Intelligence (OSINT)

**What it is:**
*   A specific method of intelligence collection.
*   Involves finding, selecting, and acquiring information **solely from publicly available sources**.
*   This collected information is then analyzed to produce **actionable intelligence**.

---

### 3. Key Information Gathered (Typical Output)

During information gathering, testers aim to collect details such as:

*   **Services running on target servers:** What applications or functions are active.
*   **Technology stack used:** Programming languages, frameworks, web servers, databases (e.g., Apache, Nginx, PHP, .NET).
*   **Important functionalities / Use cases:** Key features or purposes of the target system/application.
*   **Protection mechanisms in place:** Firewalls, WAFs (Web Application Firewalls), intrusion detection systems, etc.

---

### 4. Practical Examples & Tools

Information gathering often uses specialized tools to collect and display data. Here are examples of common outputs:

*   **Shodan.io (Search Engine for Internet-Connected Devices)**
    *   **Purpose:** Discover devices, services, and open ports connected to the internet.
    *   **Output Example:**
        *   **SSL Certificate details:** Common Name (e.g., `example.pl`), Organization, Issuer, supported SSL/TLS versions (e.g., `TLSv1`). This indicates web server configuration and ownership.
        *   **Open Ports:** Lists services running on specific ports (e.g., `HTTPS (8443)`, `HTTP (8080)`).
        *   **Geographical location:** Where the server is hosted.
    *   **What it reveals:** Running services, server technologies, potential entry points, and organizational details.

*   **Nmap (Network Mapper)**
    *   **Purpose:** A powerful open-source tool for network discovery and security auditing. It's primarily used for port scanning.
    *   **Output Example:**
        *   **Host status:** `Host is up`.
        *   **Open ports:** Lists ports found to be `open` along with their associated `SERVICE` (e.g., `80/tcp open http`, `443/tcp open https`, `22/tcp open ssh`).
        *   **Filtered ports:** Ports where Nmap couldn't determine the state due to a firewall.
    *   **What it reveals:** Which services are actively listening on a server, indicating potential attack surfaces.

*   **Burp Suite (Web Application Security Testing Tool)**
    *   **Purpose:** Used to intercept, inspect, and modify web traffic between a browser and a web server.
    *   **Output Example (HTTP History):**
        *   Shows a list of all HTTP requests and responses made by the browser.
        *   **Request details:** For example, a `GET /robots.txt HTTP/1.1` request.
        *   **`robots.txt`:** A file that website owners use to instruct web robots (like search engine crawlers) which pages or files on their site *not* to crawl. Attackers often check this file as it can inadvertently reveal sensitive directories or files that the website owner intended to hide.
    *   **What it reveals:** Details about the web application's structure, hidden directories, specific files, and how it communicates.


---
