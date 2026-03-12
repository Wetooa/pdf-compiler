# Learning Guide: Cyber Academia-Penetration Testing Day 3.pdf


*Generated on 2026-03-12 19:57:24*


*This is a simplified learning guide created from the original PDF. Use this for studying instead of reading the lengthy original text.*


---


## Pages 1-20


Here is a simplified, easy-to-read learning guide based on the provided text:

---

# Cybersecurity Academia: Penetration Testing Learning Guide

## 1. Introduction to Penetration Testing

### 1.1 Curriculum Overview
This guide covers:
*   Overview, Purpose, Importance, and Types of Penetration Testing
*   Legal and Ethical Considerations
*   Penetration Testing Tools (Common tools, Installation, Configuration)
*   Penetration Testing Phases (Pre-engagement to Reporting)
*   Penetration Testing Standards (OWASP Top 10, Technical Assessment Techniques)

### 1.2 What is Penetration Testing (Pentesting)?
Penetration Testing is a simulated cyberattack against your computer system to check for exploitable vulnerabilities.

### 1.3 Phases of a Pentest Engagement
A penetration test typically follows these phases:
1.  **Pre-engagement Interactions:** Planning and defining scope.
2.  **Information Gathering:** Collecting data about the target.
3.  **Vulnerability Analysis:** Identifying potential weaknesses.
4.  **Exploitation:** Gaining access using identified vulnerabilities.
5.  **Post-Exploitation:** Maintaining access, escalating privileges, data exfiltration.
6.  **Reporting:** Documenting findings and recommendations.

---

## 2. Phase 3: Vulnerability Analysis

### 2.1 What is Vulnerability Scanning?
Vulnerability scanning uses automated tools to check a target system or application against a list of known vulnerabilities. Its purpose is to identify potential security weaknesses.

*   Can be a standalone assessment or part of continuous monitoring.

### 2.2 How a Vulnerability Scanner Works
Scanners identify vulnerabilities by:
*   **Application Spidering/Crawling:** Exploring the application's structure.
*   **Discovery of Default/Common Content:** Finding publicly accessible or misconfigured files.
*   **Probing for Common Vulnerabilities:** Sending specific requests to test for known flaws.

### 2.3 Types of Scans
*   **Passive Scan:** Non-intrusive checks, observing the target to determine vulnerabilities without direct interaction.
*   **Active Scan:** Simulated attacks on the target to assess vulnerabilities as an outsider would.

### 2.4 Web Application Security Testing
This focuses specifically on evaluating the security of a web application. It involves actively analyzing the application for weaknesses, technical flaws, or vulnerabilities.

### 2.5 Vulnerability Scanning Output
Scanners generate reports detailing detected vulnerabilities, often including severity and potential remediation steps.

---

## 3. OWASP Web Application Security Testing Methodology

### 3.1 Approach
The OWASP methodology often uses a **black box approach**, where the tester has little to no prior information about the application being tested.

### 3.2 Testing Model
*   **Tester:** The individual performing the testing activities.
*   **Tools & Methodology:** The techniques and instruments used for testing.
*   **Application:** The target system being tested (the "black box").

### 3.3 Types of OWASP Testing

#### 3.3.1 Passive Testing
*   **Goal:** Understand the application's logic and explore it as a user would.
*   **Activities:** Use tools for information gathering.
*   **Outcome:** General understanding of system access points and functionality.

#### 3.3.2 Active Testing
*   **Goal:** In-depth testing using specific methodologies to find vulnerabilities.
*   **Categories (12 areas):**
    1.  Information Gathering
    2.  Configuration and Deployment Management Testing
    3.  Identity Management Testing
    4.  Authentication Testing
    5.  Authorization Testing
    6.  Session Management Testing
    7.  Input Validation Testing
    8.  Error Handling
    9.  Cryptography
    10. Business Logic Testing
    11. Client-side Testing
    12. API Testing

---

## 4. Active Testing Categories: Detailed Activities

