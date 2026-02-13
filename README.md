<h1>SMTP Email Validator</h1>

<p>A Python-based email validation tool that checks whether an email address is syntactically valid and whether the domain can receive emails using DNS and SMTP checks.</p>

<p>This project demonstrates practical email validation beyond simple regex-based checks.</p>

<hr>

<h2>Features</h2>
<ul>
  <li>Validates email format using regular expressions</li>
  <li>Extracts domain and checks DNS MX records</li>
  <li>Attempts SMTP connection to verify mailbox existence</li>
  <li>Provides validation results via terminal output</li>
</ul>

<hr>

<h2>Tech Stack</h2>
<ul>
  <li>Python 3</li>
  <li>smtplib</li>
  <li>dnspython</li>
  <li>re (Regular Expressions)</li>
</ul>

<hr>

<h2>Installation</h2>

<p>Clone the repository:</p>

<pre>
git clone https://github.com/AkshayR278/SMTP-Email-Validator.git
cd SMTP-Email-Validator
</pre>

<p>Install dependencies:</p>

<pre>
pip install dnspython
</pre>

<hr>

<h2>Usage</h2>

<p>Run the script:</p>

<pre>
python main.py
</pre>

<p>Example:</p>

<pre>
Enter email: example@gmail.com
</pre>

<p>The program will return validation results based on syntax, domain, and SMTP checks.</p>

<hr>

<h2>Project Structure</h2>

<pre>
SMTP-Email-Validator/
│
├── main.py
├── README.md
└── requirements.txt
</pre>

<hr>

<h2>Limitations</h2>
<ul>
  <li>SMTP verification may fail due to blocked ports, firewall rules, or anti-spam protections</li>
  <li>Some mail servers use catch-all addresses, which can cause false positives</li>
  <li>This tool does not guarantee that an email belongs to a real person</li>
</ul>

<hr>

<h2>Future Improvements</h2>
<ul>
  <li>Bulk email validation support</li>
  <li>Improved logging and error handling</li>
  <li>Disposable email domain detection</li>
  <li>CLI arguments and packaging as a Python module</li>
</ul>

<hr>

<h2>License</h2>
<p>This project is intended for educational and learning purposes.<br>
Feel free to modify and use it.</p>
