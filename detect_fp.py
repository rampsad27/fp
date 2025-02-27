import requests
from bs4 import BeautifulSoup
import re
import tkinter as tk
from tkinter import ttk, scrolledtext
import hashlib

fingerprinting_patterns = [
    re.compile(r"var np = navigator\.platform;", re.IGNORECASE),
    re.compile(r"var nv = navigator\.vendor;", re.IGNORECASE),
    re.compile(r"var cd = window\.screen\.colorDepth;", re.IGNORECASE),
    re.compile(r"var dpr = window\.devicePixelRatio;", re.IGNORECASE),
    re.compile(r"var cpu = navigator\.cpuClass;", re.IGNORECASE),
    re.compile(r"var hc = navigator\.hardwareConcurrency;", re.IGNORECASE),
    re.compile(r"var dm = navigator\.deviceMemory;", re.IGNORECASE),
    re.compile(r"var os = navigator\.oscpu;", re.IGNORECASE),
    re.compile(r"var dnt = navigator\.doNotTrack;", re.IGNORECASE),
    re.compile(r'colorGamuts = \["rec2020", "p3", "srgb"\]', re.IGNORECASE),  
    re.compile(r'Boolean\(matchMedia\("\(prefers-reduced-motion: " \+ x \+ "\)"\)\.matches\)', re.IGNORECASE),
    re.compile(r'Boolean\(matchMedia\("\(dynamic-range: " \+ x \+ "\)"\)\.matches\)', re.IGNORECASE),
    re.compile(r'Boolean\(matchMedia\("\(prefers-contrast: " \+ x \+ "\)"\)\.matches\)', re.IGNORECASE),
    re.compile(r'resolve\(\[0, \[Number\(screen\.width\), Number\(screen\.height\)\]\.sort\(\)\.reverse\(\)\.join\("x"\)\]\)', re.IGNORECASE),
    
    
    # re.compile(r'screen\.colorDepth'),
    # re.compile(r'window\.devicePixelRatio'),
    # re.compile(r'navigator\.maxTouchPoints'),
    # re.compile(r'navigator\.cpuClass'),
    # re.compile(r'navigator\.hardwareConcurrency'),
    # re.compile(r'navigator\.deviceMemory'),
    # re.compile(r'navigator\.oscpu'),
    # re.compile(r'navigator\.doNotTrack'), 
    re.compile(r'sourceBuffer'),
    re.compile(r'colorGamut'),
    re.compile(r'reducedMotion'),
    re.compile(r'hdr'),
    re.compile(r'contrast'),
    re.compile(r'invertedColors'),
    re.compile(r'forcedColors'),
    re.compile(r'monochrome'),
    re.compile(r'browserObjects'),
    re.compile(r'new Date\(\)\.getTimezoneOffset\(\)'),
    re.compile(r'Intl\.DateTimeFormat\(\)\.resolvedOptions\(\)\.timeZone'),
    re.compile(r'navigator\.language'),
    # re.compile(r'screen\.width'),
    re.compile(r'performance\.memory\.jsHeapSizeLimit'),
    re.compile(r'new (window\.AudioContext|window\.webkitAudioContext)'),
    # re.compile(r'navigator\.userAgentData'),
    # re.compile(r'canvas\.getContext\("2d"\)'),
    re.compile(r'performance\.now\(\)'),
    # re.compile(r'window\.speechSynthesis'),
    # re.compile(r'window\.ApplePaySession'),
    # re.compile(r'attributionsourceid'),
    # re.compile(r'canvas\.getContext\("webgl"\)'),
    re.compile(r'gl\.getParameter\((gl\.VERSION|gl\.VENDOR)\)'),
    re.compile(r'new FontFace\('),
    # re.compile(r'navigator\.plugins'),
    re.compile(r'navigator\.plugins\.length === 0'),
    # re.compile(r'window\.SharedArrayBuffer'),
    # re.compile(r'navigator\.webdriver'),
    re.compile(r'element\.getAttributeNames\(\)'),
    re.compile(r'new Error\(\)'),
    re.compile(r'navigator\.mimeTypes'),
    re.compile(r'InstallTrigger'),
    # re.compile(r'navigator\.connection\.rtt'),
    re.compile(r'Math\.random'),
    re.compile(r'Notification\.requestPermission')
]

url = 'http://127.0.0.1:5500/index.html'

def scrape_page(url):
    response = requests.get(url)
    script_contents = []
    if response.status_code == 200:
        page_content = response.text
        soup = BeautifulSoup(page_content, 'html.parser')
        scripts = soup.find_all('script')
        
        for script in scripts:
            if script.get('src'):
                script_src = script.get('src')
                print(f'Fetching external script: {script_src}')
                
                if script_src.startswith('http') or script_src.startswith('/'):
                    if not script_src.startswith('http'):
                        script_src = url.rsplit('/', 1)[0] + '/' + script_src.lstrip('/')
                    external_response = requests.get(script_src)
                    if external_response.status_code == 200:
                        script_contents.append(external_response.text)  
                    else:
                        print(f"Error downloading script: {script_src}")
            else:
                if script.string:
                    script_contents.append(script.string)  
    return script_contents

def detect_fingerprinting(script_content):
    detected = set()
    for pattern in fingerprinting_patterns:
        if re.search(pattern, script_content):
            detected.add(pattern.pattern)
    return detected

def generate_fingerprint_id(detected_techniques):
    fingerprint_id = hashlib.sha256(''.join(sorted(detected_techniques)).encode()).hexdigest()
    return fingerprint_id

def display_detected_fingerprints(detected_techniques, fingerprint_id):
    root = tk.Tk()
    root.title("Fingerprinting Detector")

    # Set the background color
    root.configure(background='#f0f0f0')

    # Create a main frame
    main_frame = ttk.Frame(root, padding="10 10 10 10")
    main_frame.pack(fill="both", expand=True)

    # Create a label
    label = ttk.Label(main_frame, text="Detected Fingerprinting Information:", font=("Helvetica", 16))
    label.pack(pady=10)

    # Create a text area
    text_area = scrolledtext.ScrolledText(main_frame, width=80, height=20, font=("Helvetica", 12))
    text_area.pack(padx=10, pady=10)
    

    # Insert the fingerprint ID
    text_area.insert(tk.INSERT, f"\nFingerprint ID: {fingerprint_id}\n")
    # Insert the detected techniques
    text_area.insert(tk.INSERT, "\n")
    for technique in detected_techniques:
        text_area.insert(tk.INSERT, f"- {technique}\n")

    

    # Create a button
    button = ttk.Button(main_frame, text="Close", command=root.destroy)
    button.pack(pady=10)

    root.mainloop()

def main():
    url = 'http://127.0.0.1:5500/index.html'
    scripts = scrape_page(url)
    detected_techniques = set()

    for script_content in scripts:
        if script_content:  
            detected_techniques.update(detect_fingerprinting(script_content))

    with open('fp.js', 'r') as file:
        fp_js_content = file.read()
        detected_techniques.update(detect_fingerprinting(fp_js_content))

    fingerprint_id = generate_fingerprint_id(detected_techniques)
    display_detected_fingerprints(detected_techniques, fingerprint_id)

if __name__ == "__main__":
    main()



    