### 4.1 Information Gathering
*   **Search Engine Discovery Reconnaissance:** Identify sensitive design/configuration info exposed via search engines or third parties.
*   **Fingerprint Web Server:** Determine web server type and version to find known vulnerabilities.
*   **Review Webserver Metafiles:** Analyze metadata (e.g., `robots.txt`) for hidden paths and functionality.
*   **Enumerate Applications on Webserver:** List all applications within scope on the server.
*   **Review Webpage Content:** Check comments, metadata, and JavaScript code for information leakage or debug files.
*   **Identify Application Entry Points:** Analyze requests/responses to find potential injection points.
*   **Map Execution Paths:** Understand application workflows.
*   **Fingerprint Web Application Framework:** Identify the components used by web applications.
*   **Map Application Architecture:** Create a map of the application based on research.

### 4.2 Configuration and Deployment Management Testing
*   **Test Network Infrastructure Configuration:** Review network configurations for vulnerabilities, unmaintained software, or default settings/credentials.
*   **Test Application Platform Configuration:** Ensure defaults and known files are removed, no debugging code is left in production, and logging mechanisms are secure.
*   **Review Old Backup and Unreferenced Files:** Find and analyze unreferenced files that might contain sensitive information.
*   **Test File Extensions Handling:** "Dirbust" (directory brute-force) sensitive file extensions (e.g., scripts, raw data) to find raw data or credentials.
*   **Enumerate Infrastructure and Application Admin Interfaces:** Identify hidden administrator interfaces and functionality.
*   **Test HTTP Strict Transport Security (HSTS):** Review the HSTS header and its validity.
*   **Test File Permission:** Identify rogue file permissions.
*   **Test Cloud Storage:** Assess access control configuration for storage services.
*   **Test HTTP Methods:** Enumerate supported HTTP methods, test for access control bypass, XSS, and HTTP method overriding.
*   **Test RIA Cross Domain Policy:** Review and validate policy files.
*   **Test for Subdomain Takeover:** Enumerate domains to find forgotten or misconfigured ones susceptible to takeover.

### 4.3 Identity Management Testing
*   **Test Role Definitions:** Identify and document application roles, attempt to switch or access other roles, and review permission granularity.
*   **Test User Registration Process:** Verify identity requirements align with business/security and validate the registration process.
*   **Test Account Provisioning Process:** Verify which accounts can provision other accounts and their types.
*   **Testing for Account Enumeration and Guessable User Account:** Review user identification processes (registration, login) and enumerate users through response analysis.
*   **Testing for Weak or Unenforced Username Policy:** Determine if consistent account name structures or error messages allow account enumeration.

### 4.4 Authentication Testing
*   **Testing for Credentials Transported over an Encrypted Channel:** Assess if credentials are exchanged without encryption in any use case.
*   **Testing for Default Credentials:** Enumerate applications for default credentials and check if new accounts are created with defaults or identifiable patterns.
*   **Testing for Weak Lock Out Mechanism:** Evaluate the account lockout mechanism's resistance to brute-force password guessing and unauthorized unlocking.
*   **Testing for Bypassing Authentication Schema:** Ensure authentication is applied across all services that require it.
*   **Testing for Vulnerable Remember Password:** Validate that "remember me" functions manage sessions securely and don't endanger user credentials.
*   **Testing for Browser Cache Weaknesses:** Review if the application stores sensitive information client-side or allows access without authorization through cached data.

---


---


## Pages 19-38


Here is a simplified, easy-to-read learning guide derived from the provided text (Pages 19-38), focusing on essential information for study.

---

## Active Testing Learning Guide

This guide outlines key tests performed during active penetration testing, categorized by the area of focus.

---

### 1. Identity Management Testing

Focuses on how identities are managed and authenticated within an application.

*   **Test Role Definitions:**
    *   Identify and document application roles.
    *   Attempt to switch, change, or access other roles.
    *   Review role granularity and permission needs.
*   **Test User Registration Process:**
    *   Verify identity requirements align with business and security needs.
    *   Validate the overall registration flow.
*   **Test Account Provisioning Process:**
    *   Verify which accounts can create other accounts and of what type.
*   **Test for Account Enumeration & Guessable User Accounts:**
    *   Review processes involving user identification (e.g., registration, login).
    *   Enumerate users by analyzing application responses.
*   **Test for Weak or Unenforced Username Policy:**
    *   Determine if a consistent account name structure allows account enumeration.
    *   Determine if error messages permit account enumeration.

---

### 2. Authentication Testing

Focuses on how users prove their identity and the security of that process.

*   **Test for Credentials Transported over Encrypted Channels:**
    *   Assess if any use case causes credentials to be exchanged without encryption.
*   **Test for Default Credentials:**
    *   Enumerate applications for default credentials and validate if they still exist.
    *   Review new user accounts for default passwords or patterns.
*   **Test for Weak Lockout Mechanism:**
    *   Evaluate its ability to prevent brute-force password guessing.
    *   Evaluate the unlock mechanism's resistance to unauthorized unlocking.
*   **Test for Bypassing Authentication Schema:**
    *   Ensure authentication is applied across all services requiring it.
*   **Test for Vulnerable "Remember Password" Functionality:**
    *   Validate that generated sessions are securely managed and don't expose user credentials.
*   **Test for Browser Cache Weaknesses:**
    *   Review if the application stores sensitive information client-side.
    *   Review if cached information allows access without authorization.
*   **Test for Weak Password Policy:**
    *   Determine resistance to brute-force attacks by evaluating password length, complexity, reuse, and aging requirements.
*   **Test for Weak Security Question Answers:**
    *   Determine question complexity and how straightforward they are.
    *   Assess possible user answers and brute-force capabilities.
*   **Test for Weak Password Change or Reset Functionalities:**
    *   Determine resistance to subversion that allows changing an account's password.
    *   Determine resistance of reset functionality against guessing or bypassing.
*   **Test for Weaker Authentication in Alternative Channels:**
    *   Identify alternative authentication channels.
    *   Assess their security measures and potential bypasses.

---

### 3. Authorization Testing

Focuses on what authenticated users are allowed to do.

*   **Test Directory Traversal / File Include:**
    *   Identify path traversal injection points.
    *   Assess bypass techniques and the extent of traversal possible.
*   **Test for Bypassing Authorization Schema:**
    *   Assess if horizontal (accessing another user's data) or vertical (privilege escalation) access is possible.
*   **Test for Privilege Escalation:**
    *   Identify injection points related to privilege manipulation.
    *   Fuzz (send unexpected inputs) or attempt to bypass security measures.
*   **Test for Insecure Direct Object References (IDOR):**
    *   Identify points where object references (e.g., IDs in URLs) occur.
    *   Assess access control measures for IDOR vulnerability.

---

### 4. Session Management Testing

Focuses on how user sessions are established, maintained, and terminated.

*   **Test for Session Management Schema:**
    *   Gather session tokens for the same and different users.
    *   Analyze token randomness to prevent session forging.
    *   Modify unsigned cookies containing manipulable information.
*   **Test for Cookie Attributes:**
    *   Ensure proper security configuration (e.g., HttpOnly, Secure flags) for cookies.
*   **Test for Session Fixation:**
    *   Analyze the authentication mechanism and flow.
    *   Force specific cookies and assess impact.
*   **Test for Exposed Session Variables:**
    *   Ensure proper encryption is implemented.
    *   Review caching configuration.
    *   Assess the security of channels and methods used.
*   **Test for Cross-Site Request Forgery (CSRF):**
    *   Determine if requests can be initiated on a user's behalf without their knowledge.
*   **Test Logout Functionality:**
    *   Assess the logout user interface.
    *   Analyze session timeout and if the session is properly terminated after logout.
*   **Test Session Timeout:**
    *   Validate that a hard session timeout exists.
*   **Test for Session Hijacking:**
    *   Identify vulnerable session cookies.
    *   Attempt to hijack vulnerable cookies and assess risk.
*   **Test for Session Puzzling:**
    *   Identify all session variables.
    *   Attempt to break the logical flow of session generation.

---

### 5. Input Validation Testing

Focuses on how the application handles user-supplied data.

*   **Test for Reflected Cross-Site Scripting (XSS):**
    *   Identify variables reflected in responses.
    *   Assess accepted input and encoding applied on return.
*   **Test for Stored Cross-Site Scripting (XSS):**
    *   Identify stored input reflected client-side.
    *   Assess accepted input and encoding applied on return.
*   **Test for HTTP Parameter Pollution (HPP):**
    *   Identify backend and parsing methods.
    *   Assess injection points and try bypassing input filters using HPP.
*   **Test for SQL Injection:**
    *   Identify SQL injection points.
    *   Assess severity and achievable access level.
*   **Test for LDAP Injection:**
    *   Identify LDAP injection points.
    *   Assess severity.
*   **Test for XML Injection:**
    *   Identify XML injection points.
    *   Assess types and severities of possible exploits.
*   **Test for SSI Injection:**
    *   Identify SSI (Server-Side Include) injection points.
    *   Assess severity.
*   **Test for XPath Injection:**
    *   Identify XPath injection points.
*   **Test for IMAP/SMTP Injection:**
    *   Identify IMAP/SMTP injection points.
    *   Understand data flow and system deployment.
    *   Assess injection impacts.
*   **Test for Code Injection:**
    *   Identify points where code can be injected into the application.
    *   Assess injection severity.
*   **Test for Command Injection:**
    *   Identify and assess command injection points.
*   **Test for Format String Injection:**
    *   Assess if injecting format string specifiers into user-controlled fields causes undesired application behavior.
*   **Test for Incubated Vulnerability:**
    *   Identify stored injections that require a separate recall step.
    *   Understand how recall occurs and activate it if possible.
*   **Test for HTTP Splitting / Smuggling:**
    *   Assess vulnerability to splitting (identifying possible attacks).
    *   Assess vulnerability of communication chain to smuggling (identifying possible attacks).
*   **Test for HTTP Incoming Requests:**
    *   Monitor all incoming/outgoing HTTP requests to the web server for suspicious activity.
*   **Test for Host Header Injection:**
    *   Assess if the Host header is dynamically parsed.
    *   Attempt to bypass security controls relying on the header.
*   **Test for Server-Side Template Injection (SSTI):**
    *   Detect template injection vulnerability points.
    *   Identify the templating engine.
    *   Build an exploit.
*   **Test for Server-Side Request Forgery (SSRF):**
    *   Identify SSRF injection points.
    *   Test if points are exploitable.
    *   Assess vulnerability severity.

---

### 6. Testing for Weak Cryptography

Focuses on the strength and proper implementation of encryption.

*   **Test for Weak Transport Layer Security (TLS):**
    *   Validate service configuration.
    *   Review digital certificate cryptographic strength and validity.
    *   Ensure TLS security is not bypassable and properly implemented.
*   **Test for Padding Oracle:**
    *   Identify encrypted messages relying on padding.
    *   Attempt to break padding and analyze error messages.
*   **Test for Sensitive Information Sent via Unencrypted Channels:**
    *   Identify sensitive data transmitted through various channels.
    *   Assess privacy and security of these channels.
*   **Test for Weak Encryption:**
    *   Identify weak encryption or hashing uses and implementations.

---

### 7. Business Logic Testing

Focuses on flaws in the application's unique business rules and workflows.

*   **Test Business Logic Data Validation:**
    *   Identify data injection points.
    *   Validate all checks occur backend and cannot be bypassed.
    *   Attempt to break expected data formats and analyze handling.
*   **Test Ability to Forge Requests:**
    *   Review documentation for guessable, predictable, or hidden fields.
    *   Insert logically valid data to bypass normal business logic workflow.
*   **Test Integrity Checks:**
    *   Review documentation for components handling data.
    *   Determine logically acceptable data types and who should modify/read data.
    *   Attempt to insert, update, or delete data values that should be restricted.
*   **Test for Process Timing:**
    *   Review documentation for time-sensitive functionality.
    *   Develop and execute misuse cases related to timing.
*   **Test Number of Times a Function Can Be Used Without Limits:**
    *   Identify functions that should have usage limits.
    *   Assess if a logical limit is set and properly validated.
*   **Test for the Circumvention of Workflows:**
    *   Review documentation for ways to skip or reorder steps in the application process.
    *   Develop misuse cases to circumvent identified logic flows.
*   **Test Defenses Against Application Misuse:**
    *   Review results from all tests where aggressive input led to different functionality.
    *   Understand existing defenses and verify their effectiveness against bypass techniques.
*   **Test Upload of Unexpected File Types:**
    *   Review documentation for rejected file types.
    *   Verify unwelcome file types are safely rejected.
    *   Verify batch uploads are secure and prevent bypasses.
*   **Test Upload of Malicious Files:**
    *   Identify file upload functionality.
    *   Review documentation for acceptable vs. dangerous file types.
    *   Obtain/create malicious files and attempt to upload/process them.

---

### 8. Client-Side Testing

Focuses on vulnerabilities within the client-side code (e.g., JavaScript, HTML, CSS).

*   **Test for DOM-Based Cross-Site Scripting (XSS):**
    *   Identify DOM sinks (points where data is written to the DOM).
    *   Build payloads for each sink type.
*   **Test for JavaScript Execution:**
    *   Identify sinks and possible JavaScript injection points.
*   **Test for HTML Injection:**
    *   Identify HTML injection points and assess severity of injected content.
*   **Test for Client-Side URL Redirect:**
    *   Identify injection points handling URLs or paths.
    *   Assess target redirection locations.
*   **Test for CSS Injection:**
    *   Identify CSS Injection points.
    *   Assess the impact of injection.
*   **Test for Client-Side Resource Manipulation:**
    *   Identify sinks with weak input validation.
    *   Assess the impact of resource manipulation.
*   **Test Cross-Origin Resource Sharing (CORS):**
    *   Identify endpoints implementing CORS.
    *   Ensure CORS configuration is secure or harmless.
*   **Test for Cross-Site Flashing:**
    *   Decompile and analyze application code.
    *   Assess sink inputs and unsafe method usages in Flash.
*   **Test for Clickjacking:**
    *   Understand security measures in place (e.g., X-Frame-Options).
    *   Assess strictness and bypassability of measures.
*   **Test Web Sockets:**
    *   Identify Web Socket usage.
    *   Assess implementation using similar tests as on normal HTTP channels.
*   **Test Web Messaging:**
    *   Assess the security of message origin.
    *   Validate use of safe methods and input validation.
*   **Test Browser Storage:**
    *   Determine if sensitive data is stored client-side (e.g., localStorage, sessionStorage).
    *   Examine handling of storage objects for injection attacks (invalidated input, vulnerable libraries).
*   **Test Cloud Storage:**
    *   Locate sensitive data across the system.
    *   Assess potential leakage through various techniques.

---

### 9. Error Handling & API Testing

Focuses on how the application handles errors and the security of APIs.

*   **Testing for Improper Error Handling:**
    *   Identify existing error output.
    *   Analyze different error messages returned for information leakage.
*   **Testing GraphQL APIs:**
    *   Assess deployment for secure, production-ready configuration.
    *   Validate all input fields against generic attacks.
    *   Ensure proper access controls are applied.

---

## Phase 4: Exploitation

This phase occurs **after** vulnerabilities have been identified.

### Purpose:
*   Attempt to **access the target system** and **exploit identified vulnerabilities**.
*   Simulate a real-world attack using specific tools.
*   Identify the main entry point to target high-value assets.

### Key Principle:
*   Attacks **must be based on the scenario within the scope** of the engagement.

### Common Attacks Against Web Applications (Examples):
*   **SQL Injection:** Extract sensitive information.
*   **Cross-site Scripting (XSS):** Run malicious scripts in the user's browser.
*   **Code Injection:** Run malicious code on the server.
*   **Session Hijacking:** Gain unauthorized access to a user's session.
*   **Directory Traversal:** Retrieve sensitive files from the server.

### Things to Remember in Exploitation:

1.  **Not all exploits work on all systems:**
    *   Testers must be familiar with different exploit types for specific targets.
2.  **Some exploits are more effective than others:**
    *   Choose the most appropriate exploit for the situation (e.g., XSS for a web app, not Buffer Overflow).
3.  **Some exploits require more setup than others:**
    *   Be aware of prerequisites (e.g., changing firewall rules) before attempting.
4.  **Not all identified vulnerabilities can be exploited:**
    *   Understand vulnerability types and their potential impact (e.g., some allow only reading common files, others allow code execution).

---


---